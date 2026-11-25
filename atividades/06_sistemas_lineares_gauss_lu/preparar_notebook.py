from pathlib import Path

import nbformat


SOURCE = Path(__file__).with_name("solucao.ipynb")
TARGET = SOURCE


ANIMATION_CELL = r'''# Animação da eliminação de Gauss aplicada à matriz aumentada acima
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML, display


def gerar_quadros_gauss(matriz_aumentada, tol=1e-12):
    """Registra os estados da eliminação de Gauss sem pivoteamento."""
    matriz = np.array(matriz_aumentada, dtype=float, copy=True)
    numero_equacoes = matriz.shape[0]

    if matriz.shape[1] != numero_equacoes + 1:
        raise ValueError("A matriz aumentada deve ter n linhas e n + 1 colunas")

    quadros = [{
        "matriz": matriz.copy(),
        "titulo": "Matriz aumentada inicial",
        "descricao": "Começamos com o sistema original.",
        "pivo": None,
        "linha": None,
    }]

    for coluna_pivo in range(numero_equacoes - 1):
        if abs(matriz[coluna_pivo, coluna_pivo]) < tol:
            raise np.linalg.LinAlgError(
                "Pivô nulo: seria necessário aplicar pivoteamento parcial"
            )

        quadros.append({
            "matriz": matriz.copy(),
            "titulo": f"Pivô {coluna_pivo + 1}",
            "descricao": (
                f"Usamos a posição ({coluna_pivo + 1}, {coluna_pivo + 1}) "
                "para zerar os termos abaixo dela."
            ),
            "pivo": (coluna_pivo, coluna_pivo),
            "linha": None,
        })

        for linha in range(coluna_pivo + 1, numero_equacoes):
            multiplicador = matriz[linha, coluna_pivo] / matriz[coluna_pivo, coluna_pivo]
            if abs(multiplicador) < tol:
                continue

            matriz[linha, coluna_pivo:] -= (
                multiplicador * matriz[coluna_pivo, coluna_pivo:]
            )
            matriz[linha, coluna_pivo] = 0.0

            if multiplicador >= 0:
                operacao = (
                    f"L{linha + 1} ← L{linha + 1} − "
                    f"{multiplicador:.4g} L{coluna_pivo + 1}"
                )
            else:
                operacao = (
                    f"L{linha + 1} ← L{linha + 1} + "
                    f"{abs(multiplicador):.4g} L{coluna_pivo + 1}"
                )

            quadros.append({
                "matriz": matriz.copy(),
                "titulo": f"Eliminação na linha {linha + 1}",
                "descricao": operacao,
                "pivo": (coluna_pivo, coluna_pivo),
                "linha": linha,
            })

    quadros.append({
        "matriz": matriz.copy(),
        "titulo": "Sistema triangular superior",
        "descricao": "Agora resolvemos de baixo para cima por substituição regressiva.",
        "pivo": None,
        "linha": None,
    })
    return quadros


quadros = gerar_quadros_gauss(M)
figura, eixo = plt.subplots(figsize=(9, 4.2))


def desenhar_quadro(indice):
    quadro = quadros[indice]
    eixo.clear()
    eixo.axis("off")
    eixo.set_title(quadro["titulo"], fontsize=15, fontweight="bold", pad=12)
    eixo.text(
        0.5,
        0.84,
        quadro["descricao"],
        ha="center",
        va="center",
        fontsize=11,
        transform=eixo.transAxes,
    )

    valores = [[f"{valor:.4g}" for valor in linha] for linha in quadro["matriz"]]
    tabela = eixo.table(
        cellText=valores,
        colLabels=["T1", "T2", "T3", "b"],
        cellLoc="center",
        bbox=[0.08, 0.16, 0.84, 0.56],
    )
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(12)

    for (linha_tabela, coluna_tabela), celula in tabela.get_celld().items():
        celula.set_edgecolor("#5B6573")
        celula.set_linewidth(1.0)
        if linha_tabela == 0:
            celula.set_facecolor("#E8EEF7")
            celula.set_text_props(fontweight="bold")
        else:
            celula.set_facecolor("#F7F9FC")

    if quadro["linha"] is not None:
        for coluna in range(quadro["matriz"].shape[1]):
            tabela[(quadro["linha"] + 1, coluna)].set_facecolor("#FFF2CC")

    if quadro["pivo"] is not None:
        linha_pivo, coluna_pivo = quadro["pivo"]
        tabela[(linha_pivo + 1, coluna_pivo)].set_facecolor("#4C78A8")
        tabela[(linha_pivo + 1, coluna_pivo)].set_text_props(
            color="white", fontweight="bold"
        )

    eixo.text(
        0.5,
        0.06,
        f"Quadro {indice + 1} de {len(quadros)}",
        ha="center",
        color="#5B6573",
        fontsize=10,
        transform=eixo.transAxes,
    )


animacao = FuncAnimation(
    figura,
    desenhar_quadro,
    frames=len(quadros),
    interval=1500,
    repeat=True,
)
plt.close(figura)
html_animacao = animacao.to_jshtml(default_mode="loop").replace(
    "<img id=", '<img alt="Quadro da eliminação de Gauss" id='
)
display(HTML(html_animacao))

# Conferência numérica do último quadro da animação
M_triangular = quadros[-1]["matriz"]
U_animacao = M_triangular[:, :-1]
c_animacao = M_triangular[:, -1]
solucao_animacao = np.zeros(len(c_animacao))
for i in range(len(c_animacao) - 1, -1, -1):
    solucao_animacao[i] = (
        c_animacao[i] - U_animacao[i, i + 1:] @ solucao_animacao[i + 1:]
    ) / U_animacao[i, i]

norma_residuo = np.linalg.norm(A @ solucao_animacao - b)
if norma_residuo < 1e-12:
    norma_residuo = 0.0

print("Matriz triangular superior final:\n", M_triangular)
print("Solução [T1, T2, T3]:", solucao_animacao)
print(f"Norma do resíduo: {norma_residuo:.3e}")'''


def main():
    notebook = nbformat.read(SOURCE, as_version=4)
    notebook.cells[6].source = ANIMATION_CELL
    notebook.cells[6].outputs = []
    notebook.cells[6].execution_count = None

    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None

    nbformat.validate(notebook)
    nbformat.write(notebook, TARGET)
    print(TARGET.resolve())


if __name__ == "__main__":
    main()
