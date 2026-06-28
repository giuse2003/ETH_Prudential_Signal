# Project Status

Ultimo aggiornamento: 2026-06-28

## Obiettivo

Produrre segnali prudenziali giornalieri su Ethereum, pubblicarli in una
dashboard pubblica e gestire notifiche/comandi Telegram tramite Worker
Cloudflare.

## Stato Corrente

- Repository GitHub pubblico operativo.
- Dashboard GitHub Pages attiva da branch `master`, cartella `/docs`.
- Pipeline dati Yahoo Finance operativa per `ETH-USD` e `ETH-EUR`.
- Backtest riallineato dalla prima data comune reale `ETH-USD` / `ETH-EUR`
  (`2017-11-11` nel run corrente), senza riempimento EUR all'indietro.
- Backtest esteso con profit factor, metriche qualita' trade, turnover e
  scenari costo/slippage.
- Strategia ufficiale corrente: baseline SMA50 a 2 giorni. Il segnale `VENDI`
  scatta se il Close resta sotto SMA50 per due giorni consecutivi.
- Esperimenti modello isolati in `scripts/run_model_experiments.py`; non
  modificano i segnali ufficiali.
- Esperimenti uscite protettive isolati in `scripts/run_exit_experiments.py`;
  non modificano i segnali ufficiali.
- Approfondimento stop loss da ingresso isolato in
  `scripts/run_stop_loss_experiments.py`; non modifica i segnali ufficiali.
- Approfondimento trailing stop su Close isolato in
  `scripts/run_trailing_stop_experiments.py`; non modifica i segnali ufficiali.
- Esperimento trailing stop 8% con conferma momentum/volume isolato in
  `scripts/run_confirmed_trailing_experiments.py`; non modifica i segnali
  ufficiali.
- Candidati sperimentali in progress: Trail8 momentum >= -5% e volume >= +10%
  e trailing dinamico 15%/8%. Nessuno dei due e' una regola operativa; entrambi
  restano test da validare contro drawdown, costi e robustezza temporale.
- Validazione candidati principali isolata in
  `scripts/run_candidate_validation.py`; confronta periodo completo,
  sottoperiodi e walk-forward senza modificare i segnali ufficiali.
- Test combinazioni stop ingresso/trailing confermato isolato in
  `scripts/run_combined_exit_experiments.py`; non modifica i segnali ufficiali.
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
Ran 57 tests
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
- `MODEL_IMPROVEMENT_ROADMAP.md`: baseline e piano test per migliorare il
  modello.
- `ETH_MODEL_RESEARCH_DIARY.md`: diario operativo delle analisi sul modello,
  con test fatti, decisioni, regole respinte e prossime verifiche.
- `scripts/run_model_experiments.py`: runner sperimentale per confrontare
  filtri senza variare la strategia produttiva.
- `scripts/run_entry_quality_analysis.py`: analisi trade-by-trade degli
  ingressi Baseline, con feature al momento del segnale.
- `scripts/run_entry_filter_hypotheses.py`: test sperimentale di filtri di
  ingresso derivati dall'analisi trade-by-trade.
- `scripts/run_rsi_entry_filter_validation.py`: validazione dedicata del
  filtro sperimentale RSI sugli ingressi, con soglie, costi, anni e trade.
- `scripts/run_combined_entry_exit_validation.py`: validazione sperimentale
  combinata tra filtro ingresso RSI e trailing stop 8% confermato.
- `scripts/run_combined_candidate_event_audit.py`: audit evento-per-evento del
  candidato combinato, con ingressi bloccati, uscite trailing e trade.
- `scripts/run_combined_parameter_stress.py`: stress test parametrico del
  candidato combinato su RSI, momentum, volume e walk-forward.
- `scripts/run_top_candidate_comparison.py`: confronto diretto tra Baseline e
  i migliori candidati combinati emersi dallo stress test.
- `scripts/run_false_exit_recurrence_analysis.py`: analisi della ricorrenza
  delle false uscite tipo gennaio 2021.
- `scripts/run_signal_component_analysis.py`: report separato tra benchmark,
  modelli di uscita, filtri di ingresso e combinazioni.
- `scripts/run_entry_signal_analysis.py`: analisi dedicata ai soli filtri di
  ingresso, con uscita ufficiale invariata.
- Analisi corrente del modello: solo ingressi. Benchmark operativo:
  `Baseline ufficiale`; i confronti con benchmark passivi restano fuori dalla
  selezione dei segnali.
- `scripts/run_exit_experiments.py`: runner sperimentale per confrontare
  uscite protettive senza variare la strategia produttiva.
- `scripts/run_stop_loss_experiments.py`: runner sperimentale per analizzare
  stop loss da ingresso senza variare la strategia produttiva.
- `scripts/run_trailing_stop_experiments.py`: runner sperimentale per
  analizzare trailing stop su Close senza variare la strategia produttiva.
- `scripts/run_confirmed_trailing_experiments.py`: runner sperimentale per
  analizzare trailing stop 8% confermato da momentum/volume.
- `scripts/run_candidate_validation.py`: runner sperimentale per validare i
  candidati principali su periodo completo, sottoperiodi e walk-forward.
- `scripts/run_combined_exit_experiments.py`: runner sperimentale per combinare
  stop ingresso e trailing confermato.
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
- Rendimento liquidita nel backtest.
- Pulizia completa dei file legacy Render/FastAPI.
