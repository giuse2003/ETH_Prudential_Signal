# Validazione temporale cieca del guardrail gennaio 2026

Cutoff complessivo: `2026-08-22`. Selezione congelata al `2026-01-05`.
Mercato: `ETH-USD Coinbase`, candele daily UTC. Commissione taker
`0,16%` per lato. Baseline ufficiale invariata.

## Protocollo

1. La graduatoria vede soltanto dati fino al 5 gennaio 2026.
2. Nessun punteggio usa l'esito del 6/13 gennaio o il movimento di agosto.
3. Sono ammissibili solo regole che non perdono breakout favorevoli, non
   peggiorano annualizzato, drawdown o Sharpe in nessuno dei due sistemi
   e riducono per quanto possibile le perdite breakout pre-2026.
4. Dopo il congelamento viene aperto il blocco 2026.

Avvertenza: slope SMA200, distanza SMA50/SMA200 e return 90g sono stati
scelti dopo aver studiato gennaio. Il replay e' cieco sulle soglie e sugli
esiti 2026, ma non e' un fuori campione incontaminato sulle feature.

## Graduatoria pre-2026

| Rank | Guardrail | Famiglia | Loss breakout | Episodi favorevoli persi | Delta ann. minimo | Delta DD minimo | Delta Sharpe minimo | Ammissibile |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | gap__gm14p5 | gap | 1 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 2 | gap__gm15p0 | gap | 1 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 3 | gap__gm15p5 | gap | 1 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 4 | gap__gm16p0 | gap | 1 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 5 | gap__gm16p5 | gap | 1 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 6 | gap__gm17p0 | gap | 1 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 7 | return90__rm7p5 | return90 | 2 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 8 | gap_return90__gm13p0__rm7p5 | gap_return90 | 2 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 9 | gap_return90__gm14p0__rm7p5 | gap_return90 | 2 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 10 | gap_return90__gm15p0__rm7p5 | gap_return90 | 2 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 11 | gap_return90__gm16p0__rm7p5 | gap_return90 | 2 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 12 | gap_return90__gm17p0__rm7p5 | gap_return90 | 2 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 13 | return90__rm5p0 | return90 | 2 | 0 | 0.00% | 0.00% | 0.000 | SI |
| 14 | gap__gm18p0 | gap | 2 | 0 | 0.00% | -0.00% | 0.000 | SI |
| 15 | return90__rm12p5 | return90 | 3 | 0 | 0.00% | 0.00% | 0.000 | SI |

Prima riga della classe a pari merito: `gap__gm14p5` - Blocca se SMA50/SMA200 < -14.5%.
La classe migliore contiene `6` soglie indistinguibili prima del 2026:
`gap__gm14p5`, `gap__gm15p0`, `gap__gm15p5`, `gap__gm16p0`, `gap__gm16p5`, `gap__gm17p0`.
Il guardrail principale proposto `slope_gap__sp0p0__gm15p0` occupa il rank `33`
ed e' ammissibile
usando esclusivamente il periodo precedente al 2026.

## Apertura del holdout 2026

| Sistema | Guardrail | Entry gennaio | Return gennaio | Cattura agosto | Entry agosto | Annualizzato totale | Max DD | Sharpe |
|---|---|---|---:|---|---|---:|---:|---:|
| current_rsi40_65_mom7_high5 | none | 2026-01-13 | -11.92% | SI | 2026-08-17 | 125.74% | -36.56% | 1.869 |
| current_rsi40_65_mom7_high5 | gap__gm14p5 | - | - | SI | 2026-08-17 | 128.71% | -36.56% | 1.897 |
| current_rsi40_65_mom7_high5 | gap__gm15p0 | - | - | SI | 2026-08-17 | 128.71% | -36.56% | 1.897 |
| current_rsi40_65_mom7_high5 | gap__gm15p5 | - | - | SI | 2026-08-17 | 128.71% | -36.56% | 1.897 |
| current_rsi40_65_mom7_high5 | gap__gm16p0 | - | - | SI | 2026-08-17 | 128.71% | -36.56% | 1.897 |
| current_rsi40_65_mom7_high5 | gap__gm16p5 | 2026-01-13 | -11.92% | SI | 2026-08-17 | 125.74% | -36.56% | 1.869 |
| current_rsi40_65_mom7_high5 | gap__gm17p0 | 2026-01-13 | -11.92% | SI | 2026-08-17 | 125.74% | -36.56% | 1.869 |
| current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | - | - | SI | 2026-08-17 | 128.71% | -36.56% | 1.897 |
| rsi40_mom7_high5 | none | 2026-01-06 | -11.18% | SI | 2026-08-17 | 130.49% | -36.56% | 1.870 |
| rsi40_mom7_high5 | gap__gm14p5 | - | - | SI | 2026-08-17 | 135.61% | -36.56% | 1.933 |
| rsi40_mom7_high5 | gap__gm15p0 | - | - | SI | 2026-08-17 | 135.61% | -36.56% | 1.933 |
| rsi40_mom7_high5 | gap__gm15p5 | - | - | SI | 2026-08-17 | 135.61% | -36.56% | 1.933 |
| rsi40_mom7_high5 | gap__gm16p0 | - | - | SI | 2026-08-17 | 135.61% | -36.56% | 1.933 |
| rsi40_mom7_high5 | gap__gm16p5 | 2026-01-06 | -11.18% | SI | 2026-08-17 | 132.75% | -36.56% | 1.905 |
| rsi40_mom7_high5 | gap__gm17p0 | 2026-01-06 | -11.18% | SI | 2026-08-17 | 132.75% | -36.56% | 1.905 |
| rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | - | - | SI | 2026-08-17 | 136.65% | -36.56% | 1.928 |

