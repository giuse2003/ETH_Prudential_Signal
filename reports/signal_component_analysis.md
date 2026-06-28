# Signal Component Analysis

Questo report separa entrate, uscite e combinazioni. Non modifica i segnali ufficiali.

Performance misurata in EUR con `Close_EUR`, usando gli indicatori ufficiali.

## 1. Benchmark

| Modello | Ann. | Max DD | Sharpe | PF | Ops | Esp. | 2022+ Ann. | 2022+ DD | 2022+ Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Buy & Hold ETH/EUR | 20.82% | -93.49% | 0.651 | n/a | 0 | 100.00% | -17.74% | -71.89% | 0.057 |
| Baseline ufficiale | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 28.75% | 4.12% | -49.73% | 0.284 |

## 2. Modelli Di Uscita

Qui gli ingressi restano quelli Baseline. Cambia solo il modo di uscire.

| Modello | Ann. | Max DD | Sharpe | PF | Ops | Esp. | 2022+ Ann. | 2022+ DD | 2022+ Sharpe | Ingressi bloccati | Uscite trail |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 28.75% | 4.12% | -49.73% | 0.284 | 0 | 0 |
| Trailing 8% puro | 20.61% | -40.24% | 0.698 | 2.157 | 48 | 21.90% | 2.00% | -40.24% | 0.203 | 0 | 31 |
| Trail8 confermato -5 / vol +20 | 41.36% | -45.09% | 1.047 | 5.565 | 30 | 26.50% | 6.66% | -43.75% | 0.378 | 0 | 6 |
| Trail8 confermato -6 / vol +20 | 38.50% | -45.09% | 1.004 | 5.133 | 31 | 26.15% | 9.24% | -37.39% | 0.471 | 0 | 8 |

Lettura uscite:

- `Trailing 8% puro` riduce il drawdown ma peggiora rendimento e Sharpe: resta scartato.
- `Trail8 confermato -5 / vol +20` e' l'uscita piu' pulita: migliora Sharpe senza il falso stop grave di gennaio 2021.
- `Trail8 confermato -6 / vol +20` migliora il drawdown, ma introduce la falsa uscita grave di gennaio 2021.

## 3. Modelli Di Ingresso

Qui l'uscita resta quella ufficiale sotto SMA50 per 2 giorni. Cambia solo il filtro sui nuovi ACQUISTA.

| Modello | Ann. | Max DD | Sharpe | PF | Ops | Esp. | 2022+ Ann. | 2022+ DD | 2022+ Sharpe | Ingressi bloccati | Uscite trail |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 28.75% | 4.12% | -49.73% | 0.284 | 0 | 0 |
| RSI <= 65 solo ingresso | 36.13% | -47.17% | 0.944 | 5.670 | 27 | 26.85% | 5.28% | -47.17% | 0.325 | 14 | 0 |
| RSI <= 62 solo ingresso | 35.89% | -47.17% | 0.943 | 5.652 | 27 | 26.63% | 5.28% | -47.17% | 0.325 | 21 | 0 |
| RSI <= 60 solo ingresso | 34.93% | -46.29% | 0.930 | 5.708 | 27 | 24.91% | 4.10% | -46.29% | 0.284 | 38 | 0 |

Lettura ingressi:

- `RSI <= 65` migliora Baseline in modo pulito e resta semplice da spiegare.
- `RSI <= 62` e' molto vicino a `RSI <= 65`; non cambia il 2022-oggi in modo rilevante.
- `RSI <= 60` riduce ancora alcuni rischi ma diventa piu' restrittivo.

## 4. Combinazioni Ingresso + Uscita

Questa sezione serve solo dopo aver capito separatamente entrata e uscita.

| Modello | Ann. | Max DD | Sharpe | PF | Ops | Esp. | 2022+ Ann. | 2022+ DD | 2022+ Sharpe | Ingressi bloccati | Uscite trail |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 30.26% | -49.73% | 0.828 | 4.215 | 28 | 28.75% | 4.12% | -49.73% | 0.284 | 0 | 0 |
| RSI65 + Trail8 -5 / vol +20 | 51.41% | -40.69% | 1.265 | 6.747 | 28 | 24.94% | 7.92% | -40.69% | 0.428 | 16 | 5 |
| RSI65 + Trail8 -6 / vol +20 | 50.26% | -33.99% | 1.272 | 6.554 | 29 | 24.50% | 10.53% | -33.99% | 0.525 | 18 | 7 |
| RSI62 + Trail8 -6 / vol +20 | 50.83% | -33.99% | 1.289 | 6.660 | 29 | 24.25% | 10.53% | -33.99% | 0.525 | 25 | 7 |

Lettura combinazioni:

- `RSI65 + Trail8 -5 / vol +20` e' il candidato prudente principale: meno performante del -6, ma piu' pulito sugli eventi.
- `RSI62/65 + Trail8 -6 / vol +20` sono piu' forti numericamente, ma hanno la falsa uscita grave di gennaio 2021.
- Per decidere il modello operativo non bisogna promuovere la combinazione migliore per numero assoluto; serve prima decidere se accettare o correggere il problema gennaio 2021.

## Decisione Operativa Provvisoria

- Uscita candidata pulita: `Trail8 confermato -5 / vol +20`.
- Ingresso candidato pulito: `RSI <= 65`.
- Combinazione candidata prudente: `RSI65 + Trail8 -5 / vol +20`.
- Combinazione candidata aggressiva: `RSI62/65 + Trail8 -6 / vol +20`, da correggere per il caso gennaio 2021.
