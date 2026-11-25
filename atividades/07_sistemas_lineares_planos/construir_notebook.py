from contextlib import redirect_stdout
from io import BytesIO, StringIO
from pathlib import Path
from unittest.mock import patch
import base64

import matplotlib.pyplot as plt
import nbformat
from IPython import display as ipython_display


OUTPUT = Path(__file__).with_name("planos_interativo.ipynb")


CORE_CODE = r'''import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

np.set_printoptions(precision=6, suppress=True)


def analisar_sistema(A, b, tolerancia=1e-10):
    """Classifica Ax=b e calcula solução, postos, determinante e resíduo."""
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float).reshape(-1)

    if A.shape != (3, 3) or b.shape != (3,):
        raise ValueError("Use uma matriz A 3 x 3 e um vetor b com 3 elementos.")
    if not np.all(np.isfinite(A)) or not np.all(np.isfinite(b)):
        raise ValueError("Todos os valores de A e b devem ser números finitos.")

    # Normalizar A e b conjuntamente evita underflow/overflow e mantém a
    # classificação invariável quando todas as equações mudam de escala.
    escala_sistema = max(
        float(np.max(np.abs(A))),
        float(np.max(np.abs(b))),
    )
    if escala_sistema == 0.0:
        A_normalizada = A.copy()
        b_normalizado = b.copy()
    else:
        A_normalizada = A / escala_sistema
        b_normalizado = b / escala_sistema

    valores_singulares = np.linalg.svd(A_normalizada, compute_uv=False)
    escala_A = valores_singulares[0] if valores_singulares.size else 0.0
    limiar_A = tolerancia * escala_A
    posto_A = int(np.count_nonzero(valores_singulares > limiar_A))

    # Para matrizes singulares, a consistência é verificada pelo resíduo da
    # solução de mínimos quadrados. Isso evita comparar A e [A|b] com escalas
    # diferentes quando b é muito maior que os coeficientes de A.
    solucao_referencia, *_ = np.linalg.lstsq(
        A_normalizada, b_normalizado, rcond=tolerancia
    )
    residuo_normalizado = float(
        np.linalg.norm(A_normalizada @ solucao_referencia - b_normalizado)
    )
    residuo_referencia = residuo_normalizado * escala_sistema
    escala_residuo = max(
        float(
            np.linalg.norm(A_normalizada, ord=2)
            * np.linalg.norm(solucao_referencia)
        ),
        float(np.linalg.norm(b_normalizado)),
        np.finfo(float).tiny,
    )
    consistente = residuo_normalizado <= tolerancia * escala_residuo
    posto_aumentada = posto_A if consistente else min(posto_A + 1, 3)
    determinante = float(np.linalg.det(A))

    resultado = {
        "posto_A": posto_A,
        "posto_aumentada": posto_aumentada,
        "determinante": determinante,
        "condicionamento": float("inf"),
        "solucao": None,
        "norma_residuo": None,
    }

    if posto_A < posto_aumentada:
        resultado["classificacao"] = "Sistema incompatível"
    elif posto_A < 3:
        resultado["classificacao"] = "Infinitas soluções"
        resultado["solucao_referencia"] = solucao_referencia
        resultado["norma_residuo"] = residuo_referencia
    else:
        solucao = np.linalg.solve(A_normalizada, b_normalizado)
        resultado["classificacao"] = "Solução única"
        resultado["solucao"] = solucao
        resultado["norma_residuo"] = (
            float(np.linalg.norm(A_normalizada @ solucao - b_normalizado))
            * escala_sistema
        )
        resultado["condicionamento"] = float(np.linalg.cond(A))

    return resultado


def malha_plano(normal, termo_independente, limite=6, pontos=35):
    """Cria uma malha para ax+by+cz=d, inclusive para planos verticais."""
    normal = np.asarray(normal, dtype=float).reshape(3)
    escala_equacao = float(np.max(np.abs(normal)))
    if escala_equacao == 0.0:
        raise ValueError("Uma equação com normal nula não define um plano.")
    normal = normal / escala_equacao
    termo_independente = termo_independente / escala_equacao

    eixo_dependente = int(np.argmax(np.abs(normal)))
    eixos_livres = [eixo for eixo in range(3) if eixo != eixo_dependente]
    valores = np.linspace(-limite, limite, pontos)
    primeira_livre, segunda_livre = np.meshgrid(valores, valores)
    coordenadas = [None, None, None]
    coordenadas[eixos_livres[0]] = primeira_livre
    coordenadas[eixos_livres[1]] = segunda_livre
    coordenadas[eixo_dependente] = (
        termo_independente
        - normal[eixos_livres[0]] * primeira_livre
        - normal[eixos_livres[1]] * segunda_livre
    ) / normal[eixo_dependente]
    return tuple(coordenadas)


def limite_sugerido(A, b, resultado):
    """Escolhe limites simétricos que incluam a interseção e os interceptos úteis."""
    candidatos = [5.0]
    if resultado.get("solucao") is not None:
        candidatos.append(float(np.max(np.abs(resultado["solucao"]))) * 1.6 + 1.0)
    for linha, termo in zip(A, b):
        escala_equacao = float(np.max(np.abs(linha)))
        if escala_equacao == 0.0:
            continue
        linha_normalizada = linha / escala_equacao
        termo_normalizado = termo / escala_equacao
        for coeficiente in linha_normalizada:
            if coeficiente != 0.0:
                candidatos.append(
                    abs(float(termo_normalizado / coeficiente)) * 1.15
                )
    return float(np.clip(max(candidatos), 5.0, 20.0))


def formatar_equacao(normal, termo_independente):
    nomes = ("x", "y", "z")
    partes = []
    for coeficiente, nome in zip(normal, nomes):
        sinal = "+" if coeficiente >= 0 and partes else ""
        partes.append(f"{sinal}{coeficiente:g}{nome}")
    return " ".join(partes).replace("+-", "-") + f" = {termo_independente:g}"


def plotar_planos(A, b, resultado=None, limite=None, pontos=35):
    """Representa os três planos e destaca a interseção quando ela é única."""
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float).reshape(-1)
    if resultado is None:
        resultado = analisar_sistema(A, b)
    if limite is None:
        limite = limite_sugerido(A, b, resultado)

    cores = ("#2563EB", "#D97706", "#059669")
    figura = plt.figure(figsize=(10, 8), facecolor="#F8FAFC")
    eixos = figura.add_subplot(111, projection="3d")
    eixos.set_facecolor("#F8FAFC")
    itens_legenda = []

    for indice, (normal, termo_independente, cor) in enumerate(zip(A, b, cores)):
        if not np.any(normal):
            continue
        X, Y, Z = malha_plano(normal, termo_independente, limite, pontos)
        eixos.plot_surface(
            X,
            Y,
            Z,
            color=cor,
            alpha=0.34,
            edgecolor=cor,
            linewidth=0.28,
            antialiased=True,
            shade=False,
        )
        itens_legenda.append(
            Patch(
                facecolor=cor,
                edgecolor=cor,
                alpha=0.55,
                label=f"P{indice + 1}: {formatar_equacao(normal, termo_independente)}",
            )
        )

    if resultado.get("solucao") is not None:
        x, y, z = resultado["solucao"]
        eixos.scatter(
            [x],
            [y],
            [z],
            s=150,
            c="#111827",
            marker="X",
            edgecolors="white",
            linewidths=1.3,
            depthshade=False,
        )
        eixos.text(
            x,
            y,
            z,
            f"  Interseção ({x:.3g}, {y:.3g}, {z:.3g})",
            color="#111827",
            fontsize=10,
            fontweight="bold",
        )
        itens_legenda.append(
            Patch(facecolor="#111827", edgecolor="#111827", label="Interseção única")
        )

    eixos.set_xlim(-limite, limite)
    eixos.set_ylim(-limite, limite)
    eixos.set_zlim(-limite, limite)
    eixos.set_box_aspect((1, 1, 1))
    eixos.set_xlabel("x", labelpad=8)
    eixos.set_ylabel("y", labelpad=8)
    eixos.set_zlabel("z", labelpad=8)
    eixos.set_title(
        f"Planos do sistema Ax = b — {resultado['classificacao']}",
        fontsize=15,
        fontweight="bold",
        color="#111827",
        pad=18,
    )
    eixos.view_init(elev=24, azim=38)
    eixos.grid(True, alpha=0.22)
    if itens_legenda:
        eixos.legend(
            handles=itens_legenda,
            loc="upper left",
            bbox_to_anchor=(-0.02, 1.02),
            frameon=False,
            fontsize=9,
        )
    figura.tight_layout()
    return figura, eixos
'''


