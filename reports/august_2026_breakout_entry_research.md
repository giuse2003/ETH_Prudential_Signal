# Ricerca ingresso breakout agosto 2026

Data test: `2026-08-22`. Cutoff: `2026-08-21`.
Mercato: `ETH-USD` Coinbase, candele daily UTC chiuse.
La Baseline ufficiale non e' stata modificata.

## Caso osservato

Dal Close del 16 agosto al cutoff ETH-USD e' salito di `34.24%`.

| Data | Close USD | SMA50 | SMA200 | RSI | Mom. 7g | Volume rel. | Slope SMA50 5g | Dist. SMA200 | Breakout 7g |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-08-16 | 1874.13 | 1836.25 | 2012.81 | 49.69 | -1.83% | -73.28% | 1.55% | -6.89% | -1.83% |
| 2026-08-17 | 1911.94 | 1843.10 | 2008.28 | 56.61 | 2.16% | 53.06% | 1.69% | -4.80% | 1.45% |
| 2026-08-18 | 1916.72 | 1849.22 | 2004.35 | 57.41 | 1.91% | 24.99% | 1.73% | -4.37% | 0.25% |
| 2026-08-19 | 2251.69 | 1862.87 | 2003.36 | 82.16 | 19.92% | 348.67% | 2.12% | 12.40% | 17.48% |
| 2026-08-20 | 2326.35 | 1877.24 | 2003.65 | 84.34 | 23.44% | 193.69% | 2.57% | 16.11% | 3.32% |
| 2026-08-21 | 2515.80 | 1893.58 | 2004.50 | 88.27 | 33.79% | 209.88% | 3.12% | 25.51% | 8.14% |

Il 17 agosto erano verdi RSI, momentum, volume e struttura sopra SMA50.
Erano rossi Close>SMA200 e SMA50>SMA200. Il 19 agosto il Close ha
superato SMA200, ma RSI era gia' sopra 82: la Baseline e' quindi rimasta fuori.

## Regole provate

- controlli: rimozione isolata del limite RSI e/o del gate SMA50>SMA200;
- breakout precoce: Close sopra SMA50 e massimo precedente, SMA50 crescente,
  RSI 40-65, volume forte e prezzo non troppo lontano sotto SMA200;
- impulso SMA200: rottura sopra SMA200 con momentum e volume eccezionali,
  consentendo RSI alto;
- uscite sempre identiche alla Baseline: Close 2% sotto SMA50 oppure Trail8
  confermato da momentum >= -15% e volume relativo >= +20%;
- la condizione di ingresso alternativa apre soltanto la posizione: non la
  mantiene e non sospende il Trail8. Dopo l'ingresso vale esclusivamente la
  gestione Baseline, inclusa la priorita' del suo BUY core originale.

## Confronto principale

`Pre-evento` termina il 16 agosto 2026 e impedisce al rialzo studiato
di migliorare artificialmente la valutazione storica della variante.

| Variante | Segnale target | Origine | Cattura candela 19/8 | Evento al cutoff | Ann. pre | DD pre | Sharpe pre | Ann. completo | DD completo | Sharpe completo | Ingressi alternativi | Loss alternativi |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | nessuno | - | NO | 0.00% | 97.65% | -39.87% | 1.666 | 97.46% | -39.87% | 1.665 | 0 | 0 |
| control_rsi_gt40_only | nessuno | - | NO | 0.00% | 120.80% | -39.44% | 1.723 | 120.56% | -39.44% | 1.722 | 8 | 4 |
| control_no_sma50_gate | nessuno | - | NO | 0.00% | 110.77% | -36.56% | 1.741 | 110.54% | -36.56% | 1.740 | 8 | 3 |
| control_no_sma50_no_rsi_cap | 2026-08-19 | relaxed_standard | NO | 11.56% | 134.06% | -43.03% | 1.763 | 136.43% | -43.03% | 1.780 | 19 | 8 |
| early_lb7_vol20_near5_slope0 | 2026-08-17 | early_breakout | SI | 31.37% | 106.81% | -39.87% | 1.740 | 112.48% | -39.87% | 1.786 | 2 | 0 |
| early_lb5_vol20_near10_slope0 | 2026-08-17 | early_breakout | SI | 31.37% | 120.64% | -36.56% | 1.833 | 126.68% | -36.56% | 1.877 | 6 | 1 |
| impulse_mom10_vol200_above | 2026-08-19 | sma200_impulse | NO | 11.56% | 103.60% | -39.87% | 1.701 | 105.70% | -39.87% | 1.721 | 5 | 2 |

