# RSI Entry Filter Validation

Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.

Performance misurata in EUR con `Close_EUR`; segnali e indicatori restano quelli ufficiali.

## Risultato Chiave

- Baseline periodo completo: ann. 30.26%, max DD -49.73%, Sharpe 0.828.
- `RSI <= 65` periodo completo: ann. 36.13%, max DD -47.17%, Sharpe 0.944.
- Baseline 2022-oggi: ann. 4.12%, max DD -49.73%, Sharpe 0.284.
- `RSI <= 65` 2022-oggi: ann. 5.28%, max DD -47.17%, Sharpe 0.325.

## Threshold Sweep - Periodo Completo

| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Win rate |
|---|---:|---:|---:|---:|---:|---:|
| rsi_le_65 | 36.13% | -47.17% | 0.944 | 5.670 | 27 | 40.74% |
| rsi_le_62 | 35.89% | -47.17% | 0.943 | 5.652 | 27 | 40.74% |
| rsi_le_68 | 35.41% | -47.17% | 0.931 | 5.428 | 27 | 40.74% |
| rsi_le_60 | 34.93% | -46.29% | 0.930 | 5.708 | 27 | 37.04% |
| rsi_le_70 | 34.27% | -50.88% | 0.909 | 5.092 | 27 | 40.74% |
| rsi_le_58 | 30.78% | -45.09% | 0.880 | 5.591 | 25 | 36.00% |
| baseline | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 39.29% |
| rsi_le_72 | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 39.29% |
| rsi_le_75 | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 39.29% |

## Threshold Sweep - 2022-Oggi

| Variante | Ann. | Max DD | Sharpe | Esposizione | Turnover |
|---|---:|---:|---:|---:|---:|
| rsi_le_58 | 6.44% | -42.27% | 0.375 | 17.39% | 30 |
| rsi_le_62 | 5.28% | -47.17% | 0.325 | 22.27% | 34 |
| rsi_le_68 | 5.28% | -47.17% | 0.325 | 22.27% | 34 |
| rsi_le_65 | 5.28% | -47.17% | 0.325 | 22.27% | 34 |
| baseline | 4.12% | -49.73% | 0.284 | 24.41% | 34 |
| rsi_le_72 | 4.12% | -49.73% | 0.284 | 24.41% | 34 |
| rsi_le_75 | 4.12% | -49.73% | 0.284 | 24.41% | 34 |
| rsi_le_60 | 4.10% | -46.29% | 0.284 | 20.56% | 34 |
| rsi_le_70 | 3.59% | -50.88% | 0.266 | 24.28% | 34 |

## Costi Operativi - Periodo Completo

| Variante | Scenario | Ann. | Max DD | Sharpe | PF |
|---|---|---:|---:|---:|---:|
| baseline | gross_0_00pct | 30.26% | -49.73% | 0.828 | 4.215 |
| baseline | cost_0_10pct | 29.42% | -50.43% | 0.813 | 4.152 |
| baseline | cost_0_25pct | 28.16% | -51.46% | 0.791 | 4.060 |
| baseline | stress_0_50pct | 26.10% | -53.21% | 0.753 | 3.910 |
| rsi_le_65 | gross_0_00pct | 36.13% | -47.17% | 0.944 | 5.670 |
| rsi_le_65 | cost_0_10pct | 35.28% | -47.91% | 0.929 | 5.566 |
| rsi_le_65 | cost_0_25pct | 34.02% | -49.00% | 0.907 | 5.416 |
| rsi_le_65 | stress_0_50pct | 31.93% | -50.85% | 0.870 | 5.171 |

## Anni - Baseline vs RSI <= 65

| Anno | Variante | Return | Max DD | Sharpe | Esposizione |
|---:|---|---:|---:|---:|---:|
| 2017 | baseline | 0.00% | 0.00% | n/a | 0.00% |
| 2018 | baseline | 0.00% | 0.00% | n/a | 0.00% |
| 2019 | baseline | 60.32% | -19.32% | 1.316 | 21.92% |
| 2020 | baseline | 69.85% | -38.20% | 1.205 | 52.73% |
| 2021 | baseline | 201.42% | -45.09% | 1.719 | 63.84% |
| 2022 | baseline | 0.00% | 0.00% | n/a | 0.00% |
| 2023 | baseline | 0.09% | -22.67% | 0.148 | 45.21% |
| 2024 | baseline | -14.58% | -47.85% | -0.230 | 39.62% |
| 2025 | baseline | 35.98% | -26.08% | 1.046 | 24.66% |
| 2026 | baseline | 0.00% | 0.00% | n/a | 0.00% |
| 2017 | rsi_le_65 | 0.00% | 0.00% | n/a | 0.00% |
| 2018 | rsi_le_65 | 0.00% | 0.00% | n/a | 0.00% |
| 2019 | rsi_le_65 | 60.32% | -19.32% | 1.316 | 21.92% |
| 2020 | rsi_le_65 | 136.42% | -29.21% | 1.930 | 45.90% |
| 2021 | rsi_le_65 | 201.42% | -45.09% | 1.719 | 63.84% |
| 2022 | rsi_le_65 | 0.00% | 0.00% | n/a | 0.00% |
| 2023 | rsi_le_65 | 0.09% | -22.67% | 0.148 | 45.21% |
| 2024 | rsi_le_65 | -10.22% | -45.19% | -0.130 | 30.05% |
| 2025 | rsi_le_65 | 35.98% | -26.08% | 1.046 | 24.66% |
| 2026 | rsi_le_65 | 0.00% | 0.00% | n/a | 0.00% |

## Impatto Sui Migliori Trade Baseline Dal 2022

| Entry Baseline | Return Baseline | RSI ingresso | Presente in RSI <= 65? |
|---|---:|---:|---|
| 2025-07-07 | 62.70% | 53.3 | si |
| 2024-02-06 | 38.55% | 54.0 | si |
| 2023-11-22 | 8.84% | 61.4 | si |
| 2023-03-13 | 7.30% | 59.6 | si |
| 2024-01-31 | 0.28% | 45.2 | si |
| 2025-01-07 | -1.36% | 44.4 | si |
| 2025-07-02 | -1.94% | 56.1 | si |
| 2023-06-21 | -2.59% | 60.9 | si |

## Decisione

- `RSI <= 65` e' una soglia interessante ma non ancora promossa.
- La zona 62-68 produce risultati simili sul periodo completo: questo riduce il rischio che 65 sia un numero puramente casuale.
- Il filtro migliora Sharpe e drawdown sul periodo completo e sul 2022-oggi, ma va ancora validato con walk-forward e congiunto alle uscite protettive.
- Prossimo controllo: confrontare `RSI <= 65` con il candidato trailing 8% momentum/volume, e poi testare la combinazione solo in ambiente sperimentale.
