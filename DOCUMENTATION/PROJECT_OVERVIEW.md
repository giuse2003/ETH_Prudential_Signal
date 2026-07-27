# Project Overview

## Scopo

ETH-USD Signal produce un'indicazione long/cash giornaliera su Ethereum e una
preview LIVE. Il modello non esegue ordini e non costituisce consulenza
finanziaria.

## Flusso dati

1. `data/coinbase.py` scarica candele DAILY UTC Coinbase `ETH-USD`.
2. La candela UTC in corso viene esclusa dallo storico ufficiale.
3. `indicators/technical_indicators.py` calcola SMA50, SMA200, RSI14, ATR14,
   media volumi 20 e Close di 7 giorni prima.
4. `strategy/signals.py` ricostruisce posizione, massimo post-ingresso e azione.
5. `backtest/backtest.py` applica l'esposizione dal giorno successivo e include
   la commissione dello 0,6% per lato.
6. La pipeline pubblica JSON, CSV, report, grafico e manifest come unico bundle.

`ETH-EUR` viene interrogato soltanto per il prezzo spot informativo LIVE.

## Baseline ufficiale

`ACQUISTA` richiede tutte le condizioni:

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `40 <= RSI14 <= 65` per i nuovi ingressi;
4. `Close > Close.shift(7)`;
5. `Volume > VolumeAvg20`.

`VENDI` ha precedenza e richiede almeno una condizione:

1. `Close < SMA50 * 0,98`;
2. trailing stop 8% dal massimo Close post-ingresso, con momentum 7 giorni
   `>= -15%` e volume relativo `>= +20%`.

Altrimenti l'azione e `MANTIENI STATO ATTUALE`. Il limite RSI 65 filtra solo i
nuovi ingressi. Il superamento di RSI 65 non vende una posizione gia aperta.

## Stato ed esposizione

- `ACQUISTA`: esposizione desiderata 100%;
- `VENDI`: esposizione desiderata 0%;
- `MANTIENI STATO ATTUALE`: conserva l'esposizione precedente;
- segnale a chiusura `t`: applicato al rendimento `t+1`;
- vendita SMA50: valutata anche se la posizione ricostruita e gia chiusa, ma il
  turnover cambia soltanto quando cambia l'esposizione.

## Backtest

La strategia paga lo 0,6% su ogni cambio completo di esposizione. Buy & Hold
paga lo 0,6% all'acquisto iniziale e alla liquidazione finale. Annualizzazione
e Sharpe usano 365 giorni; il risk-free e zero. Un trade aperto al cutoff non
entra in numero operazioni o win rate.

Spread, slippage, imposte e rendimento cash sono esclusi.

## DAILY e LIVE

- DAILY usa solo candele concluse e genera lo storico ufficiale.
- LIVE PREVIEW aggiunge prezzo e volume 24h provvisori e ricalcola le stesse
  regole senza modificare lo storico DAILY.
- Il monitor notifica Telegram solo quando cambia una delle sette condizioni
  LIVE e il cambiamento supera la stabilizzazione prevista.

## Pubblicazione

Ogni run viene costruito in staging. I JSON condividono lo stesso `run_id`; il
manifest registra periodo, regole, costi, metriche, commit, ambiente,
provenienza e hash. La promozione del bundle e transazionale.

Dashboard e Worker consumano gli artefatti pubblicati e non ricalcolano il
modello.

## Versionamento interno

- Baseline ufficiale: `docs/runs/baseline-v2-2026-07-26/`.
- Vecchia baseline: `docs/runs/baseline-v1-2026-07-26/`.
- Il numero interno non viene esposto nel nome del bot o nei messaggi.
- Ogni pacchetto congelato ha un tag, hash sorgenti, snapshot e manifest propri.

Il checkout corrente riproduce la Baseline ufficiale. La vecchia baseline si
riproduce dal tag storico e nel checkout corrente viene verificata come archivio
immutabile.

## Motivazione della promozione

I test completi con commissione 0,6%, walk-forward retrospettivo, ritardo di
esecuzione, PBO e Deflated Sharpe favoriscono la configurazione fissa con soglia
SMA50 al 2% e momentum Trail8 a -15%. La selezione annuale non offre un vantaggio
sufficiente a giustificarne complessita e instabilita di ranking.

Dettagli: `reports/official_baseline_implementation.md` e
`reports/walk_forward_coinbase_0_6.md`.
