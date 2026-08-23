# Breakout precoce - RSI e conferma del prezzo

Data test: `2026-08-23`. Cutoff: `2026-08-22`.
Mercato: `ETH-USD` Coinbase, candele daily UTC chiuse.
Commissione principale: taker `0,16%` per lato.
La Baseline ufficiale, il bot e la dashboard non sono stati modificati.

## Domande verificate

1. Togliere il limite RSI 65 e conservare soltanto RSI >= 40.
2. Sostituire momentum7 + massimo5 con Close sopra la media dei sette
   Close precedenti.
3. Unire le due conferme con Close sopra il massimo dei sette Close
   precedenti.

Tutte le altre condizioni del breakout restano congelate: SMA50<=SMA200,
Close>SMA50, Close non oltre 10% sotto SMA200, SMA50 non in calo in 5g
e volume almeno 20% sopra la media20. Dopo l'ingresso valgono soltanto
le uscite ufficiali della Baseline.

## Metriche principali

Il periodo `pre-evento` termina il 16 agosto 2026 e non beneficia del
movimento che ha generato questa ricerca.

| Variante | Ann. pre | DD pre | Sharpe pre | Ann. completo | DD completo | Sharpe completo | Trade completati | PF | Ingressi breakout | Perdite breakout | Entry che copre evento | Cattura 19/8 | Rendimento evento |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Baseline ufficiale | 97.65% | -39.87% | 1.666 | 97.42% | -39.87% | 1.665 | 30 | 15.995 | 0 | 0 | - | NO | 0.00% |
| Attuale: RSI 40-65, momentum7 e massimo5 | 120.64% | -36.56% | 1.833 | 125.74% | -36.56% | 1.869 | 33 | 16.830 | 6 | 1 | 2026-08-17 | SI | 26.48% |
| RSI >=40, momentum7 e massimo5 | 125.29% | -36.56% | 1.835 | 130.49% | -36.56% | 1.870 | 38 | 13.005 | 12 | 5 | 2026-08-17 | SI | 26.48% |
| RSI 40-65, Close sopra media7 precedente | 115.79% | -39.17% | 1.755 | 121.28% | -39.17% | 1.796 | 39 | 11.012 | 13 | 6 | 2026-07-28 | SI | 29.23% |
| Proposta: RSI >=40 e Close sopra media7 precedente | 118.08% | -38.66% | 1.760 | 123.62% | -38.66% | 1.800 | 40 | 10.953 | 14 | 7 | 2026-07-28 | SI | 29.23% |
| RSI 40-65, Close sopra massimo7 precedente | 120.64% | -36.56% | 1.833 | 125.74% | -36.56% | 1.869 | 33 | 16.830 | 6 | 1 | 2026-08-17 | SI | 26.48% |
| RSI >=40 e Close sopra massimo7 precedente | 125.29% | -36.56% | 1.835 | 130.49% | -36.56% | 1.870 | 38 | 13.005 | 12 | 5 | 2026-08-17 | SI | 26.48% |

## Date degli ingressi breakout

- **Attuale: RSI 40-65, momentum7 e massimo5**: 2017-02-01, 2019-03-27, 2023-01-06, 2024-11-06, 2026-01-13, 2026-08-17.
- **RSI >=40, momentum7 e massimo5**: 2017-02-01, 2018-05-03, 2019-03-27, 2020-01-15, 2022-03-28, 2023-01-06, 2023-10-24, 2024-11-06, 2025-05-13, 2025-06-10, 2026-01-06, 2026-08-17.
- **RSI 40-65, Close sopra media7 precedente**: 2017-02-01, 2018-05-07, 2018-05-14, 2019-03-27, 2020-01-19, 2020-05-07, 2023-01-06, 2023-11-20, 2024-11-06, 2025-05-29, 2025-06-11, 2026-01-13, 2026-07-28.
- **Proposta: RSI >=40 e Close sopra media7 precedente**: 2017-02-01, 2018-05-03, 2018-05-14, 2019-03-27, 2020-01-15, 2020-05-07, 2022-03-28, 2023-01-06, 2023-10-24, 2024-11-06, 2025-05-12, 2025-06-10, 2026-01-06, 2026-07-28.
- **RSI 40-65, Close sopra massimo7 precedente**: 2017-02-01, 2019-03-27, 2023-01-06, 2024-11-06, 2026-01-13, 2026-08-17.
- **RSI >=40 e Close sopra massimo7 precedente**: 2017-02-01, 2018-05-03, 2019-03-27, 2020-01-15, 2022-03-28, 2023-01-06, 2023-10-24, 2024-11-06, 2025-05-13, 2025-06-10, 2026-01-06, 2026-08-17.

