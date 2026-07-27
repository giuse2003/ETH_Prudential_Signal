# Condition Ablation Research - Coinbase ETH 0,6%

## Protocollo

- Baseline congelata: `baseline-v1-2026-07-26`.
- Periodo: `2016-12-08` -> `2026-07-26`.
- Varianti testate: 284 oltre alla baseline.
- Percorsi di segnale realmente distinti: 134/285; le soglie equivalenti non sono contate come fenomeni diversi.
- Commissioni: 0%, 0,3% e massimo 0,6% per lato; selezione effettuata sullo 0,6%.
- Validazione: quattro regimi fissi e finestre rolling di 730 giorni ogni 90 giorni.
- Una variante supera il gate solo se migliora rendimento annualizzato, drawdown e Sharpe sul periodo completo e recente, con stabilita rolling e turnover limitato.
- Il test e sperimentale e non modifica la baseline ufficiale.

## Baseline Netta 0,6%

| Ann. | Max DD | Sharpe | PF | Operazioni | Turnover | Esposizione |
|---:|---:|---:|---:|---:|---:|---:|
| 64.61% | -51.57% | 1.265 | 10.969 | 36 | 72 | 26.15% |

Il PF del report e ricalcolato sui trade chiusi includendo entrambe le commissioni; il motore ufficiale non viene modificato.

## Fenomeni Isolati Piu Robusti

| Variante | Famiglia | Ann. | Max DD | Sharpe | PF | Ops | Roll all-3 | Regimi all-3 | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `entry_early_momentum_max_8` | entry_trend_gate | 76.69% | -49.57% | 1.372 | 11.444 | 39 | 80.65% | 3/4 | PASS |
| `entry_early_momentum_max_9` | entry_trend_gate | 76.69% | -49.57% | 1.372 | 11.444 | 39 | 80.65% | 3/4 | PASS |
| `entry_early_momentum_max_10` | entry_trend_gate | 76.69% | -49.57% | 1.372 | 11.444 | 39 | 80.65% | 3/4 | PASS |
| `entry_early_momentum_max_12` | entry_trend_gate | 76.69% | -49.57% | 1.372 | 11.444 | 39 | 80.65% | 3/4 | PASS |
| `trail_momentum_20` | trail_momentum | 77.11% | -43.79% | 1.450 | 11.358 | 37 | 74.19% | 3/4 | PASS |
| `trail_momentum_15` | trail_momentum | 77.11% | -43.79% | 1.450 | 11.358 | 37 | 74.19% | 3/4 | PASS |
| `trail_momentum_11` | trail_momentum | 76.39% | -47.57% | 1.438 | 11.322 | 37 | 67.74% | 3/4 | PASS |
| `trail_momentum_10` | trail_momentum | 76.39% | -47.57% | 1.438 | 11.322 | 37 | 67.74% | 3/4 | PASS |
| `trail_momentum_09` | trail_momentum | 76.39% | -47.57% | 1.438 | 11.322 | 37 | 67.74% | 3/4 | PASS |
| `trail_momentum_12` | trail_momentum | 75.81% | -47.57% | 1.431 | 11.294 | 37 | 67.74% | 3/4 | PASS |
| `trail_momentum_disabled` | trail_momentum | 75.13% | -49.54% | 1.429 | 11.242 | 37 | 67.74% | 3/4 | PASS |
| `entry_no_sma50_gate` | entry_trend_gate | 78.21% | -49.57% | 1.382 | 11.507 | 40 | 61.29% | 3/4 | PASS |

## Sintesi Per Famiglia

