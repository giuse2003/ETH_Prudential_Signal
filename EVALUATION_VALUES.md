# Valutazione della Baseline ufficiale

Fonte canonica interna:
`docs/runs/baseline-v2-2026-07-26/manifest.json`.

## Perimetro

- mercato e fonte: Coinbase Advanced Trade `ETH-USD`;
- storico continuo: `2016-05-23` - `2026-07-26`;
- warm-up indicatori: fino al `2016-12-07`;
- valutazione: `2016-12-08` - `2026-07-26`;
- osservazioni e giorni di calendario: `3518`;
- segnale alla chiusura `t`, esposizione applicata al rendimento `t+1`;
- commissione: `0,006` a ogni lato della strategia;
- Buy & Hold: `0,006` all'acquisto e `0,006` alla vendita finale;
- spread, slippage, imposte e rendimento cash: esclusi.

## Valori canonici

| Metrica | ETH-USD Signal | Buy & Hold |
|---|---:|---:|
| Rendimento totale | `566.7264499626586` | `234.31282261951222` |
| Rendimento annualizzato | `0.9312080082742844` | `0.7625167394094554` |
| Max drawdown | `-0.4299646722120246` | `-0.940116304238034` |
| Sharpe | `1.6148009161043904` | `1.073996567087056` |
| Trade completati | `30` | n/a |
| Win rate | `0.5` | n/a |
| Profit factor | `14.94397361521486` | n/a |
| Turnover/lati | `60` | `2` |

La strategia termina fuori mercato al cutoff. L'azione sulla candela
`2026-07-26` e `MANTIENI STATO ATTUALE`.

## Confronti da non confondere

I valori sopra descrivono l'intero periodo congelato e includono le commissioni.
Il report `reports/walk_forward_coinbase_0_6.md` usa invece il periodo cucito
`2021-01-01` - `2026-07-26` per la validazione della promozione. I suoi valori
non devono essere confrontati direttamente con quelli dell'intero periodo.

La vecchia baseline e conservata in
`docs/runs/baseline-v1-2026-07-26/manifest.json`. Le sue metriche canoniche sono
lordo commissioni e restano un riferimento storico, non il modello operativo.

## Interpretazione

La Baseline ufficiale migliora sul campione storico rendimento, drawdown e
Sharpe rispetto alla vecchia baseline e al Buy & Hold. Il vantaggio storico non
dimostra che le stesse relazioni continueranno in futuro. La selezione delle
soglie e retrospettiva e resta esposta a overfitting e cambi di regime.
