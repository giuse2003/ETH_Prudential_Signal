# Entry Quality Analysis

Questa analisi e' solo ricerca. Non modifica i segnali ufficiali.

Periodo analizzato: `2022-01-01` -> `2026-06-27`.
Performance misurata in EUR con `Close_EUR`; segnali e indicatori restano quelli ufficiali della Baseline.

## Sintesi

- Trade chiusi analizzati: 17.
- Trade vincenti: 5.
- Trade perdenti: 12.
- Win rate: 29.41%.
- Rendimento medio trade: 2.49%.
- Rendimento mediano trade: -2.90%.
- Drawdown medio interno trade: -9.49%.

## Migliori Trade

| Entry signal | Exit signal | Return | Max DD trade | RSI | Vol rel | Mom 30g | Dist SMA200 |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025-07-07 | 2025-09-23 | 62.70% | -14.45% | 53.3 | 5.12% | 0.65% | 2.03% |
| 2024-02-06 | 2024-04-03 | 38.55% | -21.86% | 54.0 | 6.96% | 6.72% | 21.49% |
| 2023-11-22 | 2024-01-23 | 8.84% | -13.48% | 61.4 | 18.72% | 16.94% | 15.69% |
| 2023-03-13 | 2023-05-08 | 7.30% | -13.65% | 59.6 | 85.24% | 9.12% | 18.11% |
| 2024-01-31 | 2024-02-01 | 0.28% | 0.00% | 45.2 | 2.18% | -2.97% | 17.64% |

## Peggiori Trade

| Entry signal | Exit signal | Return | Max DD trade | RSI | Vol rel | Mom 30g | Dist SMA200 |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025-10-02 | 2025-10-10 | -13.60% | -17.39% | 57.1 | 30.26% | 3.76% | 49.58% |
| 2024-12-05 | 2024-12-22 | -12.74% | -17.15% | 68.9 | 59.35% | 57.31% | 27.09% |
| 2024-04-08 | 2024-04-12 | -10.56% | -10.56% | 58.8 | 15.00% | -5.62% | 51.21% |
| 2024-07-19 | 2024-07-25 | -9.11% | -9.85% | 60.2 | 15.04% | -1.51% | 11.01% |
| 2024-05-20 | 2024-06-24 | -7.47% | -12.88% | 70.0 | 147.04% | 16.03% | 33.18% |

## Differenze Medie Vincitori vs Perdenti

| Feature | Media vincenti | Media perdenti | Delta |
|---|---:|---:|---:|
| days_since_previous_exit | 27.00 | 72.58 | -45.58 |
| rsi | 54.70 | 59.62 | -4.91 |
| volume_rel_pct | 23.64% | 38.74% | -15.10% |
| position_52w_pct | 61.40% | 72.64% | -11.24% |
| distance_sma200_pct | 14.99% | 22.50% | -7.51% |
| momentum_7d_pct | 2.61% | 9.46% | -6.85% |
| entry_vs_previous_exit_pct | 5.48% | -1.31% | 6.79% |
| momentum_14d_pct | 2.65% | 5.66% | -3.01% |

## Prima Lettura

- Il campione dal 2022 e' piccolo: 17 trade chiusi. Le differenze sono utili per generare ipotesi, non per promuovere subito regole.
- Il filtro di ingresso va testato solo dopo aver verificato che non elimini i migliori trade.
- Il prossimo passo e' trasformare le feature piu' promettenti in filtri sperimentali e confrontarle contro Baseline, costi e sottoperiodi.
