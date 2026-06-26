# Trailing Stop Experiment Results

Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.

La regola sperimentale aggiorna lo stop sul massimo Close raggiunto dopo
l'ingresso. Se il Close scende sotto `massimo_close * (1 - stop)`, forza
`VENDI` nel frame di backtest.

Esempio: ingresso a 2.000, Close sale a 2.100, trailing stop 8% = 1.932.

## Griglia Principale

| Variante | Ann. | Max DD | Sharpe | Profit factor | Operazioni | Net 0,25% Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| trailing_19pct | 39.50% | -54.78% | 1.011 | 5.258 | 28 | 0.971 |
| trailing_21pct | 38.53% | -54.78% | 0.991 | 5.003 | 28 | 0.952 |
| trailing_17pct | 37.15% | -54.78% | 0.985 | 4.028 | 30 | 0.942 |
| trailing_18pct | 37.15% | -54.78% | 0.985 | 4.028 | 30 | 0.942 |
| trailing_20pct | 38.08% | -54.78% | 0.984 | 4.968 | 28 | 0.945 |
| trailing_16pct | 36.15% | -53.95% | 0.970 | 3.895 | 31 | 0.925 |
| trailing_15pct | 35.29% | -53.95% | 0.955 | 3.688 | 32 | 0.908 |
| trailing_13pct | 33.66% | -47.39% | 0.939 | 3.338 | 35 | 0.887 |

## Migliori Per Drawdown

| Variante | Ann. | Max DD | Sharpe | Operazioni | Net 0,25% DD |
|---|---:|---:|---:|---:|---:|
| trailing_5pct | 21.71% | -38.18% | 0.738 | 60 | -42.81% |
| trailing_6pct | 24.26% | -41.15% | 0.783 | 54 | -43.46% |
| trailing_4pct | 15.79% | -41.64% | 0.603 | 68 | -46.56% |
| trailing_8pct | 20.52% | -41.93% | 0.690 | 48 | -45.72% |
| trailing_7pct | 16.37% | -41.93% | 0.598 | 53 | -47.91% |
| trailing_9pct | 19.35% | -45.23% | 0.662 | 47 | -48.81% |
| trailing_12pct | 30.29% | -46.31% | 0.882 | 38 | -48.16% |
| trailing_13pct | 33.66% | -47.39% | 0.939 | 35 | -49.20% |

## Focus

| Variante | Ann. | Max DD | Sharpe | Net 0,25% Sharpe | Stress 0,50% Sharpe |
|---|---:|---:|---:|---:|---:|
| baseline | 31.78% | -52.57% | 0.849 | 0.812 | 0.775 |
| trailing_10pct | 23.52% | -50.22% | 0.749 | 0.683 | 0.616 |
| trailing_12pct | 30.29% | -46.31% | 0.882 | 0.824 | 0.766 |
| trailing_15pct | 35.29% | -53.95% | 0.955 | 0.908 | 0.861 |
| trailing_20pct | 38.08% | -54.78% | 0.984 | 0.945 | 0.905 |
| trailing_8pct | 20.52% | -41.93% | 0.690 | 0.615 | 0.539 |

## Sottoperiodi: Max Drawdown

| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |
|---|---:|---:|---:|---:|
| baseline | -41.34% | -44.93% | -52.57% | -26.17% |
| trailing_8pct | -38.11% | -36.06% | -41.93% | -41.01% |
| trailing_10pct | -34.12% | -33.97% | -50.22% | -41.63% |
| trailing_12pct | -34.12% | -33.97% | -46.31% | -36.20% |
| trailing_15pct | -39.63% | -33.97% | -53.95% | -26.17% |
| trailing_20pct | -37.90% | -30.69% | -54.78% | -26.17% |

## Sintesi

- Migliore Sharpe: `trailing_19pct` con Sharpe 1.011, ann. 39.50%, max DD -54.78%.
- Migliore drawdown: `trailing_5pct` con max DD -38.18%, ann. 21.71%.
- Il trailing stop 8% riduce il drawdown ma sacrifica troppo rendimento
  e Sharpe rispetto alla baseline.
- Nessuna regola viene promossa a operativa senza ulteriori controlli.
