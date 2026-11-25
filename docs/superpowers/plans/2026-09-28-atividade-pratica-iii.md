# Atividade Prática III de Cálculo Numérico — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar uma entrega acadêmica completa e verificada sobre Bisseção, Newton e Secante, pronta para execução no Google Colab e montagem de um dashboard no Mathcha.

**Architecture:** Um script de construção com `nbformat` gera um notebook autossuficiente, cujas células etiquetadas funcionam como fonte testável dos algoritmos, experimentos e animações. Testes carregam essas células diretamente e validam resultados, exportações e estrutura; depois o notebook é executado integralmente e produz CSV, GIFs e a prévia do dashboard por caminhos relativos.

**Tech Stack:** Python 3, Jupyter/nbformat/nbclient, NumPy, pandas, Matplotlib, Pillow, IPython e pytest.

**Spec:** `docs/superpowers/specs/2026-09-28-atividade-pratica-iii-design.md`

## Global Constraints

- Criar tudo sob `atividade_calculo_numerico/`; não alterar as atividades I e II existentes.
- O notebook final deve ser autossuficiente e funcionar no Google Colab sem arquivos Python auxiliares nem caminhos absolutos.
- Usar `TOL = 1e-6`, `MAX_ITER = 100` e `ZERO_TOL = 1e-12`.
- Exigir simultaneamente `abs(x_novo - x_anterior) < TOL` e `abs(f(x_novo)) < TOL`, exceto raiz já presente em um extremo ou valor inicial.
- Contar somente novas aproximações como iterações; os dois chutes da Secante permanecem no histórico sem aumentar a contagem.
- Implementar Bisseção, Newton e Secante manualmente; não usar `scipy.optimize`, `fsolve` ou equivalentes.
- Usar somente NumPy, pandas, Matplotlib, Pillow e IPython como dependências de execução do notebook.
- Gerar os três GIFs principais com `f2(x)=x**3-x-2` e os valores iniciais do enunciado.
- Exibir raízes com pelo menos 10 casas decimais e resíduos em notação científica, sem truncar os dados gravados no CSV.
- Preservar separadamente os 12 testes principais e o experimento adicional de Newton para `f4` com `x0=0`.
- Não declarar a entrega integralmente concluída sem execução top-to-bottom, inspeção visual e link compartilhável do Google Colab.
- A pasta atual não é um repositório Git; não inicializar Git nem criar commits sem solicitação do usuário. Cada tarefa termina com um checkpoint verificável em vez de commit.

## Review Focus

- Entrada não finita (`nan` ou `inf`): o método deve retornar falha compreensível, sem exceção não tratada; coberto no Task 1.
- Raiz já presente em extremo ou chute inicial: retornar convergência em zero iterações; coberto no Task 1.
- Passo pequeno com resíduo ainda grande: não aceitar convergência até as duas condições serem satisfeitas; coberto no Task 1.
- Divisor numericamente pequeno em Newton ou Secante: interromper antes da divisão com limiar `1e-12`; coberto no Task 1.
- Execução a partir de um diretório Colab limpo: criar pastas relativas e reproduzir CSV/GIFs sem depender da máquina local; coberto nos Tasks 3 e 5.

---

## File Structure

### Fontes de construção e testes

- `atividade_calculo_numerico/scripts/build_notebook.py`: constrói deterministicamente o notebook com células pequenas, ordenadas e etiquetadas.
- `atividade_calculo_numerico/tests/conftest.py`: carrega e executa células por tag para que os testes usem exatamente o código incorporado no notebook.
- `atividade_calculo_numerico/tests/test_metodos.py`: testa contratos, convergência e falhas dos três métodos.
- `atividade_calculo_numerico/tests/test_resultados.py`: testa os 12 casos, `f4`, tabela e CSV.
- `atividade_calculo_numerico/tests/test_animacoes.py`: testa geração e integridade estrutural dos três GIFs.
- `atividade_calculo_numerico/tests/test_notebook_e_dashboard.py`: testa estrutura acadêmica, portabilidade, documentação e prévia do dashboard.

### Artefatos finais

