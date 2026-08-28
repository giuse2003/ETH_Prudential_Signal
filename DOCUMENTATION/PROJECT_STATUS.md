# Project Status

Ultimo aggiornamento: 2026-08-28

## Stato corrente

- Nome pubblico: **ETH-USD Signal**.
- Fonte unica: Coinbase Advanced Trade `ETH-USD`, candele DAILY UTC.
- Storico continuo canonico: dal `2016-05-23`.
- `ETH-EUR`: solo spot informativo LIVE.
- Baseline ufficiale: due percorsi alternativi `ACQUISTA`, due condizioni `VENDI`.
- Azioni: `ACQUISTA`, `MANTIENI STATO ATTUALE`, `VENDI`.
- Commissione di backtest: `0,6%` per lato.
- Pacchetto ufficiale `v3` congelato al `2026-08-27` e riproducibile offline.
- Run operativo aggiornabile ogni giorno, con manifest, hash e `run_id`.

Il numero di versione e interno. Dashboard e Telegram mostrano soltanto il nome
del modello e non presentano la dicitura `v3`.

## Regole ufficiali

Acquisto: deve essere completo almeno un percorso.

Percorso 1, tutte vere:

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `40 <= RSI14 <= 65` sui nuovi ingressi;
4. `Close > Close.shift(7)`;
5. `Volume > VolumeAvg20`.

Percorso 2, tutte vere:

1. `SMA50 <= SMA200`;
2. `Close > SMA50` e `Close >= SMA200 * 0,90`;
3. SMA50 non in calo rispetto a cinque giorni prima;
4. `40 <= RSI14 <= 65`;
5. `Close > Close.shift(7)`;
6. `Volume >= VolumeAvg20 * 1,20`;
7. Close sopra i cinque Close precedenti;
8. guardrail superato: il percorso viene bloccato soltanto quando SMA200 sale
   da 20 giorni e SMA50 e oltre il 15% sotto SMA200.

Vendita, almeno una vera:

1. `Close < SMA50 * 0,98`;
2. Trail8 confermato da momentum 7 giorni `>= -15%` e volume relativo
   `>= +20%`.

## Pacchetti congelati

- Baseline ufficiale: `docs/runs/baseline-v3-2026-08-27/`.
- Baseline precedente: `docs/runs/baseline-v2-2026-07-26/`.
- Vecchia baseline: `docs/runs/baseline-v1-2026-07-26/`.
- I pacchetti precedenti e i relativi tag restano immutati.

## Metriche ufficiali

Periodo `2016-12-08` - `2026-08-27`, 3.550 osservazioni, commissione 0,6% per
lato:

| Metrica | ETH-USD Signal | Buy & Hold |
|---|---:|---:|
| Rendimento totale | 240.310,55% | 30.163,66% |
| Annualizzato | 122,70% | 79,95% |
| Max drawdown | -39,05% | -94,01% |
| Sharpe | 1,845 | 1,097 |
| Trade completati | 32 | n/a |

## Stato al cutoff

- Candela: `2026-08-27`.
- Azione: `MANTIENI STATO ATTUALE`.
- Stato storico del backtest: posizione breakout aperta dal `2026-08-17`.
- Stato operativo reale: `FUORI`; il percorso 2 e attivo dalle candele chiuse
  del `2026-08-28` e non ricostruisce retroattivamente l'acquisto del 17 agosto.

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
- verifica remota di Worker, dashboard e Telegram successiva al push.
