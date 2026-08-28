# Valutazione della Baseline ufficiale

Fonte canonica interna:
`docs/runs/baseline-v3-2026-08-27/manifest.json`.

## Perimetro

- mercato e fonte: Coinbase Advanced Trade `ETH-USD`;
- storico continuo: `2016-05-23` - `2026-08-27`;
- warm-up indicatori: fino al `2016-12-07`;
- valutazione: `2016-12-08` - `2026-08-27`;
- osservazioni e giorni di calendario: `3550`;
- segnale alla chiusura `t`, esposizione applicata al rendimento `t+1`;
- commissione: `0,006` a ogni lato della strategia;
- Buy & Hold: `0,006` all'acquisto e `0,006` alla vendita finale;
- spread, slippage, imposte e rendimento cash: esclusi.

## Valori canonici

| Metrica | ETH-USD Signal | Buy & Hold |
|---|---:|---:|
| Rendimento totale | `2403.105497728694` | `301.63663172195123` |
| Rendimento annualizzato | `1.22698408495972` | `0.7995028328660554` |
| Max drawdown | `-0.39054414423097705` | `-0.940116304238034` |
| Sharpe | `1.845250517257096` | `1.0966779780826854` |
| Trade completati | `32` | n/a |
| Win rate | `0.59375` | n/a |
| Profit factor | `17.813017225255965` | n/a |
| Turnover/lati | `65` | `2` |

Il backtest storico termina con il trade breakout del 17 agosto ancora aperto.
Lo stato operativo reale resta invece `FUORI`: la nuova regola si applica alle
candele chiuse dal 28 agosto senza ingresso retroattivo.

## Confronti da non confondere

I valori sopra descrivono l'intero periodo congelato e includono le commissioni.
Il report `reports/walk_forward_coinbase_0_6.md` usa invece il periodo cucito
`2021-01-01` - `2026-07-26` per la validazione della promozione. I suoi valori
non devono essere confrontati direttamente con quelli dell'intero periodo.

La vecchia baseline e conservata in
`docs/runs/baseline-v2-2026-07-26/manifest.json` e
`docs/runs/baseline-v1-2026-07-26/manifest.json`. Le metriche storiche sono
lordo commissioni e restano un riferimento storico, non il modello operativo.

## Interpretazione

La Baseline ufficiale migliora sul campione storico rendimento, drawdown e
Sharpe rispetto alla baseline precedente e al Buy & Hold. Il vantaggio storico non
dimostra che le stesse relazioni continueranno in futuro. La selezione delle
soglie e retrospettiva e resta esposta a overfitting e cambi di regime.
