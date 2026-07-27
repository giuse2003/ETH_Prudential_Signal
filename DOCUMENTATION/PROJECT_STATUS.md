# Project Status

Ultimo aggiornamento: 2026-07-27

## Stato corrente

- Nome pubblico: **ETH-USD Signal**.
- Fonte unica: Coinbase Advanced Trade `ETH-USD`, candele DAILY UTC.
- Storico continuo canonico: dal `2016-05-23`.
- `ETH-EUR`: solo spot informativo LIVE.
- Baseline ufficiale: cinque condizioni `ACQUISTA`, due condizioni `VENDI`.
- Azioni: `ACQUISTA`, `MANTIENI STATO ATTUALE`, `VENDI`.
- Commissione di backtest: `0,6%` per lato.
- Pacchetto ufficiale congelato al `2026-07-26` e riproducibile offline.
- Run operativo aggiornabile ogni giorno, con manifest, hash e `run_id`.

Il numero di versione e interno. Dashboard e Telegram mostrano soltanto il nome
del modello e non presentano la dicitura `v2`.

## Regole ufficiali

Acquisto, tutte vere:

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `40 <= RSI14 <= 65` sui nuovi ingressi;
4. `Close > Close.shift(7)`;
5. `Volume > VolumeAvg20`.

Vendita, almeno una vera:

1. `Close < SMA50 * 0,98`;
2. Trail8 confermato da momentum 7 giorni `>= -15%` e volume relativo
   `>= +20%`.

## Pacchetti congelati

- Baseline ufficiale: `docs/runs/baseline-v2-2026-07-26/`.
- Vecchia baseline: `docs/runs/baseline-v1-2026-07-26/`.
- La vecchia baseline e il tag `baseline-v1-2026-07-26` restano immutati.
- Entrambi i pacchetti usano lo stesso snapshot Coinbase al cutoff.

## Metriche ufficiali

Periodo `2016-12-08` - `2026-07-26`, 3.518 osservazioni, commissione 0,6% per
lato:

| Metrica | ETH-USD Signal | Buy & Hold |
|---|---:|---:|
| Rendimento totale | 56.672,64% | 23.431,28% |
| Annualizzato | 93,12% | 76,25% |
| Max drawdown | -43,00% | -94,01% |
| Sharpe | 1,615 | 1,074 |
| Trade completati | 30 | n/a |

## Stato al cutoff

- Candela: `2026-07-26`.
- Azione: `MANTIENI STATO ATTUALE`.
- Esposizione ricostruita: `0%`.
- Ultima vendita effettiva: `2026-07-09`.

## Componenti operative

- `pipeline.py`: dati, modello, backtest e pubblicazione;
- `reports/publication.py`: staging, manifest e promozione transazionale;
- `freeze_baseline.py` e `reproduce.py`: congelamento e verifica;
- dashboard GitHub Pages: consuma il pacchetto pubblicato;
- Cloudflare Worker: legge `live-status.json` e serve Telegram;
- Telegram: esclusivamente LIVE PREVIEW stabilizzata.

## Rischi aperti

- risultati retrospettivi e rischio di overfitting;
- dipendenza dalla qualita e continuita dei dati Coinbase;
- spread, slippage, imposte e rendimento cash esclusi;
- esposizione binaria e drawdown storico ancora materiali;
- verifica remota di Worker e Telegram successiva al push.
