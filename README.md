# ETH-USD Signal

Modello algoritmico long/cash per Ethereum basato su candele giornaliere UTC
Coinbase `ETH-USD`. Il repository e l'infrastruttura mantengono il nome
`ETH_Prudential_Signal`; il nome pubblico del modello e **ETH-USD Signal**.

## Contratto dati

- Coinbase Advanced Trade `ETH-USD` e l'unica fonte di candele, volumi,
  indicatori, segnali e backtest.
- Lo storico continuo canonico parte dal `2016-05-23`. Le date `2016-05-21` e
  `2016-05-22` sono assenti e non vengono interpolate.
- La candela UTC corrente e sempre esclusa dal run DAILY.
- Coinbase `ETH-EUR` fornisce soltanto il prezzo spot informativo dei contenuti
  LIVE e non entra nel modello.

## Baseline ufficiale

`ACQUISTA` si attiva quando e completo almeno uno dei due percorsi.

Percorso 1, trend confermato:

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `40 <= RSI(14) <= 65` per un nuovo ingresso;
4. `Close > Close.shift(7)`;
5. `Volume ETH-USD > VolumeAvg20`.

Percorso 2, breakout protetto:

1. `SMA50 <= SMA200`;
2. `Close > SMA50` e `Close >= SMA200 * 0,90`;
3. `SMA50 >= SMA50.shift(5)`;
4. `40 <= RSI(14) <= 65`;
5. `Close > Close.shift(7)`;
6. `Volume ETH-USD >= VolumeAvg20 * 1,20`;
7. `Close` sopra il massimo dei cinque Close precedenti;
8. guardrail superato: il breakout viene bloccato soltanto quando sono vere
   insieme `SMA200 / SMA200.shift(20) - 1 > 0` e
   `SMA50 / SMA200 - 1 < -0,15`.

`VENDI` scatta quando e vera almeno una delle due condizioni:

1. `Close < SMA50 * 0,98`, cioe una chiusura oltre il 2% sotto SMA50;
2. trailing stop dell'8% dal massimo Close post-ingresso, confermato da:
   momentum a 7 giorni `>= -15%` e volume relativo `>= +20%`.

La vendita ha precedenza. In ogni altro caso l'azione e
`MANTIENI STATO ATTUALE`. L'esposizione e binaria: 100% dopo `ACQUISTA`, 0%
dopo `VENDI`; il mantenimento conserva lo stato precedente.

Il segnale calcolato alla chiusura della candela `t` viene applicato al
rendimento della candela successiva. Il backtest ufficiale include una
commissione dello `0,6%` per lato. Buy & Hold paga lo stesso costo all'acquisto
iniziale e alla liquidazione finale.

## DAILY e LIVE PREVIEW

- **DAILY** usa soltanto candele Coinbase concluse e alimenta storico,
  dashboard e backtest.
- **LIVE PREVIEW** aggiunge una riga provvisoria con prezzo e volume rolling
  24h Coinbase, poi ricalcola le stesse regole.
- Telegram pubblica soltanto variazioni LIVE stabilizzate e mostra sempre
  i due percorsi di acquisto e le due condizioni di vendita.
- Il percorso breakout e operativo dalle candele chiuse del `2026-08-28`.
  Lo stato reale e ripartito `FUORI`: il segnale storico del 17 agosto non e
  stato trasformato in un acquisto retroattivo.
- Il nome della versione interna non viene mostrato nel bot, nella dashboard o
  nei messaggi operativi.

## Risultati ufficiali

Periodo completo congelato: `2016-12-08` - `2026-08-27`, 3.550 osservazioni.
Commissione inclusa: `0,6%` per lato per entrambi i modelli.

| Metrica | ETH-USD Signal | Buy & Hold |
|---|---:|---:|
| Rendimento totale | 240.310,55% | 30.163,66% |
| Rendimento annualizzato | 122,70% | 79,95% |
| Max drawdown | -39,05% | -94,01% |
| Sharpe | 1,845 | 1,097 |
| Trade completati | 32 | n/a |
| Win rate | 59,38% | n/a |
| Profit factor | 17,813 | n/a |

I valori completi sono nel manifest congelato. Il risultato e storico e non
costituisce una previsione.

## Validazione della promozione precedente

La regola ufficiale e il candidato fisso denominato internamente
`combo_trail_mom_15_sma_break_2_0`. Nel confronto retrospettivo 2021-2026 con
commissioni allo 0,6% ha ottenuto:

| Modello | Totale | Annualizzato | Max DD | Sharpe |
|---|---:|---:|---:|---:|
| Vecchia baseline | 194,63% | 21,41% | -51,57% | 0,672 |
| Baseline ufficiale | 834,01% | 49,35% | -43,00% | 1,197 |
| Buy & Hold | 161,63% | 18,85% | -79,35% | 0,610 |

Con un'ulteriore candela di ritardo, la Baseline ufficiale mantiene rendimento
annualizzato 37,44%, drawdown -47,25% e Sharpe 0,983. La strategia fissa e stata
preferita alla riottimizzazione annuale perche piu semplice e piu stabile nel
test di ritardo. Il protocollo completo, inclusi PBO e Deflated Sharpe, e in
[`reports/walk_forward_coinbase_0_6.md`](reports/walk_forward_coinbase_0_6.md).

Questa validazione e pseudo out-of-sample: le ipotesi sono state definite dopo
aver osservato anche parte della serie. Non equivale a un futuro mai visto.

## Versionamento interno

Il versionamento non cambia il nome pubblico del modello:

- Baseline ufficiale: `docs/runs/baseline-v3-2026-08-27/`;
- baseline precedente: `docs/runs/baseline-v2-2026-07-26/`;
- vecchia baseline: `docs/runs/baseline-v1-2026-07-26/`;
- tag storico immutabile: `baseline-v1-2026-07-26`;
- tag ufficiale: `baseline-v3-2026-08-27`.

La vecchia baseline resta archiviata e non viene usata dal run operativo. Il
run operativo si aggiorna con ogni nuova candela conclusa e punta sempre al
manifest congelato della Baseline ufficiale.

## Esecuzione e verifica

Richiede Python `3.13.0`.

```powershell
python -m pip install --require-hashes -r requirements.lock
python main.py --force-download
python reproduce.py --manifest docs/runs/baseline-v3-2026-08-27/manifest.json
python -m unittest discover -s tests -v
```

La vecchia baseline si riproduce dal suo tag storico; nel checkout corrente se
ne verificano comunque manifest, snapshot e hash degli artefatti. La procedura
completa e descritta in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

## Limiti

Spread, slippage, imposte e rendimento della liquidita non sono inclusi. Il
modello puo essere soggetto a overfitting e dipende dalla qualita dei dati
Coinbase. L'esposizione binaria e il drawdown storico restano rischi materiali.
Il progetto e informativo e non costituisce consulenza finanziaria.
