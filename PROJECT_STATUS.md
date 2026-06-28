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
- `scripts/run_rsi65_blocked_entry_audit.py`: audit evento-per-evento degli
  ingressi bloccati dal filtro sperimentale `RSI <= 65`.
- `scripts/run_entry_trade_comparison.py`: confronto trade-by-trade tra
  Baseline e ingresso sperimentale `RSI <= 65`, con uscita ufficiale invariata.
- `scripts/run_entry_yearly_validation.py`: validazione annuale Baseline vs
  ingresso sperimentale `RSI <= 65`, incluse operazioni per anno.
- `scripts/run_entry_cost_stress.py`: stress test costi/slippage Baseline vs
  ingresso sperimentale `RSI <= 65`.
- `scripts/run_entry_threshold_robustness.py`: robustezza soglia RSI per i
  soli ingressi, testando da `RSI <= 63` a `RSI <= 70`.
- `scripts/run_exit_signal_analysis.py`: analisi dedicata ai soli segnali di
  uscita, con ingressi Baseline invariati.
- `scripts/run_trail5_exit_event_audit.py`: audit evento-per-evento del
  candidato uscita `Trail8 confermato -5 / vol +20`.
- `scripts/run_exit_trade_comparison.py`: confronto completo trade-by-trade
  tra Baseline e candidato uscita `Trail8 confermato -5 / vol +20`.
- `scripts/run_exit_segment_impact.py`: impatto netto dei segmenti Baseline
  modificati dal candidato uscita `Trail8 confermato -5 / vol +20`.
- `scripts/run_exit_candidate_validation.py`: validazione costi/slippage e
  anno per anno del candidato uscita `Trail8 confermato -5 / vol +20`.
- `scripts/run_final_combined_candidate_validation.py`: comparazione finale
  tra Baseline ufficiale e candidato combinato `RSI <= 65` in ingresso +
  `Trail8 confermato -5 / vol +20` in uscita.
- `scripts/run_2023_residual_exit_audit.py`: audit del peggioramento residuo
  2023 e test dei filtri secondari `trade return >= 15%` e `max gain >= 35%`.
- `scripts/run_combined_walkforward_validation.py`: validazione cronologica
  del candidato combinato principale e della variante secondaria
  `trade return >= 15%`.
- `reports/final_promotion_gate.md`: gate decisionale finale per valutare la
  promozione del candidato combinato a nuova Baseline ufficiale.
- `reports/official_baseline_implementation.md`: registrazione della
  promozione effettiva del candidato combinato a Baseline ufficiale.
- Analisi ingressi chiusa provvisoriamente: `RSI <= 65` resta candidato
  principale, non ufficiale.
- Analisi uscite chiusa provvisoriamente: `Trail8 confermato -5 / vol +20`
  resta candidato uscita principale, non ufficiale.
- Comparazione finale completata: il combinato migliora la Baseline ufficiale
  su periodo completo, costi e anni principali, ma resta candidato in
  validazione per audit residuo 2023.
- Audit residuo 2023 completato: il peggioramento e' piccolo e circoscritto;
  `trade return >= 15%` e' candidato secondario, ma non viene promosso per
  rischio overfit su un solo evento.
- Validazione cronologica completata: il candidato combinato principale batte
  la Baseline in 3 finestre su 4 e resta invariato nella quarta; la variante
  `trade return >= 15%` non viene promossa per beneficio marginale.
- Gate decisionale finale completato: il candidato principale e' tecnicamente
  promuovibile; la Baseline ufficiale resta invariata fino a conferma esplicita
  di implementazione.
- Nuova Baseline ufficiale implementata: ingresso Baseline + `RSI <= 65` sui
  soli nuovi ingressi, uscita ufficiale + `Trail8 -5 / vol +20`.
- Worker Telegram deployato dopo l'implementazione per aggiornare `/conditions`
  alla nuova Baseline. Version ID Cloudflare:
  `e61c4c42-9738-4c82-bacc-b5e50c8aafbb`.
- Testo `/conditions` aggiornato per esplicitare le soglie Trail8:
  momentum 7 giorni >= -5% e volume >= media 20 giorni +20%. Version ID
  Cloudflare: `8557d497-04f3-4580-90c5-00f191331514`.
- Analisi corrente del modello: commit e push delle modifiche; poi monitoraggio
  del primo run operativo e del comando `/conditions`.
  Benchmark operativo: `Baseline ufficiale`; i confronti con benchmark passivi
  restano fuori dalla selezione dei segnali.
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
