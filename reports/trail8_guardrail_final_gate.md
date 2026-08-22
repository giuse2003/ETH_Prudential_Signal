# Trail8 Guardrail - Gate Statistico Finale

Data test: `2026-08-22`. Cutoff: `2026-08-21`.
Mercato: `ETH-USD` Coinbase, daily UTC chiuso. Commissione taker `0,16%`.
La Baseline ufficiale non e' stata modificata.

## Verdetto

**FAIL**

## Controlli

| Controllo | Soglia | Risultato | Stato |
|---|---|---|---|
| Metriche aggregate candidato | Ann., DD e Sharpe > Baseline | 72.13% / -39.45% / 1.490 | PASS |
| Deflated Sharpe 274 prove | >= 95% | 99.97% | PASS |
| Probabilita vantaggio incrementale | >= 90% | 85.75% | FAIL |
| PBO griglia locale | < 50% | 41.67% | PASS |
| PBO ricerca ampia | Diagnostica: entrambi < 50% | 70 percorsi 75.40%; famiglia 73.41% | WARN |
| Stabilita valori vicini | >= 70% migliorano tutte le metriche | 44.44% | FAIL |
| Walk-forward purge 30g | Ann., DD e Sharpe > Baseline | 72.13% / -39.45% / 1.490 | PASS |
| Walk-forward purge 90g | Ann., DD e Sharpe > Baseline | 72.13% / -39.45% / 1.490 | PASS |
| Ritardo aggiuntivo 1 giorno | Stress informativo: preferibile PASS | Ann. 54.48% vs 57.78% | WARN |
| Selettore 70 percorsi | Diagnostica: preferibile PASS | Ann. 68.17% vs 69.64% | WARN |

## PBO / CSCV

PBO sotto il 50% indica che il vincitore scelto sul training finisce
sotto la mediana nel test in meno della meta' delle suddivisioni.

| Universo | Percorsi | Split | PBO | Rank test mediano | Sharpe train | Sharpe test |
|---|---:|---:|---:|---:|---:|---:|
| full_70_paths | 70 | 252 | 75.40% | 33.80% | 1.733 | 1.594 |
| pre2020_70_paths | 70 | 252 | 30.56% | 57.75% | 2.198 | 2.020 |
| full_conservative_family | 24 | 252 | 73.41% | 34.00% | 1.714 | 1.567 |
| full_parameter_neighborhood | 9 | 252 | 41.67% | 57.50% | 1.688 | 1.663 |

## Sharpe corretto

| Serie | Sharpe | Prob. Sharpe > 0 | DSR 70 prove | DSR 274 prove | Benchmark 274 |
|---|---:|---:|---:|---:|---:|
| full_baseline | 1.665 | 100.00% | 100.00% | 100.00% | 0.208 |
| full_prudent | 1.748 | 100.00% | 100.00% | 100.00% | 0.208 |
| oos_baseline | 1.460 | 99.99% | 99.97% | 99.96% | 0.208 |
| oos_prudent | 1.490 | 100.00% | 99.98% | 99.97% | 0.208 |
| oos_pair_gate | 1.490 | 100.00% | 99.98% | 99.97% | 0.208 |
| oos_incremental_pair_minus_baseline | 0.377 | 85.75% | n/a | n/a | 0.000 |

## Stabilita parametri

Griglia locale: Trail `10-12%`, slope SMA50 `3,75-4,25%`,
estensione `4-6%`: 45 combinazioni.
Le metriche indicate come 2020+ sono pseudo-fuori-campione: il periodo
parte dal 2020, ma la famiglia di regole e' stata definita conoscendo lo storico.

- combinazioni che migliorano annualizzato, DD e Sharpe: `44.44%`;
- combinazioni accettabili con tolleranza DD di 2 punti: `44.44%`;
- percorsi di segnale distinti nella griglia locale: `8`.

| Trail | Slope | Estensione | Ann. 2020+ | DD 2020+ | Sharpe 2020+ | Delta ann. | Delta DD | Delta Sharpe | Pass |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 10.00% | 3.75% | 5.00% | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 | PASS |
| 10.00% | 4.00% | 5.00% | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 | PASS |
| 10.50% | 3.75% | 5.00% | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 | PASS |
| 10.50% | 4.00% | 5.00% | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 | PASS |
| 11.00% | 3.75% | 5.00% | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 | PASS |
| 11.00% | 4.00% | 5.00% | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 | PASS |
| 11.50% | 3.75% | 5.00% | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 | PASS |
| 11.50% | 4.00% | 5.00% | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 | PASS |
| 12.00% | 3.75% | 5.00% | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 | PASS |
| 12.00% | 4.00% | 5.00% | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 | PASS |
| 10.00% | 3.75% | 4.00% | 71.72% | -39.45% | 1.485 | 2.08% | 0.42% | 0.024 | PASS |
| 10.00% | 4.00% | 4.00% | 71.72% | -39.45% | 1.485 | 2.08% | 0.42% | 0.024 | PASS |

## Walk-forward con purge

Gli ultimi 30 o 90 giorni prima di ogni anno di test non partecipano
alla scelta dei parametri. Le candele restano disponibili durante il test
per calcolare normalmente indicatori e stato della posizione.

| Purge | Modello | Ann. | Max DD | Sharpe | Delta ann. | Delta DD | Delta Sharpe |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0g | baseline | 69.64% | -39.87% | 1.460 | 0.00% | 0.00% | 0.000 |
| 0g | wf_pair_gate | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 |
| 0g | wf_conservative_family | 64.51% | -42.96% | 1.379 | -5.13% | -3.09% | -0.081 |
| 0g | wf_full_grid | 68.17% | -48.92% | 1.406 | -1.47% | -9.05% | -0.054 |
| 30g | baseline | 69.64% | -39.87% | 1.460 | 0.00% | 0.00% | 0.000 |
| 30g | wf_pair_gate | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 |
| 30g | wf_conservative_family | 68.06% | -42.96% | 1.435 | -1.59% | -3.09% | -0.025 |
| 30g | wf_full_grid | 71.44% | -48.92% | 1.469 | 1.80% | -9.05% | 0.009 |
| 90g | baseline | 69.64% | -39.87% | 1.460 | 0.00% | 0.00% | 0.000 |
| 90g | wf_pair_gate | 72.13% | -39.45% | 1.490 | 2.48% | 0.42% | 0.030 |
| 90g | wf_conservative_family | 68.06% | -42.96% | 1.435 | -1.59% | -3.09% | -0.025 |
| 90g | wf_full_grid | 71.44% | -48.92% | 1.469 | 1.80% | -9.05% | 0.009 |

## Decisione

- fallimenti obbligatori: `2`; avvertimenti: `3`;
- `PASS` autorizzerebbe la promozione; `PASS PROVVISORIO` richiede
  monitoraggio e rollback; `FAIL` mantiene la Baseline;
- il gate resta retrospettivo: anche una promozione autorizzata non
  trasformerebbe lo storico in vero futuro mai osservato;
- la Baseline resta invariata fino a decisione esplicita.
