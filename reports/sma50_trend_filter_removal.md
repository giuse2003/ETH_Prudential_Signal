# SMA50 Trend Filter Removal

Test di ricerca: rimozione della condizione `SMA50 > SMA200` dalla Baseline.

Periodo: `2018-05-29` -> `2026-07-03`.

Variante testata:

- ingresso senza `SMA50 > SMA200`;
- invariati `Close > SMA200`, `RSI >= 40`, `RSI <= 65` sui nuovi ingressi,
  momentum 7 giorni positivo e volume sopra media 20 giorni;
- uscite invariate: `Close < SMA50` e Trail8 confermato.

## Periodo Completo

| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Win rate | Esposizione |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 50.95% | -41.10% | 1.216 | 7.400 | 29 | 34.48% | 25.22% |
| no_sma50_gt_sma200_entry | 56.07% | -41.10% | 1.247 | 7.335 | 31 | 38.71% | 28.87% |

## Periodo 2022-Oggi

| Variante | Ann. | Max DD | Sharpe | Esposizione |
|---|---:|---:|---:|---:|
| baseline | 16.95% | -27.69% | 0.774 | 18.54% |
| no_sma50_gt_sma200_entry | 22.88% | -23.25% | 0.899 | 21.58% |

## Stress Costi

| Scenario | Delta Ann. | Delta DD | Delta Sharpe | Delta PF | Delta Ops |
|---|---:|---:|---:|---:|---:|
| lordo_0_00pct | 5.12% | 0.00% | 0.031 | -0.065 | 2 |
| costo_0_10pct | 5.01% | -0.00% | 0.031 | -0.054 | 2 |
| costo_0_25pct | 4.84% | 0.00% | 0.031 | -0.039 | 2 |
| stress_0_50pct | 4.57% | 1.15% | 0.031 | -0.017 | 2 |
| stress_1_00pct | 4.05% | 2.04% | 0.031 | 0.014 | 2 |

## Validazione Annuale

| Anno | Baseline Ret | Senza SMA50 Ret | Delta Ret | Baseline DD | Senza SMA50 DD | Delta Sharpe |
|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a |
| 2019 | 56.36% | 29.21% | -27.15% | -19.32% | -35.86% | -0.476 |
| 2020 | 141.69% | 206.66% | 64.96% | -22.64% | -22.64% | 0.262 |
| 2021 | 269.31% | 269.31% | 0.00% | -41.10% | -41.10% | 0.000 |
| 2022 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a |
| 2023 | -0.47% | 7.76% | 8.23% | -23.22% | -23.25% | 0.277 |
| 2024 | 24.42% | 50.88% | 26.46% | -26.00% | -18.51% | 0.462 |
| 2025 | 58.53% | 50.87% | -7.66% | -14.70% | -14.70% | -0.179 |
| 2026 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a |

## Eventi

- Nuovi ingressi della variante: 31.
- Nuovi ingressi che la Baseline bloccava per `SMA50 <= SMA200`: 7.

| Data | Close EUR | SMA50>SMA200 | RSI | Mom 7g | Volume rel |
|---|---:|---:|---:|---:|---:|
| 2019-04-11 | 146.96 | False | 59.51 | 4.71% | 21.33% |
| 2019-09-22 | 191.98 | False | 63.28 | 11.46% | 7.30% |
| 2020-04-19 | 167.15 | False | 61.43 | 12.70% | 19.12% |
| 2020-07-06 | 213.49 | True | 58.96 | 5.84% | 30.15% |
| 2020-07-21 | 212.38 | True | 59.03 | 2.00% | 3.14% |
| 2020-10-12 | 328.23 | True | 61.35 | 9.54% | 21.07% |
| 2020-10-21 | 330.91 | True | 60.18 | 3.35% | 51.80% |
| 2021-03-17 | 1521.73 | True | 56.08 | 1.35% | 1.88% |
| 2021-03-31 | 1635.80 | True | 62.11 | 20.39% | 28.40% |
| 2021-07-26 | 1891.90 | True | 57.75 | 22.90% | 65.87% |
| 2021-10-01 | 2852.80 | True | 53.89 | 12.82% | 11.04% |
| 2021-11-23 | 3859.66 | True | 50.43 | 2.95% | 20.77% |
| 2021-11-30 | 4087.78 | True | 58.38 | 6.70% | 47.10% |
| 2023-02-02 | 1506.91 | False | 63.08 | 2.50% | 22.36% |
| 2023-03-13 | 1567.01 | True | 59.63 | 7.20% | 85.24% |
| 2023-05-05 | 1779.61 | True | 59.30 | 5.42% | 4.11% |
| 2023-05-28 | 1782.36 | True | 59.92 | 5.90% | 7.66% |
| 2023-06-02 | 1780.23 | True | 57.73 | 4.30% | 11.89% |
| 2023-06-21 | 1720.38 | True | 60.89 | 14.57% | 80.75% |
| 2023-08-01 | 1700.42 | True | 48.90 | 0.76% | 35.75% |
| 2023-11-14 | 1819.35 | False | 61.60 | 4.82% | 36.79% |
| 2024-02-06 | 2205.24 | True | 54.04 | 1.18% | 6.96% |
| 2024-04-08 | 3402.13 | True | 58.81 | 5.43% | 15.00% |
| 2024-06-20 | 3279.52 | True | 46.36 | 1.21% | 14.56% |
| 2024-07-15 | 3201.95 | True | 60.83 | 15.60% | 30.38% |
| 2024-07-19 | 3218.45 | True | 60.18 | 11.86% | 15.04% |
| 2024-11-14 | 2905.55 | False | 60.73 | 5.64% | 24.70% |
| 2025-06-09 | 2346.79 | False | 61.78 | 2.85% | 3.44% |
| 2025-07-02 | 2179.39 | True | 56.09 | 6.28% | 17.94% |
| 2025-07-07 | 2166.74 | True | 53.29 | 2.27% | 5.12% |
| ... | altri 1 eventi |  |  |  |  |

## Lettura

- Delta annualizzato lordo: 5.12%.
- Delta max drawdown lordo: 0.00%.
- Delta Sharpe lordo: 0.031.
- Anni migliorati per rendimento: 3.
- Anni peggiorati per rendimento: 2.
- La condizione va rimossa solo se migliora rendimento/rischio senza peggiorare la stabilita' annuale.