- `atividade_calculo_numerico/atividade_calculo_numerico.ipynb`: relatório computacional autossuficiente e executado.
- `atividade_calculo_numerico/resultados.csv`: tabela completa dos 12 casos principais.
- `atividade_calculo_numerico/gifs/bissecao_f2.gif`: redução do intervalo na Bisseção.
- `atividade_calculo_numerico/gifs/newton_f2.gif`: construção pela reta tangente.
- `atividade_calculo_numerico/gifs/secante_f2.gif`: construção pela reta secante.
- `atividade_calculo_numerico/dashboard_preview.png`: composição estática do dashboard vertical.
- `atividade_calculo_numerico/README.md`: execução, dependências e descrição dos arquivos.
- `atividade_calculo_numerico/GUIA_MATHCHA.md`: textos, dimensões, ordem e instruções de montagem no Mathcha.

---

### Task 1: Núcleo numérico e contratos de falha

**Files:**
- Create: `atividade_calculo_numerico/scripts/build_notebook.py`
- Create: `atividade_calculo_numerico/atividade_calculo_numerico.ipynb`
- Create: `atividade_calculo_numerico/tests/conftest.py`
- Create: `atividade_calculo_numerico/tests/test_metodos.py`

**Interfaces:**
- Consumes: constantes `TOL`, `MAX_ITER` e `ZERO_TOL` definidas no notebook.
- Produces: `bissecao(f, a, b, tol=1e-6, max_iter=100) -> dict`, `newton(f, df, x0, tol=1e-6, max_iter=100) -> dict` e `secante(f, x0, x1, tol=1e-6, max_iter=100) -> dict`.
- Produces: retorno com chaves `raiz`, `iteracoes`, `historico`, `residuo`, `convergiu`, `mensagem` e `passos`.

- [ ] **Step 1: Criar o carregador de células etiquetadas**

Em `tests/conftest.py`, definir fixtures que leem o notebook com `nbformat`, localizam tags `setup`, `funcoes` e `metodos` e executam as células no mesmo namespace. O teste deve falhar claramente se uma tag estiver ausente ou duplicada.

- [ ] **Step 2: Escrever os testes de convergência nominal**

Em `tests/test_metodos.py`, adicionar testes que chamam os três métodos para `f1` com os valores do enunciado e verificam:

```python
assert resultado["convergiu"] is True
assert resultado["residuo"] < 1e-6
assert set(resultado) == {
    "raiz", "iteracoes", "historico", "residuo",
    "convergiu", "mensagem", "passos",
}
```

- [ ] **Step 3: Escrever os testes de contagem e histórico**

Verificar que Bisseção, Newton e Secante contam apenas novas aproximações; para Secante, `len(historico) == iteracoes + 2`, e para Newton `len(historico) == iteracoes + 1`.

- [ ] **Step 4: Escrever os testes de raiz inicial ou extrema**

Usar `f(x)=x-1` com extremo/chute igual a `1.0` e verificar `convergiu is True`, `iteracoes == 0`, `raiz == 1.0` e mensagem específica de raiz inicial/extrema.

- [ ] **Step 5: Escrever os testes de falhas matemáticas**

Cobrir: Bisseção sem mudança de sinal, Newton com `abs(df(x0)) < 1e-12`, Secante com valores funcionais iguais e `max_iter=1` sem convergência. Cada caso deve retornar `convergiu is False` e mensagem que identifica a causa.

- [ ] **Step 6: Escrever os testes de entradas não finitas**

Parametrizar `nan` e `inf` em posições iniciais dos três métodos e verificar falha retornada, `numpy.nan` quando não houver aproximação finita e ausência de exceção não tratada.

- [ ] **Step 7: Escrever o teste do critério combinado**

Construir um caso controlado em que o primeiro passo fique abaixo de `tol` enquanto o resíduo permaneça acima de `tol`; verificar que o método não marca convergência nessa iteração.

- [ ] **Step 8: Executar os testes para confirmar a falha inicial**

Run: `python3 -m pytest atividade_calculo_numerico/tests/test_metodos.py -q`

Expected: FAIL porque o notebook e as tags ainda não existem.

- [ ] **Step 9: Implementar o construtor e as células do núcleo**

Em `scripts/build_notebook.py`, criar o notebook v4 com metadados Colab/Python 3 e células etiquetadas `setup`, `funcoes` e `metodos`. Implementar as três assinaturas, o dicionário de retorno comum, verificações de finitude, raízes iniciais, limiares de divisão, histórico, `passos` e parada combinada.

- [ ] **Step 10: Gerar o notebook**

Run: `python3 atividade_calculo_numerico/scripts/build_notebook.py`

Expected: arquivo `atividade_calculo_numerico/atividade_calculo_numerico.ipynb` válido em nbformat v4.

