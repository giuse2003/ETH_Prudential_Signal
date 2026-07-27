# ETH-USD Signal Rule Verification Log

Ultimo aggiornamento: 2026-07-27

## Dataset canonico

- Coinbase Advanced Trade `ETH-USD`, granularita `ONE_DAY`;
- storico continuo `2016-05-23` - `2026-07-26`;
- valutazione post warm-up `2016-12-08` - `2026-07-26`;
- 3.518 osservazioni senza duplicati o giorni mancanti;
- snapshot SHA-256:
  `09504484b0d115c6b130dbfc82f05f5dc9137ce11b1cf12604f9a1c96132c357`.

## Regole verificate

- cinque condizioni di acquisto, tutte obbligatorie;
- RSI14 compreso tra 40 e 65 soltanto sui nuovi ingressi;
- vendita SMA50 se e solo se `Close < SMA50 * 0,98`;
- nessuna vendita SMA50 per una chiusura compresa tra SMA50 e il margine 2%;
- Trail8 confermato con momentum 7 giorni `>= -15%` e volume relativo
  `>= +20%`;
- Trail8 non confermato con momentum inferiore a `-15%`;
- precedenza della vendita;
- azione neutrale `MANTIENI STATO ATTUALE`;
- segnale applicato al rendimento del giorno successivo;
- commissione 0,6% su ingresso e uscita;
- Buy & Hold con commissione su acquisto e liquidazione;
- trade finali aperti esclusi da conteggio e win rate.

## Contratto pubblicato

- esattamente cinque stati `ACQUISTA` e due stati `VENDI`;
- `status.json` e `live-status.json` usano le nuove etichette;
- `/conditions` espone margine SMA50 2%, momentum -15% e volume +20%;
- il nome pubblico non contiene il numero di versione interno.

## Metriche verificate

Periodo completo, commissione 0,6% per lato:

| Strategia | Totale | Annualizzato | Max DD | Trade | Win rate | Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| ETH-USD Signal | 56.672,64% | 93,12% | -43,00% | 30 | 50,00% | 1,615 |
| Buy & Hold | 23.431,28% | 76,25% | -94,01% | n/a | n/a | 1,074 |

Profit factor strategia: `14.94397361521486`.

## Stato al cutoff

- azione `2026-07-26`: `MANTIENI STATO ATTUALE`;
- esposizione: 0%;
- ultima vendita effettiva: `2026-07-09`.

## Comandi di verifica

```powershell
python -m pip install --require-hashes -r requirements.lock
python -m unittest discover -s tests -v
python reproduce.py --manifest docs/runs/baseline-v2-2026-07-26/manifest.json
node --check cloudflare-worker/src/worker.js
```

La vecchia baseline resta verificata come archivio immutabile e si riproduce
byte per byte dal tag `baseline-v1-2026-07-26`.
