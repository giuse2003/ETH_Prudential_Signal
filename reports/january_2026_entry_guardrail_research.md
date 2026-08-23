# Guardrail ingresso breakout - caso gennaio 2026

Data test: `2026-08-22`. Mercato: `ETH-USD Coinbase`, candele daily UTC.
Commissione principale: taker `0,16%` per lato.
La Baseline ufficiale, il bot e la dashboard non sono stati modificati.

## Obiettivo

Evitare gli ingressi breakout del 6 e 13 gennaio 2026 usando soltanto
informazioni disponibili alla chiusura della candela, senza una regola
legata alla data e senza perdere gli episodi breakout storicamente favorevoli.

## Diagnosi ex ante di gennaio 2026

| Data | Close | RSI | SMA200 slope 20g | SMA50/SMA200 | Return 90g |
|---|---:|---:|---:|---:|---:|
| 2026-01-06 | 3295.59 | 68.55 | 1.24% | -16.50% | -27.21% |
| 2026-01-13 | 3323.38 | 64.75 | 1.57% | -16.17% | -16.66% |

Entrambe le date presentano lo stesso regime: SMA200 ancora crescente
e SMA50 oltre il 15% sotto SMA200. Il rendimento a 90 giorni e' inoltre
fortemente negativo. Il 6 gennaio ha RSI sopra 65; il 13 gennaio rientra
nel corridoio 40-65, quindi il solo tetto RSI non elimina l'episodio.

## Regole confrontate

- principale: `slope_gap__sp0p0__gm15p0` - Blocca se insieme: slope SMA200 20g > 0.0% e SMA50/SMA200 < -15.0%;
- controllo a tre fattori: `risk2of3__sp0p0__gm15p0__rm10p0` - Blocca con almeno 2 rischi: slope SMA200 20g > 0.0%, SMA50/SMA200 < -15.0%, return 90g < -10.0%;
- griglia completa: filtri singoli, coppie e due rischi su tre, con
  soglie adiacenti su slope SMA200, distanza SMA50/SMA200 e return 90g.

Il filtro viene applicato solo al nuovo percorso breakout. Le entrate
e le uscite ufficiali conservano esattamente le regole correnti.

## Confronto principale

| Sistema ingresso | Guardrail | Rendimento totale | Annualizzato | Max DD | Sharpe | Profit factor | Operazioni | Breakout loss | Entry gennaio | Return gennaio | Cattura 17/08 | Episodi favorevoli persi |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---:|
| current_rsi40_65_mom7_high5 | none | 271202.84% | 125.74% | -36.56% | 1.869 | 16.830 | 33 | 1 | 2026-01-13 | -11.92% | SI | 0 |
| current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | 307926.92% | 128.71% | -36.56% | 1.897 | 19.020 | 32 | 0 | - | - | SI | 0 |
| current_rsi40_65_mom7_high5 | risk2of3__sp0p0__gm15p0__rm10p0 | 307926.92% | 128.71% | -36.56% | 1.897 | 19.020 | 32 | 0 | - | - | SI | 0 |
| rsi40_mom7_high5 | none | 331993.15% | 130.49% | -36.56% | 1.870 | 13.005 | 38 | 5 | 2026-01-06 | -11.18% | SI | 0 |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 428934.67% | 136.65% | -36.56% | 1.928 | 15.709 | 36 | 3 | - | - | SI | 0 |
| rsi40_mom7_high5 | risk2of3__sp0p0__gm15p0__rm10p0 | 413774.96% | 135.78% | -36.56% | 1.922 | 15.261 | 36 | 3 | - | - | SI | 0 |

## Migliori configurazioni ammissibili

Ammissibile significa: blocca gennaio in entrambi i sistemi, conserva
il movimento del 17 agosto e non perde episodi breakout favorevoli pregressi.

