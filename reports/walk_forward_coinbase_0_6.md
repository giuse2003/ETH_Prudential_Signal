# Walk-Forward ETH Coinbase - Commissione 0,6%

## Protocollo

- Baseline congelata: `baseline-v1-2026-07-26`.
- Serie grezza Coinbase: `2016-05-23` -> `2026-07-26`.
- Valutazione indicatori: `2016-12-08` -> `2026-07-26`.
- Pseudo out-of-sample cucito: `2021-01-01` -> `2026-07-26`.
- Definizioni esplorate: 285; percorsi di segnale distinti: 134.
- Universo prudente con soli ingressi baseline: 49 percorsi.
- Commissione applicata: 0,6% a ogni cambio completo di esposizione; Buy & Hold paga acquisto e liquidazione.
- Ogni selezione annuale usa esclusivamente dati fino al 31 dicembre precedente.
- Il portafoglio non viene azzerato artificialmente tra gli anni: ogni cambio di esposizione del modello selezionato paga la commissione.
- Questo e un walk-forward retrospettivo, non un vero futuro non osservato: l'universo delle ipotesi e stato definito dopo avere visto la serie completa.

## Regola Di Selezione

Un percorso e eleggibile solo se sul training migliora annualizzato, drawdown e Sharpe rispetto alla baseline, completa almeno cinque trade e non supera il turnover baseline di oltre 12 lati. Fra gli eleggibili viene scelto il miglior rango medio delle tre metriche; complessita e turnover rompono soltanto le parita.

## Selezioni Annuali

| Policy | Test | Eleggibili / universo | Variante scelta | Ann. train | DD train | Sharpe train | Delta return test | Delta DD test | Delta Sharpe test | Esito |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `wf_exit_only` | 2021 | 28/49 | `combo_trail_mom_11_sma_break_2_5` | 184.92% | -28.78% | 2.132 | +322.52 pp | +16.55 pp | +0.891 | MIGLIORA |
| `wf_full_grid` | 2021 | 80/134 | `combo_three_early_8_trail_10_sma_1_8` | 225.11% | -31.87% | 2.274 | +338.92 pp | +18.24 pp | +0.922 | MIGLIORA |
| `wf_exit_only` | 2022 | 32/49 | `combo_trail_mom_11_sma_break_2_5` | 242.61% | -28.78% | 2.321 | +0.00 pp | +0.00 pp | n/a | INVARIATO |
| `wf_full_grid` | 2022 | 85/134 | `combo_three_early_8_trail_10_sma_1_8` | 282.58% | -31.87% | 2.434 | +0.00 pp | +0.00 pp | n/a | INVARIATO |
| `wf_exit_only` | 2023 | 32/49 | `combo_trail_mom_11_sma_break_2_5` | 179.66% | -28.78% | 2.118 | +11.14 pp | +4.56 pp | +0.409 | MIGLIORA |
| `wf_full_grid` | 2023 | 85/134 | `combo_three_early_8_trail_10_sma_1_8` | 206.66% | -31.87% | 2.221 | +18.37 pp | +6.06 pp | +0.636 | MIGLIORA |
| `wf_exit_only` | 2024 | 32/49 | `combo_trail_mom_10_sma_break_2_0` | 141.38% | -31.87% | 1.926 | -1.94 pp | +0.54 pp | -0.058 | MISTO |
| `wf_full_grid` | 2024 | 86/134 | `combo_three_early_8_trail_10_sma_1_8` | 164.34% | -31.87% | 2.039 | +12.58 pp | -0.09 pp | +0.354 | MISTO |
| `wf_exit_only` | 2025 | 18/49 | `combo_trail_mom_15_sma_break_2_0` | 112.53% | -41.23% | 1.730 | +40.27 pp | -12.71 pp | +1.342 | MISTO |
| `wf_full_grid` | 2025 | 71/134 | `combo_three_early_8_trail_15_sma_2_0` | 130.74% | -39.15% | 1.837 | +28.20 pp | -12.71 pp | +1.019 | MISTO |
| `wf_exit_only` | 2026 | 27/49 | `combo_trail_mom_10_sma_break_2_0` | 104.24% | -46.84% | 1.681 | +0.00 pp | +0.00 pp | n/a | INVARIATO |
| `wf_full_grid` | 2026 | 93/134 | `combo_three_early_8_trail_10_sma_2_0` | 121.56% | -43.26% | 1.788 | +0.00 pp | +0.00 pp | n/a | INVARIATO |

## Curva Pseudo Out-Of-Sample 2021-2026

Le configurazioni fisse sono riferimenti scelti con hindsight; le due righe walk-forward sono le sole che ricostruiscono una selezione annuale basata sul passato.

| Modello | Totale | Ann. | Max DD | Sharpe | Turnover | Trade | Esposizione |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline netta | 194.63% | 21.41% | -51.57% | 0.672 | 48 | 24 | 25.33% |
| Buy & Hold netto | 161.63% | 18.85% | -79.35% | 0.610 | 2 | 0 | 100.00% |
| Challenger A: Trail -10 / SMA 2% | 874.11% | 50.48% | -46.84% | 1.195 | 40 | 20 | 27.45% |
| Challenger B: Trail -15 / SMA 2% | 834.01% | 49.35% | -43.00% | 1.197 | 42 | 21 | 26.22% |
| Tripla rendimento: Early 8 / Trail -10 / SMA 2% | 1018.53% | 54.27% | -43.26% | 1.233 | 42 | 21 | 29.32% |
| Tripla difensiva: Early 8 / Trail -15 / SMA 2% | 972.48% | 53.11% | -39.15% | 1.235 | 44 | 22 | 28.09% |
| Walk-forward sole uscite | 752.56% | 46.93% | -46.84% | 1.150 | 42 | 21 | 27.30% |
| Walk-forward intero universo | 882.80% | 50.72% | -45.83% | 1.191 | 46 | 23 | 28.92% |

## Risultati Annuali Dei Selettori

| Anno | Policy | Return | Delta return | DD | Delta DD | Sharpe | Delta Sharpe | Esito |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | `wf_exit_only` | 620.70% | +322.52 pp | -25.33% | +16.55 pp | 2.960 | +0.891 | MIGLIORA |
| 2021 | `wf_full_grid` | 637.10% | +338.92 pp | -23.64% | +18.24 pp | 2.991 | +0.922 | MIGLIORA |
| 2022 | `wf_exit_only` | 0.00% | +0.00 pp | 0.00% | +0.00 pp | n/a | n/a | INVARIATO |
| 2022 | `wf_full_grid` | 0.00% | +0.00 pp | 0.00% | +0.00 pp | n/a | n/a | INVARIATO |
| 2023 | `wf_exit_only` | 0.15% | +11.14 pp | -27.24% | +4.56 pp | 0.155 | +0.409 | MIGLIORA |
| 2023 | `wf_full_grid` | 7.38% | +18.37 pp | -25.74% | +6.06 pp | 0.382 | +0.636 | MIGLIORA |
| 2024 | `wf_exit_only` | -8.80% | -1.94 pp | -45.19% | +0.54 pp | -0.073 | -0.058 | MISTO |
| 2024 | `wf_full_grid` | 5.72% | +12.58 pp | -45.83% | -0.09 pp | 0.338 | +0.354 | MISTO |
| 2025 | `wf_exit_only` | 29.52% | +40.27 pp | -29.50% | -12.71 pp | 0.990 | +1.342 | MISTO |
| 2025 | `wf_full_grid` | 17.45% | +28.20 pp | -29.50% | -12.71 pp | 0.667 | +1.019 | MISTO |
| 2026 | `wf_exit_only` | 0.00% | +0.00 pp | 0.00% | +0.00 pp | n/a | n/a | INVARIATO |
| 2026 | `wf_full_grid` | 0.00% | +0.00 pp | 0.00% | +0.00 pp | n/a | n/a | INVARIATO |

## Sintesi Annuale

| Modello | Migliora | Invariato | Misto | Peggiora |
|---|---:|---:|---:|---:|
| Challenger A: Trail -10 / SMA 2% | 2 | 2 | 2 | 0 |
| Challenger B: Trail -15 / SMA 2% | 3 | 2 | 1 | 0 |
| Tripla rendimento: Early 8 / Trail -10 / SMA 2% | 3 | 2 | 1 | 0 |
| Tripla difensiva: Early 8 / Trail -15 / SMA 2% | 3 | 2 | 1 | 0 |
| Walk-forward sole uscite | 2 | 2 | 2 | 0 |
| Walk-forward intero universo | 2 | 2 | 2 | 0 |

## Stress: Una Candela Di Ritardo Aggiuntiva

Il segnale baseline e gia applicato al rendimento successivo; questo scenario aggiunge un ulteriore giorno di ritardo senza superare la commissione dello 0,6%.

| Modello | Ann. normale | Ann. ritardato | DD ritardato | Sharpe ritardato | Delta ann. da ritardo |
|---|---:|---:|---:|---:|---:|
| Baseline netta | 21.41% | 17.47% | -59.85% | 0.589 | -3.94 pp |
| Challenger A: Trail -10 / SMA 2% | 50.48% | 36.62% | -49.96% | 0.954 | -13.87 pp |
| Challenger B: Trail -15 / SMA 2% | 49.35% | 37.44% | -47.25% | 0.983 | -11.91 pp |
| Walk-forward sole uscite | 46.93% | 35.49% | -49.96% | 0.942 | -11.44 pp |
| Walk-forward intero universo | 50.72% | 36.32% | -46.98% | 0.943 | -14.41 pp |

## Probability Of Backtest Overfitting

CSCV esaustivo con 10 blocchi contigui e 252 suddivisioni simmetriche. PBO e la quota di vincitori in-sample che finiscono sotto la mediana nel complemento.
La statistica di selezione CSCV e lo Sharpe, come nel test PBO standard: misura la stabilita del ranking relativo, non replica il selettore multi-metrica. Un PBO alto puo quindi coesistere con Sharpe test positivi.

| Campione | Osservazioni | Percorsi | PBO | Rank test mediano | Sharpe train scelto | Sharpe test scelto | Test Sharpe > 0 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `full_all_paths` | 3518 | 134 | 19.44% | 91.11% | 1.680 | 1.492 | 99.60% |
| `train_to_2020_all_paths` | 1485 | 134 | 35.32% | 69.07% | 2.310 | 1.973 | 100.00% |
| `full_exit_only` | 3518 | 49 | 33.73% | 70.00% | 1.598 | 1.380 | 99.60% |
| `train_to_2020_exit_only` | 1485 | 49 | 69.84% | 40.00% | 2.151 | 1.868 | 100.00% |

## Deflated Sharpe Ratio

Il benchmark DSR e lo Sharpe massimo atteso dopo 134 tentativi distinti. La probabilita DSR corregge selezione multipla, asimmetria e code non normali; resta una diagnostica, non una garanzia.

| Serie | Variante | Osservazioni | Sharpe | Benchmark DSR | PSR > 0 | Probabilita DSR |
|---|---|---:|---:|---:|---:|---:|
| `full_best_path` | `combo_three_early_8_trail_10_sma_2_0` | 3518 | 1.735 | 0.437 | 100.00% | 100.00% |
| `full_challenger_a` | `combo_trail_mom_10_sma_break_2_0` | 3518 | 1.630 | 0.437 | 100.00% | 100.00% |
| `full_challenger_b` | `combo_trail_mom_15_sma_break_2_0` | 3518 | 1.615 | 0.437 | 100.00% | 100.00% |
| `full_triple_return` | `combo_three_early_8_trail_10_sma_2_0` | 3518 | 1.735 | 0.437 | 100.00% | 100.00% |
| `full_triple_defensive` | `combo_three_early_8_trail_15_sma_2_0` | 3518 | 1.689 | 0.437 | 100.00% | 100.00% |
| `oos_baseline` | `baseline` | 2033 | 0.672 | 0.437 | 94.36% | 71.07% |
| `oos_challenger_a` | `combo_trail_mom_10_sma_break_2_0` | 2033 | 1.195 | 0.437 | 99.82% | 96.78% |
| `oos_challenger_b` | `combo_trail_mom_15_sma_break_2_0` | 2033 | 1.197 | 0.437 | 99.82% | 96.80% |
| `oos_wf_full_grid` | `wf_full_grid` | 2033 | 1.191 | 0.437 | 99.81% | 96.69% |
| `oos_wf_exit_only` | `wf_exit_only` | 2033 | 1.150 | 0.437 | 99.74% | 95.86% |

## Lettura

- Il selettore con Sharpe pseudo out-of-sample piu alto e `wf_full_grid`: ann. 50.72%, DD -45.83%, Sharpe 1.191.
- Rispetto alla baseline, questo selettore migliora tutte e tre le metriche aggregate.
- `wf_exit_only` conta 2 anni migliori, 2 invariati e 2 misti; `wf_full_grid` mostra la stessa ripartizione: 2/2/2.
- Il Challenger B fisso offre il compromesso semplice piu difensivo: ann. 49.35%, DD -43.00%, Sharpe 1.197; il Challenger A rende +1.13 pp in piu ma ha un DD peggiore di 3.84 pp.
- Con una candela extra di ritardo, B mantiene ann. 37.44%, DD -47.25% e Sharpe 0.983, tutti migliori di A nello stesso stress.
- La riottimizzazione annuale non batte il Challenger B fisso sullo Sharpe e aggiunge complessita; il PBO iniziale del solo universo uscite rafforza la preferenza per una soglia congelata.
- I riferimenti fissi A/B e tripli non diventano out-of-sample solo perche sono misurati dal 2021: sono stati scelti dopo avere osservato anche quel periodo.
- La decisione su una baseline v2 deve pesare insieme curva cucita, PBO, DSR, stabilita annuale e stress di esecuzione.

## Integrita

- Snapshot Coinbase SHA-256: `09504484b0d115c6b130dbfc82f05f5dc9137ce11b1cf12604f9a1c96132c357`.
- La replica dei segnali baseline e stata verificata riga per riga prima del test.
- Baseline, strategia ufficiale, manifest e artefatti congelati non sono stati modificati.
