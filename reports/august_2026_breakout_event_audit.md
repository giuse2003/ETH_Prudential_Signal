# Audit robustezza degli ingressi breakout

Data test: `2026-08-22`. Cutoff: `2026-08-21`.
Candidato congelato: `early_lb5_vol20_near10_slope0`. Commissione taker `0,16%`.
La Baseline ufficiale non e' stata modificata.

## Eventi

| Entry | Esito | RSI | Mom. 7g | Volume rel. | Dist. SMA200 | SMA50/SMA200 | Return 90g | Breakout 5g | MFE | MAE | Vantaggio vs Baseline |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017-02-01 | favorable | 61.05 | 1.61% | 21.26% | -0.58% | -13.52% | -1.38% | 0.19% | 83.58% | 0.00% | 55.10% |
| 2019-03-27 | favorable | 56.30 | 0.25% | 41.22% | -9.18% | -13.59% | 21.33% | 1.88% | 29.95% | -1.16% | 18.20% |
| 2023-01-06 | favorable | 59.16 | 5.82% | 26.52% | -8.66% | -11.88% | -3.56% | 0.99% | 34.27% | -0.39% | 32.00% |
| 2024-11-06 | favorable | 61.02 | 2.49% | 204.10% | -7.90% | -14.27% | 1.52% | 8.52% | 47.08% | 0.00% | 36.33% |
| 2026-01-13 | negative | 64.75 | 0.84% | 67.73% | -8.63% | -16.17% | -16.66% | 6.56% | 0.95% | -11.64% | -11.92% |
| 2026-08-17 | open | 56.61 | 2.16% | 53.06% | -4.80% | -8.22% | -9.39% | 1.45% | 31.58% | 0.00% | 31.37% |

## Caso negativo del 13 gennaio 2026

Valori che risultano fuori dall'intervallo osservato nei quattro eventi
favorevoli. Sono descrittivi: con un solo caso negativo non costituiscono
una soglia validata.

| Caratteristica | Min favorevoli | Mediana favorevoli | Max favorevoli | 13/01/2026 | 17/08/2026 |
|---|---:|---:|---:|---:|---:|
| rsi | 56.305 | 60.088 | 61.047 | 64.752 | 56.609 |
| sma200_slope_20d | -0.081 | -0.022 | -0.010 | 0.016 | -0.056 |
| sma50_vs_sma200 | -0.143 | -0.136 | -0.119 | -0.162 | -0.082 |
| return_90d | -0.036 | 0.001 | 0.213 | -0.167 | -0.094 |

## Leave-one-event-out

Per ogni riga il rendimento del candidato nel segmento rimosso viene
sostituito con quello della Baseline. Il test termina il 16 agosto 2026.

| Evento rimosso | Annualizzato | Max DD | Sharpe | Delta ann. | Delta DD | Delta Sharpe | Migliora tutte e 3 |
|---|---:|---:|---:|---:|---:|---:|---|
| none | 120.64% | -36.56% | 1.832 | 22.99% | 3.31% | 0.166 | SI |
| 2017-02-01 | 110.88% | -36.56% | 1.762 | 13.23% | 3.31% | 0.096 | SI |
| 2019-03-27 | 116.87% | -36.56% | 1.810 | 19.22% | 3.31% | 0.144 | SI |
| 2023-01-06 | 114.41% | -36.56% | 1.785 | 16.76% | 3.31% | 0.119 | SI |
| 2024-11-06 | 113.70% | -39.87% | 1.782 | 16.05% | -0.00% | 0.116 | SI |
| 2026-01-13 | 123.55% | -36.56% | 1.861 | 25.90% | 3.31% | 0.195 | SI |

## Statistica a livello di eventi

- eventi completati: `5`; favorevoli: `4`; win rate `80.00%`;
- intervallo Wilson 95% del win rate: `37.55%` -> `96.38%`;
- sign test unilaterale contro 50%: p-value `18.75%`;
- vantaggio composto osservato sui cinque segmenti: `190.59%`;
- bootstrap per evento: probabilita' positiva `98.98%`, intervallo 5%-95% `39.90%` -> `471.50%`;
- servirebbero circa `9` perdite consecutive uguali al caso del 13 gennaio per annullare il vantaggio composto storico.

## Stato uscita del trade aperto

Aggiornamento alla candela `2026-08-21`:

- entry candidata `2026-08-17` a `1911.94 USD`;
- massimo Close `2515.80 USD` il `2026-08-21`;
- Trail8 dinamico `2314.54 USD`; Close attuale `2515.80 USD`, distanza `8.70%`;
- momentum 7g `33.79%` (confermato);
- volume relativo `209.88%` (confermato);
- livello uscita SMA50 `1855.71 USD`;
- azione candidata corrente: `MANTIENI STATO ATTUALE`;
- il livello Trail8 verra' ricalcolato su ogni nuovo massimo Close;
  un suo superamento al ribasso produce VENDI soltanto con le conferme
  momentum/volume e con la priorita' BUY originale della Baseline.

## Decisione

- il candidato non dipende da un solo episodio favorevole se il leave-one-out
  continua a migliorare tutte le metriche;
- il campione di cinque eventi completati resta troppo piccolo: il sign test
  non raggiunge significativita' statistica al 5%;
- le differenze del 13 gennaio sono indizi utili, ma trasformarle ora in
  filtri significherebbe ottimizzare una regola su un solo errore;
- ingresso alternativo e uscita sono ora separati nel runner: dopo ACQUISTA
  la gestione e' esclusivamente quella ufficiale della Baseline;
- mantenere congelato il candidato senza modificare la Baseline.
