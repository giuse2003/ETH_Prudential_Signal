# Confirmed Trailing Stop Experiment Results

Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.

Modello testato: trailing stop 8% su massimo Close post-ingresso, eseguito
solo se la conferma momentum/volume e' vera.

## Focus Variants

| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Net 0,25% Sharpe | Uscite confermate | Utili prese | Inutili prese |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| trail8_mom_ge_-5_vol_ge_20 | 42.06% | -46.50% | 1.050 | 5.427 | 30 | 1.008 | 6 | 5 | 1 |
| trail8_mom_ge_-4_vol_ge_20 | 39.96% | -52.94% | 1.006 | 5.240 | 30 | 0.965 | 5 | 3 | 2 |
| trail8_mom_ge_-7_vol_ge_22 | 38.77% | -44.93% | 0.985 | 4.847 | 30 | 0.944 | 7 | 5 | 2 |
| trail8_mom_ge_-5_vol_ge_22 | 37.44% | -46.50% | 0.961 | 4.547 | 30 | 0.920 | 5 | 4 | 1 |
| baseline | 31.78% | -52.57% | 0.849 | 4.327 | 28 | 0.812 | 0 | 0 | 0 |
| trailing8_all | 20.52% | -41.93% | 0.690 | 2.126 | 48 | 0.615 | 31 | 8 | 23 |

## Top By Sharpe

| Variante | Ann. | Max DD | Sharpe | PF | Operazioni |
|---|---:|---:|---:|---:|---:|
| trail8_mom_ge_-5_vol_ge_10 | 42.76% | -46.50% | 1.063 | 5.351 | 31 |
| trail8_mom_ge_-5_vol_ge_20 | 42.06% | -46.50% | 1.050 | 5.427 | 30 |
| trail8_mom_ge_-6_vol_ge_20 | 39.15% | -44.93% | 1.006 | 4.970 | 31 |
| trail8_mom_ge_-4_vol_ge_20 | 39.96% | -52.94% | 1.006 | 5.240 | 30 |
| trail8_mom_ge_-4_vol_ge_10 | 39.86% | -52.94% | 1.004 | 5.104 | 31 |
| trail8_mom_ge_-6_vol_ge_10 | 38.08% | -44.93% | 0.990 | 4.483 | 33 |
| trail8_mom_ge_-6_vol_ge_22 | 39.03% | -44.93% | 0.989 | 4.862 | 30 |
| trail8_mom_ge_-8_vol_ge_22 | 38.91% | -44.93% | 0.987 | 4.858 | 30 |
| trail8_mom_ge_-7_vol_ge_22 | 38.77% | -44.93% | 0.985 | 4.847 | 30 |
| trail8_mom_ge_-4_vol_ge_0 | 38.40% | -52.94% | 0.980 | 4.698 | 32 |

## Top By Drawdown

| Variante | Ann. | Max DD | Sharpe | Uscite confermate |
|---|---:|---:|---:|---:|
| trailing8_all | 20.52% | -41.93% | 0.690 | 31 |
| trail8_mom_ge_-8_vol_ge_10 | 35.00% | -44.93% | 0.942 | 14 |
| trail8_mom_ge_-8_vol_ge_0 | 32.06% | -44.93% | 0.892 | 17 |
| trail8_mom_ge_-6_vol_ge_20 | 39.15% | -44.93% | 1.006 | 8 |
| trail8_mom_ge_-6_vol_ge_10 | 38.08% | -44.93% | 0.990 | 11 |
| trail8_mom_ge_-8_vol_ge_20 | 37.25% | -44.93% | 0.978 | 11 |
| trail8_mom_ge_-7_vol_ge_20 | 37.04% | -44.93% | 0.972 | 10 |
| trail8_mom_ge_-7_vol_ge_10 | 36.24% | -44.93% | 0.959 | 12 |
| trail8_mom_ge_-6_vol_ge_0 | 34.45% | -44.93% | 0.929 | 13 |
| trail8_mom_ge_-7_vol_ge_0 | 32.66% | -44.93% | 0.898 | 14 |

## Sottoperiodi: Max Drawdown

| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |
|---|---:|---:|---:|---:|
| baseline | -41.34% | -44.93% | -52.57% | -26.17% |
| trailing8_all | -38.11% | -36.06% | -41.93% | -41.01% |
| trail8_mom_ge_-5_vol_ge_20 | -25.09% | -44.93% | -46.50% | -26.17% |
| trail8_mom_ge_-7_vol_ge_22 | -41.34% | -44.93% | -40.93% | -26.17% |
| trail8_mom_ge_-5_vol_ge_22 | -41.34% | -44.93% | -46.50% | -26.17% |
| trail8_mom_ge_-4_vol_ge_20 | -25.09% | -44.93% | -52.94% | -26.17% |

## Eventi Originali Trailing 8%

- Eventi totali: 31.
- Utili: 8.
- Inutili: 23.

## Sintesi

- Migliore Sharpe in griglia: `trail8_mom_ge_-5_vol_ge_10` con Sharpe 1.063, ann. 42.76%, max DD -46.50%.
- La conferma momentum/volume evita molte uscite inutili del trailing 8%
  ma cattura solo una parte delle uscite utili.
- Il candidato pratico resta da validare fuori campione; la dimensione
  eventi e' piccola e il rischio overfitting e' alto.
