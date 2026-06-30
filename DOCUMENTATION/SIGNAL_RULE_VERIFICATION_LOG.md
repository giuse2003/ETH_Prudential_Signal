# ETH Signal Rule Verification Log

Questo file sostituisce il log sperimentale importato dal progetto BTC.
Le metriche qui sotto sono prodotte dal run locale Ethereum eseguito con:

```text
python main.py --force-download
```

## Dataset

- Serie principale: `ETH-USD`.
- Serie EUR di supporto: `ETH-EUR`.
- Fonte dati storici: Yahoo Finance.
- Ultima candela chiusa del run: `2026-06-22`.
- Calendario: crypto 365 giorni.

## Regole correnti

- `ACQUISTA`: condizioni di trend, momentum, RSI e volume favorevoli.
- `MANTIENI`: conserva l'esposizione precedente.
- `VENDI`: prezzo sotto SMA50.
- I segnali vengono applicati al rendimento della giornata successiva per evitare look-ahead bias.

## Risultato Backtest ETH

| Strategia | Rendimento totale | Rendimento annualizzato | Drawdown massimo | Operazioni | Win rate | Sharpe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ETH Prudential Signal | +980,86% | +31,80% | -52,57% | 28 | 39,3% | 0,849 |
| Buy & Hold Ethereum | +438,05% | +21,55% | -93,96% | 0 | n/a | 0,659 |

## Artefatti Generati

- `reports/report.txt`
- `reports/backtest.json`
- `reports/equity_timeseries.csv`
- `docs/backtest.json`
