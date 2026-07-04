# SMA50 Trend Filter Robustness

Verifica aggiuntiva del candidato: rimuovere `SMA50 > SMA200` dagli ingressi.

## Currency Check

| Valuta | Variante | Ann. | Max DD | Sharpe | PF | Ann. con costi 0,25% |
|---|---|---:|---:|---:|---:|---:|
| EUR | baseline | 50.95% | -41.10% | 1.216 | 7.400 | 48.27% |
| EUR | no_sma50_gt_sma200_entry | 56.07% | -41.10% | 1.247 | 7.335 | 53.11% |
| USD | baseline | 51.81% | -40.97% | 1.217 | 7.117 | 49.12% |
| USD | no_sma50_gt_sma200_entry | 57.34% | -40.97% | 1.255 | 7.089 | 54.36% |

## Finestre Storiche

| Finestra | Delta Total | Delta Ann. | Delta DD | Delta Sharpe |
|---|---:|---:|---:|---:|
| 2018-2019 | -27.15% | -14.95% | -16.53% | -0.376 |
| 2020-2021 | 238.68% | 37.67% | 0.00% | 0.129 |
| 2022-2023 | 8.23% | 4.05% | -0.03% | 0.196 |
| 2024-2026 | 30.39% | 7.72% | 6.17% | 0.105 |
| recent_2022_today | 50.51% | 5.93% | 4.44% | 0.125 |

## Rolling Windows

- Finestre rolling 730 giorni: 25.
- Delta rendimento positivo: 92.0%.
- Delta Sharpe positivo: 68.0%.
- Peggior delta rendimento rolling: -8.52%.
- Miglior delta rendimento rolling: 283.49%.

## Trade Sbloccati

- Trade aperti quando la Baseline avrebbe bloccato `SMA50 <= SMA200`: 7.
- Rendimento medio di questi trade: 11.55%.
- Win rate di questi trade: 57.14%.

| Entry | Exit | Return | DD trade | RSI | Mom 7g | Volume rel |
|---|---|---:|---:|---:|---:|---:|
| 2019-04-11 | 2019-07-11 | 62.52% | -19.32% | 59.51 | 4.71% | 21.33% |
| 2019-09-22 | 2019-09-24 | -20.49% | -20.49% | 63.28 | 11.46% | 7.30% |
| 2020-04-19 | 2020-06-27 | 18.91% | -13.77% | 61.43 | 12.70% | 19.12% |
| 2023-02-02 | 2023-03-03 | -2.15% | -9.86% | 63.08 | 2.50% | 22.36% |
| 2023-11-14 | 2024-01-22 | 16.76% | -10.94% | 61.60 | 4.82% | 36.79% |
| 2024-11-14 | 2024-12-21 | 10.12% | -15.61% | 60.73 | 5.64% | 24.70% |
| 2025-06-09 | 2025-06-13 | -4.83% | -9.21% | 61.78 | 2.85% | 3.44% |

## Promotion Gate

| Criterio | Esito | Valore |
|---|---:|---:|
| Rendimento annuo completo migliora | PASS | 5.12% |
| Sharpe completo migliora | PASS | 0.031 |
| Stress costi 0,25% resta positivo | PASS | 4.84% |
| Finestre rolling positive almeno 60% | PASS | 92.0% |
| Nessuna finestra peggiora DD oltre 10 punti | FAIL | peggiore -16.53% |
| Nessuna finestra perde oltre 20 punti di rendimento | FAIL | peggiore -27.15% |

## Lettura

- Delta annualizzato EUR completo: 5.12%.
- Gate superati: 4/6.
- Il candidato resta interessante se vince sui costi e su abbastanza finestre rolling.
- Non va promosso se il miglioramento dipende da pochi ingressi e peggiora troppo una finestra storica.
