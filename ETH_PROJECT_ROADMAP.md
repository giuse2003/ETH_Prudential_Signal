# ETH Prudential Signal - Roadmap Operativa

Ultimo aggiornamento: 2026-06-24

Questo file tiene traccia delle problematiche riscontrate durante la creazione
del progetto Ethereum e delle attivita ancora da completare. Va aggiornato a
ogni avanzamento rilevante.

## Stato Attuale

- Repository GitHub pubblico creato:
  `https://github.com/giuse2003/ETH_Prudential_Signal`
- Dashboard GitHub Pages attiva:
  `https://giuse2003.github.io/ETH_Prudential_Signal/`
- Branch principale: `master`
- Dashboard statica pubblicata da `/docs`.
- Worker Cloudflare ETH deployato:
  `https://eth-prudential-signal.giuse2003.workers.dev/`
- Bot Telegram ETH dedicato creato e collegato via webhook:
  `@ETH_Prudential_Signal_bot`
- Test Python: 54 test passati.
- Ultimo backtest ETH generato su candela chiusa `2026-06-22`.

## Problemi Riscontrati

### 1. Metriche dashboard copiate dal progetto BTC

La sezione backtest della dashboard mostrava gli stessi valori del progetto
Bitcoin per rendimento, drawdown e Sharpe ratio.

Cause:

- i dati ETH venivano generati correttamente;
- la sezione backtest era pero hard-coded in `docs/index.html`;
- non esisteva un file JSON dedicato alle metriche di backtest.

Correzioni applicate:

- aggiunto `reports/backtest.json`;
- aggiunto `docs/backtest.json`;
- aggiornata la dashboard per leggere le metriche da `backtest.json`;
- aggiornati `main.py`, `hourly_monitor.py` e workflow GitHub Actions;
- rimossi i vecchi valori BTC dalla dashboard;
- aggiornati `PROJECT_OVERVIEW.md` e `SIGNAL_RULE_VERIFICATION_LOG.md`.

Metriche ETH correnti:

| Strategia | Rendimento totale | Rendimento annualizzato | Drawdown massimo | Operazioni | Win rate | Sharpe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ETH Prudential Signal | +980,86% | +31,80% | -52,57% | 28 | 39,3% | 0,849 |
| Buy & Hold Ethereum | +438,05% | +21,55% | -93,96% | 0 | n/a | 0,659 |

### 2. GitHub Pages non attivo inizialmente

La dashboard era presente nella cartella `docs`, ma GitHub Pages non era
ancora configurato.

Correzione applicata:

- attivato GitHub Pages da branch `master`, cartella `/docs`;
- verificato HTTP 200 sulla dashboard pubblica.

### 3. Bot Telegram ETH non operativo

Il codice e la dashboard puntano a `@ETH_Prudential_Signal_bot`, ma il bot non
e ancora pienamente configurato.

Problemi rilevati:

- il repository ETH non aveva secret GitHub Actions;
- il Worker Cloudflare ETH era assente ed e stato deployato solo come base;
- il Worker Cloudflare ETH non aveva secret Telegram configurati;
- l'endpoint `/subscribers/count` restituisce `503`;
- il webhook Telegram non risultava ancora registrato verso il Worker ETH;
- il comando `/segnale` falliva quando `docs/live-status.json` non era ancora
  disponibile;
- il deploy locale via Wrangler richiedeva un token API Cloudflare dedicato,
  perche l'ambiente locale non aveva `CLOUDFLARE_API_TOKEN` configurato;
- il workflow `Telegram command menu` esisteva nel repository, ma GitHub
  Actions non lo aveva indicizzato finche non e stato aggiornato e pushato di
  nuovo;
- i token e i secret del progetto BTC non sono leggibili da GitHub/Cloudflare,
  quindi non possono essere copiati automaticamente;
- alcuni URL raw puntavano al branch `main`, mentre il repo ETH usa `master`.

Correzioni applicate:

- deployato Worker Cloudflare `eth-prudential-signal`;
- corretto `main` -> `master` negli URL raw usati da Worker e webhook legacy;
- verificato che `https://eth-prudential-signal.giuse2003.workers.dev/`
  risponda `{"status":"ok"}`.
- creato/verificato bot Telegram dedicato `@ETH_Prudential_Signal_bot`;
- configurati i secret GitHub Actions:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`
- configurati i secret Cloudflare Worker ETH:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_WEBHOOK_SECRET`
- registrato il webhook Telegram verso:
  `https://eth-prudential-signal.giuse2003.workers.dev/webhook`.