PREVIEW_CODE = r'''A_inicial = np.array([
    [ 2.,  1., -1.],
    [-3., -1.,  2.],
    [-2.,  1.,  2.],
])
b_inicial = np.array([8., -11., -3.])

resultado_inicial = analisar_sistema(A_inicial, b_inicial)
print("Classificação:", resultado_inicial["classificacao"])
print("Solução [x, y, z]:", resultado_inicial["solucao"])
print("Norma do resíduo:", f'{resultado_inicial["norma_residuo"]:.3e}')

figura, eixos = plotar_planos(A_inicial, b_inicial, resultado_inicial)
plt.show()
'''


INTERFACE_CODE = r'''# Interface editável: todos os 9 valores de A e os 3 valores de b podem ser alterados.
if globals().get("_MODO_VALIDACAO_LOCAL", False):
    widgets = None
else:
    try:
        import ipywidgets as widgets
        from IPython.display import HTML, clear_output, display
    except ImportError:
        widgets = None

if widgets is None:
    print(
        "A interface usa ipywidgets, já disponível no Google Colab. "
        "Abra este arquivo no Colab e execute todas as células."
    )
else:
    try:
        from google.colab import output
        output.enable_custom_widget_manager()
    except ImportError:
        pass

    A_padrao = np.array([[2., 1., -1.], [-3., -1., 2.], [-2., 1., 2.]])
    b_padrao = np.array([8., -11., -3.])

    campos_A = [
        [
            widgets.FloatText(
                value=float(A_padrao[i, j]),
                description=f"a{i + 1}{j + 1}",
                layout=widgets.Layout(width="130px"),
            )
            for j in range(3)
        ]
        for i in range(3)
    ]
    campos_b = [
        widgets.FloatText(
            value=float(b_padrao[i]),
            description=f"b{i + 1}",
            layout=widgets.Layout(width="130px"),
        )
        for i in range(3)
    ]

    linhas = []
    for i in range(3):
        linhas.append(
            widgets.HBox(
                campos_A[i]
                + [widgets.HTML("<b style='font-size:20px'>│</b>"), campos_b[i]],
                layout=widgets.Layout(gap="6px"),
            )
        )

    limite_visual = widgets.FloatSlider(
        value=6.0,
        min=2.0,
        max=20.0,
        step=0.5,
        description="Limite dos eixos",
        continuous_update=False,
        style={"description_width": "initial"},
        layout=widgets.Layout(width="520px"),
    )
    botao_atualizar = widgets.Button(
        description="Resolver e atualizar gráfico",
        button_style="primary",
        icon="refresh",
        layout=widgets.Layout(width="250px"),
    )
    botao_restaurar = widgets.Button(
        description="Restaurar exemplo",
        icon="undo",
        layout=widgets.Layout(width="180px"),
    )
    saida = widgets.Output()

    def ler_entradas():
        A_usuario = np.array(
            [[campos_A[i][j].value for j in range(3)] for i in range(3)],
            dtype=float,
        )
        b_usuario = np.array([campo.value for campo in campos_b], dtype=float)
        return A_usuario, b_usuario

    def atualizar(_=None):
        with saida:
            clear_output(wait=True)
            try:
                A_usuario, b_usuario = ler_entradas()
                resultado = analisar_sistema(A_usuario, b_usuario)
                classificacao = resultado["classificacao"]
                if resultado["solucao"] is not None:
                    x, y, z = resultado["solucao"]
                    solucao_texto = f"x={x:.6g}, y={y:.6g}, z={z:.6g}"
                else:
                    solucao_texto = "não existe uma solução única"

                condicionamento = resultado["condicionamento"]
                cond_texto = "∞" if not np.isfinite(condicionamento) else f"{condicionamento:.3g}"
                residuo = resultado["norma_residuo"]
                residuo_texto = "—" if residuo is None else f"{residuo:.3e}"

                display(HTML(f"""
                <div style="padding:12px 16px;border-left:5px solid #2563eb;background:#eff6ff;margin:8px 0 16px 0">
                  <b>{classificacao}</b><br>
                  {solucao_texto}<br>
                  det(A)={resultado['determinante']:.6g} &nbsp;|&nbsp;
                  posto(A)={resultado['posto_A']} &nbsp;|&nbsp;
                  posto([A|b])={resultado['posto_aumentada']} &nbsp;|&nbsp;
                  cond(A)={cond_texto} &nbsp;|&nbsp; resíduo={residuo_texto}
                </div>
                """))
                figura, _ = plotar_planos(
                    A_usuario,
                    b_usuario,
                    resultado,
                    limite=float(limite_visual.value),
                )
                plt.show()
            except Exception as erro:
                display(HTML(f"<div style='color:#b91c1c'><b>Erro:</b> {erro}</div>"))

    def restaurar(_=None):
        for i in range(3):
            for j in range(3):
                campos_A[i][j].value = float(A_padrao[i, j])
            campos_b[i].value = float(b_padrao[i])
        limite_visual.value = 6.0
        atualizar()

    botao_atualizar.on_click(atualizar)
    botao_restaurar.on_click(restaurar)

    display(
        widgets.VBox(
            [
                widgets.HTML(
                    "<h3>Edite A e b</h3>"
                    "<p>Cada linha representa uma equação "
                    "<code>aᵢ₁x + aᵢ₂y + aᵢ₃z = bᵢ</code>.</p>"
                ),
                widgets.VBox(linhas, layout=widgets.Layout(gap="7px")),
                limite_visual,
                widgets.HBox([botao_atualizar, botao_restaurar]),
                saida,
            ],
            layout=widgets.Layout(gap="10px"),
        )
    )
    atualizar()
'''


