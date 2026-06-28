# Combined Entry/Exit Validation

Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.

Test combinato:

- filtro ingresso `RSI <= 65`;
- trailing stop 8% sul massimo Close post-ingresso;
- conferma uscita con momentum 7g >= -5% e volume relativo >= soglia.

Performance misurata in EUR con `Close_EUR`; condizioni tecniche calcolate sulla serie ufficiale.

## Periodo Completo

| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Win rate | Uscite trail |
|---|---:|---:|---:|---:|---:|---:|---:|
| rsi65_trail8_mom_-5_vol_20 | 51.41% | -40.69% | 1.265 | 6.747 | 28 | 39.29% | 5 |
| rsi65_trail8_mom_-5_vol_10 | 50.64% | -40.69% | 1.262 | 6.397 | 30 | 40.00% | 9 |
| trail8_mom_-5_vol_10 | 42.11% | -45.09% | 1.061 | 5.455 | 31 | 35.48% | 9 |
| trail8_mom_-5_vol_20 | 41.36% | -45.09% | 1.047 | 5.565 | 30 | 36.67% | 6 |
| rsi_le_65 | 36.13% | -47.17% | 0.944 | 5.670 | 27 | 40.74% | 0 |
| baseline | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 39.29% | 0 |

## Periodo 2022-Oggi

| Variante | Ann. | Max DD | Sharpe | Esposizione | Turnover |
|---|---:|---:|---:|---:|---:|
| rsi65_trail8_mom_-5_vol_10 | 7.99% | -40.69% | 0.430 | 20.13% | 36 |
| rsi65_trail8_mom_-5_vol_20 | 7.92% | -40.69% | 0.428 | 20.20% | 36 |
| trail8_mom_-5_vol_10 | 6.73% | -43.75% | 0.380 | 22.09% | 38 |
| trail8_mom_-5_vol_20 | 6.66% | -43.75% | 0.378 | 22.15% | 38 |
| rsi_le_65 | 5.28% | -47.17% | 0.325 | 22.27% | 34 |
| baseline | 4.12% | -49.73% | 0.284 | 24.41% | 34 |

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
| trail8_mom_-5_vol_20 | gross_0_00pct | 41.36% | -45.09% | 1.047 | 5.565 |
| trail8_mom_-5_vol_20 | cost_0_10pct | 40.38% | -45.15% | 1.030 | 5.461 |
| trail8_mom_-5_vol_20 | cost_0_25pct | 38.92% | -45.95% | 1.005 | 5.310 |
| trail8_mom_-5_vol_20 | stress_0_50pct | 36.52% | -48.16% | 0.962 | 5.066 |
| rsi65_trail8_mom_-5_vol_20 | gross_0_00pct | 51.41% | -40.69% | 1.265 | 6.747 |
| rsi65_trail8_mom_-5_vol_20 | cost_0_10pct | 50.43% | -41.52% | 1.248 | 6.625 |
| rsi65_trail8_mom_-5_vol_20 | cost_0_25pct | 48.97% | -42.75% | 1.223 | 6.449 |
| rsi65_trail8_mom_-5_vol_20 | stress_0_50pct | 46.56% | -44.82% | 1.180 | 6.163 |

## Sottoperiodi

| Variante | Periodo | Ann. | Max DD | Sharpe |
|---|---|---:|---:|---:|
| baseline | 2017-2020 | 37.58% | -44.30% | 0.988 |
| rsi65_trail8_mom_-5_vol_10 | 2017-2020 | 55.55% | -22.08% | 1.418 |
| rsi65_trail8_mom_-5_vol_20 | 2017-2020 | 57.50% | -22.48% | 1.415 |
| rsi_le_65 | 2017-2020 | 52.86% | -29.21% | 1.311 |
| trail8_mom_-5_vol_10 | 2017-2020 | 58.48% | -22.08% | 1.415 |
| trail8_mom_-5_vol_20 | 2017-2020 | 55.95% | -24.85% | 1.365 |
| baseline | 2021-2022 | 73.75% | -45.09% | 1.213 |
| rsi65_trail8_mom_-5_vol_10 | 2021-2022 | 147.34% | -31.02% | 1.954 |
| rsi65_trail8_mom_-5_vol_20 | 2021-2022 | 148.29% | -31.02% | 1.961 |
| rsi_le_65 | 2021-2022 | 73.75% | -45.09% | 1.213 |
| trail8_mom_-5_vol_10 | 2021-2022 | 91.73% | -45.09% | 1.392 |
| trail8_mom_-5_vol_20 | 2021-2022 | 92.47% | -45.09% | 1.399 |
| baseline | 2023-2026 | 5.34% | -49.73% | 0.322 |
| rsi65_trail8_mom_-5_vol_10 | 2023-2026 | 10.40% | -40.69% | 0.488 |
| rsi65_trail8_mom_-5_vol_20 | 2023-2026 | 10.31% | -40.69% | 0.485 |
| rsi_le_65 | 2023-2026 | 6.85% | -47.17% | 0.368 |
| trail8_mom_-5_vol_10 | 2023-2026 | 8.74% | -43.75% | 0.431 |
| trail8_mom_-5_vol_20 | 2023-2026 | 8.65% | -43.75% | 0.428 |
| baseline | 2025-2026 | 22.99% | -26.08% | 0.857 |
| rsi65_trail8_mom_-5_vol_10 | 2025-2026 | 22.99% | -26.08% | 0.857 |
| rsi65_trail8_mom_-5_vol_20 | 2025-2026 | 22.99% | -26.08% | 0.857 |
| rsi_le_65 | 2025-2026 | 22.99% | -26.08% | 0.857 |
| trail8_mom_-5_vol_10 | 2025-2026 | 22.99% | -26.08% | 0.857 |
| trail8_mom_-5_vol_20 | 2025-2026 | 22.99% | -26.08% | 0.857 |

## Decisione

- Migliore variante del test: `rsi65_trail8_mom_-5_vol_20` con ann. 51.41%, max DD -40.69%, Sharpe 1.265.
- Il miglioramento nasce dall'unione di due effetti diversi: meno ingressi in estensione e uscite protettive confermate.
- Non e' una regola operativa: va validata con walk-forward piu' severo e controllo evento per evento.
- Se supera quei controlli, diventa il primo vero candidato da confrontare contro la Baseline ufficiale.
