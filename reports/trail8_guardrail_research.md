# Trail8 - Ricerca di un guardrail selettivo

Data test: `2026-08-22`.
Periodo: `2016-12-08` -> `2026-08-21`.
Mercato: `ETH-USD` Coinbase, candele daily UTC chiuse.

Test sperimentale: nessuna regola ufficiale e' stata modificata. Gli ingressi
e l'uscita `Close < SMA50 * 0,98` restano identici. Varia soltanto il
meccanismo di conferma del Trail8 o, nei test indicati, la sua ampiezza.

## Punto di partenza

Il Trail8 modifica 15 sequenze rispetto alla stessa strategia senza trailing:
9 migliorano e 6 peggiorano. L'obiettivo e' recuperare le sei sequenze
peggiorative senza perdere la protezione delle altre nove.

## Caratteristiche delle uscite ufficiali

| Gruppo | Eventi | DD dal picco | Momentum 7g | Volume rel. | Close/SMA50 | Slope SMA50 5g | ATR/Close |
|---|---:|---:|---:|---:|---:|---:|---:|
| FALSE | 6 | -11.53% | -9.26% | 55.28% | 8.25% | 3.18% | 5.66% |
| GOOD | 10 | -13.39% | -5.89% | 80.09% | 17.65% | 6.44% | 8.45% |

## Migliori compromessi nel filtro preliminare

Filtro preliminare: max drawdown non peggiore di 3 punti, Sharpe non
inferiore di oltre 0,03 e non piu di due sequenze protettive danneggiate.
Costi taker `0,16%` per lato.

| Candidato | Ann. | Max DD | Sharpe | PF | Trade | False migliorati | False recuperati | Protettivi danneggiati |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Trail8 ufficiale | 97.46% | -39.87% | 1.665 | 15.995 | 30 | 0/6 | 0/6 | 0/9 |
| Combo Trail11 slope<=4.00% ext>=5% | 110.82% | -39.45% | 1.748 | 20.843 | 27 | 4/6 | 3/6 | 1/9 |
| Combo Trail11 slope<=4.00% ext>=8% | 111.80% | -39.45% | 1.745 | 24.726 | 25 | 5/6 | 4/6 | 2/9 |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 111.67% | -43.53% | 1.739 | 24.073 | 25 | 6/6 | 5/6 | 2/9 |
| Trail11% se slope5 <= 4% | 108.75% | -39.45% | 1.730 | 18.959 | 28 | 3/6 | 2/6 | 1/9 |
| Trail solo estensione >= 5% | 101.16% | -39.45% | 1.700 | 19.833 | 27 | 3/6 | 3/6 | 1/9 |
| Trail12 | 107.85% | -42.96% | 1.714 | 18.970 | 27 | 3/6 | 2/6 | 3/9 |
| Senza trailing | 91.13% | -48.92% | 1.451 | 18.313 | 24 | 6/6 | 6/6 | 9/9 |

## Robustezza dei candidati selezionati

| Candidato | Finestre 2 anni | Rendimento migliore | Sharpe migliore | DD migliore | Peggior delta rendimento |
|---|---:|---:|---:|---:|---:|
| Trail8 ufficiale | 97 | 0.00% | 0.00% | 100.00% | 0.00% |
| Combo Trail11 slope<=4.00% ext>=5% | 97 | 98.97% | 96.91% | 70.10% | 0.00% |
| Combo Trail11 slope<=4.00% ext>=8% | 97 | 90.72% | 75.26% | 52.58% | -17.15% |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 97 | 93.81% | 84.54% | 50.52% | -29.94% |
| Trail11% se slope5 <= 4% | 97 | 83.51% | 71.13% | 63.92% | -1.13% |
| Trail solo estensione >= 5% | 97 | 94.85% | 92.78% | 84.54% | 0.00% |
| Trail12 | 97 | 57.73% | 40.21% | 44.33% | -60.61% |
| Senza trailing | 97 | 40.21% | 30.93% | 15.46% | -1371.89% |

## Sottoperiodi

Metriche ricavate dalla curva completa, cosi lo stato di esposizione
all'inizio di ogni sottoperiodo resta coerente. Costi taker `0,16%`.