CHECKS_CODE = r'''# Checagens rápidas de consistência para o exemplo inicial
checagem = analisar_sistema(A_inicial, b_inicial)
assert checagem["classificacao"] == "Solução única"
assert np.allclose(checagem["solucao"], [2., 3., -1.])
assert np.linalg.norm(A_inicial @ checagem["solucao"] - b_inicial) < 1e-12

for normal, termo in zip(A_inicial, b_inicial):
    X, Y, Z = malha_plano(normal, termo, limite=6, pontos=15)
    assert np.max(np.abs(normal[0] * X + normal[1] * Y + normal[2] * Z - termo)) < 1e-10

print("Checagens concluídas: solução, resíduo e superfícies dos três planos estão consistentes.")
'''


def markdown_cell(source):
    return nbformat.v4.new_markdown_cell(source=source)


def code_cell(source, tag):
    return nbformat.v4.new_code_cell(
        source=source,
        metadata={"tags": [tag]},
    )


def capture_display(value):
    if isinstance(value, ipython_display.HTML):
        return nbformat.v4.new_output(
            "display_data",
            data={"text/html": value.data, "text/plain": "<HTML>"},
            metadata={},
        )
    return nbformat.v4.new_output(
        "display_data",
        data={"text/plain": repr(value)},
        metadata={},
    )


