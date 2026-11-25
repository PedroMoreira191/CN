# Especificação de projeto — Atividade Prática III de Cálculo Numérico

Data: 28 de setembro de 2026  
Disciplina: Cálculo Numérico  
Fonte normativa: `Atividade 3 CN.pdf`  
Destino principal: notebook Google Colab e dashboard ilustrativo no Mathcha

## 1. Objetivo e critérios de sucesso

Produzir um trabalho acadêmico computacional completo sobre os métodos da Bisseção, de Newton e da Secante para encontrar raízes de quatro funções. A entrega deve ser reproduzível no Google Colab, gerar automaticamente a tabela comparativa e três animações GIF, explicar os resultados obtidos e fornecer um roteiro visual pronto para montagem no Mathcha.

O projeto estará concluído somente quando:

1. o notebook executar integralmente, do início ao fim, sem erro;
2. os 12 casos principais tiverem sido executados com os valores iniciais do enunciado;
3. cada resultado convergente satisfizer o critério numérico documentado;
4. `resultados.csv` corresponder aos resultados exibidos no notebook;
5. existirem três GIFs funcionais, um por método, com geometria e textos legíveis;
6. o notebook tiver explicações matemáticas, interpretação dos resultados e uma seção de resumo para o dashboard;
7. `README.md` e `GUIA_MATHCHA.md` permitirem reproduzir e montar a entrega;
8. houver um link compartilhável do notebook no Google Colab;
9. a prévia do dashboard e os arquivos finais tiverem sido inspecionados visualmente.

## 2. Escopo dos artefatos

O projeto será criado em uma pasta isolada para não colidir com as atividades anteriores:

```text
atividade_calculo_numerico/
├── atividade_calculo_numerico.ipynb
├── README.md
├── resultados.csv
├── GUIA_MATHCHA.md
├── dashboard_preview.png
└── gifs/
    ├── bissecao_f2.gif
    ├── newton_f2.gif
    └── secante_f2.gif
```

O notebook será autossuficiente: conterá as implementações dos métodos e não exigirá um arquivo Python auxiliar para ser executado no Colab. Os arquivos CSV, GIF e a prévia do dashboard serão gerados pelo próprio notebook com caminhos relativos.

## 3. Funções e parâmetros

As funções e derivadas analíticas serão:

\[
f_1(x)=x^2-2, \qquad f_1'(x)=2x,
\]

\[
f_2(x)=x^3-x-2, \qquad f_2'(x)=3x^2-1,
\]

\[
f_3(x)=e^{-x}-x, \qquad f_3'(x)=-e^{-x}-1,
\]

\[
f_4(x)=x^3-2x+2, \qquad f_4'(x)=3x^2-2.
\]

Parâmetros globais:

```python
TOL = 1e-6
MAX_ITER = 100
ZERO_TOL = 1e-12
```

Os testes principais usarão exatamente:

| Função | Bisseção | Newton | Secante |
|---|---|---|---|
| `f1` | `[1, 2]` | `1.5` | `(1, 2)` |
| `f2` | `[1, 2]` | `1.5` | `(1, 2)` |
| `f3` | `[0, 1]` | `0.5` | `(0, 1)` |
| `f4` | `[-2, -1]` | `-2` | `(-2, -1)` |

## 4. Contrato comum dos métodos

As assinaturas públicas serão:

```python
bissecao(f, a, b, tol=1e-6, max_iter=100)
newton(f, df, x0, tol=1e-6, max_iter=100)
secante(f, x0, x1, tol=1e-6, max_iter=100)
```

Cada função retornará um dicionário com estrutura comum:

```python
{
    "raiz": float,
    "iteracoes": int,
    "historico": list[float],
    "residuo": float,
    "convergiu": bool,
    "mensagem": str,
    "passos": list[dict],
}
```

`historico` guardará as aproximações; `passos` guardará os dados geométricos necessários para as animações. O notebook contará uma iteração sempre que uma nova aproximação for calculada. Na Secante, os dois valores iniciais estarão no histórico, mas não serão contados como iterações.

