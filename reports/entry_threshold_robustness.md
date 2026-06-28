# Entry Threshold Robustness

Periodo: `2017-11-11` -> `2026-06-27`.

Confronto solo sugli ingressi. L'uscita resta invariata: `VENDI` sotto SMA50 per 2 giorni consecutivi.

Soglie testate: `RSI <= 63` fino a `RSI <= 70`.

## Risultati

| Variante | Ann. | Delta Ann. | Max DD | Delta DD | Sharpe | Delta Sharpe | PF | Ops | Nuovi ingressi bloccati | 2022+ Ann. | 2022+ DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 30.26% | 0.00% | -49.73% | 0.00% | 0.828 | 0.000 | 4.215 | 28 | 0 | 4.12% | -49.73% |
| RSI <= 63 | 36.13% | 5.87% | -47.17% | 2.56% | 0.944 | 0.116 | 5.670 | 27 | 14 | 5.28% | -47.17% |
| RSI <= 64 | 36.13% | 5.87% | -47.17% | 2.56% | 0.944 | 0.116 | 5.670 | 27 | 14 | 5.28% | -47.17% |
| RSI <= 65 | 36.13% | 5.87% | -47.17% | 2.56% | 0.944 | 0.116 | 5.670 | 27 | 14 | 5.28% | -47.17% |
| RSI <= 66 | 36.13% | 5.87% | -47.17% | 2.56% | 0.944 | 0.116 | 5.670 | 27 | 14 | 5.28% | -47.17% |
| RSI <= 67 | 36.13% | 5.87% | -47.17% | 2.56% | 0.944 | 0.116 | 5.670 | 27 | 14 | 5.28% | -47.17% |
| RSI <= 68 | 35.41% | 5.15% | -47.17% | 2.56% | 0.931 | 0.103 | 5.428 | 27 | 13 | 5.28% | -47.17% |
| RSI <= 69 | 34.35% | 4.10% | -50.61% | -0.88% | 0.910 | 0.082 | 5.115 | 27 | 8 | 3.71% | -50.61% |
| RSI <= 70 | 34.27% | 4.01% | -50.88% | -1.15% | 0.909 | 0.080 | 5.092 | 27 | 6 | 3.59% | -50.88% |

## Lettura

- Migliore Sharpe: `RSI <= 63` con Sharpe 0.944.
- Miglior rendimento annualizzato: `RSI <= 63` con ann. 36.13%.
- Miglior max drawdown: `RSI <= 63` con DD -47.17%.
- Se soglie vicine producono risultati simili, la zona e' robusta; se cambia tutto per un punto RSI, la regola e' fragile.
- Questa analisi resta un test sugli ingressi: nessun segnale ufficiale viene modificato.
