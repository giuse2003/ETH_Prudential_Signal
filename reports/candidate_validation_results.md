# Candidate Validation Results

Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.

## Periodo Completo

| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Net 0,25% Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| confirmed_trail8_mom_-5_vol_10 | 42.76% | -46.50% | 1.063 | 5.351 | 31 | 1.019 |
| confirmed_trail8_mom_-5_vol_20 | 42.06% | -46.50% | 1.050 | 5.427 | 30 | 1.008 |
| confirmed_trail8_mom_-6_vol_20 | 39.15% | -44.93% | 1.006 | 4.970 | 31 | 0.963 |
| exit_sma50_1d | 34.43% | -45.16% | 0.908 | 4.738 | 30 | 0.867 |
| entry_stop_9pct | 32.84% | -50.54% | 0.872 | 4.451 | 29 | 0.833 |
| baseline | 31.78% | -52.57% | 0.849 | 4.327 | 28 | 0.812 |

## Robustezza Per Sottoperiodi

| Variante | Mediana Sharpe | Min Sharpe | Mediana Ann. | Peggior DD | Periodi positivi |
|---|---:|---:|---:|---:|---:|
| confirmed_trail8_mom_-5_vol_10 | 1.102 | 0.093 | 42.41% | -44.93% | 3/4 |
| confirmed_trail8_mom_-5_vol_20 | 1.105 | 0.090 | 41.16% | -44.93% | 3/4 |
| confirmed_trail8_mom_-6_vol_20 | 0.996 | 0.250 | 41.16% | -44.93% | 4/4 |
| exit_sma50_1d | 1.097 | 0.117 | 35.76% | -45.16% | 3/4 |
| entry_stop_9pct | 0.983 | 0.041 | 33.62% | -48.46% | 3/4 |
| baseline | 0.960 | -0.018 | 32.99% | -50.58% | 3/4 |

## Walk-Forward

Per ogni split, seleziona il miglior candidato sul train per Sharpe e misura il test successivo.

| Train | Test | Selezionato | Test Ann. | Test DD | Test Sharpe |
|---|---|---|---:|---:|---:|
| 2017-2020 | 2021-2022 | confirmed_trail8_mom_-5_vol_10 | 91.40% | -44.93% | 1.369 |
| 2017-2022 | 2023-2024 | confirmed_trail8_mom_-5_vol_10 | -1.83% | -44.25% | 0.093 |
| 2017-2024 | 2025-2026 | confirmed_trail8_mom_-5_vol_10 | 22.53% | -26.17% | 0.835 |

## Sintesi

- Migliore sul periodo completo: `confirmed_trail8_mom_-5_vol_10` con Sharpe 1.063.
- Migliore per min Sharpe nei sottoperiodi: `confirmed_trail8_mom_-6_vol_20` con min Sharpe 0.250.
- La validazione mostra rischio overfitting: il migliore sul periodo
  completo non e' sempre il migliore nel periodo successivo.
- Nessun candidato viene promosso a regola operativa in questa fase.