Il segnale e' calcolato sul Close della data indicata; l'esposizione
prudenziale viene applicata al rendimento della candela successiva.

## Operazioni breakout delle varianti principali

| Variante | Segnale | Close | Uscita | Prezzo uscita | Motivo | Netto | DD trade | Baseline compra dopo |
|---|---|---:|---|---:|---|---:|---:|---|
| current_rsi40_65_mom7_high5 | 2017-02-01 | 10.72 | 2017-03-08 | 16.68 | trail8_exit | 55.10% | -15.24% | 2017-03-18 |
| current_rsi40_65_mom7_high5 | 2019-03-27 | 139.08 | 2019-04-11 | 164.92 | trail8_exit | 18.20% | -8.75% | 2019-04-23 |
| current_rsi40_65_mom7_high5 | 2023-01-06 | 1268.84 | 2023-03-03 | 1569.54 | sma50_exit | 23.30% | -9.87% | 2023-02-15 |
| current_rsi40_65_mom7_high5 | 2024-11-06 | 2724.27 | 2024-12-18 | 3624.84 | trail8_exit | 32.63% | -9.53% | 2024-12-09 |
| current_rsi40_65_mom7_high5 | 2026-01-13 | 3323.38 | 2026-01-20 | 2936.50 | sma50_exit | -11.92% | -12.47% | - |
| current_rsi40_65_mom7_high5 | 2026-08-17 | 1911.94 | - | - | aperto | 26.47% | -3.73% | - |
| rsi40_mom7_high5 | 2017-02-01 | 10.72 | 2017-03-08 | 16.68 | trail8_exit | 55.10% | -15.24% | 2017-03-18 |
| rsi40_mom7_high5 | 2018-05-03 | 775.51 | 2018-05-11 | 678.05 | trail8_exit | -12.85% | -16.50% | 2019-04-23 |
| rsi40_mom7_high5 | 2019-03-27 | 139.08 | 2019-04-11 | 164.92 | trail8_exit | 18.20% | -8.75% | 2019-04-23 |
| rsi40_mom7_high5 | 2020-01-15 | 166.29 | 2020-02-19 | 258.66 | trail8_exit | 55.05% | -9.70% | 2020-05-28 |
| rsi40_mom7_high5 | 2022-03-28 | 3334.47 | 2022-04-06 | 3168.52 | trail8_exit | -5.28% | -10.06% | 2023-02-15 |
| rsi40_mom7_high5 | 2023-01-06 | 1268.84 | 2023-03-03 | 1569.54 | sma50_exit | 23.30% | -9.87% | 2023-02-15 |
| rsi40_mom7_high5 | 2023-10-24 | 1785.28 | 2024-01-23 | 2240.81 | sma50_exit | 25.11% | -14.42% | 2023-11-22 |
| rsi40_mom7_high5 | 2024-11-06 | 2724.27 | 2024-12-18 | 3624.84 | trail8_exit | 32.63% | -9.53% | 2024-12-09 |
| rsi40_mom7_high5 | 2025-05-13 | 2679.88 | 2025-06-05 | 2415.34 | trail8_exit | -10.16% | -9.95% | 2025-07-02 |
| rsi40_mom7_high5 | 2025-06-10 | 2816.50 | 2025-06-13 | 2580.21 | trail8_exit | -8.68% | -8.39% | 2025-07-02 |
| rsi40_mom7_high5 | 2026-01-06 | 3295.59 | 2026-01-20 | 2936.50 | sma50_exit | -11.18% | -12.47% | - |
| rsi40_mom7_high5 | 2026-08-17 | 1911.94 | - | - | aperto | 26.47% | -3.73% | - |
| rsi40_65_mean7 | 2017-02-01 | 10.72 | 2017-03-08 | 16.68 | trail8_exit | 55.10% | -15.24% | 2017-03-18 |
| rsi40_65_mean7 | 2018-05-07 | 752.42 | 2018-05-11 | 678.05 | trail8_exit | -10.17% | -9.88% | 2019-04-23 |
| rsi40_65_mean7 | 2018-05-14 | 726.90 | 2018-05-23 | 577.20 | sma50_exit | -20.85% | -20.59% | 2019-04-23 |
| rsi40_65_mean7 | 2019-03-27 | 139.08 | 2019-04-11 | 164.92 | trail8_exit | 18.20% | -8.75% | 2019-04-23 |
| rsi40_65_mean7 | 2020-01-19 | 166.75 | 2020-02-19 | 258.66 | trail8_exit | 54.62% | -9.70% | 2020-05-28 |
| rsi40_65_mean7 | 2020-05-07 | 212.47 | 2020-05-10 | 187.73 | trail8_exit | -11.93% | -11.64% | 2020-05-28 |
| rsi40_65_mean7 | 2023-01-06 | 1268.84 | 2023-03-03 | 1569.54 | sma50_exit | 23.30% | -9.87% | 2023-02-15 |
| rsi40_65_mean7 | 2023-11-20 | 2022.55 | 2024-01-23 | 2240.81 | sma50_exit | 10.44% | -14.42% | 2023-11-22 |
| rsi40_65_mean7 | 2024-11-06 | 2724.27 | 2024-12-18 | 3624.84 | trail8_exit | 32.63% | -9.53% | 2024-12-09 |
| rsi40_65_mean7 | 2025-05-29 | 2631.68 | 2025-06-05 | 2415.34 | trail8_exit | -8.51% | -8.22% | 2025-07-02 |
| rsi40_65_mean7 | 2025-06-11 | 2772.39 | 2025-06-16 | 2545.27 | trail8_exit | -8.49% | -8.67% | 2025-07-02 |
| rsi40_65_mean7 | 2026-01-13 | 3323.38 | 2026-01-20 | 2936.50 | sma50_exit | -11.92% | -12.47% | - |
| rsi40_65_mean7 | 2026-07-28 | 1919.90 | - | - | aperto | 25.95% | -4.00% | - |
| rsi40_mean7 | 2017-02-01 | 10.72 | 2017-03-08 | 16.68 | trail8_exit | 55.10% | -15.24% | 2017-03-18 |
| rsi40_mean7 | 2018-05-03 | 775.51 | 2018-05-11 | 678.05 | trail8_exit | -12.85% | -16.50% | 2019-04-23 |
| rsi40_mean7 | 2018-05-14 | 726.90 | 2018-05-23 | 577.20 | sma50_exit | -20.85% | -20.59% | 2019-04-23 |
| rsi40_mean7 | 2019-03-27 | 139.08 | 2019-04-11 | 164.92 | trail8_exit | 18.20% | -8.75% | 2019-04-23 |
| rsi40_mean7 | 2020-01-15 | 166.29 | 2020-02-19 | 258.66 | trail8_exit | 55.05% | -9.70% | 2020-05-28 |
| rsi40_mean7 | 2020-05-07 | 212.47 | 2020-05-10 | 187.73 | trail8_exit | -11.93% | -11.64% | 2020-05-28 |
| rsi40_mean7 | 2022-03-28 | 3334.47 | 2022-04-06 | 3168.52 | trail8_exit | -5.28% | -10.06% | 2023-02-15 |
| rsi40_mean7 | 2023-01-06 | 1268.84 | 2023-03-03 | 1569.54 | sma50_exit | 23.30% | -9.87% | 2023-02-15 |
| rsi40_mean7 | 2023-10-24 | 1785.28 | 2024-01-23 | 2240.81 | sma50_exit | 25.11% | -14.42% | 2023-11-22 |
| rsi40_mean7 | 2024-11-06 | 2724.27 | 2024-12-18 | 3624.84 | trail8_exit | 32.63% | -9.53% | 2024-12-09 |
| rsi40_mean7 | 2025-05-12 | 2495.83 | 2025-06-05 | 2415.34 | trail8_exit | -3.53% | -9.95% | 2025-07-02 |
| rsi40_mean7 | 2025-06-10 | 2816.50 | 2025-06-13 | 2580.21 | trail8_exit | -8.68% | -8.39% | 2025-07-02 |
| rsi40_mean7 | 2026-01-06 | 3295.59 | 2026-01-20 | 2936.50 | sma50_exit | -11.18% | -12.47% | - |
| rsi40_mean7 | 2026-07-28 | 1919.90 | - | - | aperto | 25.95% | -4.00% | - |
| rsi40_65_high7 | 2017-02-01 | 10.72 | 2017-03-08 | 16.68 | trail8_exit | 55.10% | -15.24% | 2017-03-18 |
| rsi40_65_high7 | 2019-03-27 | 139.08 | 2019-04-11 | 164.92 | trail8_exit | 18.20% | -8.75% | 2019-04-23 |
| rsi40_65_high7 | 2023-01-06 | 1268.84 | 2023-03-03 | 1569.54 | sma50_exit | 23.30% | -9.87% | 2023-02-15 |
| rsi40_65_high7 | 2024-11-06 | 2724.27 | 2024-12-18 | 3624.84 | trail8_exit | 32.63% | -9.53% | 2024-12-09 |
| rsi40_65_high7 | 2026-01-13 | 3323.38 | 2026-01-20 | 2936.50 | sma50_exit | -11.92% | -12.47% | - |
| rsi40_65_high7 | 2026-08-17 | 1911.94 | - | - | aperto | 26.47% | -3.73% | - |
| rsi40_high7 | 2017-02-01 | 10.72 | 2017-03-08 | 16.68 | trail8_exit | 55.10% | -15.24% | 2017-03-18 |
| rsi40_high7 | 2018-05-03 | 775.51 | 2018-05-11 | 678.05 | trail8_exit | -12.85% | -16.50% | 2019-04-23 |
| rsi40_high7 | 2019-03-27 | 139.08 | 2019-04-11 | 164.92 | trail8_exit | 18.20% | -8.75% | 2019-04-23 |
| rsi40_high7 | 2020-01-15 | 166.29 | 2020-02-19 | 258.66 | trail8_exit | 55.05% | -9.70% | 2020-05-28 |
| rsi40_high7 | 2022-03-28 | 3334.47 | 2022-04-06 | 3168.52 | trail8_exit | -5.28% | -10.06% | 2023-02-15 |
| rsi40_high7 | 2023-01-06 | 1268.84 | 2023-03-03 | 1569.54 | sma50_exit | 23.30% | -9.87% | 2023-02-15 |
| rsi40_high7 | 2023-10-24 | 1785.28 | 2024-01-23 | 2240.81 | sma50_exit | 25.11% | -14.42% | 2023-11-22 |
| rsi40_high7 | 2024-11-06 | 2724.27 | 2024-12-18 | 3624.84 | trail8_exit | 32.63% | -9.53% | 2024-12-09 |
| rsi40_high7 | 2025-05-13 | 2679.88 | 2025-06-05 | 2415.34 | trail8_exit | -10.16% | -9.95% | 2025-07-02 |
| rsi40_high7 | 2025-06-10 | 2816.50 | 2025-06-13 | 2580.21 | trail8_exit | -8.68% | -8.39% | 2025-07-02 |
| rsi40_high7 | 2026-01-06 | 3295.59 | 2026-01-20 | 2936.50 | sma50_exit | -11.18% | -12.47% | - |
| rsi40_high7 | 2026-08-17 | 1911.94 | - | - | aperto | 26.47% | -3.73% | - |

