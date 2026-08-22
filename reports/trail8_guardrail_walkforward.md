# Trail8 Guardrail - Nested Walk-Forward

Data test: `2026-08-22`. Cutoff: `2026-08-21`.
Mercato: `ETH-USD` Coinbase, daily UTC chiuso.
La Baseline ufficiale non e' stata modificata.

## Metodo

- primo anno fuori campione: `2020`;
- per ogni anno, training expanding fino al 31 dicembre precedente;
- un candidato e' eleggibile solo se nel training supera la Baseline in
  annualizzato, max drawdown e Sharpe, completa almeno 5 trade e non
  aggiunge piu di 12 lati di turnover;
- fra gli eleggibili viene scelto il rango medio migliore delle tre metriche;
- al cambio anno l'esposizione viene riallineata e il turnover viene addebitato;
- regole generate: `274`; percorsi di segnale unici: `70`.

`fixed_prudent` e `fixed_aggressive` sono replay temporali, non veri risultati
fuori campione, perche le regole sono state formulate dopo avere visto tutta
la storia. I tre selettori `WF` sono la prova pseudo out-of-sample principale.

## Risultato aggregato 2020-oggi

Commissione taker `0,16%` per lato.

| Modello | Totale | Ann. | Max DD | Sharpe | Trade | Turnover | Delta ann. | Delta DD | Delta Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 3249.48% | 69.64% | -39.87% | 1.460 | 23 | 46.0 | 0.00% | 0.00% | 0.000 |
| Candidato prudente fisso | 3589.14% | 72.13% | -39.45% | 1.490 | 21 | 42.0 | 2.48% | 0.42% | 0.030 |
| Candidato tutte-6 fisso | 3734.91% | 73.13% | -43.53% | 1.476 | 19 | 38.0 | 3.49% | -3.66% | 0.016 |
| WF Baseline/candidato | 3589.14% | 72.13% | -39.45% | 1.490 | 21 | 42.0 | 2.48% | 0.42% | 0.030 |
| WF famiglia prudente | 2631.48% | 64.51% | -42.96% | 1.379 | 22 | 44.0 | -5.13% | -3.09% | -0.081 |
| WF griglia completa | 3060.99% | 68.17% | -48.92% | 1.406 | 19 | 38.0 | -1.47% | -9.05% | -0.054 |

## Selezioni annuali

Tutte le metriche `train` precedono integralmente l'anno di test.