| Guardrail | Famiglia | Delta ann. storico peggiore | Delta Sharpe storico peggiore | Ann. medio totale | DD medio totale | Sharpe medio totale |
|---|---|---:|---:|---:|---:|---:|
| gap_return90__gm16p0__rm7p5 | gap_return90 | 0.00% | 0.000 | 133.35% | -36.56% | 1.920 |
| gap_return90__gm15p0__rm7p5 | gap_return90 | 0.00% | 0.000 | 133.35% | -36.56% | 1.920 |
| gap_return90__gm14p0__rm7p5 | gap_return90 | 0.00% | 0.000 | 133.35% | -36.56% | 1.920 |
| gap_return90__gm13p0__rm7p5 | gap_return90 | 0.00% | 0.000 | 133.35% | -36.56% | 1.920 |
| gap__gm16p0 | gap | 0.00% | 0.000 | 132.16% | -36.56% | 1.915 |
| gap__gm15p5 | gap | 0.00% | 0.000 | 132.16% | -36.56% | 1.915 |
| gap__gm15p0 | gap | 0.00% | 0.000 | 132.16% | -36.56% | 1.915 |
| gap__gm14p5 | gap | 0.00% | 0.000 | 132.16% | -36.56% | 1.915 |
| slope__sm1p0 | slope | 0.00% | 0.000 | 132.68% | -36.56% | 1.913 |
| slope__sp0p0 | slope | 0.00% | 0.000 | 132.68% | -36.56% | 1.913 |
| slope__sp0p5 | slope | 0.00% | 0.000 | 132.68% | -36.56% | 1.913 |
| slope__sp1p0 | slope | 0.00% | 0.000 | 132.68% | -36.56% | 1.913 |

## Stabilita' intorno alla regola principale

| Guardrail | Evita gennaio | Cattura agosto | Episodi persi | Delta ann. storico peggiore |
|---|---|---|---:|---:|
| slope_gap__sm1p0__gm14p0 | SI | SI | 0 | 0.00% |
| slope_gap__sm1p0__gm15p0 | SI | SI | 0 | 0.00% |
| slope_gap__sm1p0__gm16p0 | SI | SI | 0 | 0.00% |
| slope_gap__sp0p0__gm14p0 | SI | SI | 0 | 0.00% |
| slope_gap__sp0p0__gm15p0 | SI | SI | 0 | 0.00% |
| slope_gap__sp0p0__gm16p0 | SI | SI | 0 | 0.00% |
| slope_gap__sp1p0__gm14p0 | SI | SI | 0 | 0.00% |
| slope_gap__sp1p0__gm15p0 | SI | SI | 0 | 0.00% |
| slope_gap__sp1p0__gm16p0 | SI | SI | 0 | 0.00% |

## Cronologia breakout senza filtro e con guardrail principale

| Sistema | Guardrail | Ingresso | Uscita | Esito | Rendimento netto |
|---|---|---|---|---|---:|
| current_rsi40_65_mom7_high5 | none | 2017-02-01 | 2017-03-08 | closed | 55.10% |
| current_rsi40_65_mom7_high5 | none | 2019-03-27 | 2019-04-11 | closed | 18.20% |
| current_rsi40_65_mom7_high5 | none | 2023-01-06 | 2023-03-03 | closed | 23.30% |
| current_rsi40_65_mom7_high5 | none | 2024-11-06 | 2024-12-18 | closed | 32.63% |
| current_rsi40_65_mom7_high5 | none | 2026-01-13 | 2026-01-20 | closed | -11.92% |
| current_rsi40_65_mom7_high5 | none | 2026-08-17 | - | open | 26.47% |
| current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2017-02-01 | 2017-03-08 | closed | 55.10% |
| current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2019-03-27 | 2019-04-11 | closed | 18.20% |
| current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2023-01-06 | 2023-03-03 | closed | 23.30% |
| current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2024-11-06 | 2024-12-18 | closed | 32.63% |
| current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2026-08-17 | - | open | 26.47% |
| rsi40_mom7_high5 | none | 2017-02-01 | 2017-03-08 | closed | 55.10% |
| rsi40_mom7_high5 | none | 2018-05-03 | 2018-05-11 | closed | -12.85% |
| rsi40_mom7_high5 | none | 2019-03-27 | 2019-04-11 | closed | 18.20% |
| rsi40_mom7_high5 | none | 2020-01-15 | 2020-02-19 | closed | 55.05% |
| rsi40_mom7_high5 | none | 2022-03-28 | 2022-04-06 | closed | -5.28% |
| rsi40_mom7_high5 | none | 2023-01-06 | 2023-03-03 | closed | 23.30% |
| rsi40_mom7_high5 | none | 2023-10-24 | 2024-01-23 | closed | 25.11% |
| rsi40_mom7_high5 | none | 2024-11-06 | 2024-12-18 | closed | 32.63% |
| rsi40_mom7_high5 | none | 2025-05-13 | 2025-06-05 | closed | -10.16% |
| rsi40_mom7_high5 | none | 2025-06-10 | 2025-06-13 | closed | -8.68% |
| rsi40_mom7_high5 | none | 2026-01-06 | 2026-01-20 | closed | -11.18% |
| rsi40_mom7_high5 | none | 2026-08-17 | - | open | 26.47% |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2017-02-01 | 2017-03-08 | closed | 55.10% |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2019-03-27 | 2019-04-11 | closed | 18.20% |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2020-01-15 | 2020-02-19 | closed | 55.05% |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2022-03-28 | 2022-04-06 | closed | -5.28% |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2023-01-06 | 2023-03-03 | closed | 23.30% |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2023-10-24 | 2024-01-23 | closed | 25.11% |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2024-11-06 | 2024-12-18 | closed | 32.63% |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2025-05-13 | 2025-06-05 | closed | -10.16% |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2025-06-10 | 2025-06-13 | closed | -8.68% |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 2026-08-17 | - | open | 26.47% |

