# Trailing Stop 8% + RSI Adattivo System Results

Questi risultati sono frutto di test sperimentali di ricerca e non modificano la strategia ufficiale.
La verifica dello stop avviene esclusivamente sulla chiusura giornaliera (Close).

## Metriche Periodo Completo

| Variante | Ann. Lordo | Max DD Lordo | Sharpe Lordo | Sharpe Netto 0,25% | PF | Operazioni | Mediana Sharpe | Min Sharpe | Periodi Positivi |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 31.77% | -52.57% | 0.849 | 0.812 | 4.327 | 28 | 0.926 | 0.235 | 4/4 |
| trailing_8_pure | 24.31% | -50.38% | 0.771 | 0.699 | 2.280 | 46 | 0.344 | -0.020 | 3/4 |
| rsi_adaptive_system_rsi_70_stop_8 | 28.75% | -50.38% | 0.860 | 0.794 | 2.529 | 43 | 0.318 | -0.062 | 2/4 |
| rsi_adaptive_system_rsi_75_stop_8 | 27.11% | -50.38% | 0.820 | 0.756 | 2.404 | 42 | 0.302 | -0.062 | 2/4 |
| rsi_adaptive_system_rsi_80_stop_8 | 25.42% | -51.24% | 0.784 | 0.722 | 2.413 | 41 | 0.263 | -0.199 | 2/4 |
| rsi_adaptive_system_rsi_70_stop_10 | 24.30% | -54.01% | 0.762 | 0.698 | 2.271 | 42 | 0.263 | -0.199 | 2/4 |
| rsi_adaptive_system_rsi_75_stop_10 | 23.80% | -54.01% | 0.751 | 0.687 | 2.240 | 42 | 0.247 | -0.199 | 2/4 |
| rsi_adaptive_system_rsi_80_stop_10 | 22.96% | -54.01% | 0.733 | 0.670 | 2.272 | 41 | 0.235 | -0.199 | 2/4 |

## Dettaglio Sottoperiodi: Sharpe Ratio

| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |
|---|---:|---:|---:|---:|
| baseline | 1.064 | 1.163 | 0.235 | 0.788 |
| trailing_8_pure | 0.642 | 1.547 | -0.020 | 0.046 |
| rsi_adaptive_system_rsi_70_stop_8 | 0.698 | 1.819 | -0.062 | -0.061 |
| rsi_adaptive_system_rsi_75_stop_8 | 0.665 | 1.713 | -0.062 | -0.061 |
| rsi_adaptive_system_rsi_80_stop_8 | 0.641 | 1.686 | -0.116 | -0.199 |
| rsi_adaptive_system_rsi_70_stop_10 | 0.698 | 1.614 | -0.171 | -0.199 |
| rsi_adaptive_system_rsi_75_stop_10 | 0.665 | 1.614 | -0.171 | -0.199 |
| rsi_adaptive_system_rsi_80_stop_10 | 0.641 | 1.586 | -0.171 | -0.199 |

## Dettaglio Sottoperiodi: Max Drawdown

| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |
|---|---:|---:|---:|---:|
| baseline | -41.93% | -45.07% | -54.21% | -26.72% |
| trailing_8_pure | -43.22% | -34.20% | -52.33% | -36.92% |
| rsi_adaptive_system_rsi_70_stop_8 | -39.35% | -31.70% | -52.33% | -39.50% |
| rsi_adaptive_system_rsi_75_stop_8 | -40.47% | -31.70% | -52.33% | -39.50% |
| rsi_adaptive_system_rsi_80_stop_8 | -42.02% | -31.70% | -54.19% | -42.85% |
| rsi_adaptive_system_rsi_70_stop_10 | -39.35% | -31.70% | -56.80% | -42.85% |
| rsi_adaptive_system_rsi_75_stop_10 | -40.47% | -31.70% | -56.80% | -42.85% |
| rsi_adaptive_system_rsi_80_stop_10 | -42.02% | -31.70% | -56.80% | -42.85% |

## Risultati Walk-Forward

| Split | Periodo Train | Periodo Test | Variante Selezionata | Sharpe Train Netto | Ann. Test Netto | Max DD Test Netto | Sharpe Test Netto |
|---|---|---|---|---:|---:|---:|---:|
| 1 | 2017-11-11 -> 2020-12-31 | 2021-01-01 -> 2022-12-31 | rsi_adaptive_system_rsi_70_stop_8 | 0.698 | 123.84% | -31.70% | 1.819 |
| 2 | 2017-11-11 -> 2022-12-31 | 2023-01-01 -> 2024-12-31 | rsi_adaptive_system_rsi_70_stop_8 | 1.214 | -6.49% | -47.63% | -0.063 |
| 3 | 2017-11-11 -> 2024-12-31 | 2025-01-01 -> 2026-06-26 | rsi_adaptive_system_rsi_70_stop_8 | 0.922 | -5.06% | -39.50% | -0.061 |

## Analisi degli Eventi di Uscita

| Variante | Uscite Tentate | Uscite Effettive | Di cui Utili | Di cui Inutili | Win Rate Uscite |
|---|---:|---:|---:|---:|---:|
| baseline | 0 | 0 | 0 | 0 | n/a |
| trailing_8_pure | 46 | 46 | 19 | 27 | 41.30% |
| rsi_adaptive_system_rsi_70_stop_8 | 43 | 43 | 17 | 26 | 39.53% |
| rsi_adaptive_system_rsi_75_stop_8 | 42 | 42 | 17 | 25 | 40.48% |
| rsi_adaptive_system_rsi_80_stop_8 | 41 | 41 | 18 | 23 | 43.90% |
| rsi_adaptive_system_rsi_70_stop_10 | 42 | 42 | 16 | 26 | 38.10% |
| rsi_adaptive_system_rsi_75_stop_10 | 42 | 42 | 16 | 26 | 38.10% |
| rsi_adaptive_system_rsi_80_stop_10 | 41 | 41 | 17 | 24 | 41.46% |

## Conclusioni

### Criteri di Accettazione:
1. Sharpe Netto 0.25% **>= 1.050** (rispetto a 0.812 della baseline).
2. Max Drawdown Netto **<= -52.57%** (non peggiora la baseline).
3. Numero operazioni **<= 35**.
4. Funzionalità positiva (Sharpe > 0) in almeno **3 sottoperiodi su 4**.
5. Walk-Forward: Sharpe positivo in almeno **2 split su 3**.

La variante migliore della griglia per Sharpe Netto è **rsi_adaptive_system_rsi_70_stop_8**:
- **Sharpe Netto 0.25%**: `0.794` (Target: >= 1.050)
- **Max Drawdown Netto 0.25%**: `-52.33%` (Target: <= -52.57%)
- **Operazioni**: `43` (Target: <= 35)
- **Sottoperiodi Positivi**: `2/4` (Target: >= 3/4)
- **Split Walk-Forward Positivi**: `1/3` (Target: >= 2/3)

⚠️ **La variante non soddisfa pienamente tutti i criteri per i seguenti motivi**: Sharpe netto insufficiente (0.794 < 1.050), troppe operazioni (43 > 35), insufficiente stabilità nei sottoperiodi (2/4), insufficiente stabilità nel Walk-Forward (1/3).