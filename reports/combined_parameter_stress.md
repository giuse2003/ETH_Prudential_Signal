# Combined Parameter Stress Test

Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.

Griglia testata:

- RSI massimo: 60, 62, 65, 68, 70;
- momentum 7g minimo: -6%, -5%, -4%;
- volume relativo minimo: +10%, +20%, +30%, +40%;
- trailing stop: 8% fisso su massimo Close post-ingresso.

Performance misurata in EUR con `Close_EUR`.

## Focus Candidato

| Variante | Ann. | Max DD | Sharpe | Recent Sharpe | PF | Operazioni |
|---|---:|---:|---:|---:|---:|---:|
| rsi65_trail8_mom-5_vol20 | 51.41% | -40.69% | 1.265 | 0.428 | 6.747 | 28 |

## Top Per Sharpe Completo

| Variante | Ann. | Max DD | Sharpe | Recent Sharpe | PF | Uscite |
|---|---:|---:|---:|---:|---:|---:|
| rsi62_trail8_mom-6_vol20 | 50.83% | -33.99% | 1.289 | 0.525 | 6.660 | 7 |
| rsi60_trail8_mom-6_vol20 | 49.44% | -32.90% | 1.287 | 0.484 | 6.391 | 8 |
| rsi65_trail8_mom-6_vol20 | 50.26% | -33.99% | 1.272 | 0.525 | 6.554 | 7 |
| rsi65_trail8_mom-5_vol20 | 51.41% | -40.69% | 1.265 | 0.428 | 6.747 | 5 |
| rsi65_trail8_mom-5_vol10 | 50.64% | -40.69% | 1.262 | 0.430 | 6.397 | 9 |
| rsi62_trail8_mom-5_vol20 | 48.97% | -40.69% | 1.254 | 0.428 | 6.003 | 6 |
| rsi62_trail8_mom-5_vol10 | 48.22% | -40.69% | 1.251 | 0.430 | 5.686 | 10 |
| rsi60_trail8_mom-5_vol20 | 47.60% | -39.71% | 1.251 | 0.378 | 5.781 | 7 |
| rsi62_trail8_mom-6_vol10 | 47.91% | -33.99% | 1.249 | 0.528 | 5.622 | 11 |
| rsi65_trail8_mom-6_vol30 | 50.58% | -40.69% | 1.249 | 0.385 | 6.696 | 5 |
| rsi65_trail8_mom-5_vol30 | 50.58% | -40.69% | 1.249 | 0.385 | 6.696 | 5 |
| rsi62_trail8_mom-6_vol30 | 48.16% | -40.69% | 1.238 | 0.385 | 5.952 | 6 |

## Top Per Robustezza

| Variante | Ann. | Max DD | Sharpe | Median Period Sharpe | Min Period Sharpe | Recent Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| rsi62_trail8_mom-6_vol20 | 50.83% | -33.99% | 1.289 | 1.136 | 0.596 | 0.525 |
| rsi60_trail8_mom-6_vol20 | 49.44% | -32.90% | 1.287 | 1.162 | 0.549 | 0.484 |
| rsi65_trail8_mom-6_vol20 | 50.26% | -33.99% | 1.272 | 1.136 | 0.596 | 0.525 |
| rsi62_trail8_mom-6_vol10 | 47.91% | -33.99% | 1.249 | 1.084 | 0.598 | 0.528 |
| rsi65_trail8_mom-6_vol10 | 47.34% | -33.99% | 1.232 | 1.084 | 0.598 | 0.528 |
| rsi65_trail8_mom-5_vol20 | 51.41% | -40.69% | 1.265 | 1.136 | 0.485 | 0.428 |
| rsi65_trail8_mom-5_vol10 | 50.64% | -40.69% | 1.262 | 1.137 | 0.488 | 0.430 |
| rsi60_trail8_mom-6_vol10 | 44.54% | -32.90% | 1.229 | 1.089 | 0.552 | 0.487 |
| rsi62_trail8_mom-5_vol20 | 48.97% | -40.69% | 1.254 | 1.136 | 0.485 | 0.428 |
| rsi62_trail8_mom-5_vol10 | 48.22% | -40.69% | 1.251 | 1.137 | 0.488 | 0.430 |
| rsi60_trail8_mom-5_vol20 | 47.60% | -39.71% | 1.251 | 1.162 | 0.429 | 0.378 |
| rsi65_trail8_mom-6_vol30 | 50.58% | -40.69% | 1.249 | 1.136 | 0.437 | 0.385 |

