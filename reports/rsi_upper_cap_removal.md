# Rimozione del tetto RSI 65 - Backtest sperimentale

Data test: `2026-08-22`.
Periodo valutato: `2016-12-08` -> `2026-08-21`.
Cutoff richiesto: `2026-08-21`. Mercato: `ETH-USD` Coinbase, candele daily UTC chiuse.

Questo test non modifica la Baseline ufficiale. Cambia una sola regola di ingresso:

- Baseline: `40 <= RSI(14) <= 65`;
- variante: `RSI(14) >= 40`, senza limite superiore;
- tutte le altre condizioni di acquisto e le due uscite restano invariate.

## Metriche periodo completo

Commissione ufficiale conservativa: `0,60%` per lato.

| Modello | Totale | Annualizzato | Max DD | Sharpe | PF | Trade | Win rate | Esposizione |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_rsi_40_65 | 56672.64% | 92.19% | -43.00% | 1.609 | 14.944 | 30 | 50.00% | 26.78% |
| rsi_ge_40_only | 160216.14% | 113.88% | -42.56% | 1.665 | 19.156 | 34 | 52.94% | 29.09% |

## Stress costi

Le tariffe VIP Coinbase sono trattate come scenari operativi: maker `0,07%`,
taker `0,16%` e misto `0,115%` medio per lato. Lo scenario taker e' il
riferimento piu conservativo quando si richiede esecuzione immediata; il
maker non garantisce il riempimento dell'ordine. Il `0,60%` resta lo stress
prudenziale configurato nel modello.

| Scenario | Modello | Annualizzato | Max DD | Sharpe | PF |
|---|---|---:|---:|---:|---:|
| lordo | baseline_rsi_40_65 | 99.41% | -38.70% | 1.686 | 16.410 |
| lordo | rsi_ge_40_only | 123.03% | -38.27% | 1.742 | 20.978 |
| promo_maker_0_07pct | baseline_rsi_40_65 | 98.55% | -39.21% | 1.677 | 16.226 |
| promo_maker_0_07pct | rsi_ge_40_only | 121.94% | -38.78% | 1.733 | 20.760 |
| promo_misto_0_115pct | baseline_rsi_40_65 | 98.01% | -39.54% | 1.671 | 16.110 |
| promo_misto_0_115pct | rsi_ge_40_only | 121.25% | -39.11% | 1.728 | 20.615 |
| promo_taker_0_16pct | baseline_rsi_40_65 | 97.46% | -39.87% | 1.665 | 15.995 |
| promo_taker_0_16pct | rsi_ge_40_only | 120.56% | -39.44% | 1.722 | 20.471 |
| prudenziale_0_60pct | baseline_rsi_40_65 | 92.19% | -43.00% | 1.609 | 14.944 |
| prudenziale_0_60pct | rsi_ge_40_only | 113.88% | -42.56% | 1.665 | 19.156 |
| stress_1_00pct | baseline_rsi_40_65 | 87.50% | -45.71% | 1.557 | 14.089 |
| stress_1_00pct | rsi_ge_40_only | 107.97% | -45.26% | 1.613 | 18.084 |

## Stabilita annuale

| Anno | Baseline ret | RSI >= 40 ret | Baseline DD | RSI >= 40 DD |
|---:|---:|---:|---:|---:|
| 2016 | 0.00% | 0.00% | 0.00% | 0.00% |
| 2017 | 1358.68% | 3825.27% | -31.87% | -31.87% |
| 2018 | 0.00% | 16.28% | 0.00% | -29.00% |
| 2019 | 42.25% | 42.25% | -20.24% | -20.24% |
| 2020 | 191.17% | 187.92% | -20.40% | -20.40% |
| 2021 | 634.42% | 634.42% | -25.06% | -25.06% |
| 2022 | 0.00% | 0.00% | 0.00% | 0.00% |
| 2023 | 1.94% | 1.94% | -26.07% | -26.07% |
| 2024 | -5.19% | -4.45% | -41.23% | -40.78% |
| 2025 | 29.52% | 17.30% | -29.50% | -36.15% |
| 2026 | 0.00% | 0.00% | 0.00% | 0.00% |

## Nuovi ingressi causati dalla rimozione del tetto

Nuovi ingressi effettivi: `8`.

| Entrata | Uscita | Prezzo USD | RSI | Rendimento netto | DD trade | Giorni |
|---|---|---:|---:|---:|---:|---:|
| 2017-02-23 | 2017-03-08 | 13.21 | 70.66 | 25.51% | -15.24% | 13 |
| 2017-03-11 | 2017-06-21 | 21.64 | 73.41 | 1395.40% | -26.81% | 102 |
| 2017-12-09 | 2017-12-22 | 485.04 | 67.79 | 39.72% | -17.49% | 13 |
| 2018-01-02 | 2018-02-01 | 865.00 | 68.91 | 16.98% | -29.00% | 30 |
| 2020-02-16 | 2020-02-19 | 258.50 | 69.38 | -0.52% | -8.70% | 3 |
| 2024-05-20 | 2024-06-11 | 3661.52 | 69.98 | -5.04% | -10.11% | 22 |
| 2024-12-05 | 2024-12-18 | 3788.93 | 67.51 | -4.87% | -9.53% | 13 |
| 2025-08-22 | 2025-09-22 | 4831.24 | 66.76 | -13.54% | -13.02% | 31 |

## Finestre mobili e caso agosto 2026

- Finestre mobili di 730 giorni: `97`.
- Rendimento migliore della Baseline: `40.21%` delle finestre.
- Sharpe migliore: `36.08%` delle finestre.
- Drawdown uguale o migliore: `43.30%` delle finestre.
- Peggior delta rendimento: `-27.39%`.
- Peggior delta drawdown: `-17.08%`.
- Dal 16 al 21 agosto 2026 i segnali restano identici: `si`.
- La rimozione del tetto RSI non intercetta il rally di agosto 2026, perche `SMA50 > SMA200` resta falsa.

## Conclusione

- Le metriche complete migliorano, ma il vantaggio e' concentrato soprattutto negli ingressi anticipati del 2017.
- La variante peggiora il 2025 e non migliora la maggioranza delle finestre mobili biennali.
- Il risultato non giustifica una promozione immediata e non risolve il movimento che ha motivato il test.
- Prossimo test corretto: un ingresso breakout separato, senza allentare globalmente il filtro RSI.
