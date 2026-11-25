# Portfólio acadêmico de Cálculo Numérico — plano de implementação

**Objetivo:** organizar, documentar, validar e publicar as dez entradas acadêmicas identificadas, preservando o histórico remoto e os artefatos originais.

**Especificação:** `docs/superpowers/specs/2026-11-25-portfolio-calculo-numerico-design.md`

## Estrutura de arquivos

- `README.md`: apresentação, índice, tabela de atividades, métodos, ferramentas e reprodução.
- `.gitignore`: exclusão de ambientes, caches, temporários e arquivos do sistema.
- `requirements.txt`: dependências comuns dos notebooks e testes.
- `atividades/NN_nome/README.md`: documentação individual.
- `atividades/NN_nome/`: notebooks, enunciados, figuras, resultados e scripts pertencentes à atividade.
- `docs/auditoria_tecnica.md`: limitações, riscos e validações reproduzíveis.
- `tests/test_portfolio.py`: estrutura, links locais e ausência de caminhos/publicações indevidas.

## Tarefa 1 — Reconectar o histórico e preservar fontes

- [ ] Copiar os metadados Git do clone temporário verificado para o workspace sem sobrescrever arquivos locais.
- [ ] Recuperar os seis arquivos rastreados pelo remoto sob nomes seguros e classificá-los por atividade.
- [ ] Confirmar `origin`, branch `main`, estado inicial e hashes relevantes.
- [ ] Criar `.gitignore` antes de adicionar arquivos.

## Tarefa 2 — Reorganizar as dez atividades

- [ ] Criar as pastas numeradas conforme o design.
- [ ] Mover notebooks, PDFs, HTML, figuras, GIFs, CSV e scripts por domínio, preservando nomes descritivos.
- [ ] Manter versões original/preenchida, entrega/alternativa e enunciado/solução claramente diferenciadas.
- [ ] Excluir da publicação apenas intermediários reproduzíveis, caches, ambiente virtual e arquivos do sistema; manter os originais em disco até a conferência final.

## Tarefa 3 — Corrigir reprodutibilidade e erro confirmado

- [ ] Em `atividades/07_sistemas_lineares_planos/`, calcular os postos de `A` e `[A|b]` com uma tolerância absoluta comum derivada da matriz aumentada.
- [ ] Adicionar regressões para sistema reescalado por `1e-12` e vetor independente de grande magnitude.
- [ ] Ajustar imports/caminhos dos scripts movidos e fontes dos geradores sem alterar resultados numéricos.
- [ ] Criar `requirements.txt` com as bibliotecas efetivamente usadas.

## Tarefa 4 — Documentar individualmente

- [ ] Escrever dez READMEs com objetivo, teoria, equações, algoritmo, resultados, discussão, execução e limitações aplicáveis.
- [ ] Incorporar figuras leves existentes com texto alternativo e oferecer GIFs/PDFs/dashboards por link.
- [ ] Creditar materiais docentes onde os próprios notebooks apontam para fontes externas.
- [ ] Não promover matrículas ou identificações conflitantes à documentação principal.

## Tarefa 5 — Construir a página principal e auditoria

- [ ] Escrever o README raiz com cabeçalho acadêmico, badges sóbrios, objetivos, índice, tabela das dez entradas, mapa dos métodos, Mermaid, ferramentas e reprodução.
- [ ] Criar `docs/auditoria_tecnica.md` com testes, limitações e arquivos não publicados.
- [ ] Verificar todos os links e imagens relativos.

## Tarefa 6 — Validação

- [ ] Executar os 10 testes da raiz e os 28 testes da Atividade III em cópia/ambiente controlado quando houver escrita de artefatos.
- [ ] Executar novos testes de estrutura, links e regressões do classificador.
- [ ] Validar JSON de todos os notebooks e ausência de outputs de erro.
- [ ] Renderizar ou inspecionar Markdown crítico e conferir imagens/GIFs/PDFs.
- [ ] Revisar `git diff`, arquivos grandes, dados sensíveis e caminhos absolutos.

## Tarefa 7 — Git e publicação

- [ ] Criar commits descritivos por organização, documentação e validação/correções.
- [ ] Fazer push sem force para `origin/main`.
- [ ] Consultar novamente o remoto e confirmar o commit publicado.
- [ ] Produzir relatório final com contagens, estrutura, arquivos, testes e limitações.

## Foco de revisão

- Renomes em sistema de arquivos sensível a maiúsculas/minúsculas não podem sobrescrever `Atividade1.ipynb`/`atividade1.ipynb`.
- Links Colab herdados não devem ser apresentados como links da solução local.
- Testes que escrevem CSV/PNG/notebooks devem rodar em cópia ou ter seus efeitos revisados.
- Informações pessoais já existentes nos originais não devem ser repetidas na página principal.
- O classificador de planos deve ser invariável a reescala e nunca produzir `rank([A|b]) < rank(A)`.