## Costi e ritardi - guardrail principale

| Sistema | Test | Scenario | Ann. | Max DD | Sharpe |
|---|---|---|---:|---:|---:|
| current_rsi40_65_mom7_high5 | cost | maker_0_07pct | 130.08% | -36.04% | 1.909 |
| current_rsi40_65_mom7_high5 | cost | taker_0_16pct | 128.71% | -36.56% | 1.897 |
| current_rsi40_65_mom7_high5 | cost | stress_0_60pct | 122.12% | -39.05% | 1.839 |
| current_rsi40_65_mom7_high5 | delay | extra_delay_0 | 128.71% | -36.56% | 1.897 |
| current_rsi40_65_mom7_high5 | delay | extra_delay_1 | 110.85% | -38.61% | 1.753 |
| current_rsi40_65_mom7_high5 | delay | extra_delay_2 | 109.87% | -39.84% | 1.743 |
| rsi40_mom7_high5 | cost | maker_0_07pct | 138.25% | -36.04% | 1.941 |
| rsi40_mom7_high5 | cost | taker_0_16pct | 136.65% | -36.56% | 1.928 |
| rsi40_mom7_high5 | cost | stress_0_60pct | 128.99% | -39.05% | 1.865 |
| rsi40_mom7_high5 | delay | extra_delay_0 | 136.65% | -36.56% | 1.928 |
| rsi40_mom7_high5 | delay | extra_delay_1 | 119.40% | -39.98% | 1.799 |
| rsi40_mom7_high5 | delay | extra_delay_2 | 120.41% | -39.84% | 1.808 |

## Conclusione

- la regola principale evita entrambe le entrate di gennaio: SI;
- conserva il movimento del 17 agosto: SI;
- conserva gli episodi favorevoli precedenti: SI;
- il miglioramento dopo gennaio e' in-sample rispetto al problema osservato
  e non basta, da solo, per una promozione ufficiale;
- il dato piu' importante e' il comportamento fino al 5 gennaio 2026:
  misura il costo storico del filtro prima del caso che lo ha motivato;
- nel sistema RSI 40-65 il guardrail modifica una sola operazione storica,
  proprio gennaio 2026; nel sistema RSI >=40 elimina anche l'ingresso
  indipendente del 3 maggio 2018, chiuso a -12,85%; il campione resta
  quindi troppo piccolo per parlare di validazione definitiva;
- decisione: guardrail candidato shadow. Baseline invariata.

## File generati

- `reports/january_2026_entry_guardrail_grid.csv`;
- `reports/january_2026_entry_guardrail_trades.csv`;
- `reports/january_2026_entry_guardrail_yearly.csv`;
- `reports/january_2026_entry_guardrail_robustness.csv`;
- `reports/january_2026_entry_guardrail_entry_features.csv`.
