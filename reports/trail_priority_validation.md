# Trail8 Priority Validation

Test sperimentale: valutare il trailing stop 8% confermato prima delle condizioni BUY quando la posizione e' gia' aperta.

La Baseline ufficiale non viene modificata.

## Metriche USD

| Modello | Totale | Ann. | Max DD | Sharpe | PF | Operazioni | Win rate | Esposizione | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 2173.16% | 43.61% | -44.93% | 1.084 | 5.889 | 28 | 39.29% | 25.26% | 56 |
| Trail8 priority | 2574.62% | 46.35% | -42.79% | 1.207 | 4.708 | 34 | 41.18% | 23.83% | 68 |

## Stress Costi

| Costo cambio esposizione | Modello | Ann. | Max DD | Sharpe | PF | Operazioni |
|---:|---|---:|---:|---:|---:|---:|
| 0.00% | Baseline ufficiale | 43.61% | -44.93% | 1.084 | 5.889 | 28 |
| 0.00% | Trail8 priority | 46.35% | -42.79% | 1.207 | 4.708 | 34 |
| 0.10% | Baseline ufficiale | 42.69% | -44.99% | 1.068 | 5.786 | 28 |
| 0.10% | Trail8 priority | 45.20% | -43.59% | 1.186 | 4.623 | 34 |
| 0.25% | Baseline ufficiale | 41.30% | -45.07% | 1.045 | 5.637 | 28 |
| 0.25% | Trail8 priority | 43.49% | -44.78% | 1.154 | 4.499 | 34 |
| 0.50% | Baseline ufficiale | 39.02% | -46.78% | 1.005 | 5.404 | 28 |
| 0.50% | Trail8 priority | 40.68% | -46.78% | 1.100 | 4.305 | 34 |
| 1.00% | Baseline ufficiale | 34.55% | -50.67% | 0.925 | 4.980 | 28 |
| 1.00% | Trail8 priority | 35.21% | -50.67% | 0.992 | 3.953 | 34 |

## Uscite Trail8 Priority

- Uscite Trail8 nella variante: 12.
- Uscite Trail8 avvenute mentre le condizioni BUY erano ancora vere: 10.

| Data | Entry | Exit USD | Return trade | Peak | Stop | Mom 7g | Volume rel | BUY ancora vero |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 2019-06-27 | 2019-04-23 | 294.27 | 71.64% | 336.75 | 309.81 | 8.31% | 60.94% | True |
| 2020-09-03 | 2020-07-21 | 385.67 | 57.41% | 477.05 | 438.89 | 0.79% | 59.36% | True |
| 2020-11-26 | 2020-10-21 | 518.80 | 32.28% | 608.45 | 559.78 | 10.00% | 85.02% | True |
| 2021-01-11 | 2020-11-27 | 1090.15 | 110.66% | 1281.08 | 1178.59 | 4.80% | 102.69% | True |
| 2021-04-07 | 2021-03-31 | 1971.08 | 2.75% | 2143.23 | 1971.77 | 2.75% | 37.80% | True |
| 2021-05-12 | 2021-04-17 | 3785.85 | 61.45% | 4168.70 | 3835.21 | 7.47% | 58.87% | True |
| 2021-09-07 | 2021-07-26 | 3426.39 | 53.42% | 3952.13 | 3635.96 | -0.21% | 85.80% | False |
| 2021-11-23 | 2021-10-01 | 4340.76 | 31.24% | 4812.09 | 4427.12 | 2.95% | 20.77% | True |
| 2021-12-03 | 2021-11-30 | 4220.71 | -8.87% | 4631.48 | 4260.96 | 4.71% | 25.17% | True |
| 2023-04-19 | 2023-03-13 | 1936.40 | 15.24% | 2120.01 | 1950.41 | 0.82% | 49.07% | True |
| 2024-03-15 | 2024-02-06 | 3735.22 | 57.46% | 4066.45 | 3741.13 | -4.03% | 39.74% | False |
| 2025-08-18 | 2025-07-07 | 4312.50 | 69.58% | 4756.28 | 4375.77 | 2.02% | 28.69% | True |

## File generati

- `reports\trail_priority_events.csv`
- `reports\trail_priority_trades.csv`
