# SMA50 Exit Timing Yearly Validation

Validazione annuale della variante `Close < SMA50` a 1 giorno contro Baseline a 2 giorni.
Ingressi e Trail8 restano invariati. Metriche in USD.

## Sintesi

- Anni con rendimento migliore usando SMA50 a 1 giorno: 3.
- Anni con rendimento peggiore usando SMA50 a 1 giorno: 3.
- Anni con drawdown annuale meno profondo: 3.
- Anni con drawdown annuale piu' profondo: 2.

## Tabella Annuale

| Anno | Ret 2g | Ret 1g | Delta ret | DD 2g | DD 1g | Delta DD | Sharpe 2g | Sharpe 1g | Entry 2g/1g | Exit 2g/1g | SMA50 exit 2g/1g | Trail8 exit 2g/1g |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a | 0/0 | 0/0 | 0/0 | 0/0 |
| 2018 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a | 0/0 | 0/0 | 0/0 | 0/0 |
| 2019 | 61.14% | 56.73% | -4.42% | -20.21% | -20.21% | 0.00% | 1.326 | 1.263 | 1/1 | 1/1 | 1/1 | 0/0 |
| 2020 | 178.27% | 156.01% | -22.25% | -24.43% | -24.97% | -0.54% | 2.291 | 2.140 | 4/5 | 3/4 | 2/3 | 1/1 |
| 2021 | 268.68% | 277.51% | 8.82% | -44.93% | -40.97% | 3.96% | 1.965 | 2.035 | 5/6 | 6/7 | 5/6 | 1/1 |
| 2022 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a | 0/0 | 0/0 | 0/0 | 0/0 |
| 2023 | 1.51% | 0.74% | -0.78% | -23.63% | -24.32% | -0.69% | 0.195 | 0.167 | 7/8 | 6/7 | 5/6 | 1/1 |
| 2024 | -1.75% | 20.40% | 22.15% | -40.39% | -28.50% | 11.88% | 0.088 | 0.803 | 7/6 | 8/7 | 7/6 | 1/1 |
| 2025 | 35.07% | 56.97% | 21.90% | -26.17% | -15.31% | 10.86% | 1.018 | 1.507 | 4/3 | 4/3 | 4/3 | 0/0 |
| 2026 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a | 0/0 | 0/0 | 0/0 | 0/0 |

## File generato

- `reports\sma50_exit_timing_yearly_validation.csv`
