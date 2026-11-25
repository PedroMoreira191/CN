# Importa a biblioteca math caso esta célula seja executada separadamente.
import math

# Cria um dicionário com os valores de referência.
valores = {
    "raiz de 2": math.sqrt(2.0),
    "pi": math.pi,
    "e": math.e
}

# Define as quantidades de casas decimais que serão avaliadas.
casas_testadas = [1, 2, 4, 6]

# Percorre cada constante armazenada no dicionário.
for nome, referencia in valores.items():
    # Exibe um título para identificar a constante analisada.
    print(f"\n--- {nome} ---")

    # Percorre cada quantidade de casas decimais.
    for casas in casas_testadas:
        # TODO: use round para calcular a aproximação.
        aproximacao = round(referencia, casas)

        # TODO: calcule o erro absoluto.
        erro_abs = abs(referencia - aproximacao)

        # TODO: calcule o erro relativo.
        erro_rel = abs(referencia - aproximacao) / abs(referencia)

        # Exibe os valores preenchidos pelo estudante.
        print(
            f"casas={casas} | aproximação={aproximacao} | "
            f"erro absoluto={erro_abs} | erro relativo={erro_rel}"
        )