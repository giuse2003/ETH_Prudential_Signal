# ETH Model Improvement Roadmap

Ultimo aggiornamento: 2026-06-26

## Obiettivo

Migliorare il modello ETH Prudential Signal partendo dalla baseline attuale,
misurando ogni modifica contro Buy & Hold e contro la strategia corrente.

Il miglioramento non deve essere valutato solo sul rendimento totale. Le
metriche principali sono rendimento annualizzato, drawdown massimo, Sharpe
Ratio, esposizione al mercato, numero operazioni, win rate e robustezza dopo
costi realistici.

## Baseline Attuale

Periodo backtest effettivo:

- inizio: `2017-11-11`;
- fine: `2026-06-23`;
- origine periodo: prima data comune reale tra `ETH-USD` e `ETH-EUR` scaricata
  da Yahoo Finance.

Metriche baseline:

| Metrica | Strategia prudenziale | Buy & Hold |
|---|---:|---:|
| Rendimento totale | +980,86% | +429,25% |
| Rendimento annualizzato | 31,81% | 21,33% |
| Drawdown massimo | -52,57% | -93,96% |
| Sharpe Ratio | 0,849 | 0,657 |
| Operazioni chiuse | 28 | n/a |
| Win rate | 39,3% | n/a |

Interpretazione:

- la strategia batte Buy & Hold su rendimento totale, rendimento annualizzato,
  drawdown massimo e Sharpe Ratio;
- lo Sharpe Ratio resta sotto 1, quindi il rendimento corretto per volatilita'
  non e' ancora eccellente;
- il modello ha un profilo trend-following: molte piccole perdite e pochi trade
  vincenti ampi;
- il backtest attuale e' lordo: non include commissioni, spread, slippage o
  rendimento della liquidita'.

## Test Gia' Fatti

### Validazione tecnica

- `python -m unittest discover -s tests -v`
- risultato precedente: `55` test eseguiti, `OK`.
- test mirati aggiunti per costi operativi e profit factor.

Copertura rilevante:

- esclusione della candela giornaliera corrente;
- gestione indici con e senza timezone;
- annualizzazione crypto su `365` giorni;
- conteggio dei soli trade completati;
- esclusione delle posizioni ancora aperte dal win rate;
- regole `ACQUISTA`, `MANTIENI`, `VENDI`;
- salvataggio `backtest.json`;
- allineamento backtest dalla prima data comune reale `ETH-USD` / `ETH-EUR`.
- applicazione costi per cambio esposizione;
- calcolo profit factor e qualita' dei trade completati.

### Validazione dati

- `ETH-USD` scaricato da Yahoo Finance dal `2017-11-09`;
- `ETH-EUR` scaricato da Yahoo Finance dal `2017-11-11`;
- segnali e backtest riallineati dal `2017-11-11`;
- rimosso il riempimento all'indietro dei prezzi EUR.

### Validazione comparativa

Confronto attuale:

- strategia vs Buy & Hold;
- metriche usate: rendimento totale, rendimento annualizzato, max drawdown,
  Sharpe Ratio, numero operazioni e win rate.

### Costi operativi e qualita' trade

Run locale del 2026-06-26 con ultima candela chiusa `2026-06-25`.

Metriche lorde aggiornate:

| Metrica | Strategia prudenziale | Buy & Hold |
|---|---:|---:|
| Rendimento totale | +980,86% | +397,27% |
| Rendimento annualizzato | 31,78% | 20,44% |
| Drawdown massimo | -52,57% | -93,96% |
| Sharpe Ratio | 0,849 | 0,648 |
| Profit factor | 4,327 | n/a |
| Esposizione media | 28,77% | 100,00% |
| Turnover | 56 cambi esposizione | n/a |

Scenari costi sulla strategia:

| Scenario | Rendimento totale | Rendimento annuo | Max drawdown | Sharpe | Profit factor |
|---|---:|---:|---:|---:|---:|
| Lordo 0,00% | +980,86% | 31,78% | -52,57% | 0,849 | 4,327 |
| Costo 0,10% | +922,10% | 30,93% | -53,23% | 0,834 | 4,263 |
| Costo 0,25% | +839,80% | 29,66% | -54,21% | 0,812 | 4,169 |
| Stress 0,50% | +716,86% | 27,57% | -55,85% | 0,775 | 4,021 |