| Famiglia | Test | Migliora all-3 completo | Supera gate | Migliore | Roll all-3 |
|---|---:|---:|---:|---|---:|
| combined_three_way | 108 | 108 | 60 | `combo_three_early_8_trail_10_sma_2_0` | 90.32% |
| combined_trail_sma | 55 | 50 | 35 | `combo_trail_mom_11_sma_break_2_0` | 93.55% |
| combined_early_trail | 27 | 21 | 13 | `combo_early_rsi_64_tm_8_tv_20` | 74.19% |
| combined_momentum_trail | 12 | 12 | 12 | `combo_early_mom_8_trail_mom_8` | 77.42% |
| entry_trend_gate | 17 | 15 | 8 | `entry_early_momentum_max_8` | 80.65% |
| trail_momentum | 13 | 10 | 7 | `trail_momentum_20` | 74.19% |
| combined_early_sma | 6 | 4 | 2 | `combo_early_mom_8_sma_break_2_0` | 80.65% |
| sell_sma50 | 11 | 1 | 0 | `sell_sma50_break_2_5` | 74.19% |
| entry_momentum | 4 | 2 | 0 | `entry_momentum_p5` | 51.61% |
| entry_volume | 4 | 0 | 0 | `entry_volume_p10` | 48.39% |
| entry_rsi_cap | 8 | 6 | 0 | `entry_rsi_max_60` | 38.71% |
| trail_width | 8 | 4 | 0 | `trail_width_10` | 38.71% |
| trail_volume | 7 | 0 | 0 | `trail_volume_disabled` | 32.26% |
| entry_ablation | 4 | 0 | 0 | `entry_no_momentum` | 22.58% |

## Combinazioni

| Variante | Ann. | Max DD | Sharpe | PF | Ops | Roll all-3 | Regimi all-3 | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `combo_trail_mom_11_sma_break_2_0` | 95.83% | -46.84% | 1.631 | 15.984 | 28 | 93.55% | 4/4 | PASS |
| `combo_trail_mom_10_sma_break_2_0` | 95.83% | -46.84% | 1.631 | 15.984 | 28 | 93.55% | 4/4 | PASS |
| `combo_trail_mom_9_sma_break_2_0` | 95.83% | -46.84% | 1.631 | 15.984 | 28 | 93.55% | 4/4 | PASS |
| `combo_trail_mom_12_sma_break_2_0` | 93.51% | -46.84% | 1.614 | 15.102 | 29 | 93.55% | 4/4 | PASS |
| `combo_three_early_8_trail_10_sma_2_0` | 111.42% | -43.26% | 1.735 | 15.807 | 31 | 90.32% | 4/4 | PASS |
| `combo_three_early_9_trail_10_sma_2_0` | 111.42% | -43.26% | 1.735 | 15.807 | 31 | 90.32% | 4/4 | PASS |
| `combo_three_early_10_trail_10_sma_2_0` | 111.42% | -43.26% | 1.735 | 15.807 | 31 | 90.32% | 4/4 | PASS |
| `combo_three_early_11_trail_10_sma_2_0` | 111.42% | -43.26% | 1.735 | 15.807 | 31 | 90.32% | 4/4 | PASS |
| `combo_three_early_12_trail_10_sma_2_0` | 111.42% | -43.26% | 1.735 | 15.807 | 31 | 90.32% | 4/4 | PASS |
| `combo_three_early_8_trail_20_sma_2_0` | 104.79% | -39.15% | 1.689 | 13.687 | 34 | 90.32% | 4/4 | PASS |
| `combo_three_early_8_trail_18_sma_2_0` | 104.79% | -39.15% | 1.689 | 13.687 | 34 | 90.32% | 4/4 | PASS |
| `combo_three_early_8_trail_15_sma_2_0` | 104.79% | -39.15% | 1.689 | 13.687 | 34 | 90.32% | 4/4 | PASS |

## Attribuzione Dei Tre Fenomeni

La decomposizione Shapley usa tutte le otto combinazioni della configurazione centrale `early 8% / trail -10% / SMA 2%`. I contributi sommano esattamente al miglioramento della combinazione completa rispetto alla baseline.