## Stabilita' per blocchi temporali del guardrail principale

| Periodo | Sistema | Guardrail | Buy | Rendimento | Max DD | Sharpe |
|---|---|---|---:|---:|---:|---:|
| 2016-2019 | current_rsi40_65_mom7_high5 | none | 9 | 3940.32% | -30.08% | 2.289 |
| 2020-2022 | current_rsi40_65_mom7_high5 | none | 8 | 2172.69% | -23.39% | 2.192 |
| 2023-2025 | current_rsi40_65_mom7_high5 | none | 15 | 165.23% | -36.56% | 1.077 |
| holdout_2026 | current_rsi40_65_mom7_high5 | none | 2 | 11.40% | -12.61% | 0.747 |
| 2016-2019 | current_rsi40_65_mom7_high5 | gap__gm14p5 | 9 | 3940.32% | -30.08% | 2.289 |
| 2020-2022 | current_rsi40_65_mom7_high5 | gap__gm14p5 | 8 | 2172.69% | -23.39% | 2.192 |
| 2023-2025 | current_rsi40_65_mom7_high5 | gap__gm14p5 | 15 | 165.23% | -36.56% | 1.077 |
| holdout_2026 | current_rsi40_65_mom7_high5 | gap__gm14p5 | 1 | 26.48% | -3.73% | 1.588 |
| 2016-2019 | current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | 9 | 3940.32% | -30.08% | 2.289 |
| 2020-2022 | current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | 8 | 2172.69% | -23.39% | 2.192 |
| 2023-2025 | current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | 15 | 165.23% | -36.56% | 1.077 |
| holdout_2026 | current_rsi40_65_mom7_high5 | slope_gap__sp0p0__gm15p0 | 1 | 26.48% | -3.73% | 1.588 |
| 2016-2019 | rsi40_mom7_high5 | none | 10 | 3421.33% | -30.08% | 2.207 |
| 2020-2022 | rsi40_mom7_high5 | none | 10 | 3237.77% | -27.44% | 2.352 |
| 2023-2025 | rsi40_mom7_high5 | none | 17 | 151.54% | -36.56% | 0.990 |
| holdout_2026 | rsi40_mom7_high5 | none | 2 | 12.33% | -12.61% | 0.756 |
| 2016-2019 | rsi40_mom7_high5 | gap__gm14p5 | 9 | 3940.32% | -30.08% | 2.289 |
| 2020-2022 | rsi40_mom7_high5 | gap__gm14p5 | 9 | 2772.62% | -23.39% | 2.292 |
| 2023-2025 | rsi40_mom7_high5 | gap__gm14p5 | 16 | 180.00% | -36.56% | 1.096 |
| holdout_2026 | rsi40_mom7_high5 | gap__gm14p5 | 1 | 26.48% | -3.73% | 1.588 |
| 2016-2019 | rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 9 | 3940.32% | -30.08% | 2.289 |
| 2020-2022 | rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 10 | 3237.77% | -27.44% | 2.352 |
| 2023-2025 | rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 17 | 151.54% | -36.56% | 0.990 |
| holdout_2026 | rsi40_mom7_high5 | slope_gap__sp0p0__gm15p0 | 1 | 26.48% | -3.73% | 1.588 |

## Esito dei gate

- classe cieca che evita entrambe le entrate di gennaio: `4/6`;
- classe cieca che conserva agosto: `6/6`;
- guardrail principale evita entrambe le entrate di gennaio: SI;
- guardrail principale conserva agosto: SI;
- guardrail principale ammissibile prima del 2026: SI;
- costi, ritardi e soglie vicine: gia' superati nel test precedente;
- nuova attivazione live indipendente del guardrail: NON ANCORA.

## Decisione

Il gate retrospettivo e' superato soltanto in parte: la famiglia distanza
SMA50/SMA200 emerge senza vedere il 2026, ma il periodo pre-2026 non identifica
una soglia unica e non tutte le soglie equivalenti bloccano gennaio.
Il guardrail combinato resta ammissibile e piu' prudente contro un blocco
eccessivo, ma non viene promosso a Baseline. Deve essere congelato in shadow
e valutato alla prima nuova attivazione indipendente; non serve attendere un
numero fisso di mesi.

## File generati

- `reports/january_2026_guardrail_blind_selection.csv`;
- `reports/january_2026_guardrail_blind_holdout.csv`;
- `reports/january_2026_guardrail_blind_periods.csv`.
- `reports/january_2026_guardrail_blind_trades.csv`.
- `reports/january_2026_guardrail_shadow_spec.json`.
