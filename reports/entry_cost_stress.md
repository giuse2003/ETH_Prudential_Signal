# Entry Cost Stress

Periodo: `2017-11-11` -> `2026-06-27`.

Confronto solo sugli ingressi: Baseline ufficiale vs Baseline + filtro `RSI <= 65`.
L'uscita resta invariata: `VENDI` sotto SMA50 per 2 giorni consecutivi.

Il costo e' applicato a ogni cambio di esposizione, quindi su ingresso e uscita.

## Periodo Completo

| Scenario | Modello | Ann. | Max DD | Sharpe | PF | Operazioni | Turnover |
|---|---|---:|---:|---:|---:|---:|---:|
| lordo_0_00pct | Baseline ufficiale | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 56 |
| lordo_0_00pct | RSI <= 65 ingresso | 36.13% | -47.17% | 0.944 | 5.670 | 27 | 54 |
| costo_0_10pct | Baseline ufficiale | 29.42% | -50.43% | 0.813 | 4.152 | 28 | 56 |
| costo_0_10pct | RSI <= 65 ingresso | 35.28% | -47.91% | 0.929 | 5.566 | 27 | 54 |
| costo_0_25pct | Baseline ufficiale | 28.16% | -51.46% | 0.791 | 4.060 | 28 | 56 |
| costo_0_25pct | RSI <= 65 ingresso | 34.02% | -49.00% | 0.907 | 5.416 | 27 | 54 |
| stress_0_50pct | Baseline ufficiale | 26.10% | -53.21% | 0.753 | 3.910 | 28 | 56 |
| stress_0_50pct | RSI <= 65 ingresso | 31.93% | -50.85% | 0.870 | 5.171 | 27 | 54 |
| stress_1_00pct | Baseline ufficiale | 22.05% | -56.61% | 0.678 | 3.635 | 28 | 56 |
| stress_1_00pct | RSI <= 65 ingresso | 27.84% | -54.44% | 0.794 | 4.732 | 27 | 54 |

## Delta RSI65 Meno Baseline

| Scenario | Delta Ann. | Delta Max DD | Delta Sharpe | Delta PF | Delta operazioni | Delta 2022+ Ann. | Delta 2022+ DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| lordo_0_00pct | 5.87% | 2.56% | 0.116 | 1.455 | -1 | 1.16% | 2.56% |
| costo_0_10pct | 5.86% | 2.52% | 0.116 | 1.414 | -1 | 1.15% | 2.52% |
| costo_0_25pct | 5.85% | 2.46% | 0.116 | 1.355 | -1 | 1.13% | 2.46% |
| stress_0_50pct | 5.83% | 2.36% | 0.116 | 1.261 | -1 | 1.11% | 2.36% |
| stress_1_00pct | 5.79% | 2.17% | 0.117 | 1.098 | -1 | 1.05% | 2.17% |

## Lettura

- Anche nello scenario piu' severo (stress_1_00pct), RSI65 mantiene un delta annuo di 5.79% rispetto alla Baseline.
- Il vantaggio non dipende dal risparmio di costi: RSI65 fa una operazione in meno, ma il delta principale viene dagli ingressi evitati/ritardati.
- La regola resta un candidato di ingresso, non una modifica ufficiale.
