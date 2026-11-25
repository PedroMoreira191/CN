# 09 · Interpolação polinomial e análise de erros

## Objetivo

Estudar interpolação, extrapolação, sensibilidade aos dados e erro de aproximação, incluindo o fenômeno de Runge e a escolha de nós.

## Fundamentação

O polinômio interpolador de Lagrange pode ser escrito como

$$P_n(x)=\sum_{i=0}^{n}y_iL_i(x),\qquad
L_i(x)=\prod_{j\ne i}\frac{x-x_j}{x_i-x_j}.$$

Ele coincide com os dados nos nós, mas isso não garante pequeno erro entre eles. A posição e a quantidade de nós influenciam fortemente a estabilidade.

## Estudos disponíveis

### Interpolação polinomial explicativa

- exemplo $P(x)=(x-1)^2$ e extrapolação $P(2)=1$;
- alterar em `+0,5` um dado em $x=2$ muda a estimativa em $x=1{,}5$ de `2,3125` para `2,59375`;
- no exemplo de Runge, os erros máximos para 5, 9 e 15 nós equiespaçados são aproximadamente `0,438`, `1,045` e `7,195` em malha fina.

### Erros de interpolação em transferência de calor

O segundo notebook compara configurações de sensores, nós equiespaçados e nós de Chebyshev–Lobatto, transformando o erro numérico em uma decisão de instrumentação.

## Arquivos

- [`interpolacao_polinomial.ipynb`](interpolacao_polinomial.ipynb) — atividade explicativa local;
- [`interpolacao_erros_transferencia_calor.ipynb`](interpolacao_erros_transferencia_calor.ipynb) — tarefa investigativa recuperada do GitHub.

## Execução

```bash
jupyter lab atividades/09_interpolacao_polinomial/
```

> [!IMPORTANT]
> O primeiro notebook não possui saídas de código salvas. Os resultados citados acima foram confirmados por recálculo, mas os gráficos devem ser regenerados ao abrir a atividade.

## Conclusão

Elevar o grau não garante melhor aproximação. Distribuição dos nós, ruído, extrapolação e escolha entre interpolação global, splines ou regressão devem ser avaliados em conjunto.