- aggiornato il Worker per usare `docs/status.json` come fallback quando
  `docs/live-status.json` non esiste ancora;
- verificato che `/live-preview` restituisca il segnale daily ETH e che
  `/segnale` funzioni dal bot Telegram.
- creato token API Cloudflare dedicato per Wrangler;
- verificato `npx wrangler whoami`;
- eseguito deploy via `npx wrangler deploy`
  (Version ID `d88bee42-afd3-4f13-ac82-d35dc9794809`).
- aggiornato e lanciato con successo il workflow `Telegram command menu`.

## Checklist Prossimi Passi

### A. Completare configurazione Telegram

- [x] Creare o verificare definitivamente il bot Telegram
      `@ETH_Prudential_Signal_bot` tramite BotFather.
- [x] Recuperare il token del bot ETH da BotFather.
- [x] Decidere se usare una chat amministratore separata per ETH.
- [x] Recuperare `TELEGRAM_CHAT_ID` per le notifiche automatiche ETH.
- [x] Generare un nuovo `TELEGRAM_WEBHOOK_SECRET` dedicato a ETH.
- [x] Configurare i secret GitHub nel repo ETH:
      - `TELEGRAM_BOT_TOKEN`
      - `TELEGRAM_CHAT_ID`
- [x] Configurare i secret Cloudflare Worker ETH:
      - `TELEGRAM_BOT_TOKEN`
      - `TELEGRAM_WEBHOOK_SECRET`
- [x] Registrare il webhook Telegram verso:
      `https://eth-prudential-signal.giuse2003.workers.dev/webhook`
- [ ] Verificare `getWebhookInfo` sul bot ETH.
- [x] Lanciare il workflow `Telegram command menu`.
- [x] Testare `/start`, `/segnale` e `/conditions` dal bot ETH.
- [ ] Testare `/help` e `/privacy` dal bot ETH.
- [ ] Testare `/iscrivimi` e `/disiscrivimi` dopo configurazione Supabase.

### B. Completare Supabase iscritti

- [x] Decidere se usare lo stesso progetto Supabase del BTC o crearne uno ETH:
      il codice usa una tabella ETH dedicata, quindi puo riusare lo stesso
      progetto Supabase senza mescolare gli iscritti.
- [x] Confermato che su Supabase esiste solo il progetto Bitcoin: si procede
      riusandolo con tabella ETH dedicata.
- [x] Separare gli iscritti ETH da quelli BTC:
      tabella `public.telegram_subscribers_eth`.
- [x] Aggiornare schema, Worker e webhook legacy per usare la tabella ETH
      dedicata.
- [ ] Configurare secret Cloudflare Worker ETH:
      - `SUPABASE_URL`
      - `SUPABASE_SERVICE_ROLE_KEY`
- [x] Preparare script locale per caricare i secret senza stamparli:
      `scripts/configure_supabase_worker_secrets.ps1`.
- [ ] Verificare:
      `https://eth-prudential-signal.giuse2003.workers.dev/subscribers/count`
- [x] Aggiungere endpoint diagnostico non sensibile:
      `https://eth-prudential-signal.giuse2003.workers.dev/subscribers/health`
- [x] Aggiungere workflow manuale `Verify Supabase subscribers`.
- [ ] Aggiornare dashboard se il contatore resta temporaneamente non disponibile.

### C. Validare GitHub Actions

- [ ] Eseguire manualmente `Hourly ETH monitor (Telegram)`.
- [ ] Verificare che il workflow aggiorni:
      - `docs/status.json`
      - `docs/chart-data.json`
      - `docs/backtest.json`
      - `docs/live-status.json`, se generato
- [ ] Verificare che il workflow invii notifiche solo al bot/chat ETH.
- [ ] Controllare che cache `.state` e CSV ETH non confliggano con BTC.
- [ ] Verificare che Pages si aggiorni dopo il commit automatico del workflow.

### D. Validare Worker Cloudflare

- [x] Verificare root endpoint:
      `https://eth-prudential-signal.giuse2003.workers.dev/`
- [ ] Verificare `/subscribers/count` dopo i secret Supabase.
- [ ] Verificare `/subscribers/health` dopo i secret Supabase.
- [x] Verificare `/live-preview` con fallback su `docs/status.json`.
- [ ] Verificare `/live-preview` con `docs/live-status.json`, quando generato.
- [ ] Verificare CORS dalla dashboard GitHub Pages.
- [ ] Controllare log con `wrangler tail eth-prudential-signal` durante test
      Telegram.
