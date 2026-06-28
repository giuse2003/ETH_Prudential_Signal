# RSI65 Blocked Entry Audit

Questo report valuta solo gli ingressi bloccati da `RSI <= 65`.
Non modifica i segnali ufficiali e mantiene invariata l'uscita ufficiale sotto SMA50 per 2 giorni consecutivi.

## Sintesi

- Segnali giornalieri bloccati: 14.
- Finestre operative bloccate: 6.
- Trade Baseline unici coinvolti: 4.
- Trade Baseline unici perdenti: 4.
- Finestre utili: 6.
- Finestre miste: 0.
- Finestre costose: 0.

Nota: piu' finestre possono appartenere allo stesso trade Baseline, perche' il filtro resta fuori e il segnale ufficiale puo' ripresentarsi nei giorni successivi.

## Eventi

| Blocco | Segnali | Prezzo blocco | RSI medio/max | Baseline exit | Return Baseline | DD trade | Max gain | Nuovo ingresso RSI65 | Delta ingresso | Return RSI65 trade | Giorni | Lettura |
|---|---:|---:|---:|---|---:|---:|---:|---|---:|---:|---:|---|
| 2020-02-16 -> 2020-02-18 | 3 | 239.72 | 73.7 / 76.6 | 2020-03-09 | -26.07% | -32.52% | 8.96% | 2020-06-02 | -11.53% | -3.95% | 107 | utile: salta trade perdente |
| 2020-05-30 -> 2020-05-30 | 1 | 218.23 | 70.5 / 70.5 | 2020-07-17 | -6.66% | -10.48% | 1.73% | 2020-06-02 | -2.82% | -3.95% | 3 | utile: ritarda ingresso perdente |
| 2020-06-01 -> 2020-06-01 | 1 | 222.01 | 68.0 / 68.0 | 2020-07-17 | -6.66% | -10.48% | 1.73% | 2020-06-02 | -4.47% | -3.95% | 1 | utile: ritarda ingresso perdente |
| 2024-05-20 -> 2024-05-24 | 5 | 3373.58 | 70.3 / 72.5 | 2024-06-24 | -7.47% | -12.88% | 6.22% | 2024-06-20 | -2.79% | -4.81% | 31 | utile: ritarda ingresso perdente |
| 2024-05-27 -> 2024-05-28 | 2 | 3583.26 | 70.6 / 72.2 | 2024-06-24 | -7.47% | -12.88% | 6.22% | 2024-06-20 | -8.48% | -4.81% | 24 | utile: ritarda ingresso perdente |
| 2024-12-05 -> 2024-12-06 | 2 | 3599.87 | 71.1 / 73.4 | 2024-12-22 | -12.74% | -17.15% | 5.32% | 2024-12-09 | -2.12% | -10.84% | 4 | utile: ritarda ingresso perdente |

## Conclusione

- `RSI <= 65` non sta solo ottimizzando una metrica aggregata: concentra i blocchi in poche finestre operative ad alto RSI.
- Tutti i trade Baseline unici intercettati dal filtro sono perdenti.
- Quando RSI65 rientra, lo fa a un prezzo inferiore rispetto al blocco iniziale.
- In questa analisi non emergono finestre costose, cioe' casi in cui RSI65 elimina un trade Baseline vincente.
- Prima di promuovere il filtro serve ancora una validazione annuale/costi e un controllo che la soglia non sia troppo dipendente da pochi eventi.
