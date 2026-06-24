# Project Status

Ultimo aggiornamento: 2026-06-24

## Obiettivo

Produrre segnali prudenziali giornalieri su Ethereum, pubblicarli in una
dashboard pubblica e gestire notifiche/comandi Telegram tramite Worker
Cloudflare.

## Stato Corrente

- Repository GitHub pubblico operativo.
- Dashboard GitHub Pages attiva da branch `master`, cartella `/docs`.
- Pipeline dati Yahoo Finance operativa per `ETH-USD` e `ETH-EUR`.
- Prezzi spot Coinbase disponibili in USD ed EUR.
- Indicatori, strategia, rischio, report e dashboard implementati.
- Backtest dashboard alimentato da `docs/backtest.json`, non piu hard-coded.
- Worker Cloudflare `eth-prudential-signal` deployato.
- Bot Telegram ETH dedicato collegato al Worker via webhook.
- Menu comandi Telegram aggiornato tramite GitHub Actions.
- Comandi `/start`, `/segnale` e `/conditions` verificati.
- GitHub Actions Secrets configurati per Telegram:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`
- Cloudflare Worker Secrets configurati per Telegram:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_WEBHOOK_SECRET`
- Supabase iscritti collegato: schema, Worker e secret puntano alla tabella
  dedicata `public.telegram_subscribers_eth`.
- Endpoint `/subscribers/count` operativo; al momento restituisce `0`
  iscritti attivi.

## Verifiche Recenti

```powershell
python -m unittest discover -s tests
node --check cloudflare-worker\src\worker.js
```

Risultato:

```text
Ran 54 tests
OK
```

Endpoint verificati:

- `GET https://eth-prudential-signal.giuse2003.workers.dev/` -> OK
- `GET https://eth-prudential-signal.giuse2003.workers.dev/live-preview` -> OK
- `GET https://eth-prudential-signal.giuse2003.workers.dev/subscribers/health`
  -> configurato true su `telegram_subscribers_eth`, senza esporre valori.
- `GET https://eth-prudential-signal.giuse2003.workers.dev/subscribers/count`
  -> `{"active_subscribers":0}`.

## Supabase

Decisione attuale:

- usare una tabella ETH dedicata: `public.telegram_subscribers_eth`;
- questa scelta consente di riusare lo stesso progetto Supabase del BTC senza
  mescolare iscritti o stati di iscrizione.
- il progetto Supabase condiviso e stato rinominato `crypto-prudential-signal`.

Da completare:

- validare il workflow GitHub Actions `Hourly ETH monitor (Telegram)`.

## File Principali

- `ETH_PROJECT_ROADMAP.md`: roadmap operativa aggiornata.
- `config.py`: configurazione centralizzata.
- `main.py`: esecuzione completa locale.
- `hourly_monitor.py`: monitor GitHub Actions.
- `strategy/signals.py`: regole segnale/rischio.
- `backtest/backtest.py`: esposizione e metriche.
- `reports/generate.py`: report e JSON dashboard.
- `cloudflare-worker/src/worker.js`: bot Telegram e API pubbliche.
- `cloudflare-worker/wrangler.toml`: configurazione Worker.
- `supabase/telegram_subscribers.sql`: schema database iscritti ETH.
- `telegram_subscribers.py`: client Supabase legacy/server-side.

## Ambito Rinviato

- Broadcast automatico a tutti gli iscritti Supabase.
- Costi di transazione, spread, slippage e rendimento liquidita nel backtest.
- Pulizia completa dei file legacy Render/FastAPI.
