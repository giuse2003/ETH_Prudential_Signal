# ETH-USD Signal

Modello algoritmico long/cash per Ethereum basato su candele giornaliere UTC
Coinbase `ETH-USD`. Il repository e l'infrastruttura mantengono il nome
`ETH_Prudential_Signal`; il nome metodologico pubblico e **ETH-USD Signal**.

## Contratto dati

- Coinbase Advanced Trade `ETH-USD` e l'unica fonte di candele, volumi,
  indicatori, segnali e backtest.
- Lo storico continuo canonico parte dal `2016-05-23`. Le date `2016-05-21` e
  `2016-05-22` sono assenti nello storico precedente e non vengono interpolate.
- La candela UTC corrente e sempre esclusa dal run DAILY.
- La cache `data/ETH-USD_coinbase_daily.csv` e soltanto una copia Coinbase.
- Non esiste fallback verso Yahoo o altri mercati.
- Coinbase `ETH-EUR` viene interrogato esclusivamente per il prezzo spot
  informativo mostrato nei contenuti LIVE.

## Baseline ETH v1

Le regole strategiche ETH approvate sono rimaste invariate durante la migrazione.

`ACQUISTA` richiede tutte e cinque le condizioni:

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `40 <= RSI(14) <= 65` per i nuovi ingressi;
4. `Close > Close.shift(7)`;
5. `Volume ETH-USD > VolumeAvg20`.

`VENDI` scatta quando e vera almeno una delle due condizioni:

1. `Close < SMA50` nella candela corrente;
2. trailing stop 8% dal massimo Close post-ingresso, confermato da momentum a
   7 giorni almeno `-5%` e volume relativo almeno `+20%`.

La vendita ha precedenza. In ogni altro caso l'azione e
`MANTIENI STATO ATTUALE`. L'esposizione e binaria: 100% dopo `ACQUISTA`, 0%
dopo `VENDI`; il mantenimento conserva lo stato precedente.

## DAILY e LIVE PREVIEW

- **DAILY** usa soltanto candele Coinbase concluse ed e l'unico input del
  backtest e dello storico ufficiale.
- **LIVE PREVIEW** aggiunge una riga provvisoria con prezzo e volume 24h
  Coinbase `ETH-USD`, ricalcola la stessa strategia e puo cambiare prima della
  chiusura UTC.
- Telegram pubblica soltanto variazioni LIVE stabilizzate; non invia segnali
  DAILY.

## Baseline e run operativo

La baseline congelata v1 e immutabile:

`docs/runs/baseline-v1-2026-07-26/manifest.json`

Il run operativo si aggiorna con ogni nuova candela conclusa. I suoi artefatti
sono descritti da `docs/manifest.json` e condividono lo stesso `run_id`.
Dashboard e Worker consumano il pacchetto pubblicato senza ricalcolare il modello.

Artefatti del run:

```text
raw_candles.csv
status.json
live-status.json
chart-data.json
historical_signals.csv
equity_timeseries.csv
report.txt
price_sma_signals.png
manifest.json
```

## Risultati baseline v1

Periodo valutato: `2016-12-08`–`2026-07-26`, 3.518 osservazioni.

| Metrica | ETH-USD Signal | Buy & Hold |
|---|---:|---:|
| Rendimento totale | 18.663,52% | 23.716,22% |
| Rendimento annualizzato | 72,16% | 76,47% |
| Max drawdown | -45,89% | -94,01% |
| Sharpe | 1,357 | 1,076 |
| Trade completati | 36 | n/a |
| Win rate | 36,11% | n/a |
| Profit factor | 14,009 | n/a |

I valori completi, non arrotondati, sono nel manifest congelato.

## Esecuzione

Richiede Python `3.13.0`.

```powershell
python -m pip install --require-hashes -r requirements.lock
python main.py --force-download
python reproduce.py --manifest docs/runs/baseline-v1-2026-07-26/manifest.json
python -m unittest discover -s tests -v
```

Per creare esplicitamente una nuova baseline serve una nuova versione e un
nuovo cutoff approvato:

```powershell
python freeze_baseline.py --as-of AAAA-MM-GG --output docs/runs/baseline-vN-AAAA-MM-GG --run-id baseline-vN-AAAA-MM-GG --source-tag baseline-vN-AAAA-MM-GG --force-download
```

## Limiti

I risultati sono storici, non una previsione. Il modello puo essere soggetto a
overfitting e dipende dalla qualita dei dati Coinbase. Commissioni, spread,
slippage, imposte e rendimento della liquidita non sono inclusi. Non esiste un
vero periodo out-of-sample separato. L'esposizione binaria e il drawdown storico
restano rischi materiali. Il progetto e informativo e non costituisce consulenza
finanziaria.

Per la procedura completa vedere [REPRODUCIBILITY.md](REPRODUCIBILITY.md) e
[EVALUATION_VALUES.md](EVALUATION_VALUES.md).