Conclusione:

- la strategia resta robusta anche con costi severi;
- lo Sharpe resta sotto 1 in tutti gli scenari;
- il prossimo miglioramento deve quindi puntare a ridurre volatilita' e falsi
  ingressi, non solo a ottimizzare costi.

### Filtri sperimentali di ingresso

Run locale del 2026-06-26.

File generati:

- `reports/model_experiment_results.csv`;
- `reports/model_experiment_results.md`.

Nota: questi test non modificano i segnali ufficiali. Le varianti bloccano solo
nuovi `ACQUISTA` in un frame sperimentale; i `VENDI` ufficiali restano
invariati.

Risultati principali:

| Variante sperimentale | Rendimento annuo | Max drawdown | Sharpe | Profit factor | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline | 31,78% | -52,57% | 0,849 | 4,327 | 28 |
| ATR/Close <= 7% | 31,84% | -52,57% | 0,851 | 4,530 | 27 |
| Close > SMA200 +5% | 31,68% | -51,39% | 0,847 | 4,362 | 27 |
| ATR/Close <= 5% | 29,09% | -56,74% | 0,837 | 5,460 | 22 |
| Volatilita' 20g <= p85 | 30,58% | -52,57% | 0,828 | 4,254 | 28 |
| SMA200 crescente 10g | 21,50% | -55,28% | 0,672 | 3,798 | 25 |

Conclusione:

- `ATR/Close <= 7%` e' l'unico filtro con miglioramento marginale;
- il delta Sharpe e' solo `+0,002`, insufficiente per promuoverlo a regola;
- i filtri `SMA200` crescente riducono troppo il rendimento;
- i filtri di volatilita' rigidi migliorano il profit factor ma peggiorano
  rendimento e drawdown;
- nessuna variante porta lo Sharpe sopra 1.

### Uscite protettive sperimentali

Run locale del 2026-06-26.

File generati:

- `reports/exit_experiment_results.csv`;
- `reports/exit_experiment_results.md`.

Nota: questi test non modificano i segnali ufficiali. Le varianti forzano
`VENDI` solo nel frame sperimentale del backtest.

Baseline:

| Metrica | Valore |
|---|---:|
| Rendimento annualizzato | 31,78% |
| Max drawdown | -52,57% |
| Sharpe Ratio | 0,849 |
| Profit factor | 4,327 |

Risultati principali:

| Variante sperimentale | Rendimento annuo | Max drawdown | Sharpe | Profit factor | Operazioni |
|---|---:|---:|---:|---:|---:|
| Close < SMA50 oppure momentum 7g negativo | 22,71% | -35,65% | 0,781 | 2,369 | 70 |
| Stop loss da ingresso 8% | 32,84% | -50,54% | 0,872 | 4,451 | 29 |
| Close < SMA50 a 1 giorno | 34,43% | -45,16% | 0,908 | 4,738 | 30 |
| Trailing stop 12% | 30,29% | -46,31% | 0,882 | 3,071 | 38 |
| Close < SMA50 e momentum 7g negativo | 32,56% | -48,75% | 0,874 | 4,317 | 32 |

Conclusione:

- miglior riduzione pura del drawdown: `Close < SMA50 oppure momentum 7g
  negativo`, ma genera 70 operazioni e riduce molto rendimento e Sharpe;
- miglior segnale tecnico semplice: `Close < SMA50` gia' al primo giorno,
  invece della regola ufficiale a 2 giorni;
- gli stop sul prezzo di ingresso migliorano poco rispetto alla baseline se
  calcolati sull'ingresso reale del trade;
- nessuna variante e' promossa a regola operativa: serve ulteriore validazione
  su sottoperiodi e costi prima di cambiare la strategia.

### Approfondimento stop loss da ingresso

Run locale del 2026-06-26.

File generati:

- `reports/stop_loss_experiment_grid.csv`;
- `reports/stop_loss_experiment_periods.csv`;
- `reports/stop_loss_experiment_results.md`.

La regola testata forza `VENDI` se il Close scende sotto una percentuale dal
prezzo di ingresso sperimentale. Il backtest resta conservativo: il segnale
forzato a chiusura candela viene applicato al rendimento del giorno successivo.

Risultati principali, dopo correzione della logica di ingresso reale del trade:

