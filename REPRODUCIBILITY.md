# Riproducibilita ETH-USD Signal

## Ambiente canonico

- Python `3.13.0` da `.python-version`;
- dipendenze dirette in `requirements.in`;
- ambiente transitivo con hash in `requirements.lock`;
- file di testo normalizzati LF tramite `.gitattributes`.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --require-hashes -r requirements.lock
```

## Baseline ufficiale

Il nome pubblico resta **Baseline**. Il pacchetto usa internamente il percorso
`docs/runs/baseline-v2-2026-07-26/` e il tag `baseline-v2-2026-07-26`.

Verifica offline completa dal checkout ufficiale:

```powershell
python reproduce.py --manifest docs/runs/baseline-v2-2026-07-26/manifest.json
```

Il comando controlla versione Python, dipendenze, hash del lock, hash dei
sorgenti, snapshot Coinbase, metriche e byte degli output rigenerati. Non
contatta la rete.

## Vecchia baseline

La vecchia baseline e immutabile in
`docs/runs/baseline-v1-2026-07-26/` e nel tag `baseline-v1-2026-07-26`.
Il checkout corrente ne verifica l'integrita degli artefatti senza eseguire il
codice storico:

```powershell
python -c "from reproducibility import verify_frozen_artifacts; print(verify_frozen_artifacts('docs/runs/baseline-v1-2026-07-26/manifest.json'))"
```

La riproduzione byte per byte della vecchia baseline deve essere eseguita con i
sorgenti del relativo tag, perche il checkout corrente contiene le regole
ufficiali successive:

```powershell
git worktree add ..\ETH_Prudential_Signal-v1 baseline-v1-2026-07-26
python ..\ETH_Prudential_Signal-v1\reproduce.py --manifest ..\ETH_Prudential_Signal-v1\docs\runs\baseline-v1-2026-07-26\manifest.json
```

La pipeline CI controlla inoltre che la directory della vecchia baseline non
presenti differenze rispetto al tag storico.

## Run operativo

`python main.py` aggiorna la cache Coinbase, recupera gli snapshot `ETH-USD` e
`ETH-EUR`, genera DAILY e LIVE PREVIEW in staging, valida hash e `run_id`,
quindi promuove l'intero pacchetto. Se la pubblicazione fallisce resta
disponibile il pacchetto precedente.

Il manifest operativo e `docs/manifest.json`. Il campo interno
`frozen_baseline_manifest` punta alla Baseline ufficiale; i pacchetti congelati
non vengono modificati dai run giornalieri.

## Nuove versioni

Una futura modifica alle regole richiede un nuovo identificatore interno, un
cutoff approvato, un pacchetto separato e un tag non spostabile. Non e ammesso
sovrascrivere una directory o un manifest gia congelato.
