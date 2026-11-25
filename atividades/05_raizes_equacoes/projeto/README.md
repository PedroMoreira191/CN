# Atividade Prática III — Cálculo Numérico

## Objetivo

Implementar manualmente os métodos da Bisseção, de Newton e da Secante, aplicá-los a quatro funções e comparar convergência, precisão, robustez e dependência dos valores iniciais. O notebook também gera três animações GIF e os materiais para o dashboard solicitado no Mathcha.

## Arquivos

```text
atividade_calculo_numerico/
├── atividade_calculo_numerico.ipynb
├── resultados.csv
├── dashboard_preview.png
├── GUIA_MATHCHA.md
├── README.md
└── gifs/
    ├── bissecao_f2.gif
    ├── newton_f2.gif
    └── secante_f2.gif
```

`scripts/build_notebook.py` e `tests/` são materiais de construção e verificação; não são necessários para abrir o notebook no Colab.

## Dependências

O notebook usa bibliotecas disponíveis por padrão no Google Colab:

- NumPy;
- pandas;
- Matplotlib;
- Pillow;
- IPython.

## Como executar

### Google Colab

1. Acesse [Google Colab](https://colab.research.google.com/).
2. Escolha **Arquivo → Fazer upload de notebook**.
3. Selecione `atividade_calculo_numerico.ipynb`.
4. Escolha **Ambiente de execução → Executar tudo**.
5. Baixe `resultados.csv`, `dashboard_preview.png` e a pasta `gifs/` gerados na sessão.

### Jupyter local

Abra um terminal nesta pasta e execute:

```bash
jupyter nbconvert --execute --to notebook --inplace atividade_calculo_numerico.ipynb
```

O notebook usa caminhos relativos e cria automaticamente a pasta `gifs/`.

## Regenerar os GIFs

Execute o notebook integralmente ou rode, em ordem, as células até a seção **9. Animações**. Os arquivos são substituídos de forma determinística:

- `bissecao_f2.gif`: mostra o intervalo e sua redução em cada iteração;
- `newton_f2.gif`: mostra o ponto atual, a tangente e a nova interseção com o eixo x;
- `secante_f2.gif`: mostra os dois pontos, a reta secante e a nova aproximação.

As três animações usam `f2(x)=x³-x-2` para permitir comparação direta.

## Critério de parada

São usados `tol=1e-6` e `max_iter=100`. Depois da primeira aproximação comparável, a convergência exige simultaneamente:

```text
abs(x_novo - x_anterior) < 1e-6
e
abs(f(x_novo)) < 1e-6
```

Newton também interrompe quando `abs(f'(x)) < 1e-12`; a Secante faz o mesmo quando seu denominador tem módulo menor que `1e-12`. A Bisseção rejeita intervalos sem mudança de sinal.

## Resultados principais

Os 12 casos solicitados convergem. Newton usa 3–4 iterações, a Secante 5–7 e a Bisseção 20–22. O experimento adicional de `f4` com `x0=0` é mantido separado e exibe o ciclo `0 → 1 → 0`.

## Google Colab

**Link histórico (acesso atual não verificado):** [Abrir notebook no Google Colab ↗](https://colab.research.google.com/drive/1FAhXt0_V3iNqLZA3MsjNvorEmtYeY4mf)

## Dashboard no Mathcha

**Link histórico (acesso atual não verificado):** [Abrir dashboard no Mathcha ↗](https://www.mathcha.io/editor/L331mtnjTGxs6oV6VmSDozZ3pSkn3BBLH4QPlx1)

O dashboard contém a síntese executiva, a tabela comparativa dos 12 testes, as três animações e as conclusões. Os arquivos locais permanecem a fonte reproduzível; confirme as permissões dos dois serviços antes de entregar os links.