## Stabilita temporale pre-evento

| Variante | Ann. fino 2019 | DD fino 2019 | Sharpe fino 2019 | Ann. 2020-16/8/2026 | DD 2020-16/8/2026 | Sharpe 2020-16/8/2026 |
|---|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 174.49% | -30.08% | 2.041 | 69.86% | -39.87% | 1.462 |
| Attuale: RSI 40-65, momentum7 e massimo5 | 234.55% | -30.08% | 2.289 | 82.09% | -36.56% | 1.580 |
| RSI >=40, momentum7 e massimo5 | 219.86% | -30.08% | 2.207 | 91.67% | -36.56% | 1.635 |
| RSI 40-65, Close sopra media7 precedente | 199.29% | -36.56% | 2.083 | 85.57% | -39.17% | 1.581 |
| Proposta: RSI >=40 e Close sopra media7 precedente | 196.35% | -38.45% | 2.064 | 89.33% | -38.66% | 1.601 |
| RSI 40-65, Close sopra massimo7 precedente | 234.55% | -30.08% | 2.289 | 82.09% | -36.56% | 1.580 |
| RSI >=40 e Close sopra massimo7 precedente | 219.86% | -30.08% | 2.207 | 91.67% | -36.56% | 1.635 |

## Costi e ritardo

