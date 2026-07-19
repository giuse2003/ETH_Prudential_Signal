# Baseline Sync Checklist

Usare questa checklist ogni volta che cambiano condizioni `ACQUISTA`, regole
`VENDI`, soglie, numero o significato delle condizioni mostrate agli utenti.
La dashboard ETH usa Cloudflare Worker come unico backend pubblico; Render e
FastAPI non fanno parte dell'architettura.

## 1. Logica e backtest

- Aggiornare `strategy/signals.py` e i formatter condivisi.
- Verificare `reports/generate.py`, `config.py`, indicatori e backtest.
- Rigenerare tutte le metriche e controllare rendimento, drawdown, Sharpe,
  profit factor, operazioni e periodi di confronto.
- Non promuovere una variante senza report, motivazione e decisione esplicita.

## 2. Dashboard e dati

- Aggiornare `docs/index.html`, `docs/app.js` e gli eventuali testi statici.
- Verificare tutte le percentuali e le metriche mostrate nella dashboard.
- Controllare `docs/status.json`, `docs/live-status.json`,
  `docs/backtest.json` e `docs/chart-data.json`.
- Verificare che il grafico conservi candele OHLC rosse/verdi, SMA50, SMA200,
  RSI 40/65, volumi e media volumi 20 giorni.
- Controllare che la candela Coinbase UTC in corso sia marcata provvisoria e
  non entri nel segnale; la candela Yahoo chiusa deve sostituirla.
- Avviare `python run_dashboard.py` e verificare desktop e mobile.

## 3. Telegram e Cloudflare

- Aggiornare i testi in `cloudflare-worker/src/worker.js`, incluso
  `/conditions`, e i formatter Python condivisi.
- Eseguire `node --check cloudflare-worker/src/worker.js`.
- Se cambia il Worker, eseguire `npx wrangler deploy` dalla sua cartella.
- Verificare `/conditions`, `/segnale`, `/subscribers/health` e
  `/subscribers/count`.
- Non reintrodurre endpoint Render, webhook FastAPI o relativi secret.

## 4. GitHub Actions

- Verificare `.github/workflows/hourly-monitor.yml` e la pubblicazione dei
  quattro JSON della dashboard.
- Il monitor deve forzare Yahoo a ogni run finche la candela daily attesa non
  risulta processata.
- Controllare l'esito del workflow e del deploy GitHub Pages dopo il push.

## 5. Documentazione

Aggiornare almeno:

- `README.md`;
- `DOCUMENTATION/PROJECT_OVERVIEW.md`;
- `DOCUMENTATION/PROJECT_STATUS.md`;
- `DOCUMENTATION/DECISION_LOG.md`;
- `DOCUMENTATION/ETH_MODEL_RESEARCH_DIARY.md`;
- questo file se cambia il perimetro operativo.

Registrare anche le alternative testate e non promosse, con motivo e possibile
uso futuro. Lo storico delle decisioni resta consultabile, ma le istruzioni
correnti non devono rimandare a servizi dismessi.

## 6. Verifica finale

```powershell
python -m unittest discover -s tests -v
node --check docs/app.js
node --check cloudflare-worker/src/worker.js
rg -n -i "onrender.com|render.yaml|telegram_webhook.py|fastapi|uvicorn" README.md DOCUMENTATION requirements.txt docs cloudflare-worker .github
git diff --check
git status --short
```

Le occorrenze Render ammesse sono soltanto voci storiche chiaramente indicate
come superate. Prima del push fare rebase su `origin/master` e ripetere i test.