## Stabilita della famiglia precoce

- combinazioni testate: `54`; percorsi distinti: `14`;
- combinazioni che catturano la candela principale: `83.33%`;
- combinazioni che migliorano annualizzato, DD e Sharpe prima dell'evento: `42.59%`;
- combinazioni che fanno entrambe le cose: `40.74%`;
- sui soli percorsi distinti, cattura target: `78.57%`.

## Candidato esplorativo selezionato

`early_lb5_vol20_near10_slope0`: Breakout 5g, volume +20%, Close entro 10.0% sotto SMA200, slope SMA50 5g >= 0.0%.

- segnale sul caso corrente: `2026-08-17`;
- rendimento simulato dal segnale al cutoff: `31.37%`;
- prima dell'evento: annualizzato `120.64%`, DD `-36.56%`, Sharpe `1.833`;
- Baseline prima dell'evento: annualizzato `97.65%`, DD `-39.87%`, Sharpe `1.666`;
- ingressi alternativi storici: `6`, di cui `1` chiusi in perdita.

## Regimi precedenti

| Periodo | Modello | Totale | Annualizzato | Max DD | Sharpe |
|---|---|---:|---:|---:|---:|
| 2017-2019 | baseline | 2103.89% | 180.63% | -30.08% | 2.063 |
| 2017-2019 | early_lb5_vol20_near10_slope0 | 3940.32% | 243.53% | -30.08% | 2.314 |
| 2020-2022 | baseline | 2172.69% | 183.26% | -23.39% | 2.192 |
| 2020-2022 | early_lb5_vol20_near10_slope0 | 2172.69% | 183.26% | -23.39% | 2.192 |
| 2023-pre-event | baseline | 47.38% | 11.29% | -39.87% | 0.514 |
| 2023-pre-event | early_lb5_vol20_near10_slope0 | 133.61% | 26.38% | -36.56% | 0.868 |

## Sensibilita ai costi

| Scenario | Modello | Ann. pre | DD pre | Sharpe pre | Ann. completo | DD completo | Sharpe completo |
|---|---|---:|---:|---:|---:|---:|---:|
| maker_0_07pct | baseline | 98.74% | -39.21% | 1.678 | 98.55% | -39.21% | 1.677 |
| maker_0_07pct | early_lb5_vol20_near10_slope0 | 121.99% | -36.14% | 1.845 | 128.08% | -36.14% | 1.889 |
| taker_0_16pct | baseline | 97.65% | -39.87% | 1.666 | 97.46% | -39.87% | 1.665 |
| taker_0_16pct | early_lb5_vol20_near10_slope0 | 120.64% | -36.56% | 1.833 | 126.68% | -36.56% | 1.877 |
| stress_0_60pct | baseline | 92.37% | -43.00% | 1.610 | 92.19% | -43.00% | 1.609 |
| stress_0_60pct | early_lb5_vol20_near10_slope0 | 114.17% | -39.05% | 1.774 | 119.94% | -39.05% | 1.818 |

## Stress ritardo di esecuzione

Il ritardo indicato si aggiunge allo shift prudenziale gia presente nel
backtest ufficiale.

