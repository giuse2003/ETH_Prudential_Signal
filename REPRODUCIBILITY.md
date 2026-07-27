# Riproducibilita ETH-USD Signal

## Ambiente canonico

- Python `3.13.0` da `.python-version`;
- dipendenze dirette in `requirements.in`;
- ambiente transitivo con hash in `requirements.lock`;
- file di testo normalizzati LF tramite `.gitattributes`.

Installazione verificabile:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --require-hashes -r requirements.lock
```

Su Linux/macOS usare `.venv/bin/python`.

## Baseline v1

Il pacchetto canonico e `docs/runs/baseline-v1-2026-07-26/`. Contiene lo
snapshot Coinbase grezzo e tutti gli output deterministici. Il PNG non fa parte
degli artefatti canonici byte per byte.

Verifica offline:

```powershell
python reproduce.py --manifest docs/runs/baseline-v1-2026-07-26/manifest.json
```

Il comando controlla versione Python, dipendenze, hash del lock, hash dei
sorgenti, snapshot Coinbase, metriche e byte degli output rigenerati. Non
contatta la rete.

## Run operativo

`python main.py` scarica o aggiorna la cache Coinbase, recupera gli snapshot
`ETH-USD` e `ETH-EUR`, genera DAILY e LIVE PREVIEW in staging, valida hash e
`run_id`, quindi promuove l'intero pacchetto. Se la pubblicazione fallisce,
resta disponibile il pacchetto precedente.

Il manifest operativo e `docs/manifest.json`; la baseline congelata non viene
modificata dai run giornalieri.