def execute_for_saved_outputs(notebook):
    namespace = {"_MODO_VALIDACAO_LOCAL": True}
    execution_count = 1

    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue

        cell.execution_count = execution_count
        execution_count += 1
        cell.outputs = []
        captured_text = StringIO()
        displayed = []

        with patch.object(
            ipython_display,
            "display",
            side_effect=lambda value: displayed.append(value),
        ):
            with patch.object(plt, "show", return_value=None):
                with redirect_stdout(captured_text):
                    exec(compile(cell.source, f"<cell-{execution_count}>", "exec"), namespace)

        if captured_text.getvalue():
            cell.outputs.append(
                nbformat.v4.new_output(
                    "stream",
                    name="stdout",
                    text=captured_text.getvalue(),
                )
            )
        cell.outputs.extend(capture_display(value) for value in displayed)

        if "preview" in cell.metadata.get("tags", []):
            buffer = BytesIO()
            namespace["figura"].savefig(
                buffer,
                format="png",
                dpi=140,
                bbox_inches="tight",
                facecolor=namespace["figura"].get_facecolor(),
            )
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
            alt_text = (
                "Três planos do sistema linear Ax=b com interseção única "
                "no ponto x=2, y=3, z=-1."
            )
            cell.outputs.append(
                nbformat.v4.new_output(
                    "display_data",
                    data={
                        "image/png": encoded,
                        "text/html": (
                            f'<img src="data:image/png;base64,{encoded}" '
                            f'alt="{alt_text}" style="max-width:100%;height:auto">'
                        ),
                        "text/plain": "<Figure: planos do sistema>",
                    },
                    metadata={},
                )
            )
            plt.close(namespace["figura"])


