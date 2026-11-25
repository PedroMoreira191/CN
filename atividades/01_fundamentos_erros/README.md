# 01 · Fundamentos e erros computacionais

## Objetivo

Introduzir a representação finita de números no computador e quantificar as consequências de arredondamento, truncamento e cancelamento em cálculos simples.

## Fundamentação

Para um valor exato $x$ e uma aproximação $\tilde{x}$:

$$E_a=|x-\tilde{x}|,\qquad E_r=\frac{|x-\tilde{x}|}{|x|},\qquad E_p=100E_r.$$

Os exercícios também comparam expressões matematicamente equivalentes que possuem comportamento numérico diferente em ponto flutuante.

## Resultados confirmados

- usar $3{,}14$ para $\pi$ produz erro absoluto aproximado de `0,0015926536` e erro percentual de `0,050696%`;
- aumentar o raio de uma esfera em 1% aumenta seu volume em aproximadamente 3,03%;
- em um exemplo de cancelamento, a forma direta resulta em `0`, enquanto uma forma algebricamente estável preserva cerca de $5\times10^{-9}$.

## Arquivos

- [`aula_02_resolvida.ipynb`](aula_02_resolvida.ipynb) — versão preenchida e principal;
- [`aula_02_original.ipynb`](aula_02_original.ipynb) — material-base preservado, com crédito no próprio notebook;
- [`exercicio_aproximacoes.py`](exercicio_aproximacoes.py) — aproximações de $\sqrt{2}$, $\pi$ e $e$.

## Execução

```bash
jupyter lab atividades/01_fundamentos_erros/aula_02_resolvida.ipynb
python3 atividades/01_fundamentos_erros/exercicio_aproximacoes.py
```

## Conclusão

Precisão de entrada, representação numérica e forma algébrica são partes do algoritmo. Expressões equivalentes no papel podem produzir respostas diferentes no computador.

