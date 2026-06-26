# Model Experiment Results

Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.

Le varianti applicano filtri solo ai nuovi ingressi `ACQUISTA`; i segnali
`VENDI` ufficiali restano invariati.

## Top Variants By Sharpe

| Variante | Ann. | Max DD | Sharpe | Profit factor | Operazioni | Net 0,25% Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| atr_close_le_7pct | 31.84% | -52.57% | 0.851 | 4.530 | 27 | 0.815 |
| baseline | 31.78% | -52.57% | 0.849 | 4.327 | 28 | 0.812 |
| close_gt_sma200_5pct | 31.68% | -51.39% | 0.847 | 4.362 | 27 | 0.812 |
| close_gt_sma200_2pct | 31.67% | -52.93% | 0.847 | 4.302 | 28 | 0.810 |
| atr_close_le_5pct | 29.09% | -56.74% | 0.837 | 5.460 | 22 | 0.805 |
| vol20_le_p85 | 30.58% | -52.57% | 0.828 | 4.254 | 28 | 0.791 |
| vol20_le_p75 | 28.83% | -55.35% | 0.799 | 4.041 | 28 | 0.761 |
| sma50_rising_10d | 26.84% | -51.80% | 0.768 | 4.140 | 22 | 0.739 |

## Sintesi

- Baseline Sharpe: 0.849.
- Migliore variante testata: `atr_close_le_7pct` con Sharpe 0.851.
- Delta Sharpe migliore vs baseline: 0.002.

Conclusione: i filtri testati non risolvono ancora lo Sharpe sotto 1.
Il filtro ATR/Close <= 7% migliora marginalmente la baseline; i filtri
su SMA200 crescente riducono troppo il rendimento.