def build_notebook(output_path=OUTPUT):
    output_path = Path(output_path)
    notebook = nbformat.v4.new_notebook()
    notebook.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.x"},
        "colab": {
            "name": output_path.name,
            "provenance": [],
            "toc_visible": True,
        },
    }
    notebook.cells = [
        markdown_cell(
            """# Planos de um sistema linear 3 × 3

**Notebook interativo compatível com o Google Colab**

Edite todos os elementos da matriz $A$ e do vetor $b$, resolva $A\\mathbf{x}=\\mathbf{b}$ e visualize geometricamente as três equações como planos no espaço."""
        ),
        markdown_cell(
            """## Objetivo

Para um sistema com três incógnitas,

$$
\\begin{aligned}
a_{11}x+a_{12}y+a_{13}z &= b_1,\\\\
a_{21}x+a_{22}y+a_{23}z &= b_2,\\\\
a_{31}x+a_{32}y+a_{33}z &= b_3,
\\end{aligned}
$$

cada equação representa um plano em $\\mathbb{R}^3$. Uma solução única aparece como o ponto de interseção comum aos três planos. O notebook também identifica sistemas incompatíveis e sistemas com infinitas soluções."""
        ),
        markdown_cell("## Preparação e funções numéricas"),
        code_cell(CORE_CODE, "core"),
        markdown_cell(
            """## Exemplo inicial

O exemplo abaixo é o mesmo utilizado na animação da eliminação de Gauss. A solução exata é $(x,y,z)=(2,3,-1)$."""
        ),
        code_cell(PREVIEW_CODE, "preview"),
        markdown_cell(
            """## Interface interativa

1. Execute a célula abaixo no Google Colab.
2. Altere qualquer um dos nove coeficientes de $A$ e qualquer elemento de $b$.
3. Clique em **Resolver e atualizar gráfico**.
4. Ajuste o limite dos eixos quando os planos ou a interseção ficarem fora da região visível."""
        ),
        code_cell(INTERFACE_CODE, "interface-colab"),
        markdown_cell("## Checagens"),
        code_cell(CHECKS_CODE, "checks"),
        markdown_cell(
            """## Como interpretar o gráfico

- **Solução única:** os três planos se encontram em um único ponto, marcado com **X**.
- **Infinitas soluções:** os planos compartilham uma reta ou coincidem de maneira compatível.
- **Sistema incompatível:** não existe um ponto comum aos três planos.
- Uma matriz com número de condicionamento muito alto pode produzir uma solução sensível a pequenas alterações nos coeficientes."""
        ),
    ]

    execute_for_saved_outputs(notebook)
    nbformat.validate(notebook)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, output_path)
    return output_path


if __name__ == "__main__":
    print(build_notebook().resolve())
