# SMA50 Exit 1pct Filter Test

Test sperimentale: uscita a 1 giorno solo se `Close <= SMA50 * 0.99`.
Se la rottura non arriva ad almeno -1%, resta valida la Baseline a 2 giorni.
Ingressi e Trail8 restano invariati. Metriche in USD.

## Metriche

| Modello | Totale | Ann. | Max DD | Sharpe | PF | Operazioni | Entry | SMA50 exit | Trail8 exit | Esposizione | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SMA50 2 giorni + Trail8 | 2173.16% | 43.58% | -44.93% | 1.084 | 5.889 | 28 | 28 | 24 | 4 | 25.25% | 56.0 |
| SMA50 1 giorno pura + Trail8 | 2843.36% | 47.94% | -40.97% | 1.179 | 7.117 | 29 | 29 | 25 | 4 | 23.66% | 58.0 |
| SMA50 1 giorno solo se -1% + Trail8 | 2433.38% | 45.39% | -40.97% | 1.129 | 6.204 | 27 | 27 | 23 | 4 | 24.42% | 54.0 |

## Delta filtro -1%

| Confronto | Delta ann. | Delta DD | Delta Sharpe | Delta PF | Delta operazioni |
|---|---:|---:|---:|---:|---:|
| vs Baseline 2 giorni | 1.81% | 3.96% | +0.045 | +0.316 | -1 |
| vs SMA50 1 giorno pura | -2.55% | 0.00% | -0.050 | -0.912 | -2 |

## File generato

- `reports\sma50_exit_1pct_filter_trades.csv`