| Fenomeno | Contributo ann. | Contributo DD | Contributo Sharpe | Quota vantaggio log-wealth |
|---|---:|---:|---:|---:|
| Ingresso anticipato non esteso | +13.82 pp | +3.08 pp | +0.106 | 29.45% |
| Trail8 su discese rapide | +12.72 pp | +5.53 pp | +0.170 | 27.18% |
| Tolleranza 2% sotto SMA50 | +20.28 pp | -0.30 pp | +0.194 | 43.37% |

Un contributo DD positivo indica un drawdown meno profondo. La tolleranza SMA50 e il maggiore motore di rendimento e Sharpe, ma da sola peggiora leggermente il DD; il Trail8 ricalibrato fornisce la quota maggiore di protezione del drawdown.

## Sensibilita Alle Commissioni

| Variante | Commissione per lato | Ann. | Max DD | Sharpe | Turnover |
|---|---:|---:|---:|---:|---:|
| `baseline` | 0,0% | 72.16% | -45.89% | 1.357 | 72 |
| `baseline` | 0,3% | 68.35% | -48.69% | 1.311 | 72 |
| `baseline` | 0,6% | 64.61% | -51.57% | 1.265 | 72 |
| `combo_trail_mom_10_sma_break_2_0` | 0,0% | 102.74% | -42.83% | 1.702 | 56 |
| `combo_trail_mom_10_sma_break_2_0` | 0,3% | 99.26% | -44.87% | 1.666 | 56 |
| `combo_trail_mom_10_sma_break_2_0` | 0,6% | 95.83% | -46.84% | 1.631 | 56 |
| `combo_three_early_8_trail_10_sma_2_0` | 0,0% | 119.69% | -39.97% | 1.810 | 62 |
| `combo_three_early_8_trail_10_sma_2_0` | 0,3% | 115.52% | -41.59% | 1.773 | 62 |
| `combo_three_early_8_trail_10_sma_2_0` | 0,6% | 111.42% | -43.26% | 1.735 | 62 |
| `combo_three_early_8_trail_15_sma_2_0` | 0,0% | 113.60% | -35.64% | 1.773 | 68 |
| `combo_three_early_8_trail_15_sma_2_0` | 0,3% | 109.16% | -37.37% | 1.731 | 68 |
| `combo_three_early_8_trail_15_sma_2_0` | 0,6% | 104.79% | -39.15% | 1.689 | 68 |

## Plateau Locale Trail-SMA50

Ogni cella mostra la quota di finestre rolling che migliora rendimento, DD e Sharpe insieme; `*` indica il superamento del gate completo.

| Trail minimo / SMA tolleranza | 1.50% | 1.75% | 2.00% | 2.25% | 2.50% |
|---|---:|---:|---:|---:|---:|
| -20% | 83.87%* | 83.87%* | 83.87%* | 83.87%* | 74.19%* |
| -18% | 83.87%* | 83.87%* | 83.87%* | 83.87%* | 74.19%* |
| -16% | 83.87%* | 83.87%* | 83.87%* | 83.87%* | 74.19%* |
| -15% | 83.87%* | 83.87%* | 83.87%* | 83.87%* | 74.19%* |
| -14% | 83.87%* | 83.87%* | 83.87%* | 83.87%* | 74.19%* |
| -13% | 83.87%* | 83.87%* | 83.87%* | 83.87%* | 74.19%* |
| -12% | 77.42% | 83.87% | 93.55%* | 80.65% | 67.74% |
| -11% | 77.42% | 83.87% | 93.55%* | 83.87% | 70.97% |
| -10% | 77.42% | 83.87% | 93.55%* | 83.87% | 70.97% |
| -9% | 77.42% | 83.87% | 93.55%* | 83.87% | 70.97% |
| -8% | 61.29% | 74.19% | 83.87%* | 74.19% | 77.42% |

- La configurazione centrale Trail `-10%` / SMA `2%` condivide esattamente lo stesso percorso di segnali con 3 celle della griglia locale.
- La configurazione completa early `8%` / Trail `-10%` / SMA `2%` e identica, evento per evento, a 5 celle della griglia a tre fattori.
- Il profilo piu protettivo early `8%` / Trail `-15%` / SMA `2%` condivide il percorso con 15 celle, incluse le soglie Trail `-18%` e `-20%`.
- Nella griglia a due fattori superano il gate 35/55 configurazioni; nella griglia a tre fattori 60/108.

