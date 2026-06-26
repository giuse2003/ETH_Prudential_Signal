# Stop Loss Experiment Results

Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.

La regola sperimentale forza `VENDI` se il Close scende sotto una
percentuale dal prezzo di ingresso. Il backtest applica comunque il
segnale al rendimento del giorno successivo.

## Griglia Principale

| Variante | Ann. | Max DD | Sharpe | Profit factor | Operazioni | Net 0,25% Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| stop_4pct | 34.67% | -44.93% | 0.911 | 4.817 | 33 | 0.866 |
| stop_10pct | 34.14% | -50.54% | 0.894 | 4.798 | 28 | 0.857 |
| stop_11pct | 33.77% | -51.71% | 0.887 | 4.713 | 28 | 0.850 |
| stop_12pct | 33.77% | -51.71% | 0.887 | 4.713 | 28 | 0.850 |
| stop_13pct | 33.49% | -52.57% | 0.883 | 4.652 | 28 | 0.845 |
| stop_5pct | 32.99% | -44.93% | 0.878 | 4.450 | 32 | 0.835 |
| stop_14pct | 33.09% | -52.57% | 0.875 | 4.568 | 28 | 0.838 |
| stop_15pct | 33.09% | -52.57% | 0.875 | 4.568 | 28 | 0.838 |

## Migliori Per Drawdown

| Variante | Ann. | Max DD | Sharpe | Operazioni | Net 0,25% DD |
|---|---:|---:|---:|---:|---:|
| stop_4pct | 34.67% | -44.93% | 0.911 | 33 | -45.07% |
| stop_5pct | 32.99% | -44.93% | 0.878 | 32 | -46.27% |
| stop_6pct | 31.06% | -49.53% | 0.842 | 31 | -51.27% |
| stop_8pct | 32.84% | -50.54% | 0.872 | 29 | -52.24% |
| stop_9pct | 32.84% | -50.54% | 0.872 | 29 | -52.24% |
| stop_10pct | 34.14% | -50.54% | 0.894 | 28 | -52.24% |
| stop_7pct | 31.73% | -50.54% | 0.853 | 30 | -52.24% |
| stop_11pct | 33.77% | -51.71% | 0.887 | 28 | -53.37% |

## Focus 8%-12%

| Variante | Ann. | Max DD | Sharpe | Net 0,25% Sharpe | Stress 0,50% Sharpe |
|---|---:|---:|---:|---:|---:|
| baseline | 31.78% | -52.57% | 0.849 | 0.812 | 0.775 |
| stop_10pct | 34.14% | -50.54% | 0.894 | 0.857 | 0.819 |
| stop_12pct | 33.77% | -51.71% | 0.887 | 0.850 | 0.813 |
| stop_8pct | 32.84% | -50.54% | 0.872 | 0.833 | 0.795 |
| stop_9pct | 32.84% | -50.54% | 0.872 | 0.833 | 0.795 |

## Sottoperiodi: Max Drawdown

| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |
|---|---:|---:|---:|---:|
| baseline | -41.34% | -44.93% | -52.57% | -26.17% |
| stop_8pct | -34.46% | -44.93% | -50.54% | -26.17% |
| stop_9pct | -34.46% | -44.93% | -50.54% | -26.17% |
| stop_10pct | -34.46% | -44.93% | -50.54% | -26.17% |
| stop_12pct | -34.46% | -44.93% | -51.71% | -26.17% |

## Sintesi

- Migliore variante per Sharpe: `stop_4pct` con Sharpe 0.911, ann. 34.67%, max DD -44.93%.
- Con entry reale del trade, stop 8% e stop 9% producono risultati
  identici nel run corrente: ann. 32,84%, max DD -50,54%, Sharpe 0,872.
- Il miglior stop da ingresso nella griglia e' stop 4%, ma resta sotto
  Sharpe 1 e non batte i trailing confermati.
- Nessuna regola viene promossa a operativa senza ulteriori controlli
  walk-forward e analisi dei trade in cui lo stop interviene.
