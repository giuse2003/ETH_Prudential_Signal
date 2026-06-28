# Trail8 -5 / Vol +20 Exit Event Audit

Periodo: `2017-11-11` -> `2026-06-27`.

Audit del candidato uscita `Trail8 confermato -5 / vol +20`.
Gli ingressi restano quelli Baseline ufficiali. Nessun segnale ufficiale viene modificato.

Definizioni:

- `Return trade`: rendimento dall'ingresso precedente alla data di uscita forzata.
- `DD subito`: peggior drawdown interno dal giorno di ingresso alla data di uscita forzata.
- `DD evitato`: peggior discesa dal prezzo di uscita fino al rientro successivo; se il prezzo non scende, vale 0.
- `Upside perso`: massimo rialzo dal prezzo di uscita fino al rientro successivo.

## Sintesi

- Uscite forzate: 6.
- Uscite con trade positivo: 4.
- Uscite con trade negativo: 2.
- Classificate utili: 5.
- Classificate neutre: 0.
- Classificate dannose: 1.

## Eventi

| Uscita | Prezzo uscita | Ingresso precedente | Prezzo ingresso | Return trade | Esito | DD subito | Rientro successivo | Prezzo rientro | Rientro vs uscita | DD evitato | Upside perso | Lettura |
|---|---:|---|---:|---:|---|---:|---|---:|---:|---:|---:|---|
| 2020-02-20 | 239.11 | 2020-02-16 | 239.72 | -0.25% | negativo | -8.45% | 2020-05-30 | 218.23 | -8.73% | 58.55% | 5.64% | utile |
| 2020-09-04 | 327.96 | 2020-07-21 | 212.38 | 54.42% | positivo | -18.58% | 2020-10-12 | 328.23 | 0.08% | 16.00% | 0.10% | utile |
| 2021-09-07 | 2892.82 | 2021-07-26 | 1891.90 | 52.91% | positivo | -13.00% | 2021-10-01 | 2852.80 | -1.38% | 18.48% | 5.74% | utile |
| 2023-04-20 | 1771.60 | 2023-03-13 | 1567.01 | 13.06% | positivo | -8.39% | 2023-05-05 | 1779.61 | 0.45% | 5.93% | 0.45% | utile |
| 2024-03-15 | 3429.87 | 2024-02-06 | 2205.24 | 55.53% | positivo | -7.80% | 2024-04-08 | 3402.13 | -0.81% | 15.24% | 0.00% | utile |
| 2024-06-17 | 3269.43 | 2024-05-20 | 3373.58 | -3.09% | negativo | -9.83% | 2024-06-20 | 3279.52 | 0.31% | 0.78% | 1.30% | dannosa |

## Lettura

- Il candidato va giudicato sugli eventi, non solo sulla metrica aggregata.
- Una buona uscita deve proteggere capitale gia' acquisito senza generare troppi rientri piu' alti.
- Le uscite con rientro successivo piu' alto vanno considerate con cautela: possono migliorare il drawdown ma perdere rendimento.