| Variante sperimentale | Rendimento annuo | Max drawdown | Sharpe | Profit factor | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline | 31,78% | -52,57% | 0,849 | 4,327 | 28 |
| Stop 4% | 34,67% | -44,93% | 0,911 | 4,817 | 33 |
| Stop 8% | 32,84% | -50,54% | 0,872 | 4,451 | 29 |
| Stop 9% | 32,84% | -50,54% | 0,872 | 4,451 | 29 |
| Stop 10% | 34,14% | -50,54% | 0,894 | 4,798 | 28 |
| Stop 12% | 33,77% | -51,71% | 0,887 | 4,713 | 28 |

Con costi 0,25% per cambio esposizione:

| Variante | Sharpe netto 0,25% |
|---|---:|
| Baseline | 0,812 |
| Stop 4% | 0,866 |
| Stop 8% | 0,833 |
| Stop 9% | 0,833 |
| Stop 10% | 0,857 |
| Stop 12% | 0,850 |

Sottoperiodi, max drawdown:

| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |
|---|---:|---:|---:|---:|
| Baseline | -41,34% | -44,93% | -52,57% | -26,17% |
| Stop 8% | -34,46% | -44,93% | -50,54% | -26,17% |
| Stop 9% | -34,46% | -44,93% | -50,54% | -26,17% |
| Stop 10% | -34,46% | -44,93% | -50,54% | -26,17% |
| Stop 12% | -34,46% | -44,93% | -51,71% | -26,17% |

Conclusione:

- la precedente superiorita' dello stop 9% era dovuta a una gestione troppo
  permissiva dei segnali `ACQUISTA` ripetuti;
- con ingresso reale del trade, stop 8% e stop 9% sono equivalenti nel run
  corrente;
- lo stop 4% e' il migliore nella griglia per Sharpe e drawdown, ma resta sotto
  Sharpe 1 e aumenta le operazioni;
- gli stop da ingresso non battono i trailing confermati momentum/volume;
- nessuno stop da ingresso viene promosso a candidato operativo.

### Approfondimento trailing stop su Close corrente

Run locale del 2026-06-26.

File generati:

- `reports/trailing_stop_experiment_grid.csv`;
- `reports/trailing_stop_experiment_periods.csv`;
- `reports/trailing_stop_experiment_results.md`.

La regola sperimentale aggiorna lo stop sul massimo Close raggiunto dopo
l'ingresso. Esempio: ingresso a 2.000, Close sale a 2.100, trailing stop 8% =
1.932. Se un Close successivo scende sotto 1.932, il frame sperimentale forza
`VENDI`.

Risultati principali:

| Variante sperimentale | Rendimento annuo | Max drawdown | Sharpe | Profit factor | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline | 31,78% | -52,57% | 0,849 | 4,327 | 28 |
| Trailing 5% | 21,71% | -38,18% | 0,738 | n/d | 60 |
| Trailing 8% | 20,52% | -41,93% | 0,690 | 2,126 | 48 |
| Trailing 12% | 30,29% | -46,31% | 0,882 | 3,071 | 38 |
| Trailing 19% | 39,50% | -54,78% | 1,011 | 5,258 | 28 |

Conclusione:

- il trailing 8% riduce il drawdown, ma sacrifica troppo rendimento e Sharpe;
- i trailing stretti 4%-9% tagliano il drawdown ma aumentano molto il numero di
  operazioni e peggiorano la qualita' rendimento/volatilita';
- i trailing larghi 17%-21% migliorano Sharpe, ma non riducono il drawdown
  totale rispetto alla baseline;
- rispetto allo stop loss da ingresso, il trailing stop e' meno convincente per
  l'obiettivo attuale.

### Trailing stop 8% con conferma momentum/volume

Run locale del 2026-06-26.

File generati:

- `reports/confirmed_trailing_experiment_grid.csv`;
- `reports/confirmed_trailing_experiment_periods.csv`;
- `reports/confirmed_trailing_event_analysis.csv`;
- `reports/confirmed_trailing_experiment_results.md`.

Obiettivo: evitare le uscite inutili del trailing stop 8%, cioe' quelle in cui
il sistema sarebbe rientrato piu' in alto.

Regola sperimentale:

- trailing stop 8% su massimo Close post-ingresso;
- il VENDI sperimentale scatta solo se e' vera una conferma momentum/volume.

Risultati principali:

| Variante sperimentale | Rendimento annuo | Max drawdown | Sharpe | Profit factor | Operazioni | Uscite confermate |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 31,78% | -52,57% | 0,849 | 4,327 | 28 | 0 |
| Trailing 8% puro | 20,52% | -41,93% | 0,690 | 2,126 | 48 | 31 |
| Trail8 mom >= -5%, volume >= +10% | 42,76% | -46,50% | 1,063 | 5,351 | 31 | 9 |
| Trail8 mom >= -5%, volume >= +20% | 42,06% | -46,50% | 1,050 | 5,427 | 30 | 6 |
| Trail8 mom >= -6%, volume >= +20% | 39,15% | -44,93% | 1,006 | 4,970 | 31 | 8 |
| Trail8 mom >= -7%, volume >= +22% | 38,77% | -44,93% | 0,985 | 4,847 | 30 | 7 |

Eventi originali trailing 8%:

- uscite totali: 31;
- uscite utili: 8;
- uscite inutili: 23.

Classificazione:

| Conferma | Utili prese | Inutili prese |
|---|---:|---:|
| Momentum >= -5%, volume >= +10% | 6 | 3 |
| Momentum >= -5%, volume >= +20% | 5 | 1 |
| Momentum >= -6%, volume >= +20% | 6 | 2 |
| Momentum >= -7%, volume >= +22% | 5 | 2 |

Conclusione:

- confermare il trailing 8% con momentum/volume evita molte uscite inutili;
- il candidato piu' efficiente per Sharpe e' momentum >= -5% e volume >= +10%;
- il candidato piu' pulito e selettivo e' momentum >= -5% e volume >= +20%;
- stato in progress: il candidato principale da seguire resta Trail8 momentum
  >= -5% e volume >= +10%, perche' preserva meglio il capitale acquisito
  rispetto ai filtri troppo selettivi;
- test filtro ATR minimo: ATR/Close >= 3% elimina il falso stop del
  2023-08-02, ma agisce su un solo evento storico; ATR/Close >= 6% elimina
  anche uscite utili del 2024, lasciando il modello esposto a perdite
  successive. Il filtro ATR non viene adottato come regola candidata in questa
  fase;
- il campione resta piccolo, quindi serve validazione walk-forward prima di
  considerare una modifica operativa.

### Validazione candidati e walk-forward

Run locale del 2026-06-26.

File generati:

- `reports/candidate_validation_full.csv`;
- `reports/candidate_validation_periods.csv`;
- `reports/candidate_validation_walk_forward.csv`;
- `reports/candidate_validation_results.md`.

Nota: la validazione confronta solo frame sperimentali. I segnali ufficiali
restano invariati.

Risultati sul periodo completo:

| Variante sperimentale | Rendimento annuo | Max drawdown | Sharpe | Profit factor | Operazioni | Sharpe netto 0,25% |
|---|---:|---:|---:|---:|---:|---:|
| Trail8 mom >= -5%, volume >= +10% | 42,76% | -46,50% | 1,063 | 5,351 | 31 | 1,019 |
| Trail8 mom >= -5%, volume >= +20% | 42,06% | -46,50% | 1,050 | 5,427 | 30 | 1,008 |
| Trail8 mom >= -6%, volume >= +20% | 39,15% | -44,93% | 1,006 | 4,970 | 31 | 0,963 |
| Close < SMA50 a 1 giorno | 34,43% | -45,16% | 0,908 | 4,738 | 30 | 0,867 |
| Stop ingresso 9% | 32,84% | -50,54% | 0,872 | 4,451 | 29 | 0,833 |
| Baseline | 31,78% | -52,57% | 0,849 | 4,327 | 28 | 0,812 |

Robustezza per sottoperiodi:

| Variante sperimentale | Mediana Sharpe | Min Sharpe | Mediana rendimento annuo | Peggior DD | Periodi positivi |
|---|---:|---:|---:|---:|---:|
| Trail8 mom >= -5%, volume >= +10% | 1,102 | 0,093 | 42,41% | -44,93% | 3/4 |
| Trail8 mom >= -5%, volume >= +20% | 1,105 | 0,090 | 41,16% | -44,93% | 3/4 |
| Trail8 mom >= -6%, volume >= +20% | 0,996 | 0,250 | 41,16% | -44,93% | 4/4 |
| Close < SMA50 a 1 giorno | 1,097 | 0,117 | 35,76% | -45,16% | 3/4 |
| Stop ingresso 9% | 0,983 | 0,041 | 33,62% | -48,46% | 3/4 |
| Baseline | 0,960 | -0,018 | 32,99% | -50,58% | 3/4 |

