# ETH-USD Signal Rule Verification Log

Ultimo aggiornamento: 2026-08-28

## Dataset canonico

- Coinbase Advanced Trade `ETH-USD`, granularita `ONE_DAY`;
- storico continuo `2016-05-23` - `2026-08-27`;
- valutazione post warm-up `2016-12-08` - `2026-08-27`;
- 3.550 osservazioni senza duplicati o giorni mancanti;
- snapshot SHA-256:
  `43315c8379173d399882f0a8372056dae9a57032cc92de9926b026245d1ef619`.

## Regole verificate

- percorso standard con cinque condizioni, tutte obbligatorie;
- percorso breakout protetto con sette conferme e guardrail di regime;
- logica di ingresso `percorso standard OR breakout protetto`;
- guardrail verificato sul falso ingresso del 13 gennaio 2026;
- attivazione operativa dal 28 agosto senza backfill dell'ingresso del 17;
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

- cinque stati per il percorso standard, otto per il breakout e due `VENDI`;
- `status.json` e `live-status.json` usano le nuove etichette;
- `/conditions` espone margine SMA50 2%, momentum -15% e volume +20%;
- il nome pubblico non contiene il numero di versione interno.

## Metriche verificate

Periodo completo, commissione 0,6% per lato:

| Strategia | Totale | Annualizzato | Max DD | Trade | Win rate | Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| ETH-USD Signal | 240.310,55% | 122,70% | -39,05% | 32 | 59,38% | 1,845 |
| Buy & Hold | 30.163,66% | 79,95% | -94,01% | n/a | n/a | 1,097 |

Profit factor strategia: `17.813017225255965`.

## Stato al cutoff

- azione operativa `2026-08-27`: `MANTIENI STATO ATTUALE`;
- stato operativo: `FUORI`;
- stato storico v3: trade breakout del 17 agosto ancora aperto.

## Comandi di verifica

```powershell
python -m pip install --require-hashes -r requirements.lock
python -m unittest discover -s tests -v
python reproduce.py --manifest docs/runs/baseline-v3-2026-08-27/manifest.json
node --check cloudflare-worker/src/worker.js
```

Le baseline v1 e v2 restano verificate come archivi immutabili.