Entradas e saídas serão convertidas para valores escalares finitos. Valores não finitos encontrados durante uma iteração produzirão uma falha explicada no retorno, em vez de uma exceção matemática não tratada.

Em uma falha ocorrida após o início das iterações, `raiz` conterá a última aproximação finita disponível e `residuo` conterá seu resíduo. Se não existir aproximação válida, ambos serão `numpy.nan`. Assim, a tabela preservará informação diagnóstica sem confundir uma falha com convergência.

## 5. Critério de parada

Depois da primeira aproximação comparável, o método convergirá apenas quando as duas condições forem satisfeitas simultaneamente:

\[
|x_{k+1}-x_k| < \mathrm{tol}
\quad\text{e}\quad
|f(x_{k+1})| < \mathrm{tol}.
\]

Essa escolha evita aceitar um passo pequeno longe da raiz ou um resíduo pequeno obtido com uma aproximação ainda instável. Um valor inicial ou extremo que já seja raiz dentro da tolerância será aceito imediatamente, com zero iterações e mensagem específica.

Na Bisseção, o passo será a diferença entre pontos médios consecutivos. Na primeira iteração, como ainda não existe ponto médio anterior, somente uma raiz exata/dentro da tolerância poderá encerrar o método; caso contrário, o algoritmo seguirá até que passo e resíduo sejam simultaneamente pequenos.

## 6. Algoritmos e tratamento de falhas

### 6.1. Bisseção

1. Avaliar os extremos e aceitar imediatamente um extremo que já satisfaça a tolerância.
2. Rejeitar o intervalo se `f(a) * f(b) > 0`, explicando que não há garantia de raiz pelo Teorema do Valor Intermediário.
3. Calcular o ponto médio, registrar o intervalo atual e atualizar o extremo que mantém a mudança de sinal.
4. Atualizar também os valores funcionais associados aos extremos, evitando reutilizar sinais obsoletos.
5. Encerrar por convergência combinada ou por `max_iter`.

### 6.2. Newton

1. Avaliar o ponto inicial e aceitar uma raiz inicial dentro da tolerância.
2. Antes da divisão, rejeitar `abs(df(x_k)) < ZERO_TOL`.
3. Calcular a nova aproximação pela fórmula de Newton e registrar o ponto, a derivada, a reta tangente e sua interseção com o eixo x.
4. Rejeitar resultados não finitos com mensagem compreensível.
5. Encerrar por convergência combinada ou por `max_iter`.

### 6.3. Secante

1. Avaliar os dois valores iniciais e aceitar qualquer um que já satisfaça a tolerância.
2. Antes da divisão, rejeitar `abs(f(x_k)-f(x_{k-1})) < ZERO_TOL`.
3. Calcular a nova aproximação, registrando os dois pontos, a reta secante e sua interseção com o eixo x.
4. Rejeitar resultados não finitos com mensagem compreensível.
5. Encerrar por convergência combinada ou por `max_iter`.

## 7. Experimentos e tabela de resultados

Os 12 casos principais serão executados por uma configuração centralizada, sem números iniciais espalhados pelo notebook. Cada linha do `pandas.DataFrame` conterá:

| Coluna | Conteúdo |
|---|---|
| `Função` | Nome e expressão resumida |
| `Método` | Bisseção, Newton ou Secante |
| `Valores iniciais` | Intervalo, ponto ou par de pontos |
| `Raiz aproximada` | Valor com pelo menos 10 casas decimais na exibição |
| `|f(x)| final` | Resíduo em notação científica |
| `Iterações` | Novas aproximações calculadas |
| `Resultado` | `Convergiu` ou mensagem curta de falha |

O CSV armazenará valores numéricos completos, sem arredondar os dados subjacentes. A formatação de apresentação será aplicada apenas à visualização no notebook e à tabela usada no dashboard.

Cada resultado marcado como convergente será validado automaticamente com `abs(f(raiz)) < TOL`. Também será feita uma comparação independente das raízes com valores de referência, sem usar bibliotecas externas para substituir os algoritmos.