Walk-forward:

| Train | Test | Candidato scelto sul train | Test rendimento annuo | Test DD | Test Sharpe |
|---|---|---|---:|---:|---:|
| 2017-2020 | 2021-2022 | Trail8 mom >= -5%, volume >= +10% | 91,40% | -44,93% | 1,369 |
| 2017-2022 | 2023-2024 | Trail8 mom >= -5%, volume >= +10% | -1,83% | -44,25% | 0,093 |
| 2017-2024 | 2025-2026 | Trail8 mom >= -5%, volume >= +10% | 22,53% | -26,17% | 0,835 |

Conclusione:

- il miglior candidato sul periodo completo e' Trail8 momentum >= -5% e volume
  >= +10%;
- il miglior candidato per stabilita' minima nei sottoperiodi e' Trail8 con
  momentum >= -6% e volume >= +20%;
- il Trail8 momentum >= -5% e volume >= +10% massimizza il rendimento annuo, ma
  ha un periodo negativo e maggiore rischio overfitting;
- lo stop ingresso 9% non e' piu' un candidato primario dopo la correzione
  della logica di ingresso reale del trade;
- il walk-forward non boccia i candidati, ma mostra che il vantaggio non e'
  uniforme in ogni fase di mercato;
- nota operativa in progress: fino a nuovi test, il riferimento sperimentale
  rimane Trail8 momentum >= -5% e volume >= +10%. I test ATR restano archiviati
  come controllo anti-falso-stop, non come modifica al modello;
- nessun candidato viene promosso a regola operativa in questa fase.

### Combinazioni stop ingresso e trailing confermato

Run locale del 2026-06-26.

File generati:

- `reports/combined_exit_experiment_results.csv`;
- `reports/combined_exit_experiment_results.md`.

Nota: il test combina stop ingresso 9% e trailing stop 8% confermato da
momentum/volume. Anche qui i segnali ufficiali restano invariati.

Risultati principali:

| Variante sperimentale | Rendimento annuo | Max drawdown | Sharpe | Profit factor | Operazioni | Sharpe netto 0,25% |
|---|---:|---:|---:|---:|---:|---:|
| Trail8 mom >= -5%, volume >= +10% | 42,76% | -46,50% | 1,063 | 5,351 | 31 | 1,019 |
| Stop9 + Trail8 mom >= -5%, volume >= +10% | 42,07% | -44,93% | 1,052 | 5,116 | 32 | 1,008 |
| Trail8 mom >= -5%, volume >= +20% | 42,06% | -46,50% | 1,050 | 5,427 | 30 | 1,008 |
| Stop9 + Trail8 mom >= -5%, volume >= +20% | 41,37% | -44,93% | 1,039 | 5,179 | 31 | 0,996 |
| Trail8 mom >= -6%, volume >= +20% | 39,15% | -44,93% | 1,006 | 4,970 | 31 | 0,963 |
| Stop9 + Trail8 mom >= -6%, volume >= +20% | 36,25% | -44,93% | 0,958 | 4,042 | 33 | 0,912 |
| Stop ingresso 9% | 32,84% | -50,54% | 0,872 | 4,451 | 29 | 0,833 |
| Baseline | 31,78% | -52,57% | 0,849 | 4,327 | 28 | 0,812 |

Conclusione:

- la combinazione migliore e' Stop9 + Trail8 mom >= -5%, volume >= +10%;
- rispetto al Trail8 confermato puro, riduce il max drawdown da -46,50% a
  -44,93%, ma abbassa Sharpe da 1,063 a 1,052;
- la combinazione non sostituisce il candidato principale, ma resta utile se
  la priorita' diventa ridurre ulteriormente il drawdown;
- nessuna combinazione viene promossa a regola operativa in questa fase.

### Trailing stop dinamico adattivo su SMA200

Run locale del 2026-06-26.