- [ ] **Step 11: Executar os testes do núcleo**

Run: `python3 -m pytest atividade_calculo_numerico/tests/test_metodos.py -q`

Expected: todos os testes PASS.

- [ ] **Step 12: Registrar checkpoint**

Salvar a saída resumida do pytest no relato de execução; não criar commit porque a pasta não usa Git.

---

### Task 2: Matriz de experimentos, validação e CSV

**Files:**
- Modify: `atividade_calculo_numerico/scripts/build_notebook.py`
- Regenerate: `atividade_calculo_numerico/atividade_calculo_numerico.ipynb`
- Create: `atividade_calculo_numerico/tests/test_resultados.py`
- Create: `atividade_calculo_numerico/resultados.csv`

**Interfaces:**
- Consumes: três métodos e quatro pares `f`/`df` do Task 1.
- Produces: `executar_experimentos(tol=TOL, max_iter=MAX_ITER) -> tuple[pandas.DataFrame, dict]`.
- Produces: DataFrame com colunas `Função`, `Método`, `Valores iniciais`, `Raiz aproximada`, `|f(x)| final`, `Iterações` e `Resultado`.

- [ ] **Step 1: Escrever o teste da configuração centralizada**

Verificar que a célula `experimentos` define as quatro funções, os três métodos por função e exatamente os valores iniciais do PDF, totalizando 12 configurações.

- [ ] **Step 2: Escrever o teste dos 12 resultados**

Executar `executar_experimentos()` e verificar 12 linhas, três métodos por função, todos os casos principais convergentes e resíduos menores que `1e-6`.

- [ ] **Step 3: Fixar raízes e iterações esperadas**

Comparar as raízes com tolerância `5e-10` para Newton/Secante e `5e-7` para Bisseção. Verificar iterações:

```python
esperadas = {
    ("f1", "Bisseção"): 21, ("f1", "Newton"): 4, ("f1", "Secante"): 6,
    ("f2", "Bisseção"): 22, ("f2", "Newton"): 3, ("f2", "Secante"): 7,
    ("f3", "Bisseção"): 20, ("f3", "Newton"): 3, ("f3", "Secante"): 5,
    ("f4", "Bisseção"): 21, ("f4", "Newton"): 4, ("f4", "Secante"): 7,
}
```

- [ ] **Step 4: Escrever o teste de validação automática**

Para cada linha convergente, recuperar a função original e verificar `abs(f(raiz)) < TOL`; verificar também que a coluna `Resultado` contém `Convergiu`.

- [ ] **Step 5: Escrever o teste do experimento adicional de `f4`**

Executar Newton para `f4` com `x0=0` e `max_iter=100`; verificar `convergiu is False`, `iteracoes == 100` e alternância entre `0.0` e `1.0` no histórico.

- [ ] **Step 6: Escrever o teste de exportação CSV**

Após salvar `resultados.csv`, reler com pandas e verificar as sete colunas, 12 linhas e igualdade numérica com o DataFrame de origem.

- [ ] **Step 7: Executar os testes para confirmar a falha inicial**

Run: `python3 -m pytest atividade_calculo_numerico/tests/test_resultados.py -q`

Expected: FAIL porque `executar_experimentos` e o CSV ainda não existem.

- [ ] **Step 8: Implementar as células de experimentos e resultados**

Adicionar tags `experimentos`, `tabela_resultados`, `validacao_resultados` e `experimento_f4`. Centralizar a configuração, gerar o DataFrame, aplicar apenas formatação de exibição e salvar o CSV sem perda de precisão.

- [ ] **Step 9: Regenerar o notebook e executar os testes**

Run: `python3 atividade_calculo_numerico/scripts/build_notebook.py`

Run: `python3 -m pytest atividade_calculo_numerico/tests/test_resultados.py -q`

Expected: todos os testes PASS e CSV com 12 linhas.

- [ ] **Step 10: Registrar checkpoint**

Registrar as 12 raízes, iterações e resíduos obtidos para comparação na verificação final.

---

### Task 3: Animações da Bisseção, de Newton e da Secante

**Files:**
- Modify: `atividade_calculo_numerico/scripts/build_notebook.py`
- Regenerate: `atividade_calculo_numerico/atividade_calculo_numerico.ipynb`
- Create: `atividade_calculo_numerico/tests/test_animacoes.py`
- Create: `atividade_calculo_numerico/gifs/bissecao_f2.gif`
- Create: `atividade_calculo_numerico/gifs/newton_f2.gif`
- Create: `atividade_calculo_numerico/gifs/secante_f2.gif`