| Policy | Test | Universo | Eleggibili | Scelto | Ann. train | DD train | Sharpe train | Delta return test | Delta DD test | Delta Sharpe test | Esito |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| wf_conservative_family | 2020 | 24 | 19 | `Trail11` | 227.30% | -30.08% | 2.207 | 0.00% | 0.00% | 0.000 | INVARIATO |
| wf_full_grid | 2020 | 70 | 47 | `Trail solo ATR >= 8%` | 227.30% | -30.08% | 2.207 | 51.43% | 0.00% | 0.271 | MIGLIORA |
| wf_pair_gate | 2020 | 2 | 1 | `Combo Trail11 slope<=4.00% ext>=5%` | 227.30% | -30.08% | 2.207 | 4.73% | 0.21% | 0.029 | MIGLIORA |
| wf_conservative_family | 2021 | 24 | 19 | `Trail12` | 232.24% | -30.08% | 2.286 | -100.83% | 0.00% | -0.212 | MISTO |
| wf_full_grid | 2021 | 70 | 47 | `Trail solo ATR >= 8%` | 232.24% | -30.08% | 2.286 | -91.75% | -4.91% | -0.246 | PEGGIORA |
| wf_pair_gate | 2021 | 2 | 1 | `Combo Trail11 slope<=4.00% ext>=5%` | 220.71% | -30.08% | 2.231 | 0.00% | 0.00% | 0.000 | INVARIATO |
| wf_conservative_family | 2022 | 24 | 18 | `Trail13% se slope5 <= 5%` | 294.22% | -30.08% | 2.455 | 0.00% | 0.00% | n/a | INVARIATO |
| wf_full_grid | 2022 | 70 | 45 | `Trail solo slope5 >= 5%` | 294.22% | -30.08% | 2.455 | 0.00% | 0.00% | n/a | INVARIATO |
| wf_pair_gate | 2022 | 2 | 1 | `Combo Trail11 slope<=4.00% ext>=5%` | 280.63% | -30.08% | 2.410 | 0.00% | 0.00% | n/a | INVARIATO |
| wf_conservative_family | 2023 | 24 | 18 | `Trail13% se slope5 <= 5%` | 214.43% | -30.08% | 2.240 | -1.02% | -0.52% | -0.032 | PEGGIORA |
| wf_full_grid | 2023 | 70 | 45 | `Trail solo slope5 >= 5%` | 214.43% | -30.08% | 2.240 | 8.19% | 6.08% | 0.235 | MIGLIORA |
| wf_pair_gate | 2023 | 2 | 1 | `Combo Trail11 slope<=4.00% ext>=5%` | 205.35% | -30.08% | 2.200 | 8.19% | 6.08% | 0.235 | MIGLIORA |
| wf_conservative_family | 2024 | 24 | 18 | `Trail13% se slope5 <= 5%` | 169.58% | -30.08% | 2.057 | -5.33% | -3.17% | -0.147 | PEGGIORA |
| wf_full_grid | 2024 | 70 | 46 | `Trail solo slope5 >= 5%` | 172.78% | -30.08% | 2.076 | -15.60% | -9.29% | -0.429 | PEGGIORA |
| wf_pair_gate | 2024 | 2 | 1 | `Combo Trail11 slope<=4.00% ext>=5%` | 166.00% | -30.08% | 2.039 | 0.73% | 0.44% | 0.021 | MIGLIORA |
| wf_conservative_family | 2025 | 24 | 9 | `Combo Trail11 slope<=3.75% ext>=8%` | 138.11% | -37.84% | 1.877 | 0.00% | 0.00% | 0.000 | INVARIATO |
| wf_full_grid | 2025 | 70 | 12 | `Combo Trail11 slope<=3.75% ext>=8%` | 138.11% | -37.84% | 1.877 | 0.00% | 0.00% | 0.000 | INVARIATO |
| wf_pair_gate | 2025 | 2 | 1 | `Combo Trail11 slope<=4.00% ext>=5%` | 136.79% | -37.84% | 1.880 | 0.00% | 0.00% | 0.000 | INVARIATO |
| wf_conservative_family | 2026 | 24 | 9 | `Combo Trail11 slope<=3.75% ext>=8%` | 123.29% | -39.45% | 1.806 | 0.00% | 0.00% | n/a | INVARIATO |
| wf_full_grid | 2026 | 70 | 12 | `Combo Trail11 slope<=3.75% ext>=8%` | 123.29% | -39.45% | 1.806 | 0.00% | 0.00% | n/a | INVARIATO |
| wf_pair_gate | 2026 | 2 | 1 | `Combo Trail11 slope<=4.00% ext>=5%` | 122.19% | -39.45% | 1.809 | 0.00% | 0.00% | n/a | INVARIATO |

## Esiti annuali

| Modello | Migliora | Invariato | Misto | Peggiora | Anni return migliori | Anni DD migliori | Anni Sharpe migliori |
|---|---:|---:|---:|---:|---:|---:|---:|
| Candidato prudente fisso | 3 | 4 | 0 | 0 | 3 | 3 | 3 |
| Candidato tutte-6 fisso | 4 | 2 | 0 | 1 | 4 | 4 | 4 |
| WF Baseline/candidato | 3 | 4 | 0 | 0 | 3 | 3 | 3 |
| WF famiglia prudente | 0 | 4 | 1 | 2 | 0 | 0 | 0 |
| WF griglia completa | 2 | 3 | 0 | 2 | 2 | 1 | 2 |

## Stress esecuzione e sensibilita temporale

Le selezioni annuali restano congelate; cambiano soltanto costi, ritardo
oppure l'anno iniziale della curva aggregata.

