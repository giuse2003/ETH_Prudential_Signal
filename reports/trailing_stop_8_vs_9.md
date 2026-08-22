# Trail8 contro Trail9 - Test sperimentale

Data test: `2026-08-22`.
Periodo: `2016-12-08` -> `2026-08-21`.

Il test cambia esclusivamente il trailing stop dall'8% al 9%. Tutte le
condizioni di ingresso, le conferme momentum/volume e l'uscita SMA50 restano invariate.
La Baseline ufficiale non viene modificata.

## Metriche

| Costi | Modello | Totale | Annualizzato | Max DD | Sharpe | PF | Trade | Esposizione |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| taker_0_16pct | Trail8 ufficiale | 73718.82% | 97.46% | -39.87% | 1.665 | 15.995 | 30 | 26.78% |
| taker_0_16pct | Trail9 test | 73252.37% | 97.33% | -39.87% | 1.664 | 15.989 | 30 | 26.83% |
| prudenziale_0_60pct | Trail8 ufficiale | 56672.64% | 92.19% | -43.00% | 1.609 | 14.944 | 30 | 26.78% |
| prudenziale_0_60pct | Trail9 test | 56313.90% | 92.06% | -43.00% | 1.607 | 14.938 | 30 | 26.83% |

## Episodi modificati

Date con segnale diverso: `1`.

| Modello | Entrata | Uscita | Rendimento netto taker | DD trade |
|---|---|---|---:|---:|
| Trail8 ufficiale | 2023-06-20 | 2023-08-02 | 2.41% | -8.33% |
| Trail9 test | 2023-06-20 | 2023-08-04 | 1.77% | -8.91% |

## Uscita 19 agosto 2025

- massimo Close post-ingresso: `4751.46 USD` il `2025-08-13`;
- Close di uscita: `4075.89 USD`;
- discesa dal massimo: `-14.22%`;
- momentum 7 giorni: `-11.20%`;
- volume relativo: `37.27%`;
- sia Trail8 sia Trail9 vendono il 19 agosto 2025;
- il successivo ingresso della Baseline resta il 25 agosto 2025.

## Conclusione

- Trail9 non risolve l'uscita e il rientro di agosto 2025.
- Sull'intera storia cambia soltanto l'uscita del 2 agosto 2023, ritardandola al 4 agosto.
- Quel ritardo riduce leggermente rendimento, Sharpe e profit factor e aumenta il DD del trade.
- Non ci sono elementi per sostituire Trail8 con Trail9.
