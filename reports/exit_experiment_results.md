# Exit Experiment Results

Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.

Le varianti forzano `VENDI` solo nel frame sperimentale del backtest.

## Baseline

- Annualizzato: 31.78%
- Max drawdown: -52.57%
- Sharpe: 0.849
- Profit factor: 4.327

## Migliori Varianti Per Drawdown

| Variante | Ann. | Max DD | Delta DD | Sharpe | Profit factor | Operazioni | Net 0,25% DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| exit_below_sma50_or_momentum_negative | 22.71% | -35.65% | 16.93% | 0.781 | 2.369 | 70 | -41.81% |
| trailing_stop_8pct | 20.52% | -41.93% | 10.64% | 0.690 | 2.126 | 48 | -45.72% |
| exit_close_below_sma50_1d | 34.43% | -45.16% | 7.41% | 0.908 | 4.738 | 30 | -46.12% |
| exit_below_sma50_or_rsi_lt35 | 34.43% | -45.16% | 7.41% | 0.908 | 4.738 | 30 | -46.12% |
| trailing_stop_12pct | 30.29% | -46.31% | 6.26% | 0.882 | 3.071 | 38 | -48.16% |
| exit_close_below_sma50_and_momentum_negative | 32.56% | -48.75% | 3.83% | 0.874 | 4.317 | 32 | -50.51% |
| exit_close_below_sma50_and_sma50_falling_10d | 32.35% | -49.35% | 3.22% | 0.859 | 4.468 | 27 | -51.09% |
| exit_close_below_sma50_and_sma50_falling_5d | 32.02% | -49.35% | 3.22% | 0.854 | 4.393 | 28 | -51.22% |
| trailing_stop_10pct | 23.52% | -50.22% | 2.36% | 0.749 | 2.315 | 43 | -53.47% |
| exit_close_below_sma50_and_rsi_lt45 | 29.74% | -50.42% | 2.15% | 0.822 | 3.830 | 31 | -51.89% |

## Migliori Varianti Per Sharpe

| Variante | Ann. | Max DD | Sharpe | Delta Sharpe | Profit factor | Operazioni |
|---|---:|---:|---:|---:|---:|---:|
| trailing_stop_20pct | 38.08% | -54.78% | 0.984 | 0.135 | 4.968 | 28 |
| trailing_stop_15pct | 35.29% | -53.95% | 0.955 | 0.106 | 3.688 | 32 |
| exit_close_below_sma50_1d | 34.43% | -45.16% | 0.908 | 0.059 | 4.738 | 30 |
| exit_below_sma50_or_rsi_lt35 | 34.43% | -45.16% | 0.908 | 0.059 | 4.738 | 30 |
| exit_close_below_sma50_and_volume_high | 34.34% | -51.51% | 0.904 | 0.055 | 4.667 | 28 |
| entry_loss_stop_10pct | 34.14% | -50.54% | 0.894 | 0.045 | 4.798 | 28 |
| exit_rsi_lt45 | 32.67% | -51.26% | 0.890 | 0.041 | 4.077 | 33 |
| entry_loss_stop_12pct | 33.77% | -51.71% | 0.887 | 0.038 | 4.713 | 28 |
| trailing_stop_12pct | 30.29% | -46.31% | 0.882 | 0.032 | 3.071 | 38 |
| trailing_stop_25pct | 32.99% | -52.57% | 0.876 | 0.027 | 4.386 | 28 |

## Sintesi

- Miglior drawdown assoluto: `exit_below_sma50_or_momentum_negative` con max DD -35.65%, ma rendimento annuo 22.71%.
- Miglior segnale tecnico semplice: `exit_close_below_sma50_1d`, max DD -45.16%, ann. 34.43%, Sharpe 0.908.
- Miglior stop sul prezzo di ingresso: `entry_loss_stop_8pct`, max DD -50.54%, ann. 32.84%, Sharpe 0.872.

Nessuna variante viene promossa a regola operativa in questa fase.