| Scenario | Modello | Ann. | Max DD | Sharpe |
|---|---|---:|---:|---:|
| taker_0_16pct | Baseline | 69.64% | -39.87% | 1.460 |
| taker_0_16pct | Candidato prudente fisso | 72.13% | -39.45% | 1.490 |
| taker_0_16pct | WF Baseline/candidato | 72.13% | -39.45% | 1.490 |
| taker_0_16pct | WF famiglia prudente | 64.51% | -42.96% | 1.379 |
| taker_0_16pct | WF griglia completa | 68.17% | -48.92% | 1.406 |
| maker_0_07pct | Baseline | 70.70% | -39.21% | 1.475 |
| maker_0_07pct | Candidato prudente fisso | 73.10% | -38.89% | 1.503 |
| maker_0_07pct | WF Baseline/candidato | 73.10% | -38.89% | 1.503 |
| maker_0_07pct | WF famiglia prudente | 65.49% | -42.44% | 1.393 |
| maker_0_07pct | WF griglia completa | 69.03% | -48.46% | 1.418 |
| prudenziale_0_60pct | Baseline | 64.55% | -43.00% | 1.388 |
| prudenziale_0_60pct | Candidato prudente fisso | 67.41% | -42.09% | 1.425 |
| prudenziale_0_60pct | WF Baseline/candidato | 67.41% | -42.09% | 1.425 |
| prudenziale_0_60pct | WF famiglia prudente | 59.79% | -45.45% | 1.311 |
| prudenziale_0_60pct | WF griglia completa | 64.00% | -51.15% | 1.349 |
| taker_0_16pct_delay_1d | Baseline | 57.78% | -44.38% | 1.282 |
| taker_0_16pct_delay_1d | Candidato prudente fisso | 54.48% | -44.86% | 1.222 |
| taker_0_16pct_delay_1d | WF Baseline/candidato | 54.48% | -44.86% | 1.222 |
| taker_0_16pct_delay_1d | WF famiglia prudente | 57.02% | -43.95% | 1.268 |
| taker_0_16pct_delay_1d | WF griglia completa | 55.90% | -47.93% | 1.225 |
| taker_0_16pct_start_2021 | Baseline | 53.55% | -39.87% | 1.272 |
| taker_0_16pct_start_2021 | Candidato prudente fisso | 55.77% | -39.45% | 1.303 |
| taker_0_16pct_start_2021 | WF Baseline/candidato | 55.77% | -39.45% | 1.303 |
| taker_0_16pct_start_2021 | WF famiglia prudente | 48.10% | -42.96% | 1.172 |
| taker_0_16pct_start_2021 | WF griglia completa | 47.75% | -48.92% | 1.145 |
| taker_0_16pct_start_2023 | Baseline | 11.24% | -39.87% | 0.513 |
| taker_0_16pct_start_2023 | Candidato prudente fisso | 13.74% | -39.45% | 0.585 |
| taker_0_16pct_start_2023 | WF Baseline/candidato | 13.74% | -39.45% | 0.585 |
| taker_0_16pct_start_2023 | WF famiglia prudente | 9.35% | -42.96% | 0.452 |
| taker_0_16pct_start_2023 | WF griglia completa | 8.54% | -48.92% | 0.422 |

## Bootstrap a blocchi

Bootstrap circolare appaiato sui rendimenti giornalieri fuori campione.
Il vantaggio misura il rapporto tra ricchezza finale del modello e Baseline.

| Modello | Blocco | Prob. sovraperformance | Vantaggio osservato | Mediana | 5% | 95% |
|---|---:|---:|---:|---:|---:|---:|
| Candidato prudente fisso | 30g | 94.35% | 10.14% | 9.19% | 0.00% | 28.13% |
| Candidato tutte-6 fisso | 30g | 83.15% | 14.49% | 13.02% | -8.76% | 46.74% |
| WF Baseline/candidato | 30g | 93.70% | 10.14% | 9.44% | -0.26% | 28.69% |
| WF famiglia prudente | 30g | 2.45% | -18.45% | -16.81% | -35.84% | -1.27% |
| WF griglia completa | 30g | 39.45% | -5.63% | -6.93% | -39.80% | 45.02% |
| Candidato prudente fisso | 90g | 93.85% | 10.14% | 9.32% | -0.32% | 28.07% |
| Candidato tutte-6 fisso | 90g | 83.60% | 14.49% | 14.43% | -7.90% | 45.85% |
| WF Baseline/candidato | 90g | 93.70% | 10.14% | 9.19% | -0.35% | 27.57% |
| WF famiglia prudente | 90g | 1.95% | -18.45% | -16.87% | -35.30% | -1.59% |
| WF griglia completa | 90g | 41.10% | -5.63% | -5.22% | -39.01% | 47.58% |

## Conclusione

- Miglior selettore per Sharpe pseudo out-of-sample: `wf_pair_gate`.
- Metriche: ann. `72.13%`, max DD `-39.45%`, Sharpe `1.490`.
- Rispetto alla Baseline migliora simultaneamente annualizzato, drawdown e Sharpe.
- Bootstrap 30 giorni: probabilita di sovraperformance `93.70%`.
- Il gate a due modelli ha selezionato il candidato prudente in tutti gli anni: `si`.
- Partendo dal 2021 il candidato/gate rende ann. `55.77%` contro `53.55%`; dal 2023 `13.74%` contro `11.24%`.
- Con una candela ulteriore di ritardo il candidato scende a ann. `54.48%`, DD `-44.86%` e Sharpe `1.222`, contro Baseline `57.78%`, `-44.38%`, `1.282`: il vantaggio non sopravvive.
- La selezione su tutta la griglia fallisce: ann. `68.17%`, DD `-48.92%`, Sharpe `1.406`.
- Anche il gate a due modelli resta pseudo out-of-sample: la regola candidata e l'universo sono stati formulati dopo avere osservato l'intera storia.
- Decisione: candidato promettente ma non promosso. Va congelato ora e osservato in paper/shadow mode su candele future realmente mai viste.
- La Baseline resta invariata.