**Interfaces:**
- Consumes: `passos` retornados pelos métodos e `f2`/`df2` do Task 1.
- Produces: `animar_bissecao(f, resultado, intervalo_plot, caminho) -> pathlib.Path`.
- Produces: `animar_newton(f, df, resultado, intervalo_plot, caminho) -> pathlib.Path`.
- Produces: `animar_secante(f, resultado, intervalo_plot, caminho) -> pathlib.Path`.

- [ ] **Step 1: Escrever os testes de criação dos GIFs**

Gerar as três animações em um diretório temporário e verificar nomes, formato GIF, dimensões mínimas de `800×500` e mais de um quadro com Pillow.

- [ ] **Step 2: Escrever os testes de quantidade de quadros**

Verificar que cada GIF contém pelo menos um quadro por iteração e que o quadro final é repetido ou tem duração maior para leitura.

- [ ] **Step 3: Escrever os testes de portabilidade de caminhos**

Executar os geradores a partir de diretório temporário, usando somente `Path` relativo fornecido, e verificar criação automática da pasta de destino.

- [ ] **Step 4: Executar os testes para confirmar a falha inicial**

Run: `python3 -m pytest atividade_calculo_numerico/tests/test_animacoes.py -q`

Expected: FAIL porque as funções de animação ainda não existem.

- [ ] **Step 5: Implementar o estilo e o gerador da Bisseção**

Adicionar célula `animacao_bissecao` com curva, zero horizontal, extremos, ponto médio, faixa do intervalo atual e do intervalo preservado, número da iteração, valores e resíduo. Fixar limites de eixo para evitar saltos.

- [ ] **Step 6: Implementar o gerador de Newton**

Adicionar célula `animacao_newton` com ponto atual, tangente, projeção `x_{k+1}`, novo ponto, iteração, valores e resíduo.

- [ ] **Step 7: Implementar o gerador da Secante**

Adicionar célula `animacao_secante` com dois pontos, reta secante, projeção `x_{k+1}`, novo ponto, iteração e resíduo.

- [ ] **Step 8: Adicionar a célula de geração e exibição**

Adicionar tag `gerar_gifs`; gerar os três arquivos com `FuncAnimation` e `PillowWriter`, usar `f2` em todos e exibi-los no notebook com `IPython.display.Image`.

- [ ] **Step 9: Regenerar o notebook e executar os testes**

Run: `python3 atividade_calculo_numerico/scripts/build_notebook.py`

Run: `python3 -m pytest atividade_calculo_numerico/tests/test_animacoes.py -q`

Expected: todos os testes PASS e três GIFs estruturalmente válidos.

- [ ] **Step 10: Registrar checkpoint**

Registrar dimensões, quadros e duração dos três GIFs para a inspeção visual posterior.

---

### Task 4: Relatório acadêmico e materiais do Mathcha

**Files:**
- Modify: `atividade_calculo_numerico/scripts/build_notebook.py`
- Regenerate: `atividade_calculo_numerico/atividade_calculo_numerico.ipynb`
- Create: `atividade_calculo_numerico/tests/test_notebook_e_dashboard.py`
- Create: `atividade_calculo_numerico/README.md`
- Create: `atividade_calculo_numerico/GUIA_MATHCHA.md`
- Create: `atividade_calculo_numerico/dashboard_preview.png`

**Interfaces:**
- Consumes: DataFrame, resultados de validação e GIFs dos Tasks 2 e 3.
- Produces: notebook narrativo completo, `gerar_dashboard_preview(df, caminho) -> pathlib.Path`, README e guia de montagem.

- [ ] **Step 1: Escrever o teste da estrutura acadêmica**

Verificar a presença e a ordem das seções: Introdução, Funções, Critérios, três métodos, Aplicação, Tabela, Animações, Discussão, estudo de `f4`, Conclusões, Resumo para o Dashboard e checklist.

- [ ] **Step 2: Escrever o teste de conteúdo obrigatório**

Verificar que o notebook contém as três fórmulas, explicação simples de passo e resíduo, `tol=1e-6`, `max_iter=100`, `ZERO_TOL=1e-12`, discussão baseada em iterações reais e distinção entre resultados principais e experimento adicional.

- [ ] **Step 3: Escrever o teste de portabilidade e dependências**

