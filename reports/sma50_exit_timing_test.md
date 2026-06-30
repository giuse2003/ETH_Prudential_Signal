# SMA50 Exit Timing Test

Test sperimentale: uscita se `Close < SMA50` per 1 giorno contro Baseline `Close < SMA50` per 2 giorni.

Ingressi e Trail8 restano invariati. Le metriche sono in USD.

## Metriche

| Modello | Entrate | Uscite | Uscite SMA50 | Uscite Trail8 | Totale | Ann. | Max DD | Sharpe | PF | Win rate | Esposizione |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SMA50 2 giorni + Trail8 | 28 | 28 | 24 | 4 | 2173.16% | 43.61% | -44.93% | 1.084 | 5.889 | 39.29% | 25.26% |
| SMA50 1 giorno + Trail8 | 29 | 29 | 25 | 4 | 2843.36% | 47.98% | -40.97% | 1.179 | 7.117 | 34.48% | 23.68% |

## Differenza 1 giorno vs 2 giorni

- Entrate: +1.
- Uscite: +1.
- Uscite SMA50 effettive: +1.
- Uscite Trail8 effettive: +0.
- Rendimento totale: 670.20%.
- Rendimento annualizzato: 4.36%.
- Max drawdown: 3.96%.
- Sharpe: +0.095.
- Profit factor: +1.228.

## File generato

- `reports\sma50_exit_timing_trades.csv`