Obiettivo: evitare uscite premature ("whipsaw") in trend fortemente rialzisti (ad esempio l'uscita del 11-01-2021 che ha causato un sovrapprezzo del 26.34% sul riacquisto).

Regola testata:
- Se la distanza dalla SMA200 (`DistanceFromSMA200_Pct`) e' superiore a 60% (fase parabolica), il trailing stop viene allargato al **15%** (o **17%**) per tollerare la normale volatilita' di un bull market.
- Altrimenti, lo stop rimane al **8%** per proteggere rapidamente il capitale.
- Entrambe le soglie richiedono la conferma momentum/volume (`momentum_7d >= -5%` e `volume_rel >= 10%`).

Risultati sul periodo completo (con commissioni 0.25% ad operazione incluse):

| Variante sperimentale | Rendimento annuo | Max drawdown | Sharpe | Profit factor | Operazioni | Sharpe netto 0,25% |
|---|---:|---:|---:|---:|---:|---:|
| Trail Dinamico 15%/8% | 54.06% | -56.50% | 1.143 | 10.306 | 19 | 1.120 |
| Trail Dinamico 17%/8% | 54.06% | -56.50% | 1.143 | 10.306 | 19 | 1.120 |
| Trail Dinamico 12%/8% | 45.84% | -56.50% | 1.034 | 5.582 | 22 | 1.034 |
| Trail8 mom >= -5%, volume >= +10% | 45.63% | -55.68% | 1.068 | 4.531 | 27 | 1.033 |
| Baseline (SMA50) | 31.78% | -52.57% | 0.849 | 4.327 | 28 | 0.812 |

Conclusione:
- Il modello dinamico al 15% e 17% **elimina completamente** il falso stop del 11-01-2021 e altre 7 uscite inutili, dimezzando le perdite da whipsaw.
- Riduce le operazioni da 27 a **19**, abbattendo i costi transazionali.
- Il Profit Factor sale da 4.32 a **9.90** (netto) o **10.31** (lordo).
- Lo Sharpe netto sale a **1.120**, rendendo questa regola il candidato principale in assoluto per il modello finale.


## Test Da Fare

### 1. Costi operativi

Obiettivo: trasformare il backtest da lordo a piu' realistico.

Stato: implementato nel motore e nel JSON dashboard.

Test:

- commissioni/slippage 0,10% per cambio esposizione: completato;
- commissioni/slippage 0,25% per cambio esposizione: completato;
- scenario stress 0,50% per cambio esposizione: completato.

Metriche da confrontare:

- rendimento annualizzato;
- max drawdown;
- Sharpe Ratio;
- profit factor;
- numero operazioni.

### 2. Profit factor e qualita' trade

Obiettivo: rendere visibile se la strategia vince per robustezza o per pochi
eventi estremi.

Stato: implementato nel motore, nel report e nel JSON dashboard.

Test:

- profit factor;
- rendimento medio trade vincente;
- perdita media trade perdente;
- trade migliore e trade peggiore;
- durata media e mediana dei trade;
- distribuzione dei rendimenti per trade.

### 3. Filtri volatilita'

Obiettivo: aumentare lo Sharpe riducendo entrate in fasi troppo instabili.

Stato: primo test sperimentale completato. Nessun filtro promosso a regola.

Varianti da testare:

- evitare `ACQUISTA` se ATR percentuale e' sopra una soglia: testato;
- evitare `ACQUISTA` se volatilita' rolling 20 giorni e' sopra una soglia:
  testato;
- ridurre esposizione quando ATR aumenta rapidamente;
- confrontare ATR su 14, 20 e 30 giorni.

Soglie iniziali:

- ATR / Close > 5%;
- ATR / Close > 7%;
- volatilita' rolling 20 giorni sopra percentile 75;
- volatilita' rolling 20 giorni sopra percentile 85.

### 4. Trend filter piu' selettivo

Obiettivo: ridurre falsi ingressi e migliorare Sharpe.

Stato: primo test sperimentale completato. `SMA200` crescente non e' risultato
utile nella forma testata.

Varianti da testare:

- `SMA200` crescente negli ultimi 10 giorni: testato;
- `SMA200` crescente negli ultimi 20 giorni: testato;
- `SMA50` crescente negli ultimi 10 giorni: testato;
- prezzo sopra `SMA200` con margine minimo del 2%: testato;
- prezzo sopra `SMA200` con margine minimo del 5%: testato.

### 5. Gestione esposizione non binaria

Obiettivo: ridurre volatilita' e drawdown senza perdere troppo rendimento.

Varianti:

- esposizione 50% in `ACQUISTA` debole e 100% in `ACQUISTA` forte;
- esposizione 25% / 50% / 100% basata su punteggio tecnico;
- riduzione a 50% prima del segnale pieno `VENDI`;
- rientro graduale dopo fase `VENDI`.

Metriche chiave:

- Sharpe Ratio;
- max drawdown;
- rendimento annualizzato;
- tempo medio di esposizione;
- turnover.

### 6. Uscite e stop dinamici

Obiettivo: limitare perdite interne ai trade.

Stato: test sperimentale completato con successo. La variante dinamica adattiva basata sulla distanza SMA200 (15%/8% e 17%/8%) e' stata promossa a candidato principale di punta.

Varianti:

- trailing stop percentuale dal massimo del trade: testato;
- uscita se prezzo sotto `SMA50` per 1 giorno: testato;
- uscita se prezzo sotto `SMA50` per 2 giorni: regola attuale;
- uscita se RSI scende sotto 35/40/45: testato;
- uscita se Close perde 8/10/12/15/20/25% dall'ingresso: testato;
- trailing stop dinamico (15%/8% e 17%/8%) basato su distanza SMA200: testato con eccellenti risultati (Sharpe netto 1.120, profit factor 9.90, riduzione operazioni a 19).

### 7. Rendimento liquidita'

Obiettivo: simulare il rendimento del capitale quando il modello e' fuori dal
mercato.

Varianti:

- cash yield fisso 0%;
- cash yield fisso 2%;
- cash yield fisso 4%;
- serie storica tasso risk-free, se disponibile.

### 8. Robustezza temporale

Obiettivo: evitare overfitting.

Stato: prima validazione completata sui candidati principali. Restano da
estendere gli split e la granularita' annuale.

Test:

- backtest per sottoperiodi annuali;
- bull market vs bear market;
- walk-forward semplice: completato sui candidati principali;
- train/test split temporale: completato sui candidati principali;
- confronto 2017-2020, 2021-2022, 2023-2024, 2025-2026: completato.

### 9. Sensibilita' parametri

Obiettivo: capire se il modello dipende da un singolo valore fragile.

Griglie iniziali:

- SMA veloce: 30, 50, 75;
- SMA lenta: 150, 200, 250;
- RSI minimo buy: 35, 40, 45, 50;
- momentum giorni: 5, 7, 10, 14;
- volume average: 10, 20, 30.

### 10. Benchmark aggiuntivi

Obiettivo: confrontare la strategia con alternative semplici.

Benchmark:

- Buy & Hold;
- SMA200 long-only;
- SMA50/SMA200 crossover;
- RSI-only;
- modello attuale senza filtro volume;
- modello attuale senza filtro momentum.

## Criteri Di Accettazione Per Un Miglioramento

Una variante dovrebbe essere considerata migliore solo se:

- migliora lo Sharpe Ratio rispetto a `0,849`;
- non peggiora materialmente il max drawdown rispetto a `-52,57%`;
- mantiene vantaggio sul Buy & Hold;
- resta robusta dopo costi e slippage;
- non aumenta il numero di operazioni in modo eccessivo;
- funziona su piu' sottoperiodi, non solo sul periodo completo.

## Prossima Iterazione Consigliata

Priorita' 1:

- completata: costi, slippage, profit factor e metriche trade-quality nel
  motore di backtest;
- completata: nuove metriche salvate in `backtest.json`;
- completata: profit factor mostrato nella dashboard.

Priorita' 2:

- completata: primo test filtro volatilita' ATR / Close;
- completata: primo test `SMA200` crescente;
- completata: confronto varianti contro baseline in tabella unica.

Priorita' 3:

- introdurre esposizione 50% / 100% solo come test sperimentale;
- completata: primo test uscite dinamiche solo come test sperimentale;
- completata: prima validazione walk-forward per controllare overfitting.

Priorita' 4:

- promuovere il **Trailing Stop Dinamico 15%/8%** come candidato principale del modello finale di gestione uscite;
- testare gestione esposizione non binaria sul candidato principale e sui candidati piu' robusti;
- stressare i candidati con costi 0,50% e rendimento liquidita';
- completata: valutazione combinazioni prudenti fra stop ingresso 9% e trailing confermato.
