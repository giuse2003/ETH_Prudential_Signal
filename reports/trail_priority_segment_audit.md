# Trail8 Priority Segment Audit

Confronto per segmento Baseline: una singola operazione Baseline contro la sequenza composta dei trade Trail8 priority nello stesso intervallo.

## Sintesi

- Segmenti Baseline con almeno una uscita Trail8 priority: 10.
- Segmenti che migliorano: 3.
- Segmenti uguali: 2.
- Segmenti che peggiorano: 5.

Escludendo il caso 2025 gia' classificato come sfavorevole:

- segmenti rimanenti: 9;
- migliorano: 3;
- uguali: 2;
- peggiorano: 4.

## Segmenti

| Baseline entry | Baseline exit | Baseline return | Trail8 sequence return | Delta | Esito | Sequenza Trail8 priority |
|---|---|---:|---:|---:|---|---|
| 2019-04-23 | 2019-07-12 | 61.14% | 52.36% | -8.78% | peggiora | 2019-04-23->2019-06-27 Trail8 priority 71.64%; 2019-06-28->2019-07-12 Official sell -11.23% |
| 2020-07-21 | 2020-09-04 | 58.45% | 57.41% | -1.05% | peggiora | 2020-07-21->2020-09-03 Trail8 priority 57.41% |
| 2020-10-21 | 2021-02-26 | 268.71% | 225.88% | -42.82% | peggiora | 2020-10-21->2020-11-26 Trail8 priority 32.28%; 2020-11-27->2021-01-11 Trail8 priority 110.66%; 2021-01-22->2021-02-26 Official sell 16.94% |
| 2021-03-31 | 2021-05-22 | 19.67% | 65.89% | 46.22% | migliora | 2021-03-31->2021-04-07 Trail8 priority 2.75%; 2021-04-17->2021-05-12 Trail8 priority 61.45% |
| 2021-07-26 | 2021-09-07 | 53.42% | 53.42% | 0.00% | uguale | 2021-07-26->2021-09-07 Trail8 priority 53.42% |
| 2021-10-01 | 2021-11-27 | 23.87% | 25.78% | 1.91% | migliora | 2021-10-01->2021-11-23 Trail8 priority 31.24%; 2021-11-25->2021-11-27 Official sell -4.16% |
| 2021-11-30 | 2021-12-04 | -11.05% | -8.87% | 2.18% | migliora | 2021-11-30->2021-12-03 Trail8 priority -8.87% |
| 2023-03-13 | 2023-04-20 | 15.64% | 15.24% | -0.40% | peggiora | 2023-03-13->2023-04-19 Trail8 priority 15.24% |
| 2024-02-06 | 2024-03-15 | 57.46% | 57.46% | 0.00% | uguale | 2024-02-06->2024-03-15 Trail8 priority 57.46% |
| 2025-07-07 | 2025-09-23 | 63.80% | 61.54% | -2.27% | peggiora | 2025-07-07->2025-08-18 Trail8 priority 69.58%; 2025-08-25->2025-09-23 Official sell -4.74% |

## File generato

- `reports\trail_priority_segment_audit.csv`
