# Valore storico del Trail8

Data test: `2026-08-22`.
Periodo: `2016-12-08` -> `2026-08-21`.

Confronto tra la Baseline ufficiale e la stessa strategia con il trailing
disattivato. Ingressi e uscita `Close < SMA50 * 0,98` restano identici.

## Metriche

| Costi | Modello | Totale | Annualizzato | Max DD | Sharpe | PF | Trade | Win rate | Esposizione |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| taker_0_16pct | Trail8 ufficiale | 73718.82% | 97.46% | -39.87% | 1.665 | 15.995 | 30 | 50.00% | 26.78% |
| taker_0_16pct | Senza trailing | 53714.46% | 91.13% | -48.92% | 1.451 | 18.313 | 24 | 58.33% | 31.60% |
| prudenziale_0_60pct | Trail8 ufficiale | 56672.64% | 92.19% | -43.00% | 1.609 | 14.944 | 30 | 50.00% | 26.78% |
| prudenziale_0_60pct | Senza trailing | 43534.98% | 87.05% | -51.15% | 1.412 | 17.273 | 24 | 58.33% | 31.60% |

## Sequenze modificate

Ogni riga confronta i due modelli dalla stessa entrata fino all'uscita
che sarebbe avvenuta senza trailing. I rendimenti includono la sequenza
completa di eventuali uscite e rientri Trail8, con costo taker `0,16%`.

| Entrata comune | Fine confronto | Uscite Trail8 | Con Trail8 | Senza Trail8 | Delta | Esito |
|---|---|---|---:|---:|---:|---|
| 2017-03-18 | 2017-07-07 | 2017-06-21 | 864.58% | 615.20% | 249.38% | migliora |
| 2017-08-05 | 2017-09-13 | 2017-09-04 | 25.42% | 9.13% | 16.29% | migliora |
| 2017-11-08 | 2018-02-02 | 2017-12-06 | 40.02% | 195.26% | -155.24% | peggiora |
| 2019-04-23 | 2019-07-11 | 2019-04-25 | 44.81% | 57.41% | -12.59% | peggiora |
| 2020-05-28 | 2020-09-05 | 2020-09-03 | 73.13% | 51.60% | 21.53% | migliora |
| 2020-10-09 | 2021-02-26 | 2020-12-23, 2021-02-22 | 313.76% | 294.29% | 19.47% | migliora |
| 2021-03-29 | 2021-05-19 | 2021-05-16 | 96.85% | 34.17% | 62.68% | migliora |
| 2021-07-26 | 2021-09-20 | 2021-09-08 | 56.59% | 33.16% | 23.44% | migliora |
| 2021-10-06 | 2021-11-26 | 2021-11-16 | 8.94% | 12.72% | -3.78% | peggiora |
| 2023-03-12 | 2023-05-10 | 2023-04-21 | 6.47% | 15.35% | -8.88% | peggiora |
| 2023-06-20 | 2023-08-04 | 2023-08-02 | 2.25% | 1.60% | 0.65% | migliora |
| 2024-02-06 | 2024-04-02 | 2024-03-20 | 47.78% | 37.82% | 9.96% | migliora |
| 2024-05-29 | 2024-06-24 | 2024-06-11 | -11.85% | -11.22% | -0.62% | peggiora |
| 2024-12-09 | 2024-12-22 | 2024-12-18 | -2.71% | -12.00% | 9.29% | migliora |
| 2025-07-02 | 2025-09-22 | 2025-08-19 | 51.24% | 62.93% | -11.68% | peggiora |

## Conclusione

- Sequenze migliorate: `9`; peggiorate: `6`.
- Trail8 aumenta rendimento annualizzato e Sharpe e riduce nettamente il max drawdown.
- Il profit factor e il win rate sono piu alti senza trailing, perche Trail8 divide alcuni trade.
- Le principali uscite premature sono dicembre 2017 e agosto 2025.
- Nel complesso Trail8 resta valido, ma non elimina il problema dei falsi stop.
