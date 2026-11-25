# Portfólio acadêmico de Cálculo Numérico — design

## Intenção

Transformar o conjunto local de atividades e o repositório `PedroMoreira191/CN` em um portfólio acadêmico navegável, reproduzível e verificável. A apresentação deve permitir que um professor compreenda objetivos, métodos, resultados e limitações sem precisar ler integralmente cada notebook.

## Evidências e restrições

- O GitHub possui sete commits e seis arquivos na branch `main`; o workspace possui dezenas de materiais adicionais e não continha metadados Git.
- Foram identificadas dez entradas didáticas: fundamentos; propagação de erros em peça circular; biofluidodinâmica; estabilidade/overflow; raízes; Gauss/LU; planos 3×3; Gauss–Seidel; interpolação; integração.
- Arquivos originais, enunciados e resultados serão preservados; intermediários, caches e ambientes locais não serão publicados.
- Informações acadêmicas divergentes ou sensíveis não serão promovidas ao README principal. O autor será identificado somente pelo nome confirmado no perfil/repositório e pelo contexto explícito dos próprios materiais.
- Resultados serão transcritos apenas quando confirmados por saídas salvas, CSV, PDF ou recálculo verificável.
- Links externos não verificados serão descritos com sua limitação, sem afirmar acesso público.

## Abordagens consideradas

1. **Manter a raiz e apenas escrever um README.** Menor risco de quebrar caminhos, mas mantém a aparência de pasta de exercícios e não atende à documentação individual.
2. **Duplicar tudo em uma pasta de portfólio.** Preserva caminhos antigos, mas dobra arquivos grandes, confunde a fonte canônica e piora o histórico.
3. **Reorganizar por atividade com renomes rastreáveis no Git (escolhida).** Produz navegação clara, preserva conteúdo e permite ao Git reconhecer renomes. Scripts e testes auxiliares ficam junto da atividade que servem; arquivos temporários não entram na publicação.

## Arquitetura

```text
README.md
requirements.txt
.gitignore
atividades/
  01_fundamentos_erros/
  02_propagacao_erros_peca_circular/
  03_biofluidodinamica/
  04_estabilidade_overflow/
  05_raizes_equacoes/
  06_sistemas_lineares_gauss_lu/
  07_sistemas_lineares_planos/
  08_gauss_seidel/
  09_interpolacao_polinomial/
  10_integracao_numerica/
docs/
  auditoria_tecnica.md
  superpowers/
```

Cada pasta terá um `README.md` com objetivo, fundamento, método, resultados comprovados, arquivos e execução. Enunciados e versões alternativas serão rotulados explicitamente. Imagens leves serão incorporadas quando já existirem; GIFs e dashboards densos serão oferecidos por link.

## Qualidade e reprodução

- Corrigir o classificador de postos dos planos 3×3 para usar tolerância comum e invariância a reescala; adicionar testes de regressão.
- Tornar caminhos e fontes dos geradores portáveis quando isso não altera a matemática.
- Registrar dependências Python em `requirements.txt` e comandos de execução por atividade.
- Executar as suítes existentes, os novos testes de links/estrutura e validações de notebooks/Markdown.
- Manter limitações explícitas: notebook de interpolação sem saídas, saída desatualizada na integração, links Colab/Mathcha não confirmados, e scripts históricos que dependiam de insumos externos.

## Não objetivos

- Não reescrever soluções matemáticas nem fabricar resultados ausentes.
- Não substituir notebooks por uma aplicação web.
- Não publicar caches, `.venv`, `.DS_Store`, arquivos temporários ou cópias redundantes.
- Não usar force push, reescrever commits antigos ou apagar originais sem uma versão preservada na nova estrutura.

