# ETH-USD Signal Rule Verification Log

Ultimo aggiornamento: 2026-07-27

## Dataset canonico

- Coinbase Advanced Trade `ETH-USD`, granularita `ONE_DAY`;
- storico continuo `2016-05-23`–`2026-07-26`;
- valutazione post warm-up `2016-12-08`–`2026-07-26`;
- 3.518 osservazioni senza duplicati o giorni mancanti;
- `ETH-EUR` esclusivamente spot informativo.

## Regole verificate

- cinque condizioni di acquisto: `Close>SMA200`, `SMA50>SMA200`, RSI 40–65
  per i nuovi ingressi, momentum 7 giorni positivo, volume sopra media 20;
- due condizioni di vendita: `Close<SMA50` oppure trailing 8% confermato;
- precedenza della vendita;
- azione neutrale `MANTIENI STATO ATTUALE`;
- esecuzione dal rendimento del giorno successivo;
- trade finali aperti esclusi da conteggio e win rate.

## Baseline v1

| Strategia | Rendimento totale | Annualizzato | Max drawdown | Trade | Win rate | Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| ETH-USD Signal | +18.663,52% | 72,16% | -45,89% | 36 | 36,11% | 1,357 |
| Buy & Hold | +23.716,22% | 76,47% | -94,01% | n/a | n/a | 1,076 |

Profit factor strategia: `14.00916695086703`.

## Verifica

```powershell
python -m pip install --require-hashes -r requirements.lock
python -m unittest discover -s tests -v
python reproduce.py --manifest docs/runs/baseline-v1-2026-07-26/manifest.json
```

La fonte canonica dei valori non arrotondati e il manifest congelato.