| Candidato | Periodo | Totale | Ann. | Max DD | Sharpe |
|---|---|---:|---:|---:|---:|
| Trail8 ufficiale | 2017-2019 | 2103.89% | 180.63% | -30.08% | 2.064 |
| Trail8 ufficiale | 2020-2022 | 2172.69% | 183.26% | -23.39% | 2.193 |
| Trail8 ufficiale | 2023-oggi | 47.38% | 11.25% | -39.87% | 0.513 |
| Combo Trail11 slope<=4.00% ext>=5% | 2017-2019 | 3678.19% | 235.92% | -30.08% | 2.232 |
| Combo Trail11 slope<=4.00% ext>=5% | 2020-2022 | 2208.84% | 184.75% | -23.39% | 2.203 |
| Combo Trail11 slope<=4.00% ext>=5% | 2023-oggi | 59.78% | 13.75% | -39.45% | 0.585 |
| Combo Trail11 slope<=4.00% ext>=8% | 2017-2019 | 3678.19% | 235.92% | -30.08% | 2.232 |
| Combo Trail11 slope<=4.00% ext>=8% | 2020-2022 | 2315.04% | 189.05% | -29.69% | 2.189 |
| Combo Trail11 slope<=4.00% ext>=8% | 2023-oggi | 59.78% | 13.75% | -39.45% | 0.585 |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2017-2019 | 3678.19% | 235.92% | -30.08% | 2.232 |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2020-2022 | 2289.01% | 188.01% | -20.73% | 2.207 |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2023-oggi | 60.52% | 13.89% | -43.53% | 0.570 |

## Audit dei due compromessi

Sono mostrate solo le sequenze che cambiano rispetto al Trail8 ufficiale.
Il confronto termina alla data in cui sarebbe uscita la strategia senza trailing.

| Candidato | Entrata | Fine | Classe Trail8 | Trail8 | Candidato | Senza trail | Delta vs Trail8 |
|---|---|---|---|---:|---:|---:|---:|
| Combo Trail11 slope<=4.00% ext>=5% | 2017-11-08 | 2018-02-02 | FALSE | 40.02% | 120.83% | 195.26% | 80.82% |
| Combo Trail11 slope<=4.00% ext>=5% | 2019-04-23 | 2019-07-11 | FALSE | 44.81% | 57.41% | 57.41% | 12.59% |
| Combo Trail11 slope<=4.00% ext>=5% | 2020-05-28 | 2020-09-05 | GOOD | 73.13% | 75.88% | 51.60% | 2.75% |
| Combo Trail11 slope<=4.00% ext>=5% | 2023-03-12 | 2023-05-10 | FALSE | 6.47% | 15.35% | 15.35% | 8.88% |
| Combo Trail11 slope<=4.00% ext>=5% | 2023-06-20 | 2023-08-04 | GOOD | 2.25% | 1.60% | 1.60% | -0.65% |
| Combo Trail11 slope<=4.00% ext>=5% | 2024-05-29 | 2024-06-24 | FALSE | -11.85% | -11.22% | -11.22% | 0.62% |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2017-11-08 | 2018-02-02 | FALSE | 40.02% | 120.83% | 195.26% | 80.82% |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2019-04-23 | 2019-07-11 | FALSE | 44.81% | 57.41% | 57.41% | 12.59% |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2020-05-28 | 2020-09-05 | GOOD | 73.13% | 75.88% | 51.60% | 2.75% |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2021-10-06 | 2021-11-26 | FALSE | 8.94% | 12.72% | 12.72% | 3.78% |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2023-03-12 | 2023-05-10 | FALSE | 6.47% | 15.35% | 15.35% | 8.88% |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2023-06-20 | 2023-08-04 | GOOD | 2.25% | 1.60% | 1.60% | -0.65% |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2024-02-06 | 2024-04-02 | GOOD | 47.78% | 37.82% | 37.82% | -9.96% |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2024-05-29 | 2024-06-24 | FALSE | -11.85% | -11.22% | -11.22% | 0.62% |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | 2025-07-02 | 2025-09-22 | FALSE | 51.24% | 62.93% | 62.93% | 11.68% |

## Stress costi

