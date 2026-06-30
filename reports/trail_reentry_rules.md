# Trail8 Reentry Rules

Test sperimentale su regole di rientro dopo uscita Trail8 priority.

La Baseline ufficiale non viene modificata.

## Regole Testate

- `cooldown Xd`: dopo una uscita Trail8 ignora nuovi ACQUISTA per X giorni.
- `reset_green Xd`: dopo una uscita Trail8 richiede almeno una condizione BUY rossa, poi X giorni consecutivi con BUY tutte verdi.

## Metriche

| Modello | Ann. | Max DD | Sharpe | PF | Operazioni | Trail8 exits | Entry bloccati |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 43.61% | -44.93% | 1.084 | 5.889 | 28 | 4 | 0 |
| Trail8 priority | 46.35% | -42.79% | 1.207 | 4.708 | 34 | 12 | 0 |
| cooldown 3d | 43.72% | -42.79% | 1.179 | 4.571 | 33 | 12 | 4 |
| cooldown 7d | 43.72% | -42.79% | 1.179 | 4.571 | 33 | 12 | 4 |
| cooldown 10d | 43.61% | -42.79% | 1.182 | 4.554 | 33 | 11 | 9 |
| cooldown 14d | 43.43% | -42.79% | 1.200 | 4.917 | 31 | 11 | 16 |
| cooldown 21d | 34.83% | -42.79% | 1.065 | 4.236 | 29 | 10 | 21 |
| cooldown 30d | 32.72% | -36.35% | 1.036 | 4.236 | 28 | 10 | 32 |
| reset_green 0d | 43.01% | -42.79% | 1.164 | 4.418 | 34 | 12 | 3 |
| reset_green 3d | 35.49% | -40.35% | 1.182 | 5.533 | 23 | 8 | 60 |
| reset_green 7d | 6.46% | -14.58% | 0.537 | inf | 1 | 1 | 145 |
| reset_green 10d | 6.46% | -14.58% | 0.537 | inf | 1 | 1 | 145 |
| reset_green 14d | 6.46% | -14.58% | 0.537 | inf | 1 | 1 | 145 |
| reset_green 21d | 6.46% | -14.58% | 0.537 | inf | 1 | 1 | 145 |
| reset_green 30d | 6.46% | -14.58% | 0.537 | inf | 1 | 1 | 145 |

## Migliori Varianti Per Sharpe

| Rank | Modello | Ann. | Max DD | Sharpe | PF | Operazioni |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Trail8 priority | 46.35% | -42.79% | 1.207 | 4.708 | 34 |
| 2 | cooldown 14d | 43.43% | -42.79% | 1.200 | 4.917 | 31 |
| 3 | reset_green 3d | 35.49% | -40.35% | 1.182 | 5.533 | 23 |
| 4 | cooldown 10d | 43.61% | -42.79% | 1.182 | 4.554 | 33 |
| 5 | cooldown 3d | 43.72% | -42.79% | 1.179 | 4.571 | 33 |
| 6 | cooldown 7d | 43.72% | -42.79% | 1.179 | 4.571 | 33 |
| 7 | reset_green 0d | 43.01% | -42.79% | 1.164 | 4.418 | 34 |
| 8 | cooldown 21d | 34.83% | -42.79% | 1.065 | 4.236 | 29 |

## File generati

- `reports\trail_reentry_rules_metrics.csv`
- `reports\trail_reentry_rules_events.csv`
