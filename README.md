# ETH Prudential Signal

Ultimo aggiornamento: 2026-07-22

ETH Prudential Signal is a transparent Ethereum risk-management model based on
daily technical indicators: SMA50, SMA200, RSI and volume confirmation. It
generates three signals — `ACQUISTA`, `MANTIENI`, `VENDI` — and publishes the
current status through a GitHub Pages dashboard and a Telegram bot.

The project is for informational and educational purposes only. It is not
financial advice.

Sistema Python per il monitoraggio prudenziale di Ethereum tramite indicatori
tecnici giornalieri, dashboard web e notifiche Telegram.

## What it does

- Analyzes Ethereum daily closed candles.
- Calculates SMA50, SMA200, RSI(14), volume average and trend conditions.
- Generates BUY / HOLD / SELL style signals.
- Compares the strategy against Ethereum Buy & Hold through backtesting.
- Publishes a public dashboard.
- Supports Telegram commands and alerts.

## Strategy rules

### BUY / ACQUISTA

- Close above SMA200.
- SMA50 above SMA200.
- 40 <= RSI(14) <= 65.
- Close above the close of 7 days ago.
- Daily volume above 20-day average volume.

### SELL / VENDI

- Close below SMA50.
- Or trailing stop 8% from the highest close reached after entry, confirmed by
  7-day momentum >= -5% and volume at least 20% above the 20-day average.

### HOLD / MANTIENI

- No buy or sell condition is triggered.

## Disclaimer

This project does not predict Ethereum price and does not guarantee profits.
It is a personal, transparent and educational project created to test simple
risk-management rules on Ethereum historical data.

Use it only as a technical monitoring tool.

## Monitor online

