# Auditoria técnica e limitações

## Escopo

O inventário consolidou notebooks, PDFs, scripts, figuras, animações, prévias HTML e resultados CSV disponíveis localmente e no histórico remoto. A organização não cria atividades nem resultados ausentes.

## Correções aplicadas

- o classificador da atividade de planos passou a usar posto relativo à escala de `A` e consistência pelo resíduo de mínimos quadrados;
- foram adicionadas regressões para sistemas reescalados por `10^{-12}` e vetores independentes de grande magnitude;
- caminhos de notebooks auxiliares foram tornados relativos;
- fontes do gerador de GIF passaram a ser localizadas pelo Matplotlib, sem caminhos da máquina original;
- caches, `.venv`, `.DS_Store` e intermediários de PDF foram excluídos da publicação por `.gitignore`.

## Observações de reprodutibilidade

- A Atividade III regrava CSV, GIFs ou prévia ao executar partes da suíte; valide mudanças no `git diff`.
- Os dois notebooks de biofluidodinâmica produzem nomes de saída iguais; a pasta `figuras/` preserva as saídas da versão marcada como entrega.
- A prévia HTML de planos é estática. A interação exige executar o notebook com `ipywidgets`.
- Os HTML exportados usam RequireJS/MathJax por CDN; os notebooks permanecem a fonte reproduzível.
- Executores que usam `exec` devem ser aplicados somente a notebooks confiáveis.

## Limitações de conteúdo

- A atividade local de interpolação possui código, mas não saídas salvas.
- O notebook de integração contém uma saída de tabela anterior ao código atual e não tem o gráfico final salvo.
- O PDF de Gauss–Seidel possui uma versão completa e outra compactada; ambas foram mantidas.
- Links externos existentes em materiais históricos não foram considerados comprovação de acesso público.

## Privacidade

Alguns originais já publicados contêm nomes e matrículas de colaboradores. Esses dados foram preservados nos arquivos históricos, mas não foram replicados no README principal. Antes de tornar o repositório público, recomenda-se confirmar com os colaboradores se a permanência desses dados é apropriada.