Rejeitar caminhos absolutos, `scipy.optimize`, `fsolve` e imports fora da lista permitida; verificar metadados de kernel Python 3 e Colab.

- [ ] **Step 4: Escrever o teste do README e do guia Mathcha**

Verificar objetivo, árvore de arquivos, dependências, execução, regeneração dos GIFs, descrição de cada GIF, critério de parada, títulos/textos exatos do dashboard, dimensões dos blocos e instrução de hyperlink do Colab.

- [ ] **Step 5: Escrever o teste da prévia do dashboard**

Gerar `dashboard_preview.png`, abrir com Pillow e verificar largura mínima de 1200 px, orientação vertical e presença não vazia de conteúdo nos blocos superior, central e inferior.

- [ ] **Step 6: Executar os testes para confirmar a falha inicial**

Run: `python3 -m pytest atividade_calculo_numerico/tests/test_notebook_e_dashboard.py -q`

Expected: FAIL porque narrativa, documentação e prévia ainda não estão completas.

- [ ] **Step 7: Completar as células Markdown do notebook**

Adicionar título, síntese numérica, teoria concisa, interpretação dos resultados executados, conclusões e seção “Resumo para o Dashboard”, mantendo texto enxuto e acadêmico.

- [ ] **Step 8: Implementar e gerar a prévia do dashboard**

Adicionar célula `dashboard_preview` que compõe cabeçalho, acesso ao Colab, fórmulas, miniaturas estáticas representativas dos GIFs, tabela dos 12 casos, conclusões e rodapé em 1200 px ou mais.

- [ ] **Step 9: Escrever README e GUIA_MATHCHA**

Usar os nomes finais dos arquivos e a disposição vertical aprovada. Incluir orientação para inserir GIF por upload/URL, manter os GIFs como anexos originais e configurar o link clicável.

- [ ] **Step 10: Regenerar e executar os testes documentais**

Run: `python3 atividade_calculo_numerico/scripts/build_notebook.py`

Run: `python3 -m pytest atividade_calculo_numerico/tests/test_notebook_e_dashboard.py -q`

Expected: todos os testes PASS.

- [ ] **Step 11: Registrar checkpoint**

Comparar a estrutura produzida com todas as seções 1–17 da especificação e anotar qualquer lacuna antes da execução integral.

---

### Task 5: Execução integral e inspeção técnica/visual

**Files:**
- Modify on a failed numerical, notebook or visual check: `atividade_calculo_numerico/scripts/build_notebook.py`
- Modify on a failed documentation check: `atividade_calculo_numerico/README.md` or `atividade_calculo_numerico/GUIA_MATHCHA.md`
- Modify on a test defect: the owning file under `atividade_calculo_numerico/tests/`
- Execute in place: `atividade_calculo_numerico/atividade_calculo_numerico.ipynb`
- Use for QA only: `/private/tmp/atividade_cn_qa/`

**Interfaces:**
- Consumes: todos os artefatos e testes anteriores.
- Produces: notebook executado com outputs salvos e evidência final de validação.

- [ ] **Step 1: Executar a suíte completa antes do notebook**

Run: `python3 -m pytest atividade_calculo_numerico/tests -q`

Expected: todos os testes PASS.

- [ ] **Step 2: Validar a estrutura nbformat**

Run: `python3 -c "import nbformat; p='atividade_calculo_numerico/atividade_calculo_numerico.ipynb'; nbformat.validate(nbformat.read(p, 4)); print('nbformat válido')"`

Expected: `nbformat válido`, sem erro de schema.

- [ ] **Step 3: Executar o notebook top-to-bottom**

Run: `python3 -m jupyter nbconvert --execute --to notebook --inplace --ExecutePreprocessor.timeout=600 atividade_calculo_numerico/atividade_calculo_numerico.ipynb`

Expected: exit code 0 e nenhuma célula com output de erro.

- [ ] **Step 4: Renderizar uma prévia HTML**

Run: `python3 -m jupyter nbconvert --to html --output-dir=/private/tmp/atividade_cn_qa atividade_calculo_numerico/atividade_calculo_numerico.ipynb`

Expected: HTML completo contendo tabela, três GIFs incorporados/referenciados e conclusões.

- [ ] **Step 5: Reconciliar notebook, CSV e referências**

Comparar as 12 linhas do CSV com os outputs executados, confirmar as iterações esperadas e validar todos os resíduos convergentes abaixo de `1e-6`.

- [ ] **Step 6: Extrair quadros para inspeção visual**