**[Apri la dashboard ETH Prudential Signal](https://giuse2003.github.io/ETH_Prudential_Signal/)**

La pagina mostra il segnale corrente, il livello di rischio, i prezzi ETH e
gli ultimi indicatori pubblicati dal monitor.

Il progetto genera tre possibili segnali:

- `ACQUISTA`: tutte le condizioni rialziste richieste sono confermate.
- `MANTIENI`: non ci sono conferme sufficienti per una nuova operazione.
- `VENDI`: le condizioni di debolezza previste dalla strategia sono confermate.

Le regole ufficiali correnti sono:

- acquisto: prezzo sopra SMA200, SMA50 sopra SMA200, RSI tra 40 e 65,
  momentum 7 giorni positivo e volume sopra la media 20 giorni;
- vendita: prezzo sotto SMA50 oppure trailing stop
  8% dal massimo Close post-ingresso, confermato da momentum 7 giorni >= -5%
  e volume almeno +20% sopra la media 20 giorni.

Il segnale e il livello di rischio sono strumenti informativi e non
costituiscono consulenza finanziaria.

## Funzionalita

- Download dei dati giornalieri `ETH-USD` e `ETH-EUR` tramite Yahoo Finance.
- Prezzi spot USD ed EUR tramite endpoint pubblico Coinbase.
- Calcolo di SMA50, SMA200, RSI(14), ATR(14), volume medio e massimo/minimo
  delle ultime 52 settimane.
- Generazione di segnale, punteggio tecnico e livello di rischio.
- Backtest della strategia rispetto al Buy & Hold.
- Report testuale, CSV storico, serie equity e grafico.
- Dashboard locale e dashboard pubblicabile con GitHub Pages.
- Monitor schedulato con GitHub Actions e notifiche Telegram esclusivamente
  LIVE quando varia almeno una delle 7 condizioni operative.
- Comando Telegram `/segnale` servito da Cloudflare Worker usando
  esclusivamente l'ultimo stato LIVE pubblicato.
- Iscrizioni Telegram persistenti su Supabase tramite `/iscrivimi` e
  `/disiscrivimi`.
- Card pubblica per aprire il bot e visualizzare il numero aggregato degli
  iscritti attivi.
- Grafico OHLC giornaliero con candele verdi/rosse, SMA50, SMA200, RSI e
  volumi: Yahoo Finance fornisce lo storico chiuso e Coinbase la candela UTC
  ancora in corso.

## Regole temporali

Ethereum viene trattato come un mercato attivo 7 giorni su 7:

- l'anno statistico contiene `365` periodi giornalieri;
- massimo e minimo a 52 settimane usano una finestra di `365` giorni;
- rendimento annualizzato e Sharpe Ratio usano `365` periodi;
- i segnali usano esclusivamente candele giornaliere concluse;
- la candela UTC del giorno corrente viene esclusa per evitare segnali basati
  su prezzo e volume ancora parziali.

## Logica del backtest

Il segnale calcolato alla chiusura del giorno viene applicato al rendimento del
giorno successivo, evitando l'uso anticipato di informazioni.

La mappatura del segnale e:

- `ACQUISTA`: esposizione 100%;
- `MANTIENI`: conserva l'esposizione precedente;
- `VENDI`: esposizione 0%.

Una operazione e definita come un trade long completato, dall'entrata
all'uscita. Il numero operazioni e il win rate considerano soltanto trade
chiusi; una posizione ancora aperta alla fine del periodo non viene inclusa.

Il backtest operativo e lordo. Nel progetto sono presenti anche report di
stress separati con costi/slippage per validare la robustezza del modello.

## Requisiti

- Python 3.13
- Dipendenze elencate in `requirements.txt`

Installazione:

```powershell
git clone https://github.com/giuse2003/ETH_Prudential_Signal.git
cd ETH_Prudential_Signal
python -m pip install -r requirements.txt
```

## Esecuzione analisi

```powershell
python main.py --force-download
```

Output principali:

- `reports/report.txt`
- `reports/historical_signals.csv`
- `reports/price_sma_signals.png`
- `reports/equity_timeseries.csv`
- `reports/status.json`

## Dashboard locale

Prima genera i dati:

```powershell
python main.py --force-download
```

Poi avvia il server:

```powershell
python run_dashboard.py
```

Apri `http://localhost:8000`.

Il server locale pubblica direttamente la cartella `docs/`, quindi mostra la
stessa dashboard distribuita con GitHub Pages.

## Dashboard GitHub Pages

La dashboard pubblica e disponibile qui:

**[https://giuse2003.github.io/ETH_Prudential_Signal/](https://giuse2003.github.io/ETH_Prudential_Signal/)**

I file della dashboard si trovano in `docs/` e leggono `docs/status.json`.

Configurazione:

1. Apri **Settings > Pages** nel repository.
2. Seleziona **Deploy from branch**.
3. Imposta il branch `master` e la cartella `/docs`.

Il workflow aggiorna `reports/status.json`, lo copia in `docs/status.json` e
pubblica il nuovo stato.

## Telegram e GitHub Actions

Configura questi GitHub Actions Secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Il workflow `.github/workflows/hourly-monitor.yml`:

1. scarica i dati aggiornati;
2. rimuove la candela giornaliera UTC ancora aperta;
3. calcola segnale e rischio sull'ultima candela chiusa;
4. aggiorna la dashboard;
5. non invia segnali DAILY;
6. verifica le 7 condizioni LIVE e invia Telegram solo quando una variazione
   resta stabile per almeno 10 minuti.

La pianificazione GitHub Actions e best effort e puo subire ritardi.

### Comando Telegram in tempo reale

Scrivi al bot:

```text
/segnale
```

Il comando viene gestito dal Cloudflare Worker:

```text
https://eth-prudential-signal.giuse2003.workers.dev
```

Il webhook:

- riceve `POST /webhook` da Telegram;
- scarica `docs/live-status.json` dal GitHub Raw URL pubblico;
- non salva copie locali e non modifica il monitor;
- usa il formatter Telegram gia esistente.
- risponde solo alla chat privata dell'utente che ha inviato il comando.
- risponde con segnale LIVE, prezzo EUR e stato sintetico delle 7 condizioni;
- se lo stato LIVE non e disponibile, restituisce un errore temporaneo senza
  ripiegare sul segnale DAILY.

Cloudflare Worker e l'unico backend pubblico del progetto. Il precedente
servizio Render/FastAPI e stato rimosso dopo aver verificato che webhook,
iscrizioni e conteggio pubblico passano tutti dal Worker.

Sono disponibili anche `/start` e `/help`.

Il webhook supporta inoltre:

```text
/iscrivimi
/disiscrivimi
/privacy
```

I comandi funzionano nelle chat private con il bot. I gruppi vengono ignorati.

La dashboard pubblica contiene il pulsante **Iscriviti su Telegram**, collegato
a `@ETH_Prudential_Signal_bot`, e mostra il conteggio aggregato ottenuto da:

```text
GET https://eth-prudential-signal.giuse2003.workers.dev/subscribers/count
```

L'endpoint restituisce soltanto `active_subscribers`. Il frontend non contiene
chiavi Supabase, token Telegram o altri secret.

Il deploy e il collegamento Telegram sono stati verificati su Cloudflare Worker:

- health check `GET /` con risposta `{"status":"ok"}`;
- webhook Telegram registrato su `/webhook`;
- comando `/segnale` verificato con risposta immediata.

Guida completa:
[CLOUDFLARE_WORKER_DEPLOYMENT.md](DOCUMENTATION/CLOUDFLARE_WORKER_DEPLOYMENT.md).

Il workflow `Telegram command menu` serve solo ad aggiornare il menu dei
comandi Telegram. Il workflow `Hourly ETH monitor (Telegram)` deve restare
attivo per aggiornare i JSON pubblici e inviare esclusivamente i cambi LIVE.

Gli iscritti Telegram ETH vengono salvati in Supabase nella tabella dedicata
`public.telegram_subscribers_eth`, separata da eventuali tabelle del progetto
BTC.

## Test

```powershell
python -m unittest discover -s tests -v
```

I test verificano:

- esclusione della candela giornaliera corrente;
- gestione di indici con e senza timezone;
- annualizzazione su 365 giorni;
- conteggio dei soli trade completati;
- esclusione delle posizioni ancora aperte dal win rate.

## Struttura

```text
backtest/       motore e metriche del backtest
data/           download, caricamento e filtro candele chiuse
indicators/     indicatori tecnici
live/           prezzi spot Coinbase
notifications/  invio Telegram
DOCUMENTATION/  documentazione progettuale e decisioni
reports/        generazione degli output
state/          stato persistente del monitor
strategy/       punteggio, segnale e rischio
tests/          test automatici
docs/           dashboard GitHub Pages
```

Per lo stato corrente e le decisioni progettuali:

- [MODEL_DOCUMENTATION_INDEX.md](DOCUMENTATION/MODEL_DOCUMENTATION_INDEX.md)
- [PROJECT_STATUS.md](DOCUMENTATION/PROJECT_STATUS.md)
- [DECISION_LOG.md](DOCUMENTATION/DECISION_LOG.md)
- [TELEGRAM_SUBSCRIBERS_ROADMAP.md](DOCUMENTATION/TELEGRAM_SUBSCRIBERS_ROADMAP.md)
- [SUPABASE_SETUP.md](DOCUMENTATION/SUPABASE_SETUP.md)
- [BASELINE_SYNC_CHECKLIST.md](DOCUMENTATION/BASELINE_SYNC_CHECKLIST.md)
