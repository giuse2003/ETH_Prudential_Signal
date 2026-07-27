# Project Overview

## Identita

ETH-USD Signal e un modello algoritmico long/cash su Coinbase `ETH-USD`.
Il nome `ETH_Prudential_Signal` resta riservato a repository, bot e Worker.

## Flusso dati

```text
Coinbase ETH-USD DAILY concluse
  -> validazione e snapshot grezzo
  -> indicatori
  -> baseline ETH stateful
  -> backtest
  -> DAILY e LIVE PREVIEW
  -> staging, manifest e hash
  -> dashboard, Worker e Telegram
```

`ETH-EUR` entra soltanto come spot informativo. Non influenza indicatori,
segnali o backtest. La cache locale contiene esclusivamente dati Coinbase e non
abilita fallback ad altri provider.

## Indicatori

- SMA50 e SMA200: media aritmetica rolling a finestra completa;
- RSI14: gain/loss separati, EWM `alpha=1/14`, `adjust=False`,
  `min_periods=14`;
- VolumeAvg20: media aritmetica rolling del volume base ETH;
- ATR14: true range ed EWM a 14 periodi;
- momentum 7 giorni: confronto con `Close.shift(7)`.

## Regole ufficiali

Un nuovo ingresso `ACQUISTA` richiede:

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `40 <= RSI14 <= 65`;
4. `Close > Close.shift(7)`;
5. `Volume > VolumeAvg20`.

`VENDI` ha precedenza e richiede almeno una condizione:

1. `Close < SMA50`;
2. trailing stop 8% dal massimo post-ingresso, confermato da momentum 7 giorni
   almeno `-5%` e volume relativo almeno `+20%`.

Altrimenti l'azione e `MANTIENI STATO ATTUALE`. Il filtro RSI massimo limita
solo i nuovi ingressi e non chiude una posizione esistente.

## Backtest

L'azione calcolata alla chiusura `t` viene applicata al rendimento `t+1`.
`ACQUISTA` imposta esposizione 100%, `VENDI` 0% e il mantenimento usa
forward-fill. Strategia e Buy & Hold condividono il periodo post warm-up.
Annualizzazione e Sharpe usano 365 giorni; i trade aperti a fine serie sono
esclusi da conteggio e win rate.

## Pubblicazione

Ogni run viene costruito in staging. Tutti i JSON condividono il `run_id`; il
manifest registra periodo, regole, metriche, commit, ambiente, hash del lock,
provenienza e hash degli artefatti. La promozione e transazionale e ripristina
il pacchetto precedente in caso di errore.

## Baseline congelata

La baseline v1 usa cutoff `2026-07-26` e snapshot Coinbase incluso. Il comando
`reproduce.py` rigenera offline gli output e confronta ambiente, sorgenti,
input, metriche e byte canonici. I run operativi successivi non modificano la
baseline.

## Interfacce

- dashboard: legge `manifest.json`, `status.json`, `live-status.json` e
  `chart-data.json` verificando il `run_id`;
- Worker: inoltra il pacchetto LIVE e gestisce iscritti/comandi, senza formule;
- Telegram: mostra `Azione`, prezzo EUR informativo, cinque condizioni buy e
  due sell con indicatori verdi/rossi;
- GitHub Actions: ambiente bloccato, cache Coinbase, pipeline unica e
  pubblicazione di tutti gli artefatti.