| Candidato | Costi | Totale | Ann. | Max DD | Sharpe | PF |
|---|---|---:|---:|---:|---:|---:|
| Trail8 ufficiale | maker_0_07pct | 77780.65% | 98.55% | -39.21% | 1.677 | 16.226 |
| Trail8 ufficiale | taker_0_16pct | 73718.82% | 97.46% | -39.87% | 1.665 | 15.995 |
| Trail8 ufficiale | prudenziale_0_60pct | 56672.64% | 92.19% | -43.00% | 1.609 | 14.944 |
| Trail8 ufficiale | stress_1_00pct | 44572.67% | 87.50% | -45.71% | 1.557 | 14.089 |
| Combo Trail11 slope<=4.00% ext>=5% | maker_0_07pct | 146150.75% | 111.87% | -38.89% | 1.758 | 21.141 |
| Combo Trail11 slope<=4.00% ext>=5% | taker_0_16pct | 139282.91% | 110.82% | -39.45% | 1.748 | 20.843 |
| Combo Trail11 slope<=4.00% ext>=5% | prudenziale_0_60pct | 110007.89% | 105.76% | -42.09% | 1.700 | 19.491 |
| Combo Trail11 slope<=4.00% ext>=5% | stress_1_00pct | 88686.21% | 101.25% | -44.39% | 1.655 | 18.390 |
| Combo Trail11 slope<=4.00% ext>=8% | maker_0_07pct | 152333.53% | 112.78% | -38.89% | 1.754 | 25.077 |
| Combo Trail11 slope<=4.00% ext>=8% | taker_0_16pct | 145693.85% | 111.80% | -39.45% | 1.745 | 24.726 |
| Combo Trail11 slope<=4.00% ext>=8% | prudenziale_0_60pct | 117101.35% | 107.09% | -42.09% | 1.701 | 23.129 |
| Combo Trail11 slope<=4.00% ext>=8% | stress_1_00pct | 95924.83% | 102.88% | -44.39% | 1.660 | 21.829 |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | maker_0_07pct | 151387.03% | 112.64% | -43.01% | 1.748 | 24.406 |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | taker_0_16pct | 144790.36% | 111.67% | -43.53% | 1.739 | 24.073 |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | prudenziale_0_60pct | 116382.09% | 106.96% | -45.99% | 1.695 | 22.552 |
| Combo Trail11 slope<=4% ext>=5% momentum>=-10% | stress_1_00pct | 95340.83% | 102.76% | -48.14% | 1.654 | 21.311 |
| Trail11% se slope5 <= 4% | maker_0_07pct | 133022.73% | 109.83% | -38.89% | 1.740 | 19.227 |
| Trail11% se slope5 <= 4% | taker_0_16pct | 126537.19% | 108.75% | -39.45% | 1.730 | 18.959 |
| Trail11% se slope5 <= 4% | prudenziale_0_60pct | 99037.26% | 103.55% | -42.09% | 1.679 | 17.739 |
| Trail11% se slope5 <= 4% | stress_1_00pct | 79181.66% | 98.92% | -44.39% | 1.633 | 16.745 |
| Trail solo estensione >= 5% | maker_0_07pct | 92629.89% | 102.15% | -38.89% | 1.710 | 20.117 |
| Trail solo estensione >= 5% | taker_0_16pct | 88275.36% | 101.16% | -39.45% | 1.700 | 19.833 |
| Trail solo estensione >= 5% | prudenziale_0_60pct | 69713.61% | 96.33% | -42.09% | 1.650 | 18.543 |
| Trail solo estensione >= 5% | stress_1_00pct | 56194.66% | 92.02% | -44.39% | 1.604 | 17.493 |
| Trail12 | maker_0_07pct | 127328.53% | 108.88% | -42.44% | 1.724 | 19.221 |
| Trail12 | taker_0_16pct | 121332.21% | 107.85% | -42.96% | 1.714 | 18.970 |
| Trail12 | prudenziale_0_60pct | 95779.47% | 102.85% | -45.45% | 1.666 | 17.823 |
| Trail12 | stress_1_00pct | 77177.60% | 98.39% | -47.62% | 1.621 | 16.881 |
| Senza trailing | maker_0_07pct | 56066.42% | 91.98% | -48.46% | 1.459 | 18.540 |
| Senza trailing | taker_0_16pct | 53714.46% | 91.13% | -48.92% | 1.451 | 18.313 |
| Senza trailing | prudenziale_0_60pct | 43534.98% | 87.05% | -51.15% | 1.412 | 17.273 |
| Senza trailing | stress_1_00pct | 35933.13% | 83.40% | -53.09% | 1.376 | 16.412 |

## Conclusione

- Regole testate: `274`.
- Candidati che recuperano tutti i 6 falsi stop senza danneggiare nessuna delle 9 uscite protettive: `0`.
- Il candidato che migliora tutte e 6 le sequenze e' `Combo Trail11 slope<=4% ext>=5% momentum>=-10%`, ma danneggia `2` uscite protettive e porta il max DD a `-43.53%`.
- Il compromesso prudente e' `Combo Trail11 slope<=4.00% ext>=5%`: migliora `4` sequenze su 6, ne recupera completamente `3` e danneggia una sola sequenza protettiva per 0,65 punti.
- Nel periodo completo il compromesso prudente passa da `97.46%` a `110.82%` annualizzato, da Sharpe `1.665` a `1.748` e da max DD `-39.87%` a `-39.45%`.
- L'assenza di separazione perfetta indica che una regola costruita per prendere tutti e sei i casi sarebbe sovra-adattata al campione.
- Il compromesso prudente resta un candidato di ricerca: richiede validazione walk-forward realmente fuori campione prima di qualunque promozione.
- La Baseline resta invariata.
