# SMA50 Exit Timing Cost Stress

Stress costi/slippage per `Close < SMA50` a 1 giorno contro Baseline a 2 giorni.
Ingressi e Trail8 restano invariati. Metriche in USD.

## Metriche

| Costo | Modello | Totale | Ann. | Max DD | Sharpe | PF | Operazioni | Turnover |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0.00% | SMA50 2 giorni + Trail8 | 2173.16% | 43.61% | -44.93% | 1.084 | 5.889 | 28 | 56.0 |
| 0.00% | SMA50 1 giorno + Trail8 | 2843.36% | 47.98% | -40.97% | 1.179 | 7.117 | 29 | 58.0 |
| 0.10% | SMA50 2 giorni + Trail8 | 2049.36% | 42.69% | -44.99% | 1.068 | 5.786 | 28 | 56.0 |
| 0.10% | SMA50 1 giorno + Trail8 | 2677.38% | 46.99% | -41.03% | 1.162 | 6.958 | 29 | 58.0 |
| 0.25% | SMA50 2 giorni + Trail8 | 1875.99% | 41.30% | -45.07% | 1.045 | 5.637 | 28 | 56.0 |
| 0.25% | SMA50 1 giorno + Trail8 | 2445.52% | 45.51% | -41.12% | 1.137 | 6.732 | 29 | 58.0 |
| 0.50% | SMA50 2 giorni + Trail8 | 1617.06% | 39.02% | -46.78% | 1.005 | 5.404 | 28 | 56.0 |
| 0.50% | SMA50 1 giorno + Trail8 | 2100.64% | 43.08% | -43.06% | 1.094 | 6.382 | 29 | 58.0 |

## Delta 1 giorno vs 2 giorni

| Costo | Delta ann. | Delta DD | Delta Sharpe | Delta PF |
|---:|---:|---:|---:|---:|
| 0.00% | 4.36% | 3.96% | +0.095 | +1.228 |
| 0.10% | 4.30% | 3.95% | +0.094 | +1.172 |
| 0.25% | 4.21% | 3.95% | +0.092 | +1.094 |
| 0.50% | 4.06% | 3.71% | +0.090 | +0.979 |

## File generato

- `reports\sma50_exit_timing_cost_stress.csv`