| Variante | Ann. taker pre | Ann. stress pre | Evento senza ritardo extra | Evento con 2 giorni extra |
|---|---:|---:|---:|---:|
| Baseline ufficiale | 97.65% | 92.37% | 0.00% | 0.00% |
| Attuale: RSI 40-65, momentum7 e massimo5 | 120.64% | 114.17% | 26.48% | 7.40% |
| RSI >=40, momentum7 e massimo5 | 125.29% | 117.68% | 26.48% | 7.40% |
| RSI 40-65, Close sopra media7 precedente | 115.79% | 108.20% | 29.23% | 29.23% |
| Proposta: RSI >=40 e Close sopra media7 precedente | 118.08% | 110.24% | 29.23% | 29.23% |
| RSI 40-65, Close sopra massimo7 precedente | 120.64% | 114.17% | 26.48% | 7.40% |
| RSI >=40 e Close sopra massimo7 precedente | 125.29% | 117.68% | 26.48% | 7.40% |

## Controlli statistici

- configurazioni testate: `13`; percorsi pre-evento distinti: `10`;
- PBO/CSCV: `82.54%`; rango mediano fuori campione `36.36%`;
- DSR, probabilita' incrementale e bootstrap per ciascuna variante
  principale sono disponibili nel CSV statistico;