## 8. Animações

As três animações principais usarão `f2(x)=x^3-x-2`, permitindo comparação visual direta com as condições iniciais do enunciado. Serão produzidas com `matplotlib.animation.FuncAnimation` e `PillowWriter`.

### 8.1. Padrão visual comum

- fundo claro, grade discreta e eixo `y=0` destacado;
- curva em azul-petróleo;
- aproximações e construções geométricas em laranja;
- intervalo ativo em azul translúcido;
- raiz/aproximação nova em verde;
- textos com contraste suficiente e tamanho legível após inserção no Mathcha;
- caixa de informação com iteração, aproximações relevantes e resíduo;
- limites de eixos fixos por animação para evitar saltos visuais;
- quadro final mantido por tempo maior para leitura.

### 8.2. Bisseção

Cada quadro mostrará `a_k`, `b_k`, o ponto médio `c_k`, o intervalo anterior, o intervalo que continua contendo a raiz, `f(c_k)` e `|f(c_k)|`.

### 8.3. Newton

Cada quadro mostrará `(x_k,f(x_k))`, a reta tangente

\[
y=f(x_k)+f'(x_k)(x-x_k),
\]

sua interseção `x_{k+1}` com o eixo x e o novo ponto projetado na curva.

### 8.4. Secante

Cada quadro mostrará os pontos referentes a `x_{k-1}` e `x_k`, a reta secante, sua interseção `x_{k+1}` com o eixo x e o resíduo da nova aproximação.

## 9. Estrutura do notebook

O notebook seguirá esta sequência:

1. título, identificação e síntese executiva;
2. introdução ao problema `f(x)=0`;
3. funções, derivadas e valores iniciais;
4. parâmetros e critérios de convergência;
5. implementação e explicação da Bisseção;
6. implementação e explicação de Newton;
7. implementação e explicação da Secante;
8. execução programática dos 12 casos;
9. tabela comparativa e exportação CSV;
10. validações automáticas;
11. geração e exibição dos três GIFs;
12. análise baseada nos valores executados;
13. estudo específico de `f4` e experimento adicional separado;
14. conclusões;
15. resumo pronto para o dashboard do Mathcha;
16. checklist final da entrega.

A análise discutirá iterações, precisão, derivadas, dependência das condições iniciais, robustez e falhas possíveis. As afirmações serão vinculadas aos resultados executados, não apenas a descrições genéricas.

## 10. Estudo de `f4`

Os três métodos serão executados primeiro com os valores solicitados, sem alterações silenciosas. Espera-se convergência para a única raiz real próxima de `-1.7692923542` com esses valores.

Em uma subseção chamada “Experimentos adicionais”, Newton será executado para `f4` com `x0=0`. Esse ponto produz o ciclo `0 → 1 → 0 → 1 → …`, pois as duas primeiras atualizações retornam aos mesmos valores, e portanto termina sem convergência em `MAX_ITER`. O experimento não substituirá nenhum dos 12 resultados principais e será explicado geometricamente.

## 11. Dashboard do Mathcha

O layout principal será vertical e acadêmico, com largura-base de 1200 px:

1. cabeçalho: “Cálculo Numérico — Atividade Prática III”;
2. subtítulo: “Raízes por Bisseção, Newton e Secante”;
3. botão/link: “Abrir notebook no Google Colab”;
4. bloco “Problema e métodos” com objetivo e três fórmulas;
5. linha com os três GIFs e títulos curtos;
6. bloco “Resultados dos 12 testes” com a tabela completa;
7. bloco “Leituras principais” com três a cinco conclusões numéricas;
8. rodapé: “Tolerância: 10⁻⁶ · Máximo: 100 iterações”.

`dashboard_preview.png` mostrará a composição estática e `GUIA_MATHCHA.md` trará:

- dimensões e ordem de cada bloco;
- textos exatos para copiar;
- indicação do arquivo a inserir em cada posição;
- instrução para criar o hyperlink do Colab;
- observação para anexar também os GIFs originais, preservando a animação;
- paleta, tipografia e espaçamento;
- checklist de montagem e compartilhamento.

