# SMA50 One-Day Promotion Gate

Periodo testato: `2017-11-11` -> `2026-06-29`.

Candidato: `Close < SMA50` a 1 giorno + Trail8.
Baseline: `Close < SMA50` per 2 giorni + Trail8.
Ingressi invariati. Metriche in USD.

## Gate

- PASS: 8.
- FAIL: 1.

| Check | Status | Nota |
|---|---:|---|
| Full annualized return improves | PASS | 47.94% vs 43.58% |
| Full max drawdown improves | PASS | -40.97% vs -44.93% |
| Full Sharpe improves | PASS | 1.179 vs 1.084 |
| Full profit factor improves | PASS | 7.117 vs 5.889 |
| Cost stress improves in every scenario | PASS | 4/4 ann, 4/4 DD, 4/4 Sharpe |
| Active yearly return improves in majority | FAIL | 3 better, 3 worse |
| Active yearly drawdown improves in majority | PASS | 3 better, 2 worse |
| Rolling windows return improves in majority | PASS | 4 better, 2 worse |
| Changed segments improve in majority | PASS | 16 improved, 8 worsened |

## Metriche Complete

| Modello | Totale | Ann. | Max DD | Sharpe | PF | Operazioni | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline SMA50 2g + Trail8 | 2173.16% | 43.58% | -44.93% | 1.084 | 5.889 | 28 | 56.0 |
| Candidate SMA50 1g + Trail8 | 2843.36% | 47.94% | -40.97% | 1.179 | 7.117 | 29 | 58.0 |

## Finestre Rolling

| Finestra | Baseline ret | Candidate ret | Delta ret | Baseline DD | Candidate DD | Delta DD | Delta Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2019-2020 | 348.41% | 301.24% | -47.17% | -24.43% | -27.45% | -3.02% | -0.111 |
| 2020-2021 | 915.58% | 856.73% | -58.85% | -44.93% | -40.97% | 3.96% | -0.005 |
| 2021-2022 | 268.68% | 277.51% | 8.82% | -44.93% | -40.97% | 3.96% | 0.049 |
| 2023-2024 | 2.83% | 25.06% | 22.22% | -40.39% | -28.50% | 11.88% | 0.343 |
| 2024-2025 | 32.71% | 88.99% | 56.28% | -42.79% | -30.25% | 12.54% | 0.589 |
| 2025-2026 | 35.07% | 56.97% | 21.90% | -26.17% | -15.31% | 10.86% | 0.400 |

## Stress Costi

| Scenario | Delta ann. | Delta DD | Delta Sharpe | Delta PF |
|---|---:|---:|---:|---:|
| gross_0.00% | 4.36% | 3.96% | 0.095 | 1.228 |
| cost_0.10% | 4.30% | 3.95% | 0.094 | 1.172 |
| cost_0.25% | 4.20% | 3.95% | 0.092 | 1.094 |
| stress_0.50% | 4.05% | 3.71% | 0.090 | 0.979 |

## Lettura

- Il candidato supera nettamente i controlli aggregati e lo stress costi.
- Il punto debole resta la distribuzione annuale: migliora molto 2024-2025 ma peggiora 2019-2020 e leggermente 2023.
- La promozione richiede una decisione esplicita: privilegiare protezione e reattivita' oppure stabilita' annuale piu' uniforme.

## File generati

- `reports\sma50_one_day_promotion_gate_checks.csv`
- `reports\sma50_one_day_promotion_gate_windows.csv`