Para cada GIF, salvar em `/private/tmp/atividade_cn_qa/` o primeiro, um intermediário e o último quadro, além de uma folha de contato. Inspecionar curva, eixo zero, geometria, textos, limites, legibilidade e ausência de sobreposição.

- [ ] **Step 7: Inspecionar o notebook e a prévia do dashboard**

Abrir o HTML renderizado e `dashboard_preview.png` no visualizador disponível; verificar títulos, fórmulas, tabela, miniaturas, margens, precisão, contraste e ausência de cortes.

- [ ] **Step 8: Corrigir e repetir verificações afetadas**

Para qualquer falha numérica ou visual, alterar somente a fonte correspondente em `build_notebook.py`, regenerar o notebook e repetir testes, execução e inspeção necessários.

- [ ] **Step 9: Executar a verificação final completa**

Run: `python3 -m pytest atividade_calculo_numerico/tests -q`

Run: `python3 -m jupyter nbconvert --execute --to notebook --inplace --ExecutePreprocessor.timeout=600 atividade_calculo_numerico/atividade_calculo_numerico.ipynb`

Expected: suíte integral PASS e notebook executado sem erro após as últimas correções.

- [ ] **Step 10: Registrar checkpoint**

Registrar contagem de testes, 12 casos, três GIFs, inspeções visuais e quaisquer limitações remanescentes.

---

### Task 6: Publicação no Google Colab e fechamento dos links

**Files:**
- Modify: `atividade_calculo_numerico/scripts/build_notebook.py`
- Modify: `atividade_calculo_numerico/README.md`
- Modify: `atividade_calculo_numerico/GUIA_MATHCHA.md`
- Regenerate and re-execute: `atividade_calculo_numerico/atividade_calculo_numerico.ipynb`

**Interfaces:**
- Consumes: notebook integralmente validado do Task 5 e sessão Google autorizada.
- Produces: `COLAB_URL` compartilhável e registrado nos três pontos exigidos.

- [ ] **Step 1: Publicar a versão validada no Google Drive/Colab**

Usar o conector Google Drive disponível; se não houver ferramenta direta, usar a sessão de navegador já autenticada. Fazer upload sem substituir arquivos do usuário e definir compartilhamento por link somente no arquivo criado para esta atividade.

- [ ] **Step 2: Construir e verificar a URL do Colab**

Obter o identificador real do arquivo e formar `https://colab.research.google.com/drive/<ID>`. Abrir a URL e confirmar que o notebook carrega no Colab com acesso compatível com o compartilhamento definido.

- [ ] **Step 3: Escrever o teste dos links finais**

Em `test_notebook_e_dashboard.py`, verificar que notebook, README e GUIA_MATHCHA contêm a mesma URL `https://colab.research.google.com/drive/` e que não há marcadores fictícios.

- [ ] **Step 4: Registrar a URL nas fontes**

Definir `COLAB_URL` em `build_notebook.py`, atualizar README e guia e regenerar o notebook. A célula final deve exibir um link clicável “Abrir notebook no Google Colab”.

- [ ] **Step 5: Reexecutar o notebook com o link definitivo**

Run: `python3 atividade_calculo_numerico/scripts/build_notebook.py`

Run: `python3 -m jupyter nbconvert --execute --to notebook --inplace --ExecutePreprocessor.timeout=600 atividade_calculo_numerico/atividade_calculo_numerico.ipynb`

Expected: execução sem erro e artefatos idênticos numericamente aos aprovados no Task 5.

- [ ] **Step 6: Atualizar o arquivo remoto sem trocar o identificador**

Substituir o conteúdo do notebook publicado pela versão final reexecutada, preservando o mesmo ID e a mesma URL compartilhável.

- [ ] **Step 7: Executar a última verificação**

Run: `python3 -m pytest atividade_calculo_numerico/tests -q`

Expected: todos os testes PASS, inclusive consistência dos links.

- [ ] **Step 8: Tratar bloqueio externo sem inventar resultado**

Se upload, autenticação ou compartilhamento falhar, preservar todos os arquivos locais completos, registrar a mensagem exata do bloqueio e não afirmar que existe link do Colab. Retomar este Task após a autenticação do usuário.

- [ ] **Step 9: Registrar checkpoint final**

Entregar a árvore de arquivos, tabela resumida de raízes/iterações, nomes dos GIFs, caso adicional de `f4`, link do Colab, instruções Mathcha e estado das verificações.