## Profili Pareto

| Profilo | Variante rappresentativa | Ann. | Max DD | Sharpe | Roll all-3 | Turnover |
|---|---|---:|---:|---:|---:|---:|
| Rendimento / Sharpe | `combo_three_early_8_trail_10_sma_2_0` | 111.42% | -43.26% | 1.735 | 90.32% | 62 |
| Protezione drawdown | `combo_three_early_8_trail_15_sma_2_0` | 104.79% | -39.15% | 1.689 | 90.32% | 68 |

Il secondo profilo rinuncia a circa 6,6 punti di rendimento annualizzato e 0,046 di Sharpe, ma migliora il drawdown di circa 4,1 punti.

## Stabilita Temporale

| Variante | Regime | Delta rendimento totale | Delta DD | Delta Sharpe |
|---|---|---:|---:|---:|
| `combo_trail_mom_10_sma_break_2_0` | 2017-2018 | +325.94 pp | +13.62 pp | +0.198 |
| `combo_trail_mom_10_sma_break_2_0` | 2019-2020 | +91.47 pp | +6.69 pp | +0.220 |
| `combo_trail_mom_10_sma_break_2_0` | 2021-2022 | +344.10 pp | +18.24 pp | +0.646 |
| `combo_trail_mom_10_sma_break_2_0` | 2023-2026 | +58.16 pp | +4.73 pp | +0.572 |
| `combo_three_early_8_trail_15_sma_2_0` | 2017-2018 | +1089.25 pp | +13.62 pp | +0.435 |
| `combo_three_early_8_trail_15_sma_2_0` | 2019-2020 | +54.06 pp | +4.74 pp | +0.074 |
| `combo_three_early_8_trail_15_sma_2_0` | 2021-2022 | +330.16 pp | +16.82 pp | +0.629 |
| `combo_three_early_8_trail_15_sma_2_0` | 2023-2026 | +74.27 pp | +12.41 pp | +0.673 |
| `combo_three_early_8_trail_10_sma_2_0` | 2017-2018 | +1089.25 pp | +13.62 pp | +0.435 |
| `combo_three_early_8_trail_10_sma_2_0` | 2019-2020 | +180.52 pp | +4.86 pp | +0.303 |
| `combo_three_early_8_trail_10_sma_2_0` | 2021-2022 | +344.10 pp | +18.24 pp | +0.646 |
| `combo_three_early_8_trail_10_sma_2_0` | 2023-2026 | +77.75 pp | +8.31 pp | +0.681 |

## Diagnostica Recente E Rolling

| Variante | Ann. dal 2022 | Max DD dal 2022 | Sharpe dal 2022 | Roll rendimento+ | Roll DD non peggiore | Roll Sharpe+ | Roll all-3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | -6.38% | -51.57% | -0.147 | n/a | n/a | n/a | n/a |
| `combo_trail_mom_10_sma_break_2_0` | 6.29% | -46.84% | 0.358 | 100.00% | 93.55% | 100.00% | 93.55% |
| `combo_three_early_8_trail_10_sma_2_0` | 9.56% | -43.26% | 0.455 | 100.00% | 90.32% | 100.00% | 90.32% |
| `combo_three_early_8_trail_15_sma_2_0` | 9.01% | -39.15% | 0.448 | 100.00% | 90.32% | 96.77% | 90.32% |

| Variante | Peggior delta rendimento rolling | Peggior delta DD rolling | Peggior delta Sharpe rolling |
|---|---:|---:|---:|
| `combo_trail_mom_10_sma_break_2_0` | +3.99 pp | -4.29 pp | +0.056 |
| `combo_three_early_8_trail_10_sma_2_0` | +8.17 pp | -4.29 pp | +0.117 |
| `combo_three_early_8_trail_15_sma_2_0` | +0.65 pp | -1.95 pp | -0.043 |

