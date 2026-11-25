# Guia de montagem do dashboard no Mathcha

**Link histórico do dashboard (acesso atual não verificado):** [Abrir no Mathcha ↗](https://www.mathcha.io/editor/L331mtnjTGxs6oV6VmSDozZ3pSkn3BBLH4QPlx1)

## Formato geral

Use um documento vertical de **1200 px** de largura, fundo branco ou cinza muito claro e margens laterais uniformes. A ordem deve ser: acesso ao código → método → visualização → evidência numérica → conclusões.

Paleta:

- azul-petróleo `#155E75` para títulos e curva;
- laranja `#F97316` para construções geométricas;
- verde `#15803D` apenas para novas aproximações e convergência;
- cinza `#334155` para texto;
- bordas `#CBD5E1`.

Use fonte sem serifa no corpo e negrito apenas em títulos ou números principais.

## Bloco 1 — Cabeçalho (1200 × 220 px)

**Título:** `Cálculo Numérico — Atividade Prática III`  
**Subtítulo:** `Raízes por Bisseção, Newton e Secante`

Logo abaixo, insira o texto clicável:

[`Abrir notebook no Google Colab ↗`](https://colab.research.google.com/drive/1FAhXt0_V3iNqLZA3MsjNvorEmtYeY4mf)

A URL acima foi registrada na entrega original, mas suas permissões atuais não foram verificadas. Para configurar o **hyperlink** no Mathcha, selecione o texto, pressione `⌘K`/`Ctrl+K`, cole a URL e escolha **Apply**; confirme o acesso em janela anônima antes da entrega.

## Bloco 2 — Problema e métodos (1200 × 300 px)

Texto curto à esquerda:

> Encontrar aproximações para f(x)=0 usando três métodos iterativos.

Três cartões à direita:

1. **Bisseção — intervalo:** `c = (a+b)/2`;
2. **Newton — tangente:** `x_(k+1) = x_k - f(x_k)/f'(x_k)`;
3. **Secante — dois pontos:** fórmula completa da Secante disponível no notebook.

## Bloco 3 — Visualização (três caixas de 380 × 360 px)

Insira, lado a lado:

1. `gifs/bissecao_f2.gif` — título `Bisseção — redução do intervalo`;
2. `gifs/newton_f2.gif` — título `Newton — reta tangente`;
3. `gifs/secante_f2.gif` — título `Secante — reta secante`.

Legenda única sob a linha:

> Aproximações para f₂(x)=x³−x−2; tolerância 10⁻⁶.

No Mathcha, pressione `\`, escolha `image-container` e use **Upload and use From Library** para cada GIF. Preserve também os três arquivos GIF como anexos originais da entrega, pois uma exportação estática do documento mostra apenas um quadro.

## Bloco 4 — Resultados dos 12 testes (1200 × 1000 px)

Copie de `resultados.csv` as colunas:

`Função | Método | Valores iniciais | Raiz aproximada | |f(x)| final | Iterações | Resultado`

Use 12 linhas agrupadas por função, três métodos por grupo. Mostre 10 casas decimais na raiz e notação científica no resíduo. Use verde somente na palavra `Convergiu`; não pinte células numéricas.

## Bloco 5 — Leituras principais (1200 × 260 px)

Copie estas cinco conclusões:

- Os 12 casos principais convergiram e satisfizeram `|f(x)| < 10⁻⁶`.
- Newton foi o mais rápido: 3–4 iterações.
- A Secante precisou de 5–7 iterações e dispensou derivadas analíticas.
- A Bisseção usou 20–22 iterações, mantendo a raiz delimitada.
- Em `f4`, Newton converge com `x0=-2`, mas entra no ciclo `0 → 1 → 0` com `x0=0`.

## Bloco 6 — Rodapé (1200 × 80 px)

`Tolerância: 10⁻⁶ · Máximo: 100 iterações · Critério: passo E resíduo`

## Arquivos a inserir

| Posição | Arquivo |
|---|---|
| Visualização 1 | `gifs/bissecao_f2.gif` |
| Visualização 2 | `gifs/newton_f2.gif` |
| Visualização 3 | `gifs/secante_f2.gif` |
| Tabela | `resultados.csv` |
| Referência de composição | `dashboard_preview.png` |
| Código e relatório | `atividade_calculo_numerico.ipynb` |

## Checklist de montagem

- [ ] Link **Abrir notebook no Google Colab** funciona em janela anônima.
- [ ] Três GIFs estão visíveis e também anexados como arquivos originais.
- [ ] Tabela contém exatamente 12 linhas e sete colunas.
- [ ] Raízes têm pelo menos 10 casas decimais.
- [ ] Resíduos aparecem em notação científica.
- [ ] Caso adicional de `f4` não substitui os resultados principais.
- [ ] Documento foi compartilhado por link no Mathcha.

Documentação oficial útil: [Picture Box](https://www.mathcha.io/documentation/picture-box/) e [Basic Editing](https://www.mathcha.io/documentation/components/basic-editing/).
