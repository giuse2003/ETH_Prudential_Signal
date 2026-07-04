# SMA50 Trend Filter Guardrails

Test esplorativo: rimuovere `SMA50 > SMA200` ma filtrare solo gli ingressi anticipati
in cui `SMA50 <= SMA200`.

## Risultati

| Variante | Ann. | Max DD | Sharpe | PF | Ops | Delta 2018-2019 | Delta recente | Rolling + | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| guard_rsi_le_62_or_vol15 | 60.55% | -41.10% | 1.321 | 9.488 | 30 | 6.16% | 50.51% | 96.00% | PASS |
| guard_mom_le_10 | 60.02% | -41.10% | 1.316 | 9.443 | 30 | 6.16% | 50.51% | 96.00% | PASS |
| guard_rsi_le_62 | 59.80% | -41.10% | 1.315 | 9.015 | 30 | 6.16% | 41.04% | 96.00% | PASS |
| guard_volrel_ge_15 | 58.71% | -41.10% | 1.294 | 8.460 | 30 | 6.16% | 27.95% | 96.00% | PASS |
| guard_volrel_ge_20 | 58.18% | -41.10% | 1.289 | 8.419 | 30 | 6.16% | 27.95% | 96.00% | PASS |
| remove_pure | 56.07% | -41.10% | 1.247 | 7.335 | 31 | -27.15% | 50.51% | 92.00% | FAIL |

## Lettura

- Migliore candidato per gate e Sharpe: `guard_rsi_le_62_or_vol15`.
- Annualizzato: 60.55%; Sharpe: 1.321; PF: 9.488.
- Il guardrail serve soprattutto a evitare il falso rimbalzo del 2019 che rende fragile la rimozione pura.
- Questi candidati non sono ancora Baseline: vanno confrontati con il principio di semplicita' e con un audit evento-per-evento.