## Audit Dei Trade Netti

Le statistiche seguenti includono lo 0,6% all'ingresso e lo 0,6% all'uscita. La concentrazione Top 3 misura quanta parte dei log-rendimenti positivi proviene dai tre trade migliori.

| Variante | Trade | Win rate | Mediana | Peggiore | Migliore | PF netto | Top 3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 36 | 33.33% | -3.67% | -11.75% | 857.04% | 10.969 | 68.14% |
| `entry_early_momentum_max_8` | 39 | 38.46% | -3.29% | -14.24% | 857.04% | 11.444 | 61.25% |
| `trail_momentum_10` | 37 | 35.14% | -3.57% | -11.75% | 857.04% | 11.322 | 56.88% |
| `sell_sma50_break_2_0` | 26 | 53.85% | 4.32% | -13.40% | 857.04% | 16.423 | 63.17% |
| `combo_trail_mom_10_sma_break_2_0` | 28 | 53.57% | 4.32% | -13.40% | 857.04% | 15.984 | 51.66% |
| `combo_three_early_8_trail_10_sma_2_0` | 31 | 54.84% | 11.87% | -13.40% | 857.04% | 15.807 | 47.07% |
| `combo_three_early_8_trail_15_sma_2_0` | 34 | 50.00% | 0.64% | -13.40% | 857.04% | 13.687 | 47.46% |

## Eventi Che Cambiano

### Ingressi anticipati aggiuntivi

| Data | Momentum 7g | Volume relativo | SMA50 vs SMA200 |
|---|---:|---:|---:|
| 2017-02-02 | 2.08% | 3.99% | -13.02% |
| 2019-04-11 | 4.61% | 32.07% | -4.05% |
| 2020-04-16 | 1.65% | 96.92% | -5.28% |
| 2020-04-23 | 7.60% | 22.65% | -9.04% |
| 2023-11-14 | 4.97% | 30.03% | -2.39% |
| 2024-11-14 | 5.57% | 10.63% | -11.11% |
| 2025-06-11 | 6.26% | 46.96% | -12.10% |

### Uscite Trail8 aggiuntive sulle discese rapide

| Data | Momentum 7g | Volume relativo | Close |
|---|---:|---:|---:|
| 2017-09-04 | -8.83% | 197.00% | 316.86 |
| 2020-12-23 | -8.29% | 81.68% | 585.11 |
| 2021-05-16 | -8.73% | 22.00% | 3585.62 |
| 2021-09-08 | -8.59% | 83.74% | 3500.34 |
| 2021-11-17 | -7.40% | 20.41% | 4289.40 |
| 2024-06-11 | -8.21% | 67.89% | 3497.31 |
| 2024-12-18 | -5.48% | 21.18% | 3624.84 |

## Lettura

- Varianti che migliorano tutte e tre le metriche sul periodo completo: 233/284.
- Varianti che superano il gate di robustezza: 137/284.
- Migliore fenomeno isolato secondo il gate: `entry_early_momentum_max_8`; ann. 76.69%, DD -49.57%, Sharpe 1.372.
- Migliore combinazione secondo il gate: `combo_trail_mom_11_sma_break_2_0`; ann. 95.83%, DD -46.84%, Sharpe 1.631.
- I risultati servono a identificare fenomeni, non a promuovere automaticamente la migliore riga numerica.
- Le soglie devono mostrare un plateau vicino al valore migliore e devono essere riesaminate con audit evento-per-evento e dati futuri realmente non osservati.

## Integrita

- Snapshot Coinbase SHA-256: `09504484b0d115c6b130dbfc82f05f5dc9137ce11b1cf12604f9a1c96132c357`.
- La replica sperimentale dei segnali baseline e stata confrontata riga per riga con l'artefatto ufficiale.
- Nessun file del modello o della baseline congelata e stato modificato.
