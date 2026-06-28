# Combined Walk-Forward Validation

Validazione cronologica del candidato combinato. Nessuna modifica ai segnali ufficiali.

Modelli:

- Baseline ufficiale;
- Combinato principale: `RSI <= 65` + `Trail8 -5 / vol +20`;
- Variante secondaria: combinato principale + `trade return >= 15%` per attivare Trail8.

## Periodo Completo

| Modello | Ann. | Max DD | Sharpe | PF | Operazioni | Ingressi bloccati | Uscite Trail8 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 0 | 0 |
| Combinato RSI65 + Trail8 | 42.74% | -45.09% | 1.079 | 5.999 | 28 | 14 | 4 |
| Combinato + gain minimo 15% | 42.81% | -45.09% | 1.079 | 6.282 | 27 | 14 | 3 |

## Finestre Cronologiche

| Finestra | Modello | Return | Max DD | Sharpe | Delta return | Delta DD | Delta Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|
| 2019-2020 | Baseline ufficiale | 172.30% | -44.30% | 1.238 | 0.00% | 0.00% | 0.000 |
| 2019-2020 | Combinato + gain minimo 15% | 316.33% | -22.48% | 1.775 | 144.03% | 21.83% | 0.537 |
| 2019-2020 | Combinato RSI65 + Trail8 | 316.33% | -22.48% | 1.775 | 144.03% | 21.83% | 0.537 |
| 2021-2022 | Baseline ufficiale | 201.42% | -45.09% | 1.213 | 0.00% | 0.00% | 0.000 |
| 2021-2022 | Combinato + gain minimo 15% | 269.77% | -45.09% | 1.399 | 68.34% | -0.00% | 0.185 |
| 2021-2022 | Combinato RSI65 + Trail8 | 269.77% | -45.09% | 1.399 | 68.34% | -0.00% | 0.185 |
| 2023-2024 | Baseline ufficiale | -11.83% | -47.85% | -0.019 | 0.00% | 0.00% | 0.000 |
| 2023-2024 | Combinato + gain minimo 15% | 4.02% | -38.47% | 0.213 | 15.85% | 9.38% | 0.231 |
| 2023-2024 | Combinato RSI65 + Trail8 | 3.55% | -38.47% | 0.203 | 15.38% | 9.38% | 0.221 |
| 2025-2026 | Baseline ufficiale | 35.98% | -26.08% | 0.857 | 0.00% | 0.00% | 0.000 |
| 2025-2026 | Combinato + gain minimo 15% | 35.98% | -26.08% | 0.857 | -0.00% | -0.00% | -0.000 |
| 2025-2026 | Combinato RSI65 + Trail8 | 35.98% | -26.08% | 0.857 | -0.00% | -0.00% | -0.000 |

## Sintesi Finestre

| Modello | Finestre | Vince return | Vince DD | Vince Sharpe | Peggior delta return | Peggior delta DD |
|---|---:|---:|---:|---:|---:|---:|
| Combinato + gain minimo 15% | 4 | 3 | 2 | 3 | -0.00% | -0.00% |
| Combinato RSI65 + Trail8 | 4 | 3 | 2 | 3 | -0.00% | -0.00% |

## Annuale Contro Baseline

| Anno | Modello | Delta return | Delta DD | Delta Sharpe |
|---:|---|---:|---:|---:|
| 2019 | Combinato + gain minimo 15% | 0.00% | 0.00% | 0.000 |
| 2019 | Combinato RSI65 + Trail8 | 0.00% | 0.00% | 0.000 |
| 2020 | Combinato + gain minimo 15% | 89.84% | 16.12% | 0.978 |
| 2020 | Combinato RSI65 + Trail8 | 89.84% | 16.12% | 0.978 |
| 2021 | Combinato + gain minimo 15% | 68.34% | -0.00% | 0.264 |
| 2021 | Combinato RSI65 + Trail8 | 68.34% | -0.00% | 0.264 |
| 2022 | Combinato + gain minimo 15% | 0.00% | 0.00% | n/a |
| 2022 | Combinato RSI65 + Trail8 | 0.00% | 0.00% | n/a |
| 2023 | Combinato + gain minimo 15% | -0.00% | -0.00% | -0.000 |
| 2023 | Combinato RSI65 + Trail8 | -0.45% | -0.35% | -0.024 |
| 2024 | Combinato + gain minimo 15% | 15.36% | 9.38% | 0.401 |
| 2024 | Combinato RSI65 + Trail8 | 15.36% | 9.38% | 0.401 |
| 2025 | Combinato + gain minimo 15% | -0.00% | -0.00% | -0.000 |
| 2025 | Combinato RSI65 + Trail8 | -0.00% | -0.00% | -0.000 |
| 2026 | Combinato + gain minimo 15% | 0.00% | 0.00% | n/a |
| 2026 | Combinato RSI65 + Trail8 | 0.00% | 0.00% | n/a |

## Uscite Trail8

| Modello | Data | Entry | Return trade | DD da picco | Mom 7d | Vol rel |
|---|---|---|---:|---:|---:|---:|
| Combinato + gain minimo 15% | 2020-09-04 | 2020-07-21 | 54.42% | -18.62% | -1.93% | 33.66% |
| Combinato + gain minimo 15% | 2021-09-07 | 2021-07-26 | 52.91% | -13.30% | -0.21% | 85.80% |
| Combinato + gain minimo 15% | 2024-03-15 | 2024-02-06 | 55.53% | -8.15% | -4.03% | 39.74% |
| Combinato RSI65 + Trail8 | 2020-09-04 | 2020-07-21 | 54.42% | -18.62% | -1.93% | 33.66% |
| Combinato RSI65 + Trail8 | 2021-09-07 | 2021-07-26 | 52.91% | -13.30% | -0.21% | 85.80% |
| Combinato RSI65 + Trail8 | 2023-04-20 | 2023-03-13 | 13.06% | -8.34% | -3.46% | 21.08% |
| Combinato RSI65 + Trail8 | 2024-03-15 | 2024-02-06 | 55.53% | -8.15% | -4.03% | 39.74% |

## Lettura

- Il test non ottimizza parametri sul futuro: confronta regole fisse su finestre successive.
- Il candidato principale e' valido se migliora la Baseline in piu' finestre senza peggioramenti concentrati.
- La variante `gain minimo 15%` e' accettabile solo se migliora senza dipendere unicamente dal 2023.
- La promozione a Baseline ufficiale resta una decisione separata: questo report misura la stabilita', non modifica la strategia.

## Decisione

- Il candidato principale supera la validazione cronologica: migliora 2019-2020, 2021-2022 e 2023-2024; resta invariato nel 2025-2026.
- La variante `gain minimo 15%` non peggiora le metriche, ma il beneficio aggiuntivo e' marginale e dipende dal singolo caso 2023.
- Per ora resta preferibile il candidato principale, perche' e' piu' semplice e gia' robusto.
- Prossimo step: preparare un gate decisionale per promuovere o meno il candidato principale a nuova Baseline ufficiale.
