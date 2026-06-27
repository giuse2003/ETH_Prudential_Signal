# RSI Adaptive Trailing Stop Experiment Results

Questi risultati sono frutto di test sperimentali di ricerca e non modificano la strategia ufficiale.
La verifica dello stop avviene esclusivamente sulla chiusura giornaliera (Close).

## Metriche Periodo Completo

| Variante | Ann. Lordo | Max DD Lordo | Sharpe Lordo | Sharpe Netto 0,25% | PF | Operazioni | Mediana Sharpe | Min Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 31.77% | -52.57% | 0.849 | 0.812 | 4.327 | 28 | 0.960 | 0.309 |
| trail_dynamic_15_8 | 54.04% | -56.50% | 1.143 | 1.120 | 10.306 | 19 | 1.121 | 0.638 |
| rsi_adaptive_rsi_80_stop_8 | 47.66% | -55.68% | 1.068 | 1.041 | 5.333 | 22 | 1.085 | 0.619 |
| rsi_adaptive_rsi_80_stop_10 | 46.47% | -60.38% | 1.045 | 1.018 | 5.263 | 22 | 1.085 | 0.638 |
| rsi_adaptive_rsi_70_stop_10 | 46.06% | -60.38% | 1.040 | 1.010 | 4.554 | 24 | 1.064 | 0.638 |
| rsi_adaptive_rsi_75_stop_10 | 46.06% | -60.38% | 1.040 | 1.010 | 4.554 | 24 | 1.064 | 0.638 |
| rsi_adaptive_rsi_75_stop_8 | 45.33% | -55.68% | 1.039 | 1.008 | 4.285 | 25 | 0.969 | 0.530 |
| rsi_adaptive_rsi_70_stop_8 | 42.38% | -55.68% | 1.006 | 0.972 | 4.045 | 27 | 0.969 | 0.530 |

## Dettaglio Sottoperiodi: Sharpe Ratio

| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |
|---|---:|---:|---:|---:|
| baseline | 1.085 | 1.186 | 0.309 | 0.834 |
| trail_dynamic_15_8 | 1.305 | 1.585 | 0.638 | 0.938 |
| rsi_adaptive_rsi_80_stop_8 | 1.232 | 1.444 | 0.619 | 0.938 |
| rsi_adaptive_rsi_80_stop_10 | 1.232 | 1.366 | 0.638 | 0.938 |
| rsi_adaptive_rsi_70_stop_10 | 1.190 | 1.390 | 0.638 | 0.938 |
| rsi_adaptive_rsi_75_stop_10 | 1.190 | 1.390 | 0.638 | 0.938 |
| rsi_adaptive_rsi_75_stop_8 | 1.190 | 1.467 | 0.530 | 0.749 |
| rsi_adaptive_rsi_70_stop_8 | 1.190 | 1.367 | 0.530 | 0.749 |

## Dettaglio Sottoperiodi: Max Drawdown

| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |
|---|---:|---:|---:|---:|
| baseline | -41.34% | -44.93% | -52.57% | -26.17% |
| trail_dynamic_15_8 | -40.85% | -56.50% | -40.90% | -24.74% |
| rsi_adaptive_rsi_80_stop_8 | -40.85% | -55.68% | -43.33% | -24.74% |
| rsi_adaptive_rsi_80_stop_10 | -40.85% | -60.38% | -40.90% | -24.74% |
| rsi_adaptive_rsi_70_stop_10 | -44.07% | -60.38% | -40.90% | -24.74% |
| rsi_adaptive_rsi_75_stop_10 | -44.07% | -60.38% | -40.90% | -24.74% |
| rsi_adaptive_rsi_75_stop_8 | -44.07% | -55.68% | -43.33% | -31.76% |
| rsi_adaptive_rsi_70_stop_8 | -44.07% | -55.68% | -43.33% | -31.76% |

## Analisi degli Eventi di Uscita

La tabella seguente mostra il numero di uscite tentate (prezzo sotto stop level), quante sono state effettivamente confermate da momentum/volume e quante di queste si sono rivelate utili (riacquisto a prezzo inferiore).

| Variante | Uscite Tentate | Uscite Confermate | Di cui Utili | Di cui Inutili | Win Rate Uscite |
|---|---:|---:|---:|---:|---:|
| baseline | 0 | 0 | 0 | 0 | n/a |
| trail_dynamic_15_8 | 253 | 19 | 8 | 11 | 42.11% |
| rsi_adaptive_rsi_80_stop_8 | 241 | 22 | 9 | 13 | 40.91% |
| rsi_adaptive_rsi_80_stop_10 | 261 | 22 | 8 | 14 | 36.36% |
| rsi_adaptive_rsi_70_stop_10 | 274 | 24 | 9 | 15 | 37.50% |
| rsi_adaptive_rsi_75_stop_10 | 265 | 24 | 9 | 15 | 37.50% |
| rsi_adaptive_rsi_75_stop_8 | 242 | 25 | 10 | 15 | 40.00% |
| rsi_adaptive_rsi_70_stop_8 | 242 | 27 | 10 | 17 | 37.04% |

## Conclusioni

### Criteri di Accettazione:
1. Riduzione del Max Drawdown sotto **-52.57%** (baseline) o almeno sotto **-56.50%** (candidato precedente).
2. Sharpe Netto 0.25% **>= 1.050**.
3. Numero operazioni **<= 30**.
4. Funzionalità positiva (Sharpe > 0) in almeno **3 sottoperiodi su 4**.

La variante migliore della griglia per Sharpe Netto è **rsi_adaptive_rsi_80_stop_8**:
- **Sharpe Netto 0.25%**: `1.041` (Target: >= 1.050)
- **Max Drawdown Netto 0.25%**: `-55.89%` (Target: < -56.50% o < -52.57%)
- **Operazioni**: `22` (Target: <= 30)
- **Sottoperiodi Positivi**: `4/4` (Target: >= 3/4)

⚠️ **La variante non soddisfa pienamente tutti i criteri per i seguenti motivi**: Sharpe netto insufficiente (1.041).