## Zona Intorno Al Candidato

| RSI | Mom | Vol | Ann. | Max DD | Sharpe | Recent Sharpe |
|---:|---:|---:|---:|---:|---:|---:|
| 62 | -6.00% | 10.00% | 47.91% | -33.99% | 1.249 | 0.528 |
| 62 | -6.00% | 20.00% | 50.83% | -33.99% | 1.289 | 0.525 |
| 62 | -6.00% | 30.00% | 48.16% | -40.69% | 1.238 | 0.385 |
| 62 | -5.00% | 10.00% | 48.22% | -40.69% | 1.251 | 0.430 |
| 62 | -5.00% | 20.00% | 48.97% | -40.69% | 1.254 | 0.428 |
| 62 | -5.00% | 30.00% | 48.16% | -40.69% | 1.238 | 0.385 |
| 62 | -4.00% | 10.00% | 45.39% | -47.17% | 1.183 | 0.324 |
| 62 | -4.00% | 20.00% | 46.99% | -47.17% | 1.204 | 0.322 |
| 62 | -4.00% | 30.00% | 46.19% | -47.17% | 1.188 | 0.283 |
| 65 | -6.00% | 10.00% | 47.34% | -33.99% | 1.232 | 0.528 |
| 65 | -6.00% | 20.00% | 50.26% | -33.99% | 1.272 | 0.525 |
| 65 | -6.00% | 30.00% | 50.58% | -40.69% | 1.249 | 0.385 |
| 65 | -5.00% | 10.00% | 50.64% | -40.69% | 1.262 | 0.430 |
| 65 | -5.00% | 20.00% | 51.41% | -40.69% | 1.265 | 0.428 |
| 65 | -5.00% | 30.00% | 50.58% | -40.69% | 1.249 | 0.385 |
| 65 | -4.00% | 10.00% | 47.77% | -47.17% | 1.196 | 0.324 |
| 65 | -4.00% | 20.00% | 49.39% | -47.17% | 1.217 | 0.322 |
| 65 | -4.00% | 30.00% | 48.58% | -47.17% | 1.202 | 0.283 |
| 68 | -6.00% | 10.00% | 39.62% | -45.09% | 1.044 | 0.528 |
| 68 | -6.00% | 20.00% | 40.91% | -45.09% | 1.065 | 0.525 |
| 68 | -6.00% | 30.00% | 41.21% | -45.09% | 1.051 | 0.385 |
| 68 | -5.00% | 10.00% | 42.74% | -45.09% | 1.080 | 0.430 |
| 68 | -5.00% | 20.00% | 41.98% | -45.09% | 1.066 | 0.428 |
| 68 | -5.00% | 30.00% | 41.21% | -45.09% | 1.051 | 0.385 |
| 68 | -4.00% | 10.00% | 40.02% | -47.17% | 1.023 | 0.324 |
| 68 | -4.00% | 20.00% | 40.09% | -47.17% | 1.024 | 0.322 |
| 68 | -4.00% | 30.00% | 39.33% | -47.17% | 1.010 | 0.283 |

## Walk-Forward

Per ogni split viene scelto il miglior parametro sul solo periodo train e
poi valutato sul periodo test successivo.

| Train | Test | Selezionato | Test Ann. | Test DD | Test Sharpe | Baseline Sharpe | Delta Sharpe |
|---|---|---|---:|---:|---:|---:|---:|
| train_2017_2020 | test_2021_2022 | rsi68_trail8_mom-5_vol10 | 91.73% | -45.09% | 1.392 | 1.213 | 0.179 |
| train_2017_2022 | test_2023_2026 | rsi65_trail8_mom-6_vol30 | 8.83% | -40.69% | 0.437 | 0.322 | 0.115 |
| train_2017_2024 | test_2025_2026 | rsi62_trail8_mom-6_vol20 | 22.99% | -26.08% | 0.857 | 0.857 | 0.000 |

## Lettura

- Baseline: ann. 30.26%, max DD -49.73%, Sharpe 0.828.
- Numero combinazioni nella zona forte: 18.
- Una zona forte richiede Sharpe completo >= 1,15, max DD non peggiore di -45%, e recent Sharpe sopra Baseline.
- Se molte combinazioni vicine superano questi criteri, il candidato e' meno dipendente da un singolo set di parametri.
- Il candidato resta sperimentale finche' non superiamo anche l'audit sul caso inefficiente 2023-04-20.
