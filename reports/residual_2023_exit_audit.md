# Audit Peggioramento Residuo 2023

Obiettivo: capire se l'uscita `Trail8 confermato -5 / vol +20` del 2023 puo' essere evitata con una regola generale.

## Caso 2023

- Segmento Baseline: `2023-03-13 -> 2023-05-08`.
- Uscita Trail8: `2023-04-20` a EUR 1771.60.
- Rendimento del trade al momento dell'uscita: 13.06%.
- Rendimento segmento Baseline: 7.30%.
- Rendimento segmento candidato: 6.82%.
- Delta candidato - Baseline: -0.48%.
- Drawdown subito fino all'uscita Trail8: -8.39%.
- Giorni tra uscita Trail8 e uscita ufficiale Baseline: 18.

## Confronto Uscite Trail8 Nel Combinato

| Uscita | Entry | Return trade | Max gain | DD da picco | RSI | Mom 7d | Vol rel | Giorni trade | Delta segmento | Lettura |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2020-09-04 | 2020-07-21 | 54.42% | 88.37% | -18.02% | 47.50 | -1.93% | 33.66% | 45 | 13.84% | utile |
| 2021-09-07 | 2021-07-26 | 52.91% | 75.76% | -13.00% | 51.35 | -0.21% | 85.80% | 43 | 28.26% | utile |
| 2023-04-20 | 2023-03-13 | 13.06% | 23.16% | -8.21% | 52.68 | -3.46% | 21.08% | 38 | -0.48% | costo residuo |
| 2024-03-15 | 2024-02-06 | 55.53% | 68.70% | -7.80% | 60.75 | -4.03% | 39.74% | 38 | 16.98% | utile |

## Regole Candidate Per Escludere Il 2023

| Regola | Uscite tenute | Uscite escluse | Esclude 2023 | Uscite utili escluse | Delta tenuto | Delta escluso |
|---|---:|---:|---|---:|---:|---:|
| richiedi gain trade >= 15% | 3 | 1 | si | 0 | 59.08% | -0.48% |
| richiedi max gain >= 35% | 3 | 1 | si | 0 | 59.08% | -0.48% |
| richiedi RSI uscita >= 55 | 1 | 3 | si | 2 | 16.98% | 41.62% |
| richiedi volume relativo >= 40% | 1 | 3 | si | 2 | 28.26% | 30.33% |
| richiedi almeno 40 giorni in trade | 2 | 2 | si | 1 | 42.10% | 16.50% |
| blocca solo se uscita ufficiale distante >= 20 giorni | 0 | 4 | si | 3 | 0.00% | 58.60% |

## Impatto Varianti Sul Modello Combinato

| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Uscite Trail8 |
|---|---:|---:|---:|---:|---:|---|
| Baseline ufficiale | 30.26% | -49.73% | 0.83 | 4.21 | 28 |  |
| Combinato attuale | 42.74% | -45.09% | 1.08 | 6.00 | 28 | 2020-09-04, 2021-09-07, 2023-04-20, 2024-03-15 |
| Combinato + trade return >= 15% | 42.81% | -45.09% | 1.08 | 6.28 | 27 | 2020-09-04, 2021-09-07, 2024-03-15 |
| Combinato + max gain >= 35% | 42.81% | -45.09% | 1.08 | 6.28 | 27 | 2020-09-04, 2021-09-07, 2024-03-15 |

## Lettura

- Uscite Trail8 utili nel combinato: 3.
- Uscite Trail8 con costo residuo: 1.
- Il caso 2023 e' un costo piccolo: peggiora il segmento di 0,48 punti ma riduce il drawdown del segmento.
- Molte regole semplici che eliminano il 2023 eliminano anche uscite utili rilevanti.
- Le uniche regole semplici che eliminano solo il 2023 nel campione sono `trade return >= 15%` e `max gain >= 35%`.
- Sono coerenti con l'idea di proteggere capitale gia' acquisito, ma modificano un solo evento storico: rischio overfit alto.
- Non emergono elementi sufficienti per trasformarle subito in filtro ufficiale.

## Decisione

- Non aggiungere subito una regola specifica per evitare il 2023.
- Accettare provvisoriamente il costo residuo 2023 come prezzo del candidato uscita.
- Tenere `trade return >= 15%` come candidato secondario da validare, non come modifica ufficiale.
- Il combinato resta candidato finale, non Baseline ufficiale.
- Il prossimo gate deve essere una validazione out-of-sample / walk-forward del combinato prima della promozione.
