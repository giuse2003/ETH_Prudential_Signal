# Chandelier Exit ATR-based Experiment Results

Questi risultati sono frutto di test sperimentali di ricerca e non modificano la strategia ufficiale.
La verifica dello stop avviene esclusivamente sulla chiusura giornaliera (Close).

## Metriche Periodo Completo

| Variante | Ann. Lordo | Max DD Lordo | Sharpe Lordo | Sharpe Netto 0,25% | PF | Operazioni | Mediana Sharpe | Min Sharpe | Periodi Positivi |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 31.77% | -52.57% | 0.849 | 0.812 | 4.327 | 28 | 0.926 | 0.235 | 4/4 |
| trail_dynamic_15_8 | 54.04% | -56.50% | 1.143 | 1.120 | 10.306 | 19 | 1.100 | 0.594 | 4/4 |
| chandelier_exit_period_20_mult_3_5 | 33.64% | -65.72% | 0.881 | 0.854 | 4.497 | 20 | 0.831 | -0.107 | 3/4 |
| chandelier_exit_period_20_mult_3_0 | 31.33% | -63.46% | 0.853 | 0.820 | 3.820 | 24 | 0.722 | -0.318 | 3/4 |
| chandelier_exit_period_14_mult_3_5 | 31.86% | -67.10% | 0.842 | 0.815 | 5.258 | 21 | 0.750 | -0.300 | 3/4 |
| chandelier_exit_period_14_mult_3_0 | 28.30% | -69.80% | 0.795 | 0.761 | 3.421 | 25 | 0.671 | -0.486 | 3/4 |
| chandelier_exit_period_20_mult_2_5 | 25.86% | -62.45% | 0.765 | 0.718 | 2.695 | 33 | 0.205 | -0.492 | 2/4 |
| chandelier_exit_period_20_mult_2_0 | 25.42% | -51.57% | 0.778 | 0.717 | 2.331 | 41 | 0.253 | -0.188 | 2/4 |
| chandelier_exit_period_14_mult_2_0 | 25.04% | -54.26% | 0.767 | 0.708 | 2.417 | 40 | 0.260 | -0.185 | 2/4 |
| chandelier_exit_period_14_mult_2_5 | 24.44% | -64.68% | 0.735 | 0.690 | 2.613 | 32 | 0.169 | -0.511 | 2/4 |

## Dettaglio Sottoperiodi: Sharpe Ratio

| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |
|---|---:|---:|---:|---:|
| baseline | 1.064 | 1.163 | 0.235 | 0.788 |
| trail_dynamic_15_8 | 1.288 | 1.573 | 0.594 | 0.912 |
| chandelier_exit_period_20_mult_3_5 | 1.335 | 1.396 | -0.107 | 0.328 |
| chandelier_exit_period_20_mult_3_0 | 1.335 | 1.447 | -0.318 | 0.110 |
| chandelier_exit_period_14_mult_3_5 | 1.205 | 1.580 | -0.300 | 0.296 |
| chandelier_exit_period_14_mult_3_0 | 1.335 | 1.435 | -0.486 | 0.006 |
| chandelier_exit_period_20_mult_2_5 | 0.830 | 1.752 | -0.421 | -0.492 |
| chandelier_exit_period_20_mult_2_0 | 0.643 | 1.725 | -0.188 | -0.136 |
| chandelier_exit_period_14_mult_2_0 | 0.657 | 1.674 | -0.185 | -0.136 |
| chandelier_exit_period_14_mult_2_5 | 0.830 | 1.751 | -0.511 | -0.492 |

## Dettaglio Sottoperiodi: Max Drawdown

| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |
|---|---:|---:|---:|---:|
| baseline | -41.93% | -45.07% | -54.21% | -26.72% |
| trail_dynamic_15_8 | -40.85% | -56.50% | -42.35% | -25.11% |
| chandelier_exit_period_20_mult_3_5 | -36.89% | -41.12% | -66.74% | -26.72% |
| chandelier_exit_period_20_mult_3_0 | -36.89% | -41.12% | -64.54% | -37.00% |
| chandelier_exit_period_14_mult_3_5 | -36.89% | -41.12% | -67.56% | -26.73% |
| chandelier_exit_period_14_mult_3_0 | -36.89% | -41.12% | -70.84% | -37.00% |
| chandelier_exit_period_20_mult_2_5 | -53.03% | -30.35% | -64.55% | -43.18% |
| chandelier_exit_period_20_mult_2_0 | -41.74% | -31.70% | -53.24% | -39.28% |
| chandelier_exit_period_14_mult_2_0 | -41.88% | -34.00% | -55.83% | -39.28% |
| chandelier_exit_period_14_mult_2_5 | -53.03% | -34.55% | -66.65% | -43.18% |

## Risultati Walk-Forward

| Split | Periodo Train | Periodo Test | Variante Selezionata | Sharpe Train Netto | Ann. Test Netto | Max DD Test Netto | Sharpe Test Netto |
|---|---|---|---|---:|---:|---:|---:|
| 1 | 2017-11-11 -> 2020-12-31 | 2021-01-01 -> 2022-12-31 | chandelier_exit_period_14_mult_3_0 | 1.335 | 99.65% | -41.12% | 1.435 |
| 2 | 2017-11-11 -> 2022-12-31 | 2023-01-01 -> 2024-12-31 | chandelier_exit_period_20_mult_3_0 | 1.359 | -23.08% | -56.83% | -0.601 |
| 3 | 2017-11-11 -> 2024-12-31 | 2025-01-01 -> 2026-06-26 | chandelier_exit_period_20_mult_3_5 | 0.940 | 5.75% | -26.72% | 0.328 |

## Analisi degli Eventi di Uscita

| Variante | Uscite Tentate | Uscite Effettive | Di cui Utili | Di cui Inutili | Win Rate Uscite |
|---|---:|---:|---:|---:|---:|
| baseline | 0 | 0 | 0 | 0 | n/a |
| trail_dynamic_15_8 | 19 | 19 | 14 | 5 | 73.68% |
| chandelier_exit_period_20_mult_3_5 | 20 | 20 | 9 | 11 | 45.00% |
| chandelier_exit_period_20_mult_3_0 | 24 | 24 | 11 | 13 | 45.83% |
| chandelier_exit_period_14_mult_3_5 | 21 | 21 | 8 | 13 | 38.10% |
| chandelier_exit_period_14_mult_3_0 | 25 | 25 | 11 | 14 | 44.00% |
| chandelier_exit_period_20_mult_2_5 | 33 | 33 | 12 | 21 | 36.36% |
| chandelier_exit_period_20_mult_2_0 | 41 | 41 | 16 | 25 | 39.02% |
| chandelier_exit_period_14_mult_2_0 | 40 | 40 | 16 | 24 | 40.00% |
| chandelier_exit_period_14_mult_2_5 | 32 | 32 | 11 | 21 | 34.38% |

## Conclusioni

### Criteri di Accettazione:
1. Sharpe Netto 0.25% **>= 1.050** (rispetto a 0.812 della baseline).
2. Max Drawdown Netto **<= -52.57%** (non peggiora la baseline).
3. Numero operazioni **<= 35**.
4. Funzionalità positiva (Sharpe > 0) in almeno **3 sottoperiodi su 4**.
5. Walk-Forward: Sharpe positivo in almeno **2 split su 3**.

La variante migliore della griglia per Sharpe Netto è **chandelier_exit_period_20_mult_3_5**:
- **Sharpe Netto 0.25%**: `0.854` (Target: >= 1.050)
- **Max Drawdown Netto 0.25%**: `-66.74%` (Target: <= -52.57%)
- **Operazioni**: `20` (Target: <= 35)
- **Sottoperiodi Positivi**: `3/4` (Target: >= 3/4)
- **Split Walk-Forward Positivi**: `2/3` (Target: >= 2/3)

⚠️ **La variante non soddisfa pienamente tutti i criteri per i seguenti motivi**: drawdown netto peggiore della baseline (-66.74% > -52.57%), Sharpe netto insufficiente (0.854 < 1.050).