| Ritardo extra | Modello | Evento al cutoff | Ann. pre | DD pre | Sharpe pre | Ann. completo | DD completo | Sharpe completo |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0g | baseline | 0.00% | 97.65% | -39.87% | 1.666 | 97.46% | -39.87% | 1.665 |
| 0g | early_lb5_vol20_near10_slope0 | 31.37% | 120.64% | -36.56% | 1.832 | 126.68% | -36.56% | 1.877 |
| 1g | baseline | 0.00% | 82.95% | -44.38% | 1.522 | 82.79% | -44.38% | 1.521 |
| 1g | early_lb5_vol20_near10_slope0 | 31.08% | 103.53% | -40.15% | 1.688 | 109.08% | -40.15% | 1.734 |
| 2g | baseline | 0.00% | 83.95% | -44.91% | 1.527 | 83.79% | -44.91% | 1.526 |
| 2g | early_lb5_vol20_near10_slope0 | 11.56% | 106.01% | -39.84% | 1.705 | 108.13% | -39.84% | 1.724 |

## Segmenti divergenti dalla Baseline

Ogni riga comprende un periodo continuo in cui i rendimenti giornalieri
del candidato differiscono da quelli della Baseline, inclusi i costi.

| Trigger | Origine | Fine segmento | Buy Baseline successivo | Return candidato | Return Baseline | Vantaggio ricchezza | Stato |
|---|---|---|---|---:|---:|---:|---|
| 2017-02-01 | early_breakout | 2017-03-09 | 2017-03-18 | 55.10% | 0.00% | 55.10% | closed |
| 2019-03-27 | early_breakout | 2019-04-12 | 2019-04-23 | 18.20% | 0.00% | 18.20% | closed |
| 2023-01-06 | early_breakout | 2023-02-16 | 2023-02-15 | 28.87% | -2.37% | 32.00% | closed |
| 2024-11-06 | early_breakout | 2024-12-10 | 2024-12-09 | 33.06% | -2.40% | 36.33% | closed |
| 2026-01-13 | early_breakout | 2026-01-21 | nessuno | -11.92% | 0.00% | -11.92% | closed |
| 2026-08-17 | early_breakout | 2026-08-21 | nessuno | 31.37% | 0.00% | 31.37% | open |

## Controlli statistici pre-evento

| Controllo | Risultato | Lettura secondaria | Percorsi/prove |
|---|---:|---:|---:|
| PBO tutti i percorsi distinti | 19.05% | rank test mediano 77.17% | 22 |
| PBO famiglia breakout precoce | 17.06% | rank test mediano 87.50% | 11 |
| Deflated Sharpe corretto per 71 prove | 100.00% | benchmark Sharpe 0.163 | 71 |
| Probabilita vantaggio incrementale | 99.73% | Sharpe differenziale 0.799 | 2 |
| Bootstrap blocchi 30g | 98.35% | percentile 5% 18.63% | 2 |
| Bootstrap blocchi 90g | 97.35% | percentile 5% 14.39% | 2 |

## Selezione cronologica ancorata

La scelta usa soltanto i rendimenti fino al 31 dicembre 2019; il periodo
2020-16 agosto 2026 viene valutato senza cambiare i parametri.
Variante selezionata dal solo training: `early_lb5_vol20_near10_slope0`.

| Periodo | Modello | Totale | Annualizzato | Max DD | Sharpe |
|---|---|---:|---:|---:|---:|
| train_to_2019 | baseline | 2103.89% | 174.49% | -30.08% | 2.041 |
| train_to_2019 | early_lb5_vol20_near10_slope0 | 3940.32% | 234.55% | -30.08% | 2.289 |
| test_2020_pre_event | baseline | 3249.48% | 69.86% | -39.87% | 1.462 |
| test_2020_pre_event | early_lb5_vol20_near10_slope0 | 5209.23% | 82.09% | -36.56% | 1.580 |

## Interpretazione

- il caso corrente e' conosciuto e ha generato la domanda: non e' un test
  fuori campione e non puo' autorizzare da solo una nuova regola;
- il controllo pre-evento e i regimi precedenti servono a verificare se il
  percorso alternativo aveva gia' comportamento ragionevole prima del caso;
- la selezione resta esplorativa. Nessun segnale ufficiale, dashboard o bot
  viene modificato da questo report.