- [x] Creare un token API Cloudflare dedicato per deploy e tail da CLI.
- [x] Configurare localmente `CLOUDFLARE_API_TOKEN` per usare `wrangler deploy`.
- [ ] Sul PC di casa, prima di configurare un nuovo token/API, verificare se
      esiste gia una configurazione Wrangler/API del progetto
      `BTC_Prudential_Signal` riutilizzabile in modo sicuro.
- [ ] Sul PC di casa, riallineare solo la configurazione locale
      (`git pull`, Node/Wrangler o runtime Codex, `CLOUDFLARE_API_TOKEN`) senza
      ricreare bot, secret GitHub, secret Cloudflare o webhook gia configurati
      lato cloud.

### E. Pulizia Documentazione

- [ ] Rileggere `README.md` e rimuovere eventuali affermazioni che dicono
      "operativo" prima che bot e Supabase siano davvero completati.
- [ ] Aggiornare `PROJECT_STATUS.md` con lo stato reale ETH.
- [ ] Aggiornare `DECISION_LOG.md` separando decisioni copiate dal progetto BTC
      da decisioni effettivamente validate su ETH.
- [ ] Valutare se mantenere `RENDER_DEPLOYMENT.md` come legacy o archiviarlo.

### F. Verifiche finali prima di considerare il progetto completo

- [ ] Dashboard pubblica mostra dati ETH aggiornati.
- [ ] Backtest dashboard e `reports/report.txt` hanno metriche coerenti.
- [ ] Bot Telegram ETH risponde ai comandi.
- [ ] Iscrizione/disiscrizione funziona.
- [ ] Contatore iscritti dashboard funziona.
- [ ] Workflow orario aggiorna dashboard e invia notifiche ETH.
- [ ] Nessun endpoint ETH usa token, chat ID o Worker BTC.
- [ ] Test Python passano.
- [ ] Ultime modifiche committate e pushate.

## Comandi Utili

```powershell
python main.py --force-download
python -m unittest discover -s tests
gh secret list --repo giuse2003/ETH_Prudential_Signal
cd cloudflare-worker
npx wrangler deploy
npx wrangler secret list
npx wrangler tail eth-prudential-signal
$env:CLOUDFLARE_API_TOKEN="..."
```

## Registro Avanzamenti

| Data | Stato | Note |
| --- | --- | --- |
| 2026-06-23 | Creato progetto ETH | Repo, dashboard, backtest ETH e Pages attivi. |
| 2026-06-23 | Corretto backtest dashboard | Rimosse metriche statiche BTC, aggiunto `backtest.json`. |
| 2026-06-23 | Deploy Worker base | Worker ETH risponde su root, ma mancano secret Telegram/Supabase. |
| 2026-06-23 | Creato questo file | Roadmap iniziale per completamento bot e automazioni. |
| 2026-06-24 | Configurato Telegram base | Bot ETH dedicato, secret GitHub/Cloudflare e webhook verso Worker completati. |
| 2026-06-24 | Corretto `/segnale` Worker | Aggiunto fallback da `live-status.json` mancante a `status.json`; `/live-preview` e `/segnale` funzionano. |
| 2026-06-24 | Configurato token API Cloudflare | `wrangler whoami` e `wrangler deploy` funzionano da CLI; deploy Version ID `d88bee42-afd3-4f13-ac82-d35dc9794809`. |
| 2026-06-24 | Nota PC Lenovo/casa | Le configurazioni cloud sono gia attive; sul PC di casa va controllata prima l'eventuale API/Wrangler del progetto BTC. |
| 2026-06-24 | Aggiornato menu comandi Telegram | Workflow `Telegram command menu` registrato da GitHub Actions e completato con successo. |
| 2026-06-24 | Decisa separazione Supabase ETH | Schema e codice puntano a `public.telegram_subscribers_eth`, evitando conflitti con BTC. |
| 2026-06-24 | Deploy Worker con tabella ETH | Deploy Version ID `e6f86860-d16a-4c9c-9029-84b4f0213395`; `/subscribers/count` resta 503 finche mancano i secret Supabase. |
| 2026-06-24 | Aggiunta verifica Supabase | Endpoint `/subscribers/health` e workflow manuale `Verify Supabase subscribers` preparati; deploy Worker Version ID `8fee045f-d5da-4811-827e-13412c1f9d0b`. |
| 2026-06-24 | Preparato caricamento secret Supabase | Aggiunto script PowerShell per caricare `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` da variabili d'ambiente locali. |
| 2026-06-24 | Scelta Supabase esistente | Confermato che esiste solo il progetto Supabase Bitcoin; ETH usera lo stesso progetto con tabella `telegram_subscribers_eth`. |