- le configurazioni diagnostiche e le sensibilita' 5/10 giorni sono
  riportate integralmente nei CSV metriche, ingressi e trigger.

Confronto diretto contro il candidato attuale, sempre fino al 16 agosto:

| Variante | PSR vantaggio | Bootstrap 30g: prob. migliore | P05 30g | Bootstrap 90g: prob. migliore | P05 90g |
|---|---:|---:|---:|---:|---:|
| RSI >=40, momentum7 e massimo5 | 76.77% | 63.10% | -39.25% | 63.75% | -41.90% |
| RSI 40-65, Close sopra media7 precedente | 33.32% | 33.60% | -64.65% | 33.60% | -68.09% |
| Proposta: RSI >=40 e Close sopra media7 precedente | 48.31% | 41.00% | -63.25% | 40.95% | -66.62% |
| RSI 40-65, Close sopra massimo7 precedente | IDENTICO | IDENTICO | 0.00% | IDENTICO | 0.00% |
| RSI >=40 e Close sopra massimo7 precedente | 76.77% | 63.10% | -39.25% | 63.75% | -41.90% |

## Lettura prudenziale

- un numero maggiore di ingressi non costituisce automaticamente un
  miglioramento: va letto insieme a drawdown, Sharpe e nuove perdite;
- la media7 misura recupero sopra la tendenza breve, non un vero breakout;
- il massimo7 conserva la natura di breakout e fonde le vecchie condizioni
  in una formula unica, ma puo' essere piu' selettivo;
- nessuna variante viene promossa automaticamente da questo test.

## Conclusioni del test

- `Close > massimo dei 7 Close precedenti`, mantenendo RSI 40-65,
  produce esattamente gli stessi segnali e le stesse metriche del
  candidato attuale: nello storico disponibile e' una semplificazione
  equivalente di momentum7 + massimo5;
- eliminare il tetto RSI porta l'annualizzato pre-evento da 120,64% a
  125,29%, ma lo Sharpe resta praticamente fermo (1,833 -> 1,835),
  gli ingressi breakout raddoppiano da 6 a 12 e le perdite passano da
  1 a 5; il profit factor complessivo scende da 16,830 a 13,005;
  il bootstrap diretto gli assegna soltanto circa 63% di probabilita'
  di battere il candidato attuale, con percentile 5% fortemente negativo;
- la proposta `RSI >=40 + Close sopra media7` cattura il movimento
  corrente da una posizione aperta il 28 luglio, ma prima dell'evento
  riduce annualizzato, drawdown e Sharpe rispetto al candidato attuale
  e porta le perdite breakout da 1 a 7;
  anche PSR e bootstrap diretti non mostrano un vantaggio sul candidato;
- il PBO elevato segnala che scegliere ora la variante col rendimento
  piu' alto sarebbe fragile. Il massimo7 puo' restare come formulazione
  equivalente da monitorare; RSI senza tetto resta una variante shadow;
  la media7 non e' candidata alla sostituzione.

## File completi

- `reports/breakout_rsi_confirmation_metrics.csv`;
- `reports/breakout_rsi_confirmation_entries.csv`;
- `reports/breakout_rsi_confirmation_triggers.csv`;
- `reports/breakout_rsi_confirmation_yearly.csv`;
- `reports/breakout_rsi_confirmation_costs.csv`;
- `reports/breakout_rsi_confirmation_delays.csv`;
- `reports/breakout_rsi_confirmation_statistics.csv`.