## 12. Publicação no Google Colab

Após a validação local, o notebook será publicado por uma sessão Google autorizada disponível no ambiente. O arquivo compartilhado deverá permitir abertura no Colab e seu link será registrado no `README.md`, no `GUIA_MATHCHA.md` e no bloco final do notebook.

Se a sessão não estiver autenticada ou não permitir upload/compartilhamento, isso será tratado como bloqueio externo explícito: o notebook local continuará completo e importável, mas a entrega não será declarada integralmente concluída até existir um link compartilhável.

## 13. Verificação técnica e visual

### 13.1. Verificação numérica

- testes normais dos 12 casos;
- testes de mudança de sinal ausente na Bisseção;
- teste de derivada quase nula em Newton;
- teste de denominador quase nulo na Secante;
- teste de raiz em ponto inicial/extremo;
- teste de limite máximo de iterações;
- confirmação de resíduo para toda linha convergente;
- conferência da convenção de contagem de iterações.

### 13.2. Verificação do notebook

- validação estrutural com `nbformat`;
- execução top-to-bottom em ambiente limpo;
- salvamento dos outputs executados;
- renderização para HTML e inspeção do conteúdo, tabelas e gráficos;
- nova execução integral após qualquer alteração em código ou dependências.

### 13.3. Verificação dos arquivos

- leitura do CSV e reconciliação com o DataFrame;
- abertura de todos os GIFs com Pillow;
- verificação de formato, dimensões, número de quadros e duração;
- inspeção visual do primeiro, de um intermediário e do último quadro de cada GIF;
- inspeção visual de `dashboard_preview.png` em tamanho de leitura;
- conferência final dos nomes e caminhos relativos.

## 14. Dependências e portabilidade

Serão usadas somente bibliotecas comuns no Colab:

```text
numpy
pandas
matplotlib
Pillow
IPython
```

O código usará `pathlib.Path`, criará as pastas de saída quando necessário e não dependerá do diretório absoluto da máquina local.

## 15. Limites de escopo

O projeto não usará `scipy.optimize` para calcular as raízes, não criará uma aplicação web, não alterará atividades anteriores e não dependerá de serviços pagos. A montagem efetiva do documento no Mathcha não será automatizada; o projeto entregará todos os materiais, a prévia e instruções exatas para uma montagem manual rápida e verificável.

## 16. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Divergência entre notebook e CSV | Gerar o CSV diretamente do DataFrame executado |
| GIF ilegível no dashboard | Dimensionar texto para exibição reduzida e inspecionar quadros renderizados |
| Contagem de iterações ambígua | Documentar que apenas novas aproximações são contadas |
| Aceitação prematura de falsa convergência | Exigir simultaneamente passo e resíduo abaixo da tolerância |
| Resultado inesperado em `f4` | Preservar o caso principal e separar experimentos adicionais |
| Notebook dependente da máquina local | Usar apenas caminhos relativos e dependências disponíveis no Colab |
| Falha de autenticação no Google | Entregar arquivo importável e reportar o bloqueio sem inventar um link |
| Animação não preservada na exportação do Mathcha | Entregar e anexar os GIFs originais além da composição no documento |

## 17. Resultado esperado dos casos principais

Os valores abaixo servem como referência de validação, não como dados fixos da implementação:

| Função | Bisseção | Newton | Secante |
|---|---:|---:|---:|
| `f1` | `1.414213657379` (21) | `1.414213562373` (4) | `1.414213562373` (6) |
| `f2` | `1.521379709244` (22) | `1.521379706805` (3) | `1.521379706805` (7) |
| `f3` | `0.567143440247` (20) | `0.567143290410` (3) | `0.567143290410` (5) |
| `f4` | `-1.769292354584` (21) | `-1.769292354239` (4) | `-1.769292354236` (7) |

Os números entre parênteses são as iterações esperadas sob o critério combinado e a convenção de contagem definidos nesta especificação.
