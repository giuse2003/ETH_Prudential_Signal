# Exit Candidate Validation

Periodo: `2017-11-11` -> `2026-06-27`.

Candidato uscita: `Trail8 confermato -5 / vol +20`.
Ingressi Baseline invariati. Nessun segnale ufficiale viene modificato.

## Stress Costi

| Scenario | Modello | Ann. | Max DD | Sharpe | PF | Ops | Turnover |
|---|---|---:|---:|---:|---:|---:|---:|
| lordo_0_00pct | Baseline ufficiale | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 56 |
| lordo_0_00pct | Trail8 -5 / vol +20 | 41.36% | -45.09% | 1.047 | 5.565 | 30 | 60 |
| costo_0_10pct | Baseline ufficiale | 29.42% | -50.43% | 0.813 | 4.152 | 28 | 56 |
| costo_0_10pct | Trail8 -5 / vol +20 | 40.38% | -45.15% | 1.030 | 5.461 | 30 | 60 |
| costo_0_25pct | Baseline ufficiale | 28.16% | -51.46% | 0.791 | 4.060 | 28 | 56 |
| costo_0_25pct | Trail8 -5 / vol +20 | 38.92% | -45.95% | 1.005 | 5.310 | 30 | 60 |
| stress_0_50pct | Baseline ufficiale | 26.10% | -53.21% | 0.753 | 3.910 | 28 | 56 |
| stress_0_50pct | Trail8 -5 / vol +20 | 36.52% | -48.16% | 0.962 | 5.066 | 30 | 60 |
| stress_1_00pct | Baseline ufficiale | 22.05% | -56.61% | 0.678 | 3.635 | 28 | 56 |
| stress_1_00pct | Trail8 -5 / vol +20 | 31.83% | -52.41% | 0.877 | 4.631 | 30 | 60 |

## Delta Candidato Meno Baseline

| Scenario | Delta Ann. | Delta DD | Delta Sharpe | Delta PF | Delta Ops |
|---|---:|---:|---:|---:|---:|
| lordo_0_00pct | 11.10% | 4.64% | 0.219 | 1.351 | 2 |
| costo_0_10pct | 10.96% | 5.28% | 0.217 | 1.309 | 2 |
| costo_0_25pct | 10.76% | 5.51% | 0.214 | 1.250 | 2 |
| stress_0_50pct | 10.42% | 5.05% | 0.209 | 1.156 | 2 |
| stress_1_00pct | 9.78% | 4.20% | 0.199 | 0.997 | 2 |

## Validazione Annuale

| Anno | Baseline Ret | Candidato Ret | Delta Ret | Baseline DD | Candidato DD | Delta DD | Baseline Sharpe | Candidato Sharpe |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a |
| 2018 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a |
| 2019 | 60.32% | 60.32% | 0.00% | -19.32% | -19.32% | 0.00% | 1.316 | 1.316 |
| 2020 | 69.85% | 151.72% | 81.87% | -38.20% | -22.08% | 16.12% | 1.205 | 2.057 |
| 2021 | 201.42% | 269.77% | 68.34% | -45.09% | -45.09% | -0.00% | 1.719 | 1.983 |
| 2022 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a |
| 2023 | 0.09% | -0.36% | -0.45% | -22.67% | -23.02% | -0.35% | 0.148 | 0.125 |
| 2024 | -14.58% | -4.40% | 10.17% | -47.85% | -41.64% | 6.21% | -0.230 | 0.016 |
| 2025 | 35.98% | 35.98% | -0.00% | -26.08% | -26.08% | -0.00% | 1.046 | 1.046 |
| 2026 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a |

## Lettura

- Anche nello scenario costi piu' severo, il delta annuo resta 9.78%.
- Anni in cui cambia il rendimento in modo reale: 2020, 2021, 2023, 2024.
- Anni migliorati: 3.
- Anni peggiorati: 1.
- Se il candidato supera costi e anni, il passo successivo e' il test combinato con RSI <= 65.
