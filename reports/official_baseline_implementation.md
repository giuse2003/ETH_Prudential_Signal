# Official Baseline Implementation

Data: `2026-06-28`.

Questo report registra la promozione del candidato combinato a Baseline
ufficiale del progetto.

## Regole Implementate

Ingresso:

- condizioni storiche Baseline:
  - `Close > SMA200`;
  - `SMA50 > SMA200`;
  - `RSI >= 40`;
  - `Close > Close_7d_ago`;
  - `Volume > VolumeAvg20`;
- nuovo filtro sui soli nuovi ingressi:
  - `RSI <= 65`.

Nota operativa importante:

- `RSI <= 65` filtra solo i nuovi ingressi;
- se la posizione e' gia' aperta e le vecchie condizioni di acquisto restano
  vere, il sistema mantiene la posizione;
- questo evita di trasformare il filtro ingresso in una falsa regola di uscita.

Uscita:

- uscita ufficiale storica:
  - `Close < SMA50`;
- nuova uscita protettiva:
  - trailing stop 8% dal massimo `Close` raggiunto da quando la posizione e'
    aperta;
  - il trailing vende solo se confermato da:
    - momentum 7 giorni >= -5%;
    - volume relativo >= +20%.

Variante non implementata:

- `trade return >= 15%` come ulteriore conferma del trailing.

Motivo:

- migliora solo marginalmente;
- dipende dal singolo caso 2023;
- aumenta complessita' e rischio overfit.

## File Modificati

- `strategy/signals.py`
  - aggiunte costanti ufficiali del modello;
  - aggiunto filtro `RSI <= 65` sui nuovi ingressi;
  - aggiunto trailing stop 8% confermato da momentum e volume;
  - aggiunte colonne diagnostiche:
    - `Entry_RSI_Filter_Passed`;
    - `Official_Sell`;
    - `Trail8_Stop_Hit`;
    - `Trail8_Confirmed`.
- `reports/generate.py`
  - aggiornate condizioni esposte in `status.json` e `live-status.json`.
- `cloudflare-worker/src/worker.js`
  - aggiornato testo `/conditions`;
  - aggiornato fallback di condizioni buy/sell.
- `tests/test_signal_rules.py`
  - aggiunti test dedicati al nuovo filtro RSI;
  - aggiunti test dedicati al trailing stop;
  - aggiunto test regressione: `RSI <= 65` vale solo sui nuovi ingressi.
- `tests/test_chart_data_json.py`
- `tests/test_telegram_message.py`
- `tests/test_telegram_webhook.py`
  - aggiornati layout condizioni e aspettative.

## Verifica Metriche

Verifica locale su `data/indicators_with_signals.csv`, ricalcolando i segnali
ufficiali fino alla candela `2026-06-27` e misurando il backtest in EUR:

| Metrica | Valore |
|---|---:|
| Annualizzato | +42,74% |
| Max drawdown | -45,09% |
| Sharpe | 1,079 |
| Profit factor | 5,999 |
| Operazioni | 28 |
| Uscite Trail8 confermate | 4 |

Uscite Trail8 confermate:

- `2020-09-04`;
- `2021-09-07`;
- `2023-04-20`;
- `2024-03-15`.

Queste metriche coincidono con il candidato approvato nel gate decisionale.

## Test Eseguiti

```powershell
python -m py_compile strategy\signals.py reports\generate.py telegram_webhook.py
node --check cloudflare-worker\src\worker.js
python -m unittest discover -s tests -v
```

Risultato:

```text
Ran 60 tests
OK
```

Nota:

- durante i test compare il warning noto sul download Yahoo non riuscito e
  fallback al file storico temporaneo;
- il warning non blocca i test.

## Stato

La nuova Baseline ufficiale e' implementata nel codice.

Prossimo passo:

- commit e push delle modifiche;
- dopo il push, monitorare il prossimo run operativo per verificare
  `status.json`, `live-status.json`, dashboard e Telegram.
