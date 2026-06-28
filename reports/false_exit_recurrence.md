# False Exit Recurrence Analysis

Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.

Obiettivo: verificare se la falsa uscita di gennaio 2021 si ripete nel tempo.

Definizione di evento tipo gennaio 2021:

- uscita trailing confermata;
- `VENDI` ufficiale successivo a prezzo piu' alto;
- rientro candidato a prezzo piu' alto;
- saldo del segmento peggiore della Baseline di almeno 5 punti percentuali.

## Sintesi Per Variante

| Variante | Uscite | VENDI ufficiale piu' alto | Rientro piu' alto | Segmenti peggiori | Tipo gennaio 2021 |
|---|---:|---:|---:|---:|---:|
| rsi62_mom-6_vol20 | 7 | 1 | 3 | 2 | 1 |
| rsi65_mom-5_vol20 | 5 | 0 | 2 | 1 | 0 |
| rsi65_mom-6_vol20 | 7 | 1 | 3 | 2 | 1 |
| trail_only_mom-6_vol20 | 8 | 1 | 4 | 3 | 1 |

## Eventi Tipo Gennaio 2021

| Variante | Uscita | Entry | Baseline segment | Delta segmento | Rientro | Delta rientro |
|---|---|---|---|---:|---|---:|
| rsi62_mom-6_vol20 | 2021-01-11 | 2020-10-21 | 2020-10-21 -> 2021-02-26 | -42.55% | 2021-01-22 | 13.32% |
| rsi65_mom-6_vol20 | 2021-01-12 | 2020-10-21 | 2020-10-21 -> 2021-02-26 | -57.44% | 2021-01-22 | 18.86% |
| trail_only_mom-6_vol20 | 2021-01-12 | 2020-10-21 | 2020-10-21 -> 2021-02-26 | -89.30% | 2021-01-19 | 32.75% |

## Tutti I Segmenti Peggiori

| Variante | Uscita | Delta segmento | VENDI ufficiale delta | Rientro delta | Lettura |
|---|---|---:|---:|---:|---|
| rsi62_mom-6_vol20 | 2021-01-11 | -42.55% | 33.62% | 13.32% | grave: trend prosegue |
| rsi62_mom-6_vol20 | 2023-04-20 | -0.48% | -5.09% | 0.45% | minore |
| rsi65_mom-5_vol20 | 2023-04-20 | -0.48% | -5.09% | 0.45% | minore |
| rsi65_mom-6_vol20 | 2021-01-12 | -57.44% | 40.15% | 18.86% | grave: trend prosegue |
| rsi65_mom-6_vol20 | 2023-04-20 | -0.48% | -5.09% | 0.45% | minore |
| trail_only_mom-6_vol20 | 2021-01-12 | -89.30% | 40.15% | 32.75% | grave: trend prosegue |
| trail_only_mom-6_vol20 | 2023-04-20 | -0.48% | -5.09% | 0.45% | minore |
| trail_only_mom-6_vol20 | 2024-06-17 | -0.28% | -4.52% | 0.31% | minore |

## Decisione

- Il comportamento grave di gennaio 2021 appare isolato nel campione.
- Si ripete solo come effetto della soglia `momentum >= -6%`; non compare nella variante `momentum >= -5%`.
- Esistono falsi segnali minori, soprattutto 2023-04-20, ma con impatto molto piu' piccolo.
- Quindi gennaio 2021 va trattato come caso speciale di trend parabolico, non come errore ricorrente ordinario.
