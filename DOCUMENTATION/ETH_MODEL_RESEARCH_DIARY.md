# ETH Model Research Diary

Ultimo aggiornamento: 2026-07-27

Questo file e' il diario operativo del lavoro sul miglioramento del modello
ETH-USD Signal.

Nota cronologica:

- le sezioni iniziali riassumono lo stato ufficiale corrente dopo la
  decisione operativa del 2026-06-30;
- le sezioni `Registro Analisi` documentano in ordine la sequenza dei test,
  delle esclusioni e delle decisioni;
- quando una regola passa da candidata a ufficiale, la decisione viene
  registrata anche in `DECISION_LOG.md` e nel report dedicato in `reports/`.

Regola di lavoro:

- ogni test deve restare separato dalla strategia ufficiale finche' non viene
  esplicitamente promosso;
- le modifiche ai segnali ufficiali non si fanno durante le analisi
  esplorative;
- ogni idea va registrata con dati, risultato e decisione;
- un miglioramento e' valido solo se regge su piu' periodi, non su un singolo
  evento storico.

## Registro Operativo 2026-07-27 - Coerenza ETH-USD Signal v1

Obiettivo:

- applicare al progetto ETH lo stesso principio di coerenza documentale usato
  sul progetto BTC-USD;
- chiarire il mercato effettivo del modello senza cambiare la Baseline;
- separare cio' che e' operativo oggi da cio' che richiedera un futuro
  congelamento riproducibile.

Decisione:

- il nome metodologico pubblico diventa **ETH-USD Signal**;
- `ETH_Prudential_Signal` resta il nome del repository e dell'infrastruttura;
- `ETH-USD` e' la serie del modello per indicatori, segnali e backtest;
- `ETH-EUR` resta controvalore informativo e supporto report/dashboard;
- Coinbase resta live preview e non entra nella candela DAILY chiusa;
- Telegram continua a pubblicare solo variazioni LIVE stabilizzate;
- la Baseline ufficiale e le sue condizioni restano invariate;
- il progetto ETH non dispone ancora del pacchetto congelato con manifest,
  hash SHA-256, lockfile con hash e `reproduce.py` introdotto nel progetto
  BTC-USD.

Impatto:

- riallineati README, status, overview, indice documentale e checklist;
- le metriche operative correnti vengono dichiarate come valori del JSON
  pubblico `docs/backtest.json`;
- eventuale congelamento futuro dovra essere trattato come nuova attivita
  metodologica, con tag e artefatti dedicati.

## Strategia Ufficiale Corrente

La strategia ufficiale corrente e' la Baseline prudenziale.

Segnale `ACQUISTA` quando tutte le condizioni sono vere:

- Close > SMA200;
- SMA50 > SMA200;
- RSI >= 40;
- RSI <= 65;
- Close > Close di 7 giorni prima;
- Volume > VolumeAvg20.

Segnale `VENDI` quando almeno una condizione e' vera:

- Close < SMA50;
- trailing stop 8% dal massimo Close post-ingresso, confermato da:
  - momentum 7 giorni >= -5%;
  - volume relativo >= +20% rispetto alla media 20 giorni.

`MANTIENI` conserva l'esposizione precedente.

Nota importante: ulteriori esperimenti su ATR, filtri aggiuntivi o varianti
del trailing restano storici/sperimentali finche' non vengono promossi.

## Baseline Completa

Periodo dati completo disponibile nei segnali:

- inizio: 2017-11-11;
- ultima candela chiusa nel pacchetto pubblico corrente: 2026-07-25.

Metriche Baseline complete:

| Metrica | Valore |
|---|---:|
| Rendimento totale | +2843,36% |
| Rendimento annualizzato | +47,47% |
| Max drawdown | -40,97% |
| Sharpe ratio | 1,174 |
| Profit factor | 7,117 |
| Operazioni chiuse | 29 |
| Win rate | 34,48% |
| Esposizione media | 23,47% |
| Turnover | 58 cambi esposizione |

Interpretazione:

- la Baseline batte Buy & Hold sul periodo completo;
- lo Sharpe e' sopra 1 nel pacchetto corrente, ma resta da validare su un
  campione out-of-sample congelato;
- il sistema funziona con poche grandi operazioni vincenti e molte piccole
  operazioni deboli;
- il miglioramento deve concentrarsi su falsi ingressi, false uscite e
  contenimento drawdown.

## Confronto Dal 2022 A Oggi

Periodo: 2022-01-01 -> 2026-06-27.

Confronto in ETH/EUR, usando i segnali Baseline ufficiali e rendimento
misurato su Close_EUR.

| Metrica | Buy & Hold | ETH Prudential Baseline |
|---|---:|---:|
| Rendimento totale | -58,37% | +19,89% |
| Rendimento annualizzato | -17,74% | +4,12% |
| Max drawdown | -71,89% | -49,73% |
| Sharpe ratio | 0,057 | 0,284 |
| Esposizione media | 100,00% | 24,41% |
| Operazioni chiuse | n/a | 17 |
| Win rate | n/a | 29,41% |
| Profit factor | n/a | 1,563 |
| Trade medio | n/a | +2,49% |
| Trade mediano | n/a | -2,90% |
| Miglior trade | n/a | +62,70% |
| Peggior trade | n/a | -13,60% |
| Durata media trade | n/a | 23,5 giorni |

Lettura:

- dal 2022 la Baseline ha protetto molto meglio del Buy & Hold;
- il vantaggio principale viene dall'essere fuori dal mercato nelle fasi
  ribassiste;
- la qualita' degli ingressi resta debole: win rate basso e trade mediano
  negativo;
- il prossimo lavoro deve analizzare le entrate vincenti e perdenti per
  filtrare i falsi ingressi senza perdere i grandi trend.

## Andamento ETH/EUR Dal 2020

Periodo analizzato: 2020-01-01 -> 2026-06-27.

| Anno | Rendimento ETH/EUR | Max drawdown |
|---|---:|---:|
| 2020 | +418,05% | -62,23% |
| 2021 | +438,86% | -55,80% |
| 2022 | -66,34% | -71,89% |
| 2023 | +84,27% | -25,20% |
| 2024 | +51,07% | -46,10% |
| 2025 | -21,94% | -62,24% |
| 2026 al 27/06 | -45,96% | -52,74% |

Dal 2020 al 2026-06-27:

- ETH/EUR passa da 116,59 EUR a 1.379,86 EUR;
- rendimento totale: +1.083,53%;
- CAGR: +46,37%;
- massimo del periodo: 4.300,86 EUR il 2021-11-16;
- minimo del periodo: 85,10 EUR il 2020-03-13;
- max drawdown del periodo: -77,20%.

## Metriche Annuali Baseline

Periodo completo: 2017-11-11 -> 2026-06-27.

| Periodo | Rendimento | Max drawdown | Sharpe | Operazioni | Win rate | Profit factor | Esposizione |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 0,00% | 0,00% | n/a | 0 | 0,00% | n/a | 0,00% |
| 2018 | 0,00% | 0,00% | n/a | 0 | 0,00% | n/a | 0,00% |
| 2019 | +61,14% | -20,21% | 1,324 | 1 | 100,00% | inf | 21,92% |
| 2020 | +92,67% | -34,09% | 1,412 | 4 | 25,00% | 1,422 | 52,73% |
| 2021 | +197,46% | -44,93% | 1,679 | 6 | 66,67% | 8,598 | 63,84% |
| 2022 | 0,00% | 0,00% | n/a | 0 | 0,00% | n/a | 0,00% |
| 2023 | +4,23% | -21,58% | 0,287 | 5 | 20,00% | 0,666 | 45,21% |
| 2024 | -18,55% | -50,58% | -0,257 | 8 | 25,00% | 0,828 | 39,62% |
| 2025 | +35,07% | -26,17% | 1,016 | 4 | 25,00% | 3,524 | 24,66% |
| 2026 | 0,00% | 0,00% | n/a | 0 | 0,00% | n/a | 0,00% |

Osservazione:

- il 2024 e' l'anno critico della Baseline;
- il 2022 e il 2026 mostrano esposizione zero nella Baseline;
- il 2023 e il 2024 sono i periodi principali per studiare falsi ingressi e
  uscite inefficienti.

## Test Fatti Su Uscite Protettive

### Stop loss fisso da ingresso

Testato stop loss da ingresso all'8%.

Risultato:

- utile in alcuni casi per ridurre perdite;
- meccanismo giudicato non soddisfacente perche' non protegge il capitale
  acquisito durante un trade;
- non promosso.

### Trailing stop su prezzo corrente

Definizione testata:

- dopo l'ingresso, lo stop si calcola sul massimo Close raggiunto durante il
  trade;
- se il prezzo chiude sotto la soglia trailing, il sistema esce.

Testati trailing stop al 5% e all'8%.

Risultato:

- trailing 5% troppo sensibile;
- trailing 8% piu' interessante ma con molte uscite inutili;
- non promosso da solo.

### Trailing stop 8% confermato da momentum e volume

Candidato in progress:

- trailing stop 8%;
- conferma momentum 7 giorni >= -5%;
- conferma volume relativo >= +10%.

Metriche sperimentali principali:

| Metrica | Valore |
|---|---:|
| Rendimento annualizzato | +42,76% |
| Max drawdown | -46,50% |
| Sharpe ratio | 1,063 |
| Profit factor | 5,351 |
| Operazioni | 31 |

Stato:

- interessante;
- migliora Sharpe e drawdown rispetto alla Baseline;
- resta sperimentale;
- da validare meglio su sottoperiodi, costi e robustezza temporale.

### Trailing stop 8% con volume >= +20%

Risultato sintetico:

- 6 uscite confermate;
- 5 utili e 1 inutile;
- rendimento annualizzato circa +42,06%;
- max drawdown -46,50%;
- Sharpe circa 1,050.

Stato:

- variante piu' selettiva;
- utile come confronto;
- non promossa.

### Trailing dinamico 15% / 8%

Risultato sintetico:

- rendimento annualizzato circa +54,04%;
- max drawdown circa -56,50%;
- Sharpe circa 1,143;
- operazioni 19.

Decisione:

- non promosso perche' peggiora il drawdown rispetto alla Baseline;
- puo' restare come scenario ad alto rendimento, non come regola prudenziale.

## Test Respinti

### ATR filter

Osservazioni:

- ATR/Close >= 3% eliminava l'uscita inutile del 2023-08-02;
- era pero' una regola sostanzialmente costruita su un singolo evento;
- ATR/Close >= 6% eliminava anche uscite utili, incluse protezioni importanti
  del capitale nel 2024.

Decisione:

- ATR filter respinto per ora.

Motivo:

- le uscite devono preservare il capitale acquisito;
- il filtro ATR rischiava di impedire uscite necessarie.

### Chandelier ATR exit

Decisione:

- respinto.

Motivo:

- peggiorava molto il drawdown, arrivando circa a -66% in alcuni test.

### RSI adaptive / trailing RSI

Decisione:

- respinto per ora.

Motivo:

- instabile;
- troppe operazioni;
- miglioramento non robusto rispetto a costi, drawdown e sottoperiodi.

## Principio Di Miglioramento Attuale

Il prossimo focus non e' cambiare subito il segnale ufficiale.

Il prossimo focus e':

1. analizzare tutte le entrate storiche;
2. separare entrate vincenti, perdenti e inutili;
3. cercare pattern comuni negli ingressi sbagliati;
4. testare filtri di ingresso senza cambiare la Baseline ufficiale;
5. promuovere una regola solo se migliora piu' metriche e regge su piu'
   periodi.

## Definizione Di Entrata Corretta

Una entrata e' da considerare corretta se:

- produce un trade positivo, oppure evita di perdere un grande trend;
- non genera subito un drawdown eccessivo;
- non rientra poco prima di un nuovo `VENDI`;
- migliora Sharpe, profit factor o drawdown;
- non elimina i pochi trade molto vincenti;
- funziona su piu' anni, non solo su un singolo caso storico.

## Variabili Da Analizzare Sugli Ingressi

Per ogni ingresso storico vanno registrati:

- data ingresso effettivo;
- prezzo ingresso;
- data uscita;
- prezzo uscita;
- rendimento trade;
- drawdown massimo durante il trade;
- durata trade;
- RSI all'ingresso;
- distanza da SMA50;
- distanza da SMA200;
- pendenza SMA50;
- pendenza SMA200;
- momentum 7 giorni;
- momentum 14 giorni;
- momentum 30 giorni;
- volume relativo;
- ATR/Close;
- posizione rispetto a massimo/minimo 52 settimane;
- numero di giorni dall'ultima uscita;
- esito del rientro rispetto al prezzo della precedente uscita.

## Filtri Di Ingresso Da Testare

Da testare solo in ambiente sperimentale:

- SMA50 crescente;
- SMA200 crescente;
- Close sopra SMA50 al momento dell'ingresso;
- RSI compreso tra 40 e 65;
- distanza massima da SMA200;
- volume relativo confermato;
- momentum 14/30 giorni positivo;
- ATR/Close sotto soglia;
- cooldown dopo uscita;
- filtro anti-rientro se il prezzo rientra troppo vicino o troppo sopra il
  prezzo di uscita.

## Registro Analisi - 2026-06-28

Analisi avviata sugli ingressi Baseline dal 2022 a oggi.

File generati:

- `scripts/run_entry_quality_analysis.py`;
- `reports/entry_quality_analysis.md`;
- `scripts/run_entry_filter_hypotheses.py`;
- `reports/entry_filter_hypotheses.md`.

Nota: i CSV generati dagli script restano ignorati da Git come gli altri output
tabellari in `reports/*.csv`; sono rigenerabili.

### Qualita' ingressi 2022-oggi

Periodo: 2022-01-01 -> 2026-06-27.

Risultati:

| Metrica | Valore |
|---|---:|
| Trade chiusi analizzati | 17 |
| Trade vincenti | 5 |
| Trade perdenti | 12 |
| Win rate | 29,41% |
| Rendimento medio trade | +2,49% |
| Rendimento mediano trade | -2,90% |
| Drawdown medio interno trade | -9,49% |

Migliori trade:

| Entry signal | Exit signal | Return |
|---|---|---:|
| 2025-07-07 | 2025-09-23 | +62,70% |
| 2024-02-06 | 2024-04-03 | +38,55% |
| 2023-11-22 | 2024-01-23 | +8,84% |
| 2023-03-13 | 2023-05-08 | +7,30% |
| 2024-01-31 | 2024-02-01 | +0,28% |

Peggiori trade:

| Entry signal | Exit signal | Return |
|---|---|---:|
| 2025-10-02 | 2025-10-10 | -13,60% |
| 2024-12-05 | 2024-12-22 | -12,74% |
| 2024-04-08 | 2024-04-12 | -10,56% |
| 2024-07-19 | 2024-07-25 | -9,11% |
| 2024-05-20 | 2024-06-24 | -7,47% |

Prime differenze medie osservate tra ingressi vincenti e perdenti:

- RSI medio vincitori 54,70 contro 59,62 dei perdenti;
- volume relativo medio vincitori +23,64% contro +38,74% dei perdenti;
- posizione nel range 52w vincitori 61,40% contro 72,64% dei perdenti;
- distanza da SMA200 vincitori +14,99% contro +22,50% dei perdenti;
- momentum 7g vincitori +2,61% contro +9,46% dei perdenti.

Lettura:

- gli ingressi perdenti sembrano piu' spesso acquisti in estensione;
- il campione e' piccolo, quindi queste sono ipotesi di lavoro;
- non basta filtrare il recente: bisogna verificare che il filtro non distrugga
  il periodo completo.

### Ipotesi filtri ingresso

Performance misurata in EUR con `Close_EUR`.

Baseline 2022-oggi:

| Metrica | Valore |
|---|---:|
| Rendimento annualizzato | +4,12% |
| Max drawdown | -49,73% |
| Sharpe | 0,284 |
| Esposizione | 24,41% |

Migliore ipotesi 2022-oggi:

- variante: `rsi65_dist30_mom7_8`;
- regola sperimentale: blocca nuovi `ACQUISTA` se RSI > 65, distanza da SMA200
  > +30%, oppure momentum 7g > +8%;
- rendimento annualizzato: +12,64%;
- max drawdown: -38,76%;
- Sharpe: 0,587;
- esposizione: 20,87%.

Problema:

- sul periodo completo la stessa variante scende a rendimento annualizzato
  +16,51% e Sharpe 0,706;
- la Baseline EUR sul periodo completo fa +30,26% annuo e Sharpe 0,828;
- quindi la variante migliora il 2022-oggi ma taglia troppo rendimento storico.

Decisione:

- nessun filtro di ingresso viene promosso;
- `RSI <= 65` isolato e' piu' interessante sul periodo completo:
  +36,13% annuo, max drawdown -47,17%, Sharpe 0,944;
- va testato meglio per anni, costi e impatto sui grandi trade;
- la combinazione aggressiva resta solo come indicazione diagnostica del
  problema 2022-oggi.

## Criteri Per Promuovere Una Regola

Una regola sperimentale puo' essere candidata alla promozione solo se:

- aumenta Sharpe in modo significativo;
- migliora o non peggiora il max drawdown;
- migliora profit factor;
- riduce i falsi ingressi;
- non elimina i grandi trade vincenti;
- resta valida con costi 0,10%, 0,25% e stress 0,50%;
- regge su sottoperiodi annuali e walk-forward;
- non e' costruita su un solo evento storico.

## Prossima Analisi

Approfondire il filtro `RSI <= 65` perche':

- migliora il periodo completo senza tagliare troppo rendimento;
- migliora il drawdown rispetto alla Baseline EUR;
- e' semplice e difendibile;
- sembra coerente con il problema degli ingressi in estensione.

Test da fare:

- confronto annuale Baseline vs `RSI <= 65`;
- impatto sui 5 migliori trade dal 2022;
- scenari costi 0,10%, 0,25%, 0,50%;
- walk-forward;
- verifica se la soglia 65 e' stabile o scelta casuale.

## Registro Analisi - Prosecuzione 2026-06-28

### Validazione filtro RSI sugli ingressi

File generati:

- `scripts/run_rsi_entry_filter_validation.py`;
- `reports/rsi_entry_filter_validation.md`.

Performance misurata in EUR con `Close_EUR`.

Confronto principale:

| Variante | Periodo | Ann. | Max DD | Sharpe | Profit factor |
|---|---|---:|---:|---:|---:|
| Baseline | completo | +30,26% | -49,73% | 0,828 | 4,215 |
| RSI <= 65 | completo | +36,13% | -47,17% | 0,944 | 5,670 |
| Baseline | 2022-oggi | +4,12% | -49,73% | 0,284 | n/a |
| RSI <= 65 | 2022-oggi | +5,28% | -47,17% | 0,325 | n/a |

Sweep soglie:

- `RSI <= 62`, `RSI <= 65` e `RSI <= 68` producono risultati molto simili
  sul periodo completo;
- questo riduce il rischio che la soglia 65 sia solo un numero casuale;
- `RSI <= 58` migliora di piu' il periodo 2022-oggi ma sacrifica troppo il
  periodo completo;
- `RSI <= 72` e `RSI <= 75` coincidono di fatto con la Baseline.

Costi sul periodo completo:

| Variante | Scenario | Ann. | Max DD | Sharpe |
|---|---|---:|---:|---:|
| Baseline | 0,25% | +28,16% | -51,46% | 0,791 |
| RSI <= 65 | 0,25% | +34,02% | -49,00% | 0,907 |
| Baseline | 0,50% stress | +26,10% | -53,21% | 0,753 |
| RSI <= 65 | 0,50% stress | +31,93% | -50,85% | 0,870 |

Decisione:

- `RSI <= 65` diventa un filtro di ingresso candidato, ma non operativo;
- migliora periodo completo, drawdown, Sharpe e costi;
- non risolve da solo il problema del 2022-oggi;
- va studiato insieme alle uscite protettive.

### Validazione combinata ingresso + uscita

File generati:

- `scripts/run_combined_entry_exit_validation.py`;
- `reports/combined_entry_exit_validation.md`.

Test combinato:

- filtro ingresso `RSI <= 65`;
- trailing stop 8% sul massimo Close post-ingresso;
- conferma uscita con momentum 7g >= -5%;
- conferma volume relativo >= +10% o >= +20%.

Risultati sul periodo completo:

| Variante | Ann. | Max DD | Sharpe | Profit factor | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline | +30,26% | -49,73% | 0,828 | 4,215 | 28 |
| RSI <= 65 | +36,13% | -47,17% | 0,944 | 5,670 | 27 |
| Trail8 mom -5 vol +20 | +41,36% | -45,09% | 1,047 | 5,565 | 30 |
| RSI65 + Trail8 mom -5 vol +20 | +51,41% | -40,69% | 1,265 | 6,747 | 28 |
| RSI65 + Trail8 mom -5 vol +10 | +50,64% | -40,69% | 1,262 | 6,397 | 30 |

Risultati 2022-oggi:

| Variante | Ann. | Max DD | Sharpe |
|---|---:|---:|---:|
| Baseline | +4,12% | -49,73% | 0,284 |
| RSI <= 65 | +5,28% | -47,17% | 0,325 |
| Trail8 mom -5 vol +20 | +6,66% | -43,75% | 0,378 |
| RSI65 + Trail8 mom -5 vol +20 | +7,92% | -40,69% | 0,428 |
| RSI65 + Trail8 mom -5 vol +10 | +7,99% | -40,69% | 0,430 |

Costi sul candidato `RSI65 + Trail8 mom -5 vol +20`:

| Scenario | Ann. | Max DD | Sharpe | Profit factor |
|---|---:|---:|---:|---:|
| Lordo | +51,41% | -40,69% | 1,265 | 6,747 |
| Costo 0,10% | +50,43% | -41,52% | 1,248 | 6,625 |
| Costo 0,25% | +48,97% | -42,75% | 1,223 | 6,449 |
| Stress 0,50% | +46,56% | -44,82% | 1,180 | 6,163 |

Sottoperiodi:

- 2017-2020: Baseline Sharpe 0,988; combinato vol +20 Sharpe 1,415;
- 2021-2022: Baseline Sharpe 1,213; combinato vol +20 Sharpe 1,961;
- 2023-2026: Baseline Sharpe 0,322; combinato vol +20 Sharpe 0,485;
- 2025-2026: invariato tra varianti nel run corrente.

Decisione:

- la combinazione `RSI65 + Trail8 mom -5 vol +20` e' il miglior candidato
  sperimentale emerso finora;
- supera Sharpe 1 anche dopo costi 0,25% e nello stress 0,50%;
- riduce il max drawdown dal -49,73% al -40,69% nel confronto EUR;
- non va ancora promossa: serve controllo evento per evento e walk-forward piu'
  severo;
- il segnale ufficiale resta invariato.

### Audit evento per evento del candidato combinato

File generati:

- `scripts/run_combined_candidate_event_audit.py`;
- `reports/combined_candidate_event_audit.md`.

Candidato auditato:

- ingresso filtrato con `RSI <= 65`;
- trailing stop 8%;
- conferma momentum 7g >= -5%;
- conferma volume relativo >= +20%.

Eventi rilevati:

| Tipo evento | Conteggio |
|---|---:|
| Segnali `ACQUISTA` bloccati da RSI > 65 | 189 |
| Nuovi ingressi effettivamente bloccati | 16 |
| Episodi distinti di nuovo ingresso bloccato | 7 |
| `ACQUISTA` bloccati mentre gia' esposti | 173 |
| Uscite trailing confermate | 5 |

Episodi di nuovo ingresso bloccato:

| Periodo | Giorni | Lettura |
|---|---:|---|
| 2020-02-16 -> 2020-02-18 | 3 | RSI 71-77, distanza SMA200 47-59%, momentum alto |
| 2020-05-30 | 1 | RSI 70, distanza SMA200 37% |
| 2020-06-01 | 1 | RSI 68, momentum 20% |
| 2021-05-13 -> 2021-05-14 | 2 | distanza SMA200 156-177%, fase estremamente estesa |
| 2024-05-20 -> 2024-05-24 | 5 | RSI 68-73, volume relativo molto alto |
| 2024-05-27 -> 2024-05-28 | 2 | RSI 69-72, distanza SMA200 36-38% |
| 2024-12-05 -> 2024-12-06 | 2 | RSI 69-73, distanza SMA200 27-34% |

Uscite trailing confermate:

| Uscita | Entry | Return da entry | VENDI ufficiale successivo | Delta vs VENDI ufficiale | Rientro candidato | Delta rientro |
|---|---|---:|---|---:|---|---:|
| 2020-09-04 | 2020-07-21 | +54,42% | 2020-09-06 | -8,96% | 2020-10-12 | +0,08% |
| 2021-05-12 | 2021-03-31 | +91,62% | 2021-05-22 | -39,87% | 2021-07-26 | -39,64% |
| 2021-09-07 | 2021-07-26 | +52,91% | 2021-09-21 | -18,48% | 2021-10-01 | -1,38% |
| 2023-04-20 | 2023-03-13 | +13,06% | 2023-05-08 | -5,09% | 2023-05-05 | +0,45% |
| 2024-03-15 | 2024-02-06 | +55,53% | 2024-04-03 | -10,92% | 2024-04-08 | -0,81% |

Saldo sul segmento Baseline contenente l'uscita trailing:

| Uscita trailing | Segmento Baseline | Return Baseline | Return candidato stesso intervallo | Delta candidato |
|---|---|---:|---:|---:|
| 2020-09-04 | 2020-07-21 -> 2020-09-06 | +40,58% | +54,42% | +13,84% |
| 2021-05-12 | 2021-03-31 -> 2021-05-22 | +15,22% | +91,62% | +76,40% |
| 2021-09-07 | 2021-07-26 -> 2021-09-21 | +24,64% | +52,91% | +28,26% |
| 2023-04-20 | 2023-03-13 -> 2023-05-08 | +7,30% | +6,82% | -0,48% |
| 2024-03-15 | 2024-02-06 -> 2024-04-03 | +38,55% | +55,53% | +16,98% |

Decisione:

- 4 uscite trailing su 5 migliorano il segmento Baseline;
- 1 uscita peggiora lievemente il segmento, nel caso 2023-04-20;
- tutte le uscite anticipano un `VENDI` ufficiale successivo a prezzo piu'
  basso;
- il rientro puo' essere leggermente piu' alto in 2 casi, ma il saldo di
  protezione resta favorevole in 4 casi su 5;
- il candidato resta sperimentale ma supera il primo audit evento-per-evento.

Prossimo controllo:

- walk-forward piu' severo;
- verificare quanto il risultato dipende dai parametri `RSI 65`, `momentum -5`
  e `volume +20`;
- controllare il caso 2023-04-20 per capire se esiste una conferma aggiuntiva
  che elimini l'unica uscita leggermente inefficiente senza perdere le altre 4.

### Stress test parametri del candidato combinato

File generati:

- `scripts/run_combined_parameter_stress.py`;
- `reports/combined_parameter_stress.md`.

Griglia testata:

- RSI massimo: 60, 62, 65, 68, 70;
- momentum 7g minimo: -6%, -5%, -4%;
- volume relativo minimo: +10%, +20%, +30%, +40%;
- trailing stop fisso: 8%.

Risultato principale:

- il candidato non dipende da un singolo punto;
- esiste una zona forte con RSI 60-65, momentum -6/-5 e volume +10/+20;
- 18 combinazioni superano contemporaneamente:
  - Sharpe completo >= 1,15;
  - max drawdown non peggiore di -45%;
  - Sharpe 2022-oggi sopra Baseline.

Top per Sharpe completo:

| Variante | Ann. | Max DD | Sharpe | Sharpe 2022-oggi | PF |
|---|---:|---:|---:|---:|---:|
| RSI62 + Trail8 mom -6 vol +20 | +50,83% | -33,99% | 1,289 | 0,525 | 6,660 |
| RSI60 + Trail8 mom -6 vol +20 | +49,44% | -32,90% | 1,287 | 0,484 | 6,391 |
| RSI65 + Trail8 mom -6 vol +20 | +50,26% | -33,99% | 1,272 | 0,525 | 6,554 |
| RSI65 + Trail8 mom -5 vol +20 | +51,41% | -40,69% | 1,265 | 0,428 | 6,747 |
| RSI65 + Trail8 mom -5 vol +10 | +50,64% | -40,69% | 1,262 | 0,430 | 6,397 |

Lettura:

- la variante iniziale `RSI65 + mom -5 + vol +20` resta forte;
- la zona `mom -6 + vol +20` migliora nettamente il drawdown;
- `RSI62 + mom -6 + vol +20` diventa la migliore variante statistica della
  griglia: Sharpe 1,289 e max drawdown -33,99%;
- la scelta tra `RSI65/mom -5` e `RSI62/mom -6` non va fatta solo sul numero
  migliore: va verificata sugli eventi e sui trade persi/aggiunti.

Walk-forward:

| Train | Test | Parametri selezionati | Test Sharpe | Baseline Sharpe | Delta |
|---|---|---|---:|---:|---:|
| 2017-2020 | 2021-2022 | RSI68 mom -5 vol +10 | 1,392 | 1,213 | +0,179 |
| 2017-2022 | 2023-2026 | RSI65 mom -6 vol +30 | 0,437 | 0,322 | +0,115 |
| 2017-2024 | 2025-2026 | RSI62 mom -6 vol +20 | 0,857 | 0,857 | 0,000 |

Decisione:

- il candidato combinato supera lo stress test parametrico iniziale;
- la robustezza migliora se allarghiamo la conferma momentum da -5% a -6%;
- volume +20% resta un punto solido;
- RSI 62-65 e' la zona piu' interessante;
- nessuna regola viene promossa: serve audit evento-per-evento della nuova
  variante migliore `RSI62 + mom -6 + vol +20` e confronto diretto con
  `RSI65 + mom -5 + vol +20`.

### Confronto diretto candidati migliori

File generati:

- `scripts/run_top_candidate_comparison.py`;
- `reports/top_candidate_comparison.md`.

Varianti confrontate:

- Baseline ufficiale;
- `RSI65 + Trail8 mom -5 vol +20`;
- `RSI62 + Trail8 mom -6 vol +20`;
- `RSI65 + Trail8 mom -6 vol +20`.

Risultati periodo completo:

| Variante | Ann. | Max DD | Sharpe | PF | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline | +30,26% | -49,73% | 0,828 | 4,215 | 28 |
| RSI65 mom -5 vol +20 | +51,41% | -40,69% | 1,265 | 6,747 | 28 |
| RSI62 mom -6 vol +20 | +50,83% | -33,99% | 1,289 | 6,660 | 29 |
| RSI65 mom -6 vol +20 | +50,26% | -33,99% | 1,272 | 6,554 | 29 |

Risultati 2022-oggi:

| Variante | Ann. | Max DD | Sharpe |
|---|---:|---:|---:|
| Baseline | +4,12% | -49,73% | 0,284 |
| RSI65 mom -5 vol +20 | +7,92% | -40,69% | 0,428 |
| RSI62 mom -6 vol +20 | +10,53% | -33,99% | 0,525 |
| RSI65 mom -6 vol +20 | +10,53% | -33,99% | 0,525 |

Costi 0,25%:

| Variante | Ann. | Max DD | Sharpe |
|---|---:|---:|---:|
| Baseline | +28,16% | -51,46% | 0,791 |
| RSI65 mom -5 vol +20 | +48,97% | -42,75% | 1,223 |
| RSI62 mom -6 vol +20 | +48,32% | -36,28% | 1,244 |
| RSI65 mom -6 vol +20 | +47,75% | -36,28% | 1,227 |

Stress costi 0,50%:

| Variante | Ann. | Max DD | Sharpe |
|---|---:|---:|---:|
| Baseline | +26,10% | -53,21% | 0,753 |
| RSI65 mom -5 vol +20 | +46,56% | -44,82% | 1,180 |
| RSI62 mom -6 vol +20 | +45,84% | -38,59% | 1,198 |
| RSI65 mom -6 vol +20 | +45,28% | -38,59% | 1,181 |

Criticita' evento-per-evento:

- `mom -6` aggiunge un'uscita nel gennaio 2021 che non era presente nella
  variante `mom -5`;
- questa uscita e' una falsa uscita in trend forte:
  - `RSI62 mom -6 vol +20`: uscita 2021-01-11, rientro 2021-01-22 a +13,32%;
    saldo sul segmento Baseline 2020-10-21 -> 2021-02-26: -42,55%;
  - `RSI65 mom -6 vol +20`: uscita 2021-01-12, rientro 2021-01-22 a +18,86%;
    saldo sullo stesso segmento: -57,44%;
- nonostante questo, le metriche globali restano migliori grazie al drawdown
  molto piu' basso e ad altre uscite protettive;
- questa criticita' rende la variante `mom -6` piu' forte statisticamente ma
  meno pulita concettualmente.

Decisione:

- `RSI62 mom -6 vol +20` e' il migliore per Sharpe e drawdown;
- `RSI65 mom -6 vol +20` e' quasi equivalente ma blocca meno ingressi;
- `RSI65 mom -5 vol +20` e' meno performante ma evita la falsa uscita di
  gennaio 2021;
- nessuna variante viene promossa;
- prossimo test: cercare una conferma anti-falsa-uscita per gennaio 2021 senza
  perdere le uscite protettive del 2021-05, 2021-09, 2024-03 e 2024-12.

### Ricorrenza falsa uscita gennaio 2021

File generati:

- `scripts/run_false_exit_recurrence_analysis.py`;
- `reports/false_exit_recurrence.md`.

Definizione di evento tipo gennaio 2021:

- uscita trailing confermata;
- `VENDI` ufficiale successivo a prezzo piu' alto;
- rientro candidato a prezzo piu' alto;
- saldo del segmento peggiore della Baseline di almeno 5 punti percentuali.

Risultato:

| Variante | Uscite | Segmenti peggiori | Eventi tipo gennaio 2021 |
|---|---:|---:|---:|
| RSI62 mom -6 vol +20 | 7 | 2 | 1 |
| RSI65 mom -5 vol +20 | 5 | 1 | 0 |
| RSI65 mom -6 vol +20 | 7 | 2 | 1 |
| Trail only mom -6 vol +20 | 8 | 3 | 1 |

Eventi tipo gennaio 2021:

| Variante | Uscita | Segmento Baseline | Delta segmento | Rientro | Delta rientro |
|---|---|---|---:|---|---:|
| RSI62 mom -6 vol +20 | 2021-01-11 | 2020-10-21 -> 2021-02-26 | -42,55% | 2021-01-22 | +13,32% |
| RSI65 mom -6 vol +20 | 2021-01-12 | 2020-10-21 -> 2021-02-26 | -57,44% | 2021-01-22 | +18,86% |
| Trail only mom -6 vol +20 | 2021-01-12 | 2020-10-21 -> 2021-02-26 | -89,30% | 2021-01-19 | +32,75% |

Falsi segnali minori:

- 2023-04-20: peggiora il segmento di circa -0,48%;
- 2024-06-17 nella variante senza filtro RSI: peggiora di circa -0,28%.

Decisione:

- il comportamento grave del gennaio 2021 appare isolato;
- il problema nasce dalla soglia `momentum >= -6%`;
- la variante `momentum >= -5%` evita questa falsa uscita grave;
- quindi gennaio 2021 va trattato come fenomeno raro di trend parabolico, non
  come errore ricorrente ordinario;
- questo rende `RSI65 mom -5 vol +20` meno aggressiva ma piu' pulita;
- `RSI62/65 mom -6 vol +20` resta statisticamente superiore, ma richiede una
  protezione anti-trend-parabolico prima di essere considerata candidata
  promuovibile.

### Separazione tra ingresso, uscita e combinazioni

File generati:

- `scripts/run_signal_component_analysis.py`;
- `reports/signal_component_analysis.md`.

Motivazione:

- la tabella unica con benchmark passivo, Baseline, uscite, ingressi e
  combinazioni generava confusione;
- i modelli vanno valutati per funzione:
  - benchmark;
  - uscita;
  - ingresso;
  - combinazioni.

Regola di analisi da qui in avanti:

- un modello di uscita si valuta lasciando invariati gli ingressi Baseline;
- un filtro di ingresso si valuta lasciando invariata l'uscita ufficiale;
- una combinazione si valuta solo dopo aver capito separatamente i due
  componenti.

Risultati chiave separati:

Benchmark:

| Modello | Ann. | Max DD | Sharpe |
|---|---:|---:|---:|
| Baseline ufficiale | +30,26% | -49,73% | 0,828 |

Uscite, con ingressi Baseline invariati:

| Modello uscita | Ann. | Max DD | Sharpe | Lettura |
|---|---:|---:|---:|---|
| Baseline ufficiale | +30,26% | -49,73% | 0,828 | riferimento |
| Trailing 8% puro | +20,61% | -40,24% | 0,698 | scartato: troppi falsi stop |
| Trail8 -5 / vol +20 | +41,36% | -45,09% | 1,047 | uscita pulita candidata |
| Trail8 -6 / vol +20 | +38,50% | -45,09% | 1,004 | migliora 2022+, ma falso stop gennaio 2021 |

Ingressi, con uscita ufficiale invariata:

| Filtro ingresso | Ann. | Max DD | Sharpe | Lettura |
|---|---:|---:|---:|---|
| Baseline ufficiale | +30,26% | -49,73% | 0,828 | riferimento |
| RSI <= 65 | +36,13% | -47,17% | 0,944 | candidato ingresso pulito |
| RSI <= 62 | +35,89% | -47,17% | 0,943 | simile a RSI65, piu' restrittivo |
| RSI <= 60 | +34,93% | -46,29% | 0,930 | troppo restrittivo rispetto al vantaggio |

Combinazioni:

| Combinazione | Ann. | Max DD | Sharpe | Lettura |
|---|---:|---:|---:|---|
| RSI65 + Trail8 -5 / vol +20 | +51,41% | -40,69% | 1,265 | candidato prudente principale |
| RSI65 + Trail8 -6 / vol +20 | +50,26% | -33,99% | 1,272 | forte ma falso stop gennaio 2021 |
| RSI62 + Trail8 -6 / vol +20 | +50,83% | -33,99% | 1,289 | migliore metricamente, ma piu' aggressivo |

Decisione:

- uscita candidata pulita: `Trail8 confermato -5 / vol +20`;
- ingresso candidato pulito: `RSI <= 65`;
- combinazione candidata prudente: `RSI65 + Trail8 -5 / vol +20`;
- combinazione aggressiva da correggere: `RSI62/65 + Trail8 -6 / vol +20`;
- le prossime analisi devono mantenere questa separazione.

### Focus corrente: solo ingressi

File generati:

- `scripts/run_entry_signal_analysis.py`;
- `reports/entry_signal_analysis.md`.

Regola metodologica:

- benchmark operativo: `Baseline ufficiale`;
- uscita sempre invariata: `VENDI` sotto SMA50 per 2 giorni consecutivi;
- nessun trailing stop in questa analisi;
- nessuna combinazione ingresso + uscita in questa analisi;
- nessuna modifica promossa nei segnali ufficiali.

Metriche ingresso-only:

| Filtro ingresso | Ann. | Max DD | Sharpe | PF | Ops | 2022+ Ann. | 2022+ DD | Nuovi ingressi bloccati |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | +30,26% | -49,73% | 0,828 | 4,215 | 28 | +4,12% | -49,73% | 0 |
| RSI <= 65 | +36,13% | -47,17% | 0,944 | 5,670 | 27 | +5,28% | -47,17% | 14 |
| RSI <= 62 | +35,89% | -47,17% | 0,943 | 5,652 | 27 | +5,28% | -47,17% | 21 |
| RSI <= 60 | +34,93% | -46,29% | 0,930 | 5,708 | 27 | +4,10% | -46,29% | 38 |

Decisione provvisoria sugli ingressi:

- `RSI <= 65` e' il candidato principale: migliora rendimento, drawdown,
  Sharpe e profit factor rispetto alla Baseline, bloccando meno ingressi delle
  soglie piu' severe;
- `RSI <= 62` resta in osservazione, ma al momento non giustifica la maggiore
  restrittivita';
- `RSI <= 60` e' troppo restrittivo rispetto al beneficio;
- il prossimo approfondimento deve restare sugli ingressi, evento per evento,
  prima di tornare ai modelli di uscita.

### Audit ingressi bloccati da RSI <= 65

File generati:

- `scripts/run_rsi65_blocked_entry_audit.py`;
- `reports/rsi65_blocked_entry_audit.md`.

Metodo:

- analisi solo sugli ingressi;
- uscita ufficiale invariata;
- soglia testata: blocco dei nuovi `ACQUISTA` quando `RSI > 65`;
- confronto evento-per-evento tra ingresso Baseline e successivo comportamento
  del filtro RSI65.

Risultato:

| Misura | Valore |
|---|---:|
| Segnali giornalieri bloccati | 14 |
| Finestre operative bloccate | 6 |
| Trade Baseline unici coinvolti | 4 |
| Trade Baseline unici perdenti | 4 |
| Finestre utili | 6 |
| Finestre miste | 0 |
| Finestre costose | 0 |

Eventi principali:

| Blocco | Return Baseline | Max DD trade | Nuovo ingresso RSI65 | Delta ingresso | Return trade RSI65 | Lettura |
|---|---:|---:|---|---:|---:|---|
| 2020-02-16 -> 2020-02-18 | -26,07% | -32,52% | 2020-06-02 | -11,53% | -3,95% | salta trade perdente |
| 2020-05-30 | -6,66% | -10,48% | 2020-06-02 | -2,82% | -3,95% | ritarda ingresso perdente |
| 2020-06-01 | -6,66% | -10,48% | 2020-06-02 | -4,47% | -3,95% | ritarda ingresso perdente |
| 2024-05-20 -> 2024-05-24 | -7,47% | -12,88% | 2024-06-20 | -2,79% | -4,81% | ritarda ingresso perdente |
| 2024-05-27 -> 2024-05-28 | -7,47% | -12,88% | 2024-06-20 | -8,48% | -4,81% | ritarda ingresso perdente |
| 2024-12-05 -> 2024-12-06 | -12,74% | -17,15% | 2024-12-09 | -2,12% | -10,84% | ritarda ingresso perdente |

Conclusione:

- l'evidenza evento-per-evento conferma il filtro `RSI <= 65`;
- il filtro intercetta solo trade Baseline perdenti nei casi analizzati;
- quando rientra, il prezzo di rientro e' sempre piu' basso del prezzo
  bloccato;
- non sono emersi casi in cui il filtro taglia un trade Baseline vincente;
- la regola resta sperimentale: prima di promuoverla servono validazione
  annuale, costi/slippage e controllo della dipendenza da pochi eventi.

### Confronto trade-by-trade Baseline vs RSI <= 65

File generati:

- `scripts/run_entry_trade_comparison.py`;
- `reports/entry_trade_comparison.md`.

Periodo:

- inizio serie comune ETH/EUR -> candela del 2026-06-27.

Regole:

- Baseline ufficiale invariata;
- modello sperimentale: Baseline + filtro nuovo ingresso `RSI <= 65`;
- uscita invariata: `VENDI` sotto SMA50 per 2 giorni consecutivi;
- prezzi e rendimenti calcolati su `Close_EUR` della candela del segnale.

Sintesi:

| Modello | Trade | Ann. | Max DD sistema | Sharpe | PF | Win rate | Loss medio | DD medio trade |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 28 | +30,26% | -49,73% | 0,828 | 4,215 | 39,29% | -7,64% | -13,96% |
| RSI <= 65 ingresso | 27 | +36,13% | -47,17% | 0,944 | 5,670 | 40,74% | -6,03% | -12,92% |

Trade modificati dal filtro:

| Ingresso RSI65 | Prezzo | Uscita | Return | DD subito | DD evitato vs Baseline | Lettura |
|---|---:|---|---:|---:|---:|---|
| 2020-06-02 | 212,07 | 2020-07-17 | -3,95% | -8,78% | +1,69% | ritarda ingresso Baseline perdente |
| 2024-06-20 | 3279,52 | 2024-06-24 | -4,81% | -5,07% | +7,81% | ritarda ingresso Baseline perdente |
| 2024-12-09 | 3523,42 | 2024-12-22 | -10,84% | -17,15% | 0,00% | migliora entry/return, non riduce DD interno |

Conclusione:

- il filtro `RSI <= 65` modifica solo 3 trade effettivi rispetto alla Baseline;
- non elimina trade vincenti;
- riduce il loss medio e migliora profit factor, Sharpe e rendimento
  annualizzato;
- la riduzione del drawdown di sistema e' moderata, quindi il filtro migliora
  soprattutto la qualita' degli ingressi, non risolve da solo il problema del
  drawdown;
- prossimo passo: validazione annuale e stress con costi/slippage prima di
  promuovere il filtro.

### Validazione annuale Baseline vs RSI <= 65

File generati:

- `scripts/run_entry_yearly_validation.py`;
- `reports/entry_yearly_validation.md`.

Metodo:

- confronto anno per anno;
- uscita ufficiale invariata;
- conteggio operazioni diviso in:
  - ingressi aperti nell'anno;
  - trade chiusi nell'anno.

Risultati annuali:

| Anno | Baseline Ret | RSI65 Ret | Delta Ret | Baseline DD | RSI65 DD | Delta DD | Entry B/R | Chiusi B/R |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 0,00% | 0,00% | 0,00% | 0,00% | 0,00% | 0,00% | 0/0 | 0/0 |
| 2018 | 0,00% | 0,00% | 0,00% | 0,00% | 0,00% | 0,00% | 0/0 | 0/0 |
| 2019 | +60,32% | +60,32% | 0,00% | -19,32% | -19,32% | 0,00% | 1/1 | 1/1 |
| 2020 | +69,85% | +136,42% | +66,57% | -38,20% | -29,21% | +8,99% | 5/4 | 4/3 |
| 2021 | +201,42% | +201,42% | 0,00% | -45,09% | -45,09% | 0,00% | 5/5 | 6/6 |
| 2022 | 0,00% | 0,00% | 0,00% | 0,00% | 0,00% | 0,00% | 0/0 | 0/0 |
| 2023 | +0,09% | +0,09% | 0,00% | -22,67% | -22,67% | 0,00% | 6/6 | 5/5 |
| 2024 | -14,58% | -10,22% | +4,36% | -47,85% | -45,19% | +2,66% | 7/7 | 8/8 |
| 2025 | +35,98% | +35,98% | 0,00% | -26,08% | -26,08% | 0,00% | 4/4 | 4/4 |
| 2026 | 0,00% | 0,00% | 0,00% | 0,00% | 0,00% | 0,00% | 0/0 | 0/0 |

Lettura:

- il numero di operazioni cambia solo nel 2020;
- il rendimento cambia in modo reale nel 2020 e nel 2024;
- `RSI <= 65` non peggiora nessun anno in modo materiale;
- il vantaggio principale e' concentrato nel 2020, con supporto minore nel
  2024;
- questo e' favorevole, ma non basta ancora per promuovere il filtro: serve
  stress con costi/slippage e controllo di robustezza soglia.

### Stress costi/slippage Baseline vs RSI <= 65

File generati:

- `scripts/run_entry_cost_stress.py`;
- `reports/entry_cost_stress.md`.

Metodo:

- confronto solo sugli ingressi;
- uscita ufficiale invariata;
- costi applicati a ogni cambio esposizione, quindi ingresso e uscita;
- scenari: 0,00%, 0,10%, 0,25%, 0,50%, 1,00% per cambio esposizione.

Risultati periodo completo:

| Scenario | Baseline Ann. | RSI65 Ann. | Delta Ann. | Baseline DD | RSI65 DD | Delta DD | Delta Sharpe | Delta PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| lordo 0,00% | +30,26% | +36,13% | +5,87% | -49,73% | -47,17% | +2,56% | +0,116 | +1,455 |
| costo 0,10% | +29,42% | +35,28% | +5,86% | -50,43% | -47,91% | +2,52% | +0,116 | +1,414 |
| costo 0,25% | +28,16% | +34,02% | +5,85% | -51,46% | -49,00% | +2,46% | +0,116 | +1,355 |
| stress 0,50% | +26,10% | +31,93% | +5,83% | -53,21% | -50,85% | +2,36% | +0,116 | +1,261 |
| stress 1,00% | +22,05% | +27,84% | +5,79% | -56,61% | -54,44% | +2,17% | +0,117 | +1,098 |

Lettura:

- il vantaggio di `RSI <= 65` resta stabile anche con costi molto severi;
- il delta annuo resta circa +5,8 punti;
- il max drawdown resta meno profondo in tutti gli scenari;
- RSI65 fa una operazione in meno, ma il vantaggio non deriva solo dal
  risparmio costi: deriva soprattutto dagli ingressi evitati o ritardati;
- dopo audit eventi, validazione annuale e stress costi, il filtro `RSI <= 65`
  e' un candidato ingresso robusto, ancora non promosso a segnale ufficiale.

### Robustezza soglia RSI fino a 70

File generati:

- `scripts/run_entry_threshold_robustness.py`;
- `reports/entry_threshold_robustness.md`.

Metodo:

- confronto solo sugli ingressi;
- uscita ufficiale invariata;
- soglie testate: `RSI <= 63`, `64`, `65`, `66`, `67`, `68`, `69`, `70`;
- Baseline ufficiale come benchmark operativo.

Risultati:

| Variante | Ann. | Max DD | Sharpe | PF | Ops | Nuovi ingressi bloccati | 2022+ Ann. |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | +30,26% | -49,73% | 0,828 | 4,215 | 28 | 0 | +4,12% |
| RSI <= 63 | +36,13% | -47,17% | 0,944 | 5,670 | 27 | 14 | +5,28% |
| RSI <= 64 | +36,13% | -47,17% | 0,944 | 5,670 | 27 | 14 | +5,28% |
| RSI <= 65 | +36,13% | -47,17% | 0,944 | 5,670 | 27 | 14 | +5,28% |
| RSI <= 66 | +36,13% | -47,17% | 0,944 | 5,670 | 27 | 14 | +5,28% |
| RSI <= 67 | +36,13% | -47,17% | 0,944 | 5,670 | 27 | 14 | +5,28% |
| RSI <= 68 | +35,41% | -47,17% | 0,931 | 5,428 | 27 | 13 | +5,28% |
| RSI <= 69 | +34,35% | -50,61% | 0,910 | 5,115 | 27 | 8 | +3,71% |
| RSI <= 70 | +34,27% | -50,88% | 0,909 | 5,092 | 27 | 6 | +3,59% |

Lettura:

- la zona `RSI <= 63` fino a `RSI <= 67` e' perfettamente stabile: stessi
  risultati, stessi ingressi bloccati, stesse metriche;
- `RSI <= 68` resta positivo ma inizia a perdere rendimento e profit factor;
- `RSI <= 69` e `RSI <= 70` peggiorano il max drawdown rispetto alla Baseline;
- quindi il limite superiore non deve essere portato a 69/70;
- `RSI <= 65` resta una scelta equilibrata e spiegabile dentro una fascia
  robusta, non un punto fragile ottimizzato.

### Decisione di chiusura provvisoria sugli ingressi

Decisione:

- `RSI <= 65` e' il miglior candidato disponibile per filtrare i nuovi
  ingressi;
- non diventa ancora segnale ufficiale della Baseline;
- resta appuntato come candidato ingresso principale nel diario di ricerca;
- la Baseline ufficiale resta invariata;
- il filtro potra' diventare ufficiale solo dopo test combinato con il futuro
  candidato di uscita.

Motivazione:

- il filtro affianca le condizioni di acquisto Baseline, non le sostituisce;
- formula candidata:
  `Close > SMA200`, `SMA50 > SMA200`, `RSI >= 40`, `RSI <= 65`,
  `Close > Close_7d_ago`, `Volume > VolumeAvg20`;
- ha superato audit evento-per-evento, validazione annuale, stress
  costi/slippage e robustezza soglia;
- il beneficio sul drawdown e' reale ma moderato, quindi il problema principale
  resta il segnale di uscita.

Regola operativa per i prossimi test:

- da ora si procede sul segnale di uscita;
- durante i test di uscita gli ingressi restano quelli Baseline ufficiali;
- il candidato `RSI <= 65` verra' riutilizzato solo nella fase successiva di
  test combinato ingresso + uscita.

### Ripresa analisi uscite: confronto iniziale

File generati:

- `scripts/run_exit_signal_analysis.py`;
- `reports/exit_signal_analysis.md`.

Metodo:

- analisi solo sulle uscite;
- ingressi Baseline ufficiali invariati;
- nessun filtro RSI65 sugli ingressi;
- benchmark operativo: `Baseline ufficiale`;
- periodo: 2017-11-11 -> 2026-06-27.

Risultati:

| Modello uscita | Ann. | Max DD | Sharpe | PF | Ops | Uscite forzate | 2022+ Ann. | 2022+ DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | +30,26% | -49,73% | 0,828 | 4,215 | 28 | 0 | +4,12% | -49,73% |
| SMA50 1 giorno | +32,49% | -48,09% | 0,880 | 4,506 | 32 | 26 | +10,15% | -40,94% |
| Trailing 8% puro | +20,61% | -40,24% | 0,698 | 2,157 | 48 | 31 | +2,00% | -40,24% |
| Trail8 confermato -5 / vol +20 | +41,36% | -45,09% | 1,047 | 5,565 | 30 | 6 | +6,66% | -43,75% |
| Trail8 confermato -6 / vol +20 | +38,50% | -45,09% | 1,004 | 5,133 | 31 | 8 | +9,24% | -37,39% |

Lettura:

- `Trailing 8% puro` riduce il drawdown ma peggiora rendimento, Sharpe e
  profit factor: resta scartato;
- `SMA50 1 giorno` migliora il periodo recente ma forza troppe uscite e non
  offre il miglior equilibrio;
- `Trail8 confermato -5 / vol +20` migliora rendimento, drawdown, Sharpe e
  profit factor con solo 6 uscite forzate;
- `Trail8 confermato -6 / vol +20` sembra forte sul recente, ma ripropone il
  falso stop grave del 2021-01-12;
- quindi il candidato uscita principale da approfondire e' `Trail8 confermato
  -5 / vol +20`.

Decisione provvisoria sulle uscite:

- nessuna uscita viene promossa a regola ufficiale;
- prossimo test: audit evento-per-evento del solo `Trail8 confermato -5 / vol
  +20`, distinguendo uscite utili, neutre e dannose rispetto all'uscita
  ufficiale e al rientro successivo.

### Audit evento-per-evento Trail8 -5 / vol +20

File generati:

- `scripts/run_trail5_exit_event_audit.py`;
- `reports/trail5_exit_event_audit.md`.

Metodo:

- analisi solo sulle uscite;
- ingressi Baseline ufficiali invariati;
- candidato testato: `Trail8 confermato -5 / vol +20`;
- per ogni uscita sono misurati:
  - data e prezzo di uscita;
  - data e prezzo del rientro successivo;
  - rendimento dal precedente ingresso alla data di uscita;
  - drawdown subito nel trade;
  - drawdown evitato tra uscita e rientro successivo;
  - upside perso tra uscita e rientro successivo.

Risultati:

| Uscita | Prezzo uscita | Rientro | Prezzo rientro | Return trade | DD subito | DD evitato | Upside perso | Lettura |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 2020-02-20 | 239,11 | 2020-05-30 | 218,23 | -0,25% | -8,45% | +58,55% | +5,64% | utile |
| 2020-09-04 | 327,96 | 2020-10-12 | 328,23 | +54,42% | -18,58% | +16,00% | +0,10% | utile |
| 2021-09-07 | 2892,82 | 2021-10-01 | 2852,80 | +52,91% | -13,00% | +18,48% | +5,74% | utile |
| 2023-04-20 | 1771,60 | 2023-05-05 | 1779,61 | +13,06% | -8,39% | +5,93% | +0,45% | utile |
| 2024-03-15 | 3429,87 | 2024-04-08 | 3402,13 | +55,53% | -7,80% | +15,24% | +0,00% | utile |
| 2024-06-17 | 3269,43 | 2024-06-20 | 3279,52 | -3,09% | -9,83% | +0,78% | +1,30% | dannosa |

Sintesi:

- uscite forzate: 6;
- trade positivi al momento dell'uscita: 4;
- trade negativi al momento dell'uscita: 2;
- uscite utili: 5;
- uscite dannose: 1;
- nessuna uscita neutra.

Lettura:

- il candidato protegge bene capitale acquisito in 5 casi su 6;
- la principale anomalia e' il 2024-06-17: esce in perdita, evita poco
  drawdown e rientra leggermente piu' alto dopo 3 giorni;
- il candidato resta valido da approfondire, ma prima della promozione serve
  capire se l'uscita dannosa del 2024-06-17 puo' essere filtrata senza perdere
  le cinque uscite utili.

### Confronto completo operazioni Baseline vs Trail8 -5 / vol +20

File generati:

- `scripts/run_exit_trade_comparison.py`;
- `reports/exit_trade_comparison.md`.

Correzione metodologica:

- l'audit precedente sulle 6 uscite anticipate non basta per giudicare il
  modello;
- serve confrontare tutte le operazioni Baseline con tutte le operazioni del
  candidato;
- alcune uscite anticipate spezzano un trade Baseline e generano nuovi trade
  successivi.

Sintesi:

| Misura | Baseline | Trail8 -5 / vol +20 |
|---|---:|---:|
| Operazioni chiuse | 28 | 30 |
| Rendimento annualizzato | +30,26% | +41,36% |
| Max DD sistema | -49,73% | -45,09% |
| Sharpe | 0,828 | 1,047 |
| Profit factor | 4,215 | 5,565 |
| Win rate | 39,29% | 36,67% |

Operazioni:

- operazioni identiche per ingresso e uscita: 22;
- uscite anticipate Trail8 confermate: 6;
- trade Baseline modificati: 6;
- trade candidati diversi rispetto alla Baseline: 8;
- operazioni candidato con drawdown minore del riferimento Baseline: 8.

Trade candidati modificati principali:

| # | Ingresso | Uscita | Tipo uscita | Return | DD subito | DD evitato vs Baseline | Delta return vs Baseline | Rif. Baseline |
|---:|---|---|---|---:|---:|---:|---:|---|
| 2 | 2020-02-16 | 2020-02-20 | trail8 | -0,25% | -8,45% | +24,07% | +25,82% | 2020-02-16 -> 2020-03-09 |
| 4 | 2020-07-21 | 2020-09-04 | trail8 | +54,42% | -18,58% | +10,63% | +13,84% | 2020-07-21 -> 2020-09-06 |
| 9 | 2021-07-26 | 2021-09-07 | trail8 | +52,91% | -13,00% | +16,08% | +28,26% | 2021-07-26 -> 2021-09-21 |
| 13 | 2023-03-13 | 2023-04-20 | trail8 | +13,06% | -8,39% | +5,26% | +5,75% | 2023-03-13 -> 2023-05-08 |
| 14 | 2023-05-05 | 2023-05-08 | ufficiale | -5,52% | -5,52% | +8,13% | -12,82% | 2023-03-13 -> 2023-05-08 |
| 20 | 2024-02-06 | 2024-03-15 | trail8 | +55,53% | -7,80% | +14,05% | +16,98% | 2024-02-06 -> 2024-04-03 |
| 22 | 2024-05-20 | 2024-06-17 | trail8 | -3,09% | -9,83% | +3,05% | +4,38% | 2024-05-20 -> 2024-06-24 |
| 23 | 2024-06-20 | 2024-06-24 | ufficiale | -4,81% | -5,07% | +7,81% | +2,65% | 2024-05-20 -> 2024-06-24 |

Lettura:

- il confronto serio conferma che il candidato migliora le metriche aggregate;
- i trade identici sono 22, quindi il candidato interviene in modo mirato;
- il caso 2023-03 genera un'uscita anticipata positiva ma anche un rientro
  successivo negativo: il saldo va valutato sul segmento completo;
- il caso 2024-06 resta da studiare, ma nel confronto con l'intero trade
  Baseline il segmento candidato riduce sia perdita sia drawdown;
- prossima analisi: valutare i 6 segmenti modificati come blocchi completi,
  non solo come singoli trade, per capire il contributo netto di ogni modifica.

### Impatto netto dei 6 segmenti modificati

File generati:

- `scripts/run_exit_segment_impact.py`;
- `reports/exit_segment_impact.md`.

Metodo:

- ogni segmento e' un trade Baseline originale modificato dal candidato;
- il candidato puo' spezzare il segmento in piu' trade;
- il confronto viene fatto sul saldo completo del segmento.

Sintesi:

| Misura | Valore |
|---|---:|
| Segmenti modificati | 6 |
| Segmenti con delta rendimento positivo | 4 |
| Segmenti con delta rendimento negativo | 2 |
| Rendimento composto Baseline sui segmenti | +78,22% |
| Rendimento composto candidato sui segmenti | +260,97% |
| Delta composto candidato - Baseline | +182,75% |

Dettaglio:

| # | Segmento Baseline | Return Baseline | DD Baseline | Return candidato | DD candidato | DD evitato | Delta return | Lettura |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 2020-02-16 -> 2020-03-09 | -26,07% | -32,52% | -0,25% | -8,45% | +24,07% | +25,82% | migliora rendimento e DD |
| 2 | 2020-07-21 -> 2020-09-06 | +40,58% | -29,21% | +54,42% | -18,58% | +10,63% | +13,84% | migliora rendimento e DD |
| 3 | 2021-07-26 -> 2021-09-21 | +24,64% | -29,08% | +52,91% | -13,00% | +16,08% | +28,26% | migliora rendimento e DD |
| 4 | 2023-03-13 -> 2023-05-08 | +7,30% | -13,65% | +6,82% | -8,39% | +5,26% | -0,48% | riduce DD, perde poco rendimento |
| 5 | 2024-02-06 -> 2024-04-03 | +38,55% | -21,86% | +55,53% | -7,80% | +14,05% | +16,98% | migliora rendimento e DD |
| 6 | 2024-05-20 -> 2024-06-24 | -7,47% | -12,88% | -7,75% | -9,83% | +3,05% | -0,28% | riduce DD, perde poco rendimento |

Conclusione:

- il candidato `Trail8 confermato -5 / vol +20` e' valido sui segmenti
  modificati;
- 4 segmenti su 6 migliorano sia rendimento sia drawdown;
- 2 segmenti peggiorano il rendimento di poco, ma riducono il drawdown;
- il saldo composto dei segmenti modificati e' nettamente favorevole;
- il candidato resta il principale candidato uscita.

Prossimo passo:

- stress costi/slippage dedicato al candidato uscita;
- validazione anno per anno;
- solo dopo test combinato con il candidato ingresso `RSI <= 65`.

### Validazione candidato uscita: costi e anni

File generati:

- `scripts/run_exit_candidate_validation.py`;
- `reports/exit_candidate_validation.md`;
- `reports/exit_candidate_cost_stress.csv`;
- `reports/exit_candidate_yearly_validation.csv`.

Metodo:

- candidato uscita: `Trail8 confermato -5 / vol +20`;
- ingressi Baseline ufficiali invariati;
- stress costi/slippage da 0,00% a 1,00% per cambio esposizione;
- validazione anno per anno.

Stress costi:

| Scenario | Baseline Ann. | Candidato Ann. | Delta Ann. | Baseline DD | Candidato DD | Delta DD | Delta Sharpe | Delta PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| lordo 0,00% | +30,26% | +41,36% | +11,10% | -49,73% | -45,09% | +4,64% | +0,219 | +1,351 |
| costo 0,10% | +29,42% | +40,38% | +10,96% | -50,43% | -45,15% | +5,28% | +0,217 | +1,309 |
| costo 0,25% | +28,16% | +38,92% | +10,76% | -51,46% | -45,95% | +5,51% | +0,214 | +1,250 |
| stress 0,50% | +26,10% | +36,52% | +10,42% | -53,21% | -48,16% | +5,05% | +0,209 | +1,156 |
| stress 1,00% | +22,05% | +31,83% | +9,78% | -56,61% | -52,41% | +4,20% | +0,199 | +0,997 |

Validazione annuale:

| Anno | Baseline Ret | Candidato Ret | Delta Ret | Baseline DD | Candidato DD | Delta DD |
|---:|---:|---:|---:|---:|---:|---:|
| 2019 | +60,32% | +60,32% | 0,00% | -19,32% | -19,32% | 0,00% |
| 2020 | +69,85% | +151,72% | +81,87% | -38,20% | -22,08% | +16,12% |
| 2021 | +201,42% | +269,77% | +68,34% | -45,09% | -45,09% | 0,00% |
| 2023 | +0,09% | -0,36% | -0,45% | -22,67% | -23,02% | -0,35% |
| 2024 | -14,58% | -4,40% | +10,17% | -47,85% | -41,64% | +6,21% |
| 2025 | +35,98% | +35,98% | 0,00% | -26,08% | -26,08% | 0,00% |

Conclusione:

- il candidato uscita supera lo stress costi/slippage;
- anche con costo 1,00% per cambio esposizione resta sopra Baseline di circa
  +9,78 punti annui;
- migliora in modo materiale 2020, 2021 e 2024;
- peggiora lievemente il 2023: -0,45% rendimento e -0,35% drawdown;
- il peggioramento 2023 e' contenuto e coerente con il segmento 2023-03 gia'
  identificato;
- il candidato `Trail8 confermato -5 / vol +20` resta candidato uscita
  principale.

Prossimo passo:

- test combinato fra candidato ingresso `RSI <= 65` e candidato uscita `Trail8
  confermato -5 / vol +20`;
- confronto contro Baseline ufficiale su periodo completo, anni, costi e
  segmenti critici;
- solo dopo si potra' discutere una possibile promozione a segnale ufficiale.

### Comparazione finale candidato combinato

File generati:

- `scripts/run_final_combined_candidate_validation.py`;
- `reports/final_combined_candidate_validation.md`;
- `reports/final_combined_cost_stress.csv`;
- `reports/final_combined_yearly_validation.csv`;
- `reports/final_combined_trades.csv`.

Metodo:

- Baseline ufficiale invariata;
- ingresso candidato: Baseline + `RSI <= 65` sui nuovi acquisti;
- uscita candidata: uscita ufficiale + `Trail8 confermato -5 / vol +20`;
- periodo completo: `2017-11-11` -> `2026-06-27`;
- stress costi/slippage da 0,00% a 1,00% per cambio esposizione;
- validazione anno per anno.

Risultato lordo periodo completo:

| Modello | Ann. | Max DD | Sharpe | Profit factor | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline ufficiale | +30,26% | -49,73% | 0,828 | 4,215 | 28 |
| Combinato RSI65 + Trail8 -5/vol20 | +42,74% | -45,09% | 1,079 | 5,999 | 28 |
| Delta | +12,48% | +4,64% | +0,251 | +1,784 | 0 |

Stress costi:

| Scenario | Delta Ann. | Delta DD | Delta Sharpe | Delta PF |
|---|---:|---:|---:|---:|
| lordo 0,00% | +12,48% | +4,64% | +0,251 | +1,784 |
| costo 0,10% | +12,40% | +5,28% | +0,250 | +1,737 |
| costo 0,25% | +12,28% | +6,23% | +0,248 | +1,671 |
| stress 0,50% | +12,08% | +7,84% | +0,246 | +1,564 |
| stress 1,00% | +11,68% | +7,75% | +0,240 | +1,379 |

Validazione annuale:

| Anno | Delta rendimento | Delta drawdown | Lettura |
|---:|---:|---:|---|
| 2020 | +89,84% | +16,12% | migliora molto |
| 2021 | +68,34% | 0,00% | migliora rendimento, DD invariato |
| 2023 | -0,45% | -0,35% | unico peggioramento residuo |
| 2024 | +15,36% | +9,38% | migliora rendimento e DD |
| 2025 | 0,00% | 0,00% | invariato |

Eventi:

- ingressi bloccati da `RSI <= 65`: 14 segnali giornalieri;
- uscite forzate Trail8 confermate nel combinato: 4;
- operazioni totali: 28, come la Baseline.

Conclusione:

- il candidato combinato e' il migliore test disponibile finora;
- migliora rendimento annualizzato, drawdown, Sharpe e profit factor;
- resta robusto anche con costi/slippage elevati;
- non aumenta il numero totale di operazioni rispetto alla Baseline;
- il 2023 resta l'unico anno con peggioramento residuo, piccolo ma da non
  ignorare;
- il combinato non diventa ancora segnale ufficiale: resta candidato finale in
  validazione.

Decisione:

- mantenere la Baseline ufficiale invariata;
- tenere `RSI <= 65` come candidato ingresso principale;
- tenere `Trail8 confermato -5 / vol +20` come candidato uscita principale;
- usare il combinato come candidato finale da valutare al prossimo gate
  decisionale.

Prossimo passo:

- audit dedicato del peggioramento residuo 2023;
- verificare se il segmento 2023 va accettato come costo fisiologico del
  modello oppure se esiste una regola generale che lo evita senza danneggiare
  2020, 2021 e 2024;
- solo dopo decidere se promuovere il combinato a nuova Baseline ufficiale.

### Audit peggioramento residuo 2023

File generati:

- `scripts/run_2023_residual_exit_audit.py`;
- `reports/residual_2023_exit_audit.md`;
- `reports/residual_2023_exit_audit.csv`;
- `reports/residual_2023_exit_filter_tests.csv`;
- `reports/residual_2023_exit_variant_metrics.csv`.

Obiettivo:

- capire se il peggioramento del 2023 puo' essere eliminato con una regola
  generale;
- evitare una regola costruita solo su una singola uscita storica;
- mantenere invariata la Baseline ufficiale.

Caso analizzato:

- segmento Baseline: `2023-03-13 -> 2023-05-08`;
- uscita Trail8 candidata: `2023-04-20` a EUR 1771,60;
- rendimento del trade al momento dell'uscita: +13,06%;
- rendimento segmento Baseline: +7,30%;
- rendimento segmento candidato: +6,82%;
- delta candidato - Baseline: -0,48%;
- drawdown subito fino all'uscita Trail8: -8,39%.

Confronto uscite Trail8 nel combinato:

| Uscita | Return trade | Max gain | RSI | Mom 7d | Vol rel | Delta segmento | Lettura |
|---|---:|---:|---:|---:|---:|---:|---|
| 2020-09-04 | +54,42% | +88,37% | 47,50 | -1,93% | +33,66% | +13,84% | utile |
| 2021-09-07 | +52,91% | +75,76% | 51,35 | -0,21% | +85,80% | +28,26% | utile |
| 2023-04-20 | +13,06% | +23,16% | 52,68 | -3,46% | +21,08% | -0,48% | costo residuo |
| 2024-03-15 | +55,53% | +68,70% | 60,75 | -4,03% | +39,74% | +16,98% | utile |

Filtri provati:

| Filtro | Esclude 2023 | Uscite utili escluse | Lettura |
|---|---|---:|---|
| `trade return >= 15%` | si | 0 | promettente ma modifica un solo evento |
| `max gain >= 35%` | si | 0 | equivalente nel campione |
| `RSI uscita >= 55` | si | 2 | scarta troppe uscite utili |
| `volume relativo >= 40%` | si | 2 | scarta troppe uscite utili |
| `giorni in trade >= 40` | si | 1 | scarta una uscita utile |

Impatto delle due varianti promettenti:

| Modello | Ann. | Max DD | Sharpe | PF | Operazioni | Uscite Trail8 |
|---|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | +30,26% | -49,73% | 0,828 | 4,215 | 28 | 0 |
| Combinato attuale | +42,74% | -45,09% | 1,079 | 5,999 | 28 | 4 |
| Combinato + `trade return >= 15%` | +42,81% | -45,09% | 1,079 | 6,282 | 27 | 3 |
| Combinato + `max gain >= 35%` | +42,81% | -45,09% | 1,079 | 6,282 | 27 | 3 |

Conclusione:

- il peggioramento 2023 e' piccolo e circoscritto: -0,48% sul segmento;
- il candidato combinato resta molto superiore alla Baseline anche accettando
  quel costo;
- `trade return >= 15%` e `max gain >= 35%` eliminano il 2023 senza perdere le
  uscite utili presenti nel campione;
- pero' entrambe le regole modificano un solo evento storico: rischio overfit
  alto;
- non ci sono prove sufficienti per trasformare subito questi filtri in
  regola ufficiale.

Decisione:

- non modificare la Baseline ufficiale;
- non modificare il candidato combinato principale per ora;
- accettare provvisoriamente il costo 2023 come costo fisiologico del modello;
- annotare `trade return >= 15%` come candidato secondario coerente con la
  logica "proteggere capitale acquisito";
- validare il candidato secondario solo con test walk-forward/out-of-sample e
  stress parametrico, non con ottimizzazione sul singolo evento 2023.

Prossimo passo:

- validazione walk-forward del candidato combinato attuale;
- confronto walk-forward anche con la variante secondaria `trade return >= 15%`;
- se la variante secondaria resta utile fuori dal segmento 2023, potra' essere
  rivalutata; altrimenti resta scartata come filtro troppo ottimizzato.

### Validazione cronologica / walk-forward del combinato

File generati:

- `scripts/run_combined_walkforward_validation.py`;
- `reports/combined_walkforward_validation.md`;
- `reports/combined_walkforward_full_metrics.csv`;
- `reports/combined_walkforward_windows.csv`;
- `reports/combined_walkforward_yearly.csv`;
- `reports/combined_walkforward_events.csv`.

Metodo:

- Baseline ufficiale invariata;
- candidato principale: `RSI <= 65` in ingresso + `Trail8 -5 / vol +20` in
  uscita;
- variante secondaria: candidato principale + `trade return >= 15%` per
  attivare l'uscita Trail8;
- confronto su finestre cronologiche successive:
  - `2019-2020`;
  - `2021-2022`;
  - `2023-2024`;
  - `2025-2026`.

Periodo completo:

| Modello | Ann. | Max DD | Sharpe | PF | Operazioni | Ingressi bloccati | Uscite Trail8 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | +30,26% | -49,73% | 0,828 | 4,215 | 28 | 0 | 0 |
| Combinato principale | +42,74% | -45,09% | 1,079 | 5,999 | 28 | 14 | 4 |
| Combinato + `trade return >= 15%` | +42,81% | -45,09% | 1,079 | 6,282 | 27 | 14 | 3 |

Finestre cronologiche:

| Finestra | Baseline Return | Combinato Return | Delta Return | Delta DD | Delta Sharpe |
|---|---:|---:|---:|---:|---:|
| 2019-2020 | +172,30% | +316,33% | +144,03% | +21,83% | +0,537 |
| 2021-2022 | +201,42% | +269,77% | +68,34% | 0,00% | +0,185 |
| 2023-2024 | -11,83% | +3,55% | +15,38% | +9,38% | +0,221 |
| 2025-2026 | +35,98% | +35,98% | 0,00% | 0,00% | 0,000 |

Lettura:

- il candidato principale batte la Baseline in 3 finestre su 4;
- nella quarta finestra, `2025-2026`, resta identico perche' non interviene;
- non esiste una finestra cronologica in cui il candidato principale peggiora
  materialmente la Baseline;
- il miglioramento piu' importante e' nel `2019-2020`;
- il miglioramento recente `2023-2024` e' positivo: trasforma una finestra
  negativa della Baseline in una finestra leggermente positiva;
- la variante `trade return >= 15%` migliora appena il periodo completo, ma il
  beneficio aggiuntivo dipende dal singolo caso 2023.

Decisione:

- il candidato principale supera la validazione cronologica;
- non promuovere la variante `trade return >= 15%`, perche' aggiunge
  complessita' e il suo beneficio incrementale e' troppo legato a un singolo
  evento;
- mantenere il candidato principale come modello da portare al gate
  decisionale finale;
- la Baseline ufficiale resta invariata fino a decisione esplicita.

Prossimo passo:

- gate decisionale finale: decidere se promuovere il candidato principale a
  nuova Baseline ufficiale;
- se promosso, implementare la modifica in `strategy/signals.py` con test
  dedicati;
- se non promosso, mantenere tutto come report sperimentale e continuare con
  altri filtri solo dopo nuova ipotesi chiara.

### Gate decisionale finale

File generato:

- `reports/final_promotion_gate.md`.

Decisione tecnica:

- il candidato combinato principale e' tecnicamente promuovibile a nuova
  Baseline ufficiale;
- la variante secondaria `trade return >= 15%` non viene promossa;
- la Baseline ufficiale resta invariata fino a decisione esplicita di
  implementazione.

Candidato promuovibile:

- ingresso: condizioni Baseline attuali + `RSI <= 65`;
- uscita: uscita ufficiale attuale + `Trail8 -5 / vol +20`.

Criteri superati:

| Criterio | Esito |
|---|---|
| rendimento annualizzato | superato: +42,74% vs +30,26% |
| max drawdown | superato: -45,09% vs -49,73% |
| Sharpe | superato: 1,079 vs 0,828 |
| profit factor | superato: 5,999 vs 4,215 |
| operazioni totali | superato: 28 vs 28 |
| stress costi/slippage | superato anche con 1,00% |
| validazione cronologica | superato: migliora 3 finestre su 4, invariato nella quarta |
| rischio overfit | controllato: variante piu' complessa non promossa |

Rischi residui:

- campione operativo limitato a 28 operazioni chiuse;
- vantaggio concentrato in pochi eventi importanti, anche se non in uno solo;
- piccola sottoperformance 2023 accettata come costo fisiologico;
- implementazione operativa del trailing richiede stato post-ingresso:
  massimo Close raggiunto durante la posizione.

Raccomandazione:

- promuovere il candidato principale;
- non promuovere `trade return >= 15%`;
- implementare solo dopo conferma esplicita, con test unitari dedicati e
  verifica del monitor live.

### Implementazione ufficiale nuova Baseline

File generato:

- `reports/official_baseline_implementation.md`.

Decisione implementata:

- il candidato combinato principale e' stato promosso a Baseline ufficiale;
- la variante `trade return >= 15%` non e' stata implementata;
- il diario resta nel root del progetto come parte integrante della
  reversibilita' delle decisioni.

Regole ufficiali ora in codice:

- nuovo ingresso solo se:
  - `Close > SMA200`;
  - `SMA50 > SMA200`;
  - `RSI >= 40`;
  - `RSI <= 65`;
  - `Close > Close_7d_ago`;
  - `Volume > VolumeAvg20`;
- vendita se:
  - `Close < SMA50` per 2 giorni consecutivi;
  - oppure trailing stop 8% dal massimo Close post-ingresso, confermato da
    momentum 7 giorni >= -5% e volume relativo >= +20%.

Nota tecnica importante:

- `RSI <= 65` filtra solo i nuovi ingressi;
- non viene usato per chiudere o indebolire una posizione gia' aperta;
- se una posizione e' gia' aperta e le condizioni ufficiali di acquisto
  storiche restano vere, il sistema mantiene la posizione e non valuta il
  trailing in quel giorno;
- questa distinzione replica il candidato validato e impedisce di ottenere per
  errore la variante piu' aggressiva da +51,41%.

File modificati:

- `strategy/signals.py`;
- `reports/generate.py`;
- `cloudflare-worker/src/worker.js`;
- `tests/test_signal_rules.py`;
- `tests/test_chart_data_json.py`;
- `tests/test_telegram_message.py`;
- `tests/test_telegram_webhook.py`;
- `PROJECT_STATUS.md`;
- `ETH_MODEL_RESEARCH_DIARY.md`.

Metriche di verifica dopo implementazione:

| Metrica | Valore |
|---|---:|
| Annualizzato | +42,74% |
| Max drawdown | -45,09% |
| Sharpe | 1,079 |
| Profit factor | 5,999 |
| Operazioni | 28 |
| Uscite Trail8 confermate | 4 |

Uscite Trail8 confermate:

- `2020-09-04`;
- `2021-09-07`;
- `2023-04-20`;
- `2024-03-15`.

Test eseguiti:

- `python -m py_compile strategy\signals.py reports\generate.py telegram_webhook.py`;
- `node --check cloudflare-worker\src\worker.js`;
- `python -m unittest discover -s tests -v`.

Risultato:

- 60 test OK;
- warning Yahoo noto e non bloccante durante i test.

Prossimo passo:

- commit e push;
- dopo il push, monitorare il primo aggiornamento operativo di dashboard,
  `status.json`, `live-status.json` e Telegram.

### Deploy Worker Telegram dopo nuova Baseline

Motivo:

- il comando Telegram `/conditions` risponde tramite Cloudflare Worker;
- dopo l'implementazione locale della nuova Baseline il Worker deployato
  mostrava ancora il testo vecchio:
  - 5 condizioni di acquisto;
  - 1 sola condizione di vendita;
- quindi era necessario deployare il Worker aggiornato.

Azioni eseguite:

- allineati localmente i file dashboard:
  - `docs/status.json`;
  - `docs/chart-data.json`;
  - `docs/backtest.json`;
  - `docs/live-status.json`;
- deploy Cloudflare Worker eseguito con:
  - `npx wrangler deploy`.

Esito deploy:

- Worker: `eth-prudential-signal`;
- URL: `https://eth-prudential-signal.giuse2003.workers.dev`;
- Version ID: `e61c4c42-9738-4c82-bacc-b5e50c8aafbb`.

Risultato atteso su Telegram `/conditions`:

- ACQUISTA:
  1. prezzo sopra SMA200;
  2. SMA50 sopra SMA200;
  3. RSI uguale o maggiore di 40;
  4. RSI uguale o minore di 65;
  5. prezzo sopra quello di 7 giorni prima;
  6. volume sopra media 20 giorni.
- VENDI:
  1. prezzo sotto SMA50;
  2. trailing stop 8% confermato da momentum e volume.

Nota:

- il deploy Worker aggiorna subito `/conditions`;
- il push GitHub resta comunque necessario per rendere persistenti repository,
  docs e workflow.

### Chiarimento testo `/conditions` su momentum e volume

Motivo:

- il messaggio Telegram `/conditions` indicava genericamente
  "trailing stop 8% confermato da momentum e volume";
- serviva esplicitare le soglie operative reali della nuova uscita.

Modifica eseguita:

- aggiornato `cloudflare-worker/src/worker.js`;
- aggiornato `reports/generate.py` per rendere coerenti anche le condizioni
  esportate nei JSON del monitor.

Nuovo testo vendita Trail8:

- trailing stop 8% dal massimo post-ingresso, confermato da:
  - momentum 7 giorni uguale o maggiore di -5%;
  - volume almeno 20% sopra la media 20 giorni.

Deploy:

- comando: `npx wrangler deploy`;
- Worker: `eth-prudential-signal`;
- Version ID Cloudflare: `8557d497-04f3-4580-90c5-00f191331514`.

Verifica/allineamento successivo:

- aggiornato anche `docs/index.html`, perche' la sezione statica "Come nasce
  un segnale" mostrava ancora 5 condizioni di acquisto e 1 di vendita;
- rigenerato `docs/live-status.json` con 6 condizioni BUY e 2 condizioni SELL;
- aggiornata l'etichetta LIVE/Fallback della condizione Trail8 con le soglie
  esplicite:
  - momentum 7g >= -5%;
  - volume >= media20 +20%.

Nuovo deploy Worker:

- comando: `npx wrangler deploy`;
- Worker: `eth-prudential-signal`;
- Version ID Cloudflare: `4aecc8cd-e00e-4120-ab1f-cb6180cc4d87`.

### Allineamento visuale dashboard RSI 65

Motivo:

- la logica ufficiale e i testi erano gia' aggiornati con `RSI <= 65` sugli
  ingressi;
- il grafico della dashboard mostrava ancora solo la linea `RSI 40`, creando
  ambiguita' visiva sul filtro di ingresso superiore.

Modifica eseguita:

- aggiunta in legenda la voce `Soglia RSI 65`;
- aggiunta nel pannello RSI una linea dedicata a quota 65;
- mantenuta la linea `RSI 40`, che resta la soglia minima del filtro RSI;
- uniformata la soglia `RSI 65` allo stesso colore e stile continuo della
  soglia `RSI 40`, per rappresentare graficamente il range RSI operativo;
- aggiornati i parametri cache degli asset dashboard:
  - `style.css?v=9`;
  - `app.js?v=10`.

Decisione:

- nessuna modifica ai segnali;
- intervento solo di allineamento grafico/documentale della dashboard.

### Audit documentazione modello

Motivo:

- verificare che la costruzione del modello, le decisioni prese, le regole
  promosse e le varianti scartate siano memorizzate nei file `.md` del
  progetto;
- evitare che file di sintesi mostrino ancora la vecchia Baseline dopo la
  promozione del modello.

File riallineati:

- `README.md`;
- `PROJECT_OVERVIEW.md`;
- `PROJECT_STATUS.md`;
- `MODEL_IMPROVEMENT_ROADMAP.md`;
- `ETH_PROJECT_ROADMAP.md`;
- `DECISION_LOG.md`.

File aggiunto:

- `MODEL_DOCUMENTATION_INDEX.md`, indice dei documenti rilevanti per stato
  ufficiale, diario, decisioni, report di validazione e reversibilita'.

Esito:

- le regole ufficiali correnti sono documentate nei file di sintesi;
- la promozione del candidato combinato e' registrata nel decision log;
- le varianti non promosse restano tracciate come storiche/sperimentali;
- nessuna modifica ai segnali o al codice operativo del modello.

### Riordino documentazione in cartella dedicata

Motivo:

- rendere piu' ordinata la root del progetto;
- separare la documentazione progettuale stabile dalla dashboard pubblica in
  `docs/` e dai report tecnici rigenerabili in `reports/`;
- mantenere piu' chiaro il percorso cronologico delle decisioni.

Modifica eseguita:

- creata cartella `DOCUMENTATION/`;
- spostati nella nuova cartella i documenti `.md` progettuali:
  - diario modello;
  - roadmap;
  - decision log;
  - overview;
  - status;
  - guide Cloudflare, Supabase, Telegram e Render;
  - log di verifica regole;
- lasciato `README.md` nella root come pagina iniziale standard del
  repository;
- lasciati i report in `../reports/`, perche' sono output tecnici generati dagli
  script.

Decisione:

- da ora la documentazione progettuale da leggere deve stare in
  `DOCUMENTATION/`;
- i nuovi report di test possono restare in `../reports/` se sono generati da
  script o collegati direttamente alle analisi quantitative.

### Correzione README su range RSI acquisto

Motivo:

- la formulazione `RSI(14) <= 65 for new entries` era corretta tecnicamente,
  ma meno chiara nella sezione pubblica `BUY / ACQUISTA`;
- la frase aggiuntiva che spiegava che il filtro non forzava uscite era
  fuorviante in una sezione dedicata alle condizioni di acquisto.

Modifica eseguita:

- rimossa dal README la frase esplicativa sulle uscite;
- sostituite le due condizioni RSI separate con una sola formula:
  - `40 <= RSI(14) <= 65`.

Decisione:

- nessuna modifica al modello;
- nessuna modifica ai segnali;
- solo correzione della formulazione pubblica della condizione di acquisto.

### Test sperimentale Trail8 prima delle condizioni BUY

Motivo:

- e' emerso che, nella Baseline attuale, il trailing stop viene valutato solo
  dopo le condizioni di acquisto;
- in una fase forte/parabolica il prezzo puo' rompere il Trail8 mentre le
  condizioni BUY restano ancora vere;
- serve verificare se conviene uscire comunque quando il Trail8 e' confermato.

Regola testata:

- Baseline invariata per gli ingressi;
- `VENDI` ufficiale sotto SMA50 resta invariato;
- quando la posizione e' gia' aperta, il Trail8 confermato viene valutato
  prima delle condizioni BUY;
- se Trail8 e' colpito e confermato da momentum 7g >= -5% e volume relativo
  >= +20%, il sistema esce anche se le condizioni BUY sono ancora vere.

Risultati USD sul periodo completo:

| Modello | Ann. | Max DD | Sharpe | PF | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline ufficiale | 43,61% | -44,93% | 1,084 | 5,889 | 28 |
| Trail8 priority | 46,35% | -42,79% | 1,207 | 4,708 | 34 |

Stress costi:

- con costo 0,25% per cambio esposizione:
  - Baseline ufficiale: ann. 41,30%, max DD -45,07%, Sharpe 1,045;
  - Trail8 priority: ann. 43,49%, max DD -44,78%, Sharpe 1,154;
- con stress 1,00%:
  - Baseline ufficiale: ann. 34,55%, Sharpe 0,925;
  - Trail8 priority: ann. 35,21%, Sharpe 0,992.

Eventi:

- uscite Trail8 priority totali: 12;
- uscite Trail8 priority mentre le condizioni BUY erano ancora vere: 10;
- caso 2025:
  - entrata 2025-07-07 a 2543,01 USD;
  - uscita Trail8 priority 2025-08-18 a 4312,50 USD;
  - rendimento trade +69,58%;
  - nella Baseline ufficiale lo stesso trade restava aperto fino al VENDI del
    2025-09-23.

File generati:

- `scripts/run_trail_priority_validation.py`;
- `reports/trail_priority_validation.md`;
- `reports/trail_priority_events.csv`;
- `reports/trail_priority_trades.csv`.

Decisione provvisoria:

- la variante migliora rendimento annualizzato, max drawdown e Sharpe;
- aumenta pero' le operazioni da 28 a 34 e riduce il profit factor;
- non viene promossa automaticamente;
- prossimo controllo consigliato: analisi evento-per-evento delle 12 uscite
  Trail8 priority, distinguendo uscite utili da falsi stop.

### Audit cronologico operazioni Trail8 priority

Motivo:

- verificare tutta la cronologia acquisti/vendite della variante Trail8
  priority;
- confrontare ogni operazione contro il mantenimento Baseline sul segmento
  corrispondente;
- capire se le uscite Trail8 generano rientri vicini e se quei rientri sono
  vantaggiosi o svantaggiosi.

Risultati:

- operazioni Trail8 priority chiuse: 34;
- operazioni Baseline chiuse: 28;
- confronto trade singolo vs mantenimento Baseline:
  - 5 operazioni migliorano;
  - 24 sono uguali;
  - 5 peggiorano;
- uscite Trail8 priority: 12;
- rientri dopo uscita Trail8:
  - 6 rientri piu' bassi, quindi vantaggiosi;
  - 6 rientri piu' alti, quindi svantaggiosi.

Lettura provvisoria:

- la variante migliora le metriche complessive, ma non perche' ogni uscita sia
  migliore;
- alcune uscite Trail8 anticipano bene una caduta successiva;
- altre tagliano troppo presto trend ancora validi e costringono a rientrare
  piu' in alto;
- serve una seconda selezione qualitativa sulle 12 uscite Trail8 priority per
  separare protezione vera da falso stop.

File generati:

- `scripts/run_trail_priority_trade_audit.py`;
- `reports/trail_priority_trade_audit.md`;
- `reports/trail_priority_trade_audit.csv`;
- `reports/trail_priority_reentry_audit.csv`.

Decisione:

- nessuna modifica alla Baseline ufficiale;
- il tema resta aperto come miglioramento interessante da analizzare in modo
  evento-per-evento.

### Classificazione uscita Trail8 priority 2025

Evento analizzato:

- entrata iniziale: 2025-07-07 a 2543,01 USD;
- uscita Trail8 priority: 2025-08-18 a 4312,50 USD;
- rientro successivo: 2025-08-25 a 4372,99 USD;
- uscita finale: 2025-09-23 a 4165,50 USD.

Risultato:

- primo trade Trail8: +69,58%;
- secondo trade dopo rientro: -4,74%;
- sequenza composta Trail8 priority: +61,54%;
- Baseline restando dentro fino al 2025-09-23: +63,80%;
- delta Trail8 priority vs Baseline: -2,27 punti percentuali.

Decisione qualitativa:

- l'uscita Trail8 priority del 2025 viene classificata come uscita inutile /
  peggiorativa nel complesso;
- il rientro e' avvenuto piu' in alto e ha assorbito il beneficio apparente
  dell'uscita anticipata;
- questo evento entra nel gruppo dei falsi stop da studiare prima di qualsiasi
  promozione della variante.

### Audit per segmento Baseline delle altre uscite Trail8 priority

Motivo:

- dopo aver classificato il caso 2025 come sfavorevole, serviva valutare le
  altre uscite Trail8 priority non come trade isolati, ma come sequenza
  composta dentro il segmento Baseline corrispondente.

Metodo:

- ogni segmento Baseline e' una operazione unica della Baseline ufficiale;
- dentro quel segmento la variante Trail8 priority puo' generare piu'
  operazioni;
- il confronto corretto e' tra rendimento Baseline del segmento e rendimento
  composto della sequenza Trail8 priority.

Risultati:

- segmenti Baseline con almeno una uscita Trail8 priority: 10;
- segmenti che migliorano: 3;
- segmenti uguali: 2;
- segmenti che peggiorano: 5.

Escludendo il caso 2025 gia' accantonato:

- segmenti rimanenti: 9;
- migliorano: 3;
- uguali: 2;
- peggiorano: 4.

Segmenti migliori:

- 2021-03-31 -> 2021-05-22: +65,89% contro +19,67%;
- 2021-10-01 -> 2021-11-27: +25,78% contro +23,87%;
- 2021-11-30 -> 2021-12-04: -8,87% contro -11,05%.

Segmenti peggiori principali:

- 2020-10-21 -> 2021-02-26: +225,88% contro +268,71%;
- 2019-04-23 -> 2019-07-12: +52,36% contro +61,14%;
- 2020-07-21 -> 2020-09-04: +57,41% contro +58,45%;
- 2023-03-13 -> 2023-04-20: +15,24% contro +15,64%.

Decisione provvisoria:

- la variante Trail8 priority migliora le metriche aggregate, ma a livello
  evento-per-evento non e' ancora abbastanza selettiva;
- le uscite utili sono concentrate in pochi segmenti;
- molte uscite sono uguali o leggermente peggiorative, mentre il grande falso
  stop 2020-2021 pesa molto;
- prima di promuovere la regola serve trovare una caratteristica comune delle
  uscite utili rispetto a quelle peggiorative.

File generati:

- `scripts/run_trail_priority_segment_audit.py`;
- `reports/trail_priority_segment_audit.md`;
- `reports/trail_priority_segment_audit.csv`.

### Test barriere di rientro dopo Trail8 priority

Motivo:

- dopo una uscita Trail8 priority, il sistema puo' rientrare subito se le
  condizioni BUY restano o tornano verdi;
- alcuni rientri sono svantaggiosi perche' avvengono piu' in alto;
- serviva testare se una barriera temporale o una conferma di reset delle
  condizioni BUY migliora la qualita' dei rientri.

Regole testate:

- `cooldown Xd`: dopo una uscita Trail8 ignora nuovi ACQUISTA per X giorni;
- `reset_green Xd`: dopo una uscita Trail8 richiede almeno una condizione BUY
  rossa, poi X giorni consecutivi con BUY tutte verdi.

Griglia:

- X = 0, 3, 7, 10, 14, 21, 30 giorni.

Risultati principali USD:

| Modello | Ann. | Max DD | Sharpe | PF | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline ufficiale | 43,61% | -44,93% | 1,084 | 5,889 | 28 |
| Trail8 priority | 46,35% | -42,79% | 1,207 | 4,708 | 34 |
| cooldown 14d | 43,43% | -42,79% | 1,200 | 4,917 | 31 |
| cooldown 10d | 43,61% | -42,79% | 1,182 | 4,554 | 33 |
| cooldown 3d / 7d | 43,72% | -42,79% | 1,179 | 4,571 | 33 |
| reset_green 3d | 35,49% | -40,35% | 1,182 | 5,533 | 23 |

Lettura:

- Trail8 priority puro resta migliore per rendimento e Sharpe assoluto;
- cooldown 14d e' il compromesso piu' interessante: riduce operazioni da 34 a
  31, mantiene drawdown -42,79% e Sharpe 1,200, ma perde rendimento rispetto
  al Trail8 puro;
- cooldown 3d e 7d producono lo stesso risultato nel campione;
- reset_green oltre 3 giorni diventa troppo restrittivo e blocca quasi tutti i
  rientri;
- reset_green 3d riduce molto il drawdown e aumenta il profit factor, ma taglia
  troppo rendimento.

Decisione provvisoria:

- nessuna regola di rientro viene promossa;
- il cooldown fisso, soprattutto 10-14 giorni, merita analisi evento-per-evento;
- la regola reset_green va trattata con cautela perche' sembra troppo
  selettiva.

File generati:

- `scripts/run_trail_reentry_rules.py`;
- `reports/trail_reentry_rules.md`;
- `reports/trail_reentry_rules_metrics.csv`;
- `reports/trail_reentry_rules_events.csv`.

### Test rientro solo dopo VENDI ufficiale SMA50

Regola testata:

- se il sistema esce con Trail8 priority, ignora ogni nuovo `ACQUISTA`;
- il blocco resta attivo finche' non arriva il `VENDI` ufficiale:
  - prezzo sotto SMA50;
- dopo quel reset il sistema puo' valutare nuovi ingressi.

Motivo:

- evitare rientri troppo rapidi dopo Trail8;
- in particolare evitare casi come il 2025, dove il sistema usciva con Trail8
  e poi rientrava piu' in alto pochi giorni dopo.

Risultato USD:

| Modello | Ann. | Max DD | Sharpe | PF | Operazioni | Entry bloccati |
|---|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 43,61% | -44,93% | 1,084 | 5,889 | 28 | 0 |
| Trail8 priority | 46,35% | -42,79% | 1,207 | 4,708 | 34 | 0 |
| Wait official sell | 28,92% | -42,79% | 0,999 | 4,097 | 27 | 28 |

Lettura:

- la regola evita rientri rapidi e blocca 28 potenziali ingressi;
- elimina anche rientri sfavorevoli, ma blocca troppo spesso rientri utili;
- resta fuori troppo a lungo in trend forti, in particolare nel 2020-2021;
- rendimento annualizzato e Sharpe scendono sotto la Baseline ufficiale.

Decisione:

- regola non promossa;
- utile come riferimento negativo;
- per ora restano piu' interessanti cooldown brevi/medi, soprattutto 10-14
  giorni, da analizzare evento-per-evento.

### Test uscita SMA50 a 1 giorno

Motivo:

- verificare se conviene anticipare il `VENDI` ufficiale da prezzo sotto SMA50
  per 2 giorni consecutivi a prezzo sotto SMA50 gia' dopo 1 giorno;
- ingressi e Trail8 restano invariati.

Risultati USD:

| Modello | Entrate | Uscite | Uscite SMA50 | Uscite Trail8 | Totale | Ann. | Max DD | Sharpe | PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SMA50 2 giorni + Trail8 | 28 | 28 | 24 | 4 | 2173,16% | 43,61% | -44,93% | 1,084 | 5,889 |
| SMA50 1 giorno + Trail8 | 29 | 29 | 25 | 4 | 2843,36% | 47,98% | -40,97% | 1,179 | 7,117 |

Differenza 1 giorno vs 2 giorni:

- entrate: +1;
- uscite: +1;
- uscite SMA50 effettive: +1;
- uscite Trail8 effettive: nessuna differenza;
- rendimento annualizzato: +4,36 punti percentuali;
- max drawdown: migliora di 3,96 punti percentuali;
- Sharpe: +0,095;
- profit factor: +1,228.

Decisione provvisoria:

- la regola SMA50 a 1 giorno e' molto interessante sulle metriche aggregate;
- non viene promossa automaticamente;
- prossimo controllo necessario: audit trade-by-trade per capire quale
  operazione aggiuntiva crea il miglioramento e se introduce falsi stop.

File generati:

- `scripts/run_sma50_exit_timing_test.py`;
- `reports/sma50_exit_timing_test.md`;
- `reports/sma50_exit_timing_trades.csv`.

### Audit trade-by-trade uscita SMA50 a 1 giorno

Motivo:

- completare il test precedente con una comparazione puntuale operazione per
  operazione;
- verificare se il vantaggio della variante `Close < SMA50` a 1 giorno e'
  robusto o concentrato in pochi casi;
- includere anche i casi in cui la variante non apre una micro-operazione
  presente nella Baseline.

Risultato:

- segmenti Baseline confrontati: 28;
- segmenti modificati dalla variante a 1 giorno: 24;
- segmenti migliorati: 16;
- segmenti peggiorati: 8;
- segmenti invariati: 4.

Lettura:

- il miglioramento non dipende da una sola operazione isolata;
- la variante anticipa molte uscite SMA50 e riduce diverse perdite, soprattutto
  nel 2024 e nel 2025;
- ci sono comunque falsi anticipi: alcuni segmenti peggiorano perche' l'uscita
  a 1 giorno chiude troppo presto o genera una doppia operazione meno
  efficiente;
- le uscite Trail8 restano invariate: la modifica riguarda solo la regola
  SMA50.

Esempi principali:

- 2025-10-02 -> 2025-10-10 Baseline: -14,37%; variante 1 giorno: -2,65%;
  delta +11,72 punti percentuali;
- 2021-10-01 -> 2021-11-27 Baseline: +23,87%; variante 1 giorno: +12,32%;
  delta -11,54 punti percentuali;
- 2024-04-08 -> 2024-04-12 Baseline: -12,24%; variante 1 giorno: -5,14%;
  delta +7,10 punti percentuali;
- 2020-06-02 -> 2020-07-17 Baseline: -1,87%; variante 1 giorno: -9,07%;
  delta -7,20 punti percentuali.

Decisione provvisoria:

- la regola `Close < SMA50` a 1 giorno resta un candidato forte per migliorare
  il segnale di uscita;
- non viene ancora promossa a regola ufficiale;
- prossimo passo: validazione anno per anno e controllo dei casi peggiori, per
  capire se serve una conferma minima o un filtro anti-falso segnale.

File generati:

- `scripts/run_sma50_exit_timing_audit.py`;
- `reports/sma50_exit_timing_audit.md`;
- `reports/sma50_exit_timing_audit.csv`;
- `reports/sma50_exit_timing_changed_segments.csv`.

### Validazione annuale uscita SMA50 a 1 giorno

Motivo:

- verificare se il vantaggio della variante SMA50 a 1 giorno e' distribuito
  nel tempo;
- distinguere miglioramento recente da robustezza storica;
- mantenere invariati ingressi e Trail8.

Risultati annuali USD:

| Anno | Ret 2g | Ret 1g | Delta ret | DD 2g | DD 1g | Delta DD | Entry 2g/1g | Exit 2g/1g |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 61,14% | 56,73% | -4,42% | -20,21% | -20,21% | 0,00% | 1/1 | 1/1 |
| 2020 | 178,27% | 156,01% | -22,25% | -24,43% | -24,97% | -0,54% | 4/5 | 3/4 |
| 2021 | 268,68% | 277,51% | +8,82% | -44,93% | -40,97% | +3,96% | 5/6 | 6/7 |
| 2023 | 1,51% | 0,74% | -0,78% | -23,63% | -24,32% | -0,69% | 7/8 | 6/7 |
| 2024 | -1,75% | 20,40% | +22,15% | -40,39% | -28,50% | +11,88% | 7/6 | 8/7 |
| 2025 | 35,07% | 56,97% | +21,90% | -26,17% | -15,31% | +10,86% | 4/3 | 4/3 |

Sintesi:

- anni con rendimento migliore: 3;
- anni con rendimento peggiore: 3;
- anni con drawdown annuale meno profondo: 3;
- anni con drawdown annuale piu' profondo: 2;
- 2017, 2018, 2022 e 2026 non hanno operazioni utili nel confronto.

Lettura:

- il vantaggio aggregato e' forte, ma arriva soprattutto da 2024 e 2025;
- il 2020 peggiora in modo significativo per rendimento, quindi la variante
  non e' uniformemente superiore;
- il 2021 migliora rendimento e drawdown;
- il 2023 peggiora poco, ma aumenta il numero di micro-operazioni;
- la variante riduce molto il drawdown negli anni recenti, coerentemente con
  l'obiettivo di protezione del capitale acquisito.

Decisione provvisoria:

- la SMA50 a 1 giorno resta un candidato serio per il segnale di uscita;
- non viene ancora promossa a Baseline;
- prossimo passo: stress con costi/slippage e analisi dei peggiori falsi stop,
  soprattutto 2020 e 2021-10.

File generati:

- `scripts/run_sma50_exit_timing_yearly_validation.py`;
- `reports/sma50_exit_timing_yearly_validation.md`;
- `reports/sma50_exit_timing_yearly_validation.csv`.

### Stress costi uscita SMA50 a 1 giorno

Motivo:

- verificare se il vantaggio della variante resiste a costi/slippage;
- controllare il rischio tipico delle regole piu' reattive: piu' turnover e
  piu' micro-operazioni;
- mantenere invariati ingressi e Trail8.

Risultati USD:

| Costo | Modello | Ann. | Max DD | Sharpe | PF | Operazioni | Turnover |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0,00% | SMA50 2 giorni + Trail8 | 43,61% | -44,93% | 1,084 | 5,889 | 28 | 56,0 |
| 0,00% | SMA50 1 giorno + Trail8 | 47,98% | -40,97% | 1,179 | 7,117 | 29 | 58,0 |
| 0,10% | SMA50 2 giorni + Trail8 | 42,69% | -44,99% | 1,068 | 5,786 | 28 | 56,0 |
| 0,10% | SMA50 1 giorno + Trail8 | 46,99% | -41,03% | 1,162 | 6,958 | 29 | 58,0 |
| 0,25% | SMA50 2 giorni + Trail8 | 41,30% | -45,07% | 1,045 | 5,637 | 28 | 56,0 |
| 0,25% | SMA50 1 giorno + Trail8 | 45,51% | -41,12% | 1,137 | 6,732 | 29 | 58,0 |
| 0,50% | SMA50 2 giorni + Trail8 | 39,02% | -46,78% | 1,005 | 5,404 | 28 | 56,0 |
| 0,50% | SMA50 1 giorno + Trail8 | 43,08% | -43,06% | 1,094 | 6,382 | 29 | 58,0 |

Delta variante 1 giorno vs Baseline 2 giorni:

- costo 0,00%: ann. +4,36 punti, DD +3,96 punti, Sharpe +0,095;
- costo 0,10%: ann. +4,30 punti, DD +3,95 punti, Sharpe +0,094;
- costo 0,25%: ann. +4,21 punti, DD +3,95 punti, Sharpe +0,092;
- costo 0,50%: ann. +4,06 punti, DD +3,71 punti, Sharpe +0,090.

Lettura:

- il vantaggio non scompare con i costi;
- il turnover aumenta poco: 58 contro 56;
- il profit factor resta migliore in tutti gli scenari;
- lo stress rafforza il candidato, ma non cancella il problema dei falsi stop
  rilevati nel 2020 e nel segmento 2021-10.

Decisione provvisoria:

- la variante SMA50 a 1 giorno supera il controllo costi/slippage;
- resta candidata forte, non ancora regola ufficiale;
- prossimo passo consigliato: analizzare i peggiori falsi stop e valutare se
  una conferma selettiva puo' preservare il vantaggio del 2024-2025 senza
  peggiorare il 2020.

File generati:

- `scripts/run_sma50_exit_timing_cost_stress.py`;
- `reports/sma50_exit_timing_cost_stress.md`;
- `reports/sma50_exit_timing_cost_stress.csv`.

### Test filtro rottura SMA50 almeno -1%

Motivo:

- provare a ridurre i falsi stop della variante SMA50 a 1 giorno;
- vendere dopo 1 solo giorno sotto SMA50 soltanto se la rottura e'
  significativa;
- mantenere la Baseline a 2 giorni quando la chiusura e' sotto SMA50 ma meno
  dell'1%.

Regola testata:

- `VENDI` se `Close <= SMA50 * 0,99`;
- oppure resta valido il `VENDI` Baseline se `Close < SMA50` per 2 giorni;
- ingressi e Trail8 invariati.

Risultati USD:

| Modello | Totale | Ann. | Max DD | Sharpe | PF | Operazioni | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|
| SMA50 2 giorni + Trail8 | 2173,16% | 43,61% | -44,93% | 1,084 | 5,889 | 28 | 56,0 |
| SMA50 1 giorno pura + Trail8 | 2843,36% | 47,98% | -40,97% | 1,179 | 7,117 | 29 | 58,0 |
| SMA50 1 giorno solo se -1% + Trail8 | 2433,38% | 45,43% | -40,97% | 1,129 | 6,204 | 27 | 54,0 |

Lettura:

- il filtro -1% batte la Baseline ufficiale;
- riduce operazioni e turnover rispetto alla variante pura a 1 giorno;
- non batte la variante pura a 1 giorno su rendimento, Sharpe o profit factor;
- conserva lo stesso max drawdown della variante pura.

Decisione provvisoria:

- variante utile come versione piu' prudente;
- non promossa rispetto alla SMA50 a 1 giorno pura;
- per ora il filtro -1% non sembra il miglior modo per isolare i falsi stop.

File generati:

- `scripts/run_sma50_exit_1pct_filter_test.py`;
- `reports/sma50_exit_1pct_filter_test.md`;
- `reports/sma50_exit_1pct_filter_trades.csv`.

### Griglia conferme aggiuntive su SMA50 a 1 giorno

Motivo:

- non lasciare la regola di uscita soltanto come `Close < SMA50` a 1 giorno;
- provare conferme aggiuntive per ridurre i falsi stop;
- testare tutto lo storico disponibile, dal 2017-11-11 al 2026-06-29;
- mantenere invariati ingressi e Trail8.

Conferme testate:

- distanza sotto SMA50: da -0,25% a -5,00%;
- momentum 7 giorni: da -1,00% a -10,00%;
- volume relativo rispetto alla media 20 giorni: da -10% a +50%;
- RSI: soglie 40, 42, 45, 48, 50, 52;
- candela rossa;
- close sotto il close del giorno precedente;
- slope SMA50 negativa su 5 giorni;
- combinazioni OR/AND fra distanza, momentum, volume e RSI.

Risultati principali USD:

| Modello | Ann. | Totale | Max DD | Sharpe | PF | Operazioni | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|
| SMA50 2 giorni + Trail8 | 43,58% | 2173,16% | -44,93% | 1,084 | 5,889 | 28 | 56,0 |
| SMA50 1 giorno pura | 47,94% | 2843,36% | -40,97% | 1,179 | 7,117 | 29 | 58,0 |
| 1g + volume relativo >= -10% | 48,02% | 2857,31% | -40,97% | 1,178 | 7,244 | 28 | 56,0 |
| 1g + RSI <= 52 | 47,56% | 2778,12% | -40,97% | 1,172 | 6,948 | 29 | 58,0 |
| 1g + distanza <= -0,25% | 46,78% | 2649,51% | -40,97% | 1,157 | 6,667 | 28 | 56,0 |
| 1g + distanza <= -0,50% | 46,78% | 2649,51% | -40,97% | 1,157 | 6,667 | 28 | 56,0 |

Sintesi:

- varianti effettive testate oltre ai due riferimenti: 91;
- varianti che battono la Baseline su annualizzato, drawdown e Sharpe: 81;
- varianti che battono o pareggiano la SMA50 1 giorno pura su annualizzato,
  drawdown e Sharpe insieme: 0.

Lettura:

- la SMA50 1 giorno pura resta il riferimento piu' forte tra le regole semplici
  testate;
- `volume relativo >= -10%` migliora leggermente rendimento annualizzato e
  profit factor, riducendo anche turnover, ma non migliora lo Sharpe rispetto
  alla 1 giorno pura;
- le conferme piu' severe riducono operazioni e turnover, ma tagliano anche
  uscite utili;
- la griglia conferma che la regola a 1 giorno pura e' difficile da battere
  senza introdurre complessita' non giustificata.

Decisione provvisoria:

- nessuna conferma aggiuntiva viene promossa sopra SMA50 1 giorno pura;
- `volume relativo >= -10%` resta candidata secondaria da osservare, ma il
  vantaggio e' troppo sottile per giustificare una regola nuova;
- il prossimo Promotion Gate dovrebbe confrontare soprattutto:
  - Baseline SMA50 2 giorni + Trail8;
  - SMA50 1 giorno pura + Trail8;
  - eventuale variante secondaria volume relativo >= -10%.

File generati:

- `scripts/run_sma50_exit_confirmation_grid.py`;
- `reports/sma50_exit_confirmation_grid.md`;
- `reports/sma50_exit_confirmation_grid.csv`;
- `reports/sma50_exit_confirmation_grid_yearly_top.csv`.

### Promotion Gate SMA50 a 1 giorno

Motivo:

- concentrare i test sul miglior candidato emerso: `Close < SMA50` a 1 giorno
  + Trail8;
- confrontarlo con la Baseline `Close < SMA50` per 2 giorni + Trail8;
- verificare metriche aggregate, costi, finestre rolling, anni attivi e audit
  segmenti;
- non modificare ancora i segnali ufficiali.

Periodo:

- dal 2017-11-11 al 2026-06-29;
- dati e indicatori ETH-USD;
- ingressi invariati.

Gate:

| Check | Esito | Nota |
|---|---:|---|
| Rendimento annualizzato completo migliora | PASS | 47,94% vs 43,58% |
| Max drawdown completo migliora | PASS | -40,97% vs -44,93% |
| Sharpe completo migliora | PASS | 1,179 vs 1,084 |
| Profit factor completo migliora | PASS | 7,117 vs 5,889 |
| Stress costi migliora in tutti gli scenari | PASS | 4/4 ann., 4/4 DD, 4/4 Sharpe |
| Rendimento annuale migliora nella maggioranza degli anni attivi | FAIL | 3 anni meglio, 3 anni peggio |
| Drawdown annuale migliora nella maggioranza degli anni attivi | PASS | 3 meglio, 2 peggio |
| Finestre rolling migliorano nella maggioranza | PASS | 4 meglio, 2 peggio |
| Segmenti modificati migliorano nella maggioranza | PASS | 16 migliorano, 8 peggiorano |

Risultato:

- PASS: 8;
- FAIL: 1.

Metriche complete USD:

| Modello | Totale | Ann. | Max DD | Sharpe | PF | Operazioni | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline SMA50 2g + Trail8 | 2173,16% | 43,58% | -44,93% | 1,084 | 5,889 | 28 | 56,0 |
| Candidate SMA50 1g + Trail8 | 2843,36% | 47,94% | -40,97% | 1,179 | 7,117 | 29 | 58,0 |

Finestre rolling:

| Finestra | Delta ret | Delta DD | Delta Sharpe |
|---|---:|---:|---:|
| 2019-2020 | -47,17% | -3,02% | -0,111 |
| 2020-2021 | -58,85% | +3,96% | -0,005 |
| 2021-2022 | +8,82% | +3,96% | +0,049 |
| 2023-2024 | +22,22% | +11,88% | +0,343 |
| 2024-2025 | +56,28% | +12,54% | +0,589 |
| 2025-2026 | +21,90% | +10,86% | +0,400 |

Lettura:

- il candidato supera quasi tutti i criteri tecnici;
- il vantaggio e' molto forte dal 2023 in poi, soprattutto nel 2024-2025;
- il punto debole resta il 2019-2020, dove la reattivita' a 1 giorno peggiora
  il rendimento;
- la scelta finale non e' piu' solo statistica: bisogna decidere se il modello
  deve privilegiare la protezione del capitale acquisito e la riduzione del
  drawdown, accettando qualche falso stop storico.

Decisione provvisoria:

- SMA50 1 giorno + Trail8 e' il candidato principale per sostituire SMA50 2
  giorni + Trail8;
- non ancora promosso automaticamente;
- prossimo passo consigliato: discutere il FAIL annuale 3/3 e decidere se
  considerarlo accettabile alla luce dei miglioramenti su drawdown, Sharpe,
  costi e periodo recente.

File generati:

- `scripts/run_sma50_one_day_promotion_gate.py`;
- `reports/sma50_one_day_promotion_gate.md`;
- `reports/sma50_one_day_promotion_gate_checks.csv`;
- `reports/sma50_one_day_promotion_gate_windows.csv`.

### Decisione finale sul compromesso SMA50 a 1 giorno

Decisione:

- accettare il compromesso della SMA50 a 1 giorno;
- registrare la decisione nel `DECISION_LOG.md`;
- non introdurre ulteriori filtri sopra la regola pura;
- implementare la modifica operativa in modo atomico su modello, report,
  dashboard e Telegram.

Motivo specifico:

- la regola a 1 giorno protegge prima il capitale acquisito;
- migliora rendimento annualizzato, drawdown massimo, Sharpe e profit factor;
- supera lo stress costi;
- migliora la maggioranza dei segmenti modificati;
- il peggioramento 2019-2020 viene accettato consapevolmente come costo della
  maggiore reattivita' del modello.

Compromesso accettato:

- il rendimento annuale migliora in 3 anni attivi e peggiora in 3 anni attivi;
- il vecchio filtro a 2 giorni resta storicamente piu' calmo in alcuni regimi;
- la nuova regola viene preferita perche' e' piu' coerente con l'obiettivo del
  modello: protezione prudenziale del capitale e riduzione del drawdown.

Stato:

- decisione approvata e messa agli atti;
- implementazione ufficiale eseguita su calcolo segnali, dashboard, report e
  messaggi Telegram.

### Implementazione ufficiale SMA50 a 1 giorno

Modifica applicata:

- sostituita la vecchia uscita `Close < SMA50` per 2 giorni consecutivi;
- nuova uscita ufficiale: `Close < SMA50` gia' dopo 1 candela giornaliera
  chiusa;
- Trail8 invariato;
- condizioni di acquisto invariate.

File operativi allineati:

- `strategy/signals.py`;
- `reports/generate.py`;
- `cloudflare-worker/src/worker.js`;
- `docs/index.html`;
- `docs/status.json`;
- `docs/live-status.json`;
- `docs/backtest.json`;
- `README.md`;
- documentazione corrente in `DOCUMENTATION/`;
- test automatici.

Verifiche:

- rigenerati dati/report con `python main.py --force-download`;
- copiata la dashboard aggiornata in `docs/`;
- verificato che `status.json` esponga `below_sma50_1d`;
- suite `unittest` completata con 60 test passati;
- ricerca sui file operativi: nessun riferimento residuo alla vecchia regola
  di conferma SMA50 a 2 giorni.

### Test rimozione condizione ingresso SMA50 > SMA200

Motivo:

- verificare se la condizione di acquisto `SMA50 > SMA200` puo' essere
  eliminata dalla Baseline;
- isolare solo questa modifica, lasciando invariati:
  - `Close > SMA200`;
  - `RSI >= 40`;
  - `RSI <= 65`;
  - momentum 7 giorni positivo;
  - volume sopra media 20 giorni;
  - uscite `Close < SMA50` a 1 giorno e Trail8 confermato.

Periodo:

- dati rigenerati fino alla candela chiusa `2026-07-03`;
- performance principali misurate in EUR tramite `Close_EUR`;
- controllo di coerenza eseguito anche in USD.

Confronto principale:

| Variante | Ann. | Max DD | Sharpe | Profit factor | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline ufficiale | 50,95% | -41,10% | 1,216 | 7,400 | 29 |
| Senza `SMA50 > SMA200` | 56,07% | -41,10% | 1,247 | 7,335 | 31 |

Controllo USD:

| Variante | Ann. | Max DD | Sharpe | Profit factor | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline ufficiale | 51,81% | -40,97% | 1,217 | 7,117 | 29 |
| Senza `SMA50 > SMA200` | 57,34% | -40,97% | 1,255 | 7,089 | 31 |

Robustezza rimozione pura:

- stress costi 0,25% ancora positivo: delta annualizzato +4,84 punti;
- finestre rolling 730 giorni positive nel 92% dei casi;
- il candidato fallisce pero' 2 gate di stabilita':
  - peggiora il segmento 2018-2019 di -27,15 punti di rendimento;
  - peggiora il drawdown del segmento 2018-2019 di -16,53 punti.

Trade sbloccati perche' `SMA50 <= SMA200`:

| Entry | Exit | Return | DD trade | RSI | Mom 7g | Volume rel |
|---|---|---:|---:|---:|---:|---:|
| 2019-04-11 | 2019-07-11 | +62,52% | -19,32% | 59,51 | +4,71% | +21,33% |
| 2019-09-22 | 2019-09-24 | -20,49% | -20,49% | 63,28 | +11,46% | +7,30% |
| 2020-04-19 | 2020-06-27 | +18,91% | -13,77% | 61,43 | +12,70% | +19,12% |
| 2023-02-02 | 2023-03-03 | -2,15% | -9,86% | 63,08 | +2,50% | +22,36% |
| 2023-11-14 | 2024-01-22 | +16,76% | -10,94% | 61,60 | +4,82% | +36,79% |
| 2024-11-14 | 2024-12-21 | +10,12% | -15,61% | 60,73 | +5,64% | +24,70% |
| 2025-06-09 | 2025-06-13 | -4,83% | -9,21% | 61,78 | +2,85% | +3,44% |

Lettura:

- la rimozione pura e' interessante sulle metriche aggregate;
- il peggioramento 2018-2019 e' troppo ampio per promuoverla direttamente;
- il falso rimbalzo del 2019-09-22 mostra il rischio della rimozione senza
  protezioni.

### Guardrail su rimozione SMA50 > SMA200

Motivo:

- capire se la rimozione puo' essere resa piu' robusta applicando un guardrail
  solo agli ingressi anticipati, cioe' quando `SMA50 <= SMA200`.

Varianti principali:

| Variante | Ann. | Max DD | Sharpe | Profit factor | Delta 2018-2019 | Rolling + | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|
| `RSI <= 62 oppure volume rel >= +15%` | 60,55% | -41,10% | 1,321 | 9,488 | +6,16% | 96,00% | PASS |
| `momentum 7g <= +10%` | 60,02% | -41,10% | 1,316 | 9,443 | +6,16% | 96,00% | PASS |
| `RSI <= 62` | 59,80% | -41,10% | 1,315 | 9,015 | +6,16% | 96,00% | PASS |
| `volume rel >= +15%` | 58,71% | -41,10% | 1,294 | 8,460 | +6,16% | 96,00% | PASS |
| rimozione pura | 56,07% | -41,10% | 1,247 | 7,335 | -27,15% | 92,00% | FAIL |

Lettura:

- i guardrail eliminano il difetto principale della rimozione pura;
- la variante piu' semplice e difendibile e' `momentum 7g <= +10%` sugli
  ingressi con `SMA50 <= SMA200`;
- la variante numericamente migliore, `RSI <= 62 oppure volume rel >= +15%`,
  e' meno elegante e piu' esposta al rischio di regola costruita sul campione.

Decisione:

- non modificare la Baseline;
- non eliminare ora `SMA50 > SMA200`;
- registrare il test come prova fatta e lasciare la strategia ufficiale
  invariata;
- eventuale lavoro futuro puo' ripartire dal guardrail semplice
  `momentum 7g <= +10%`, ma solo con audit evento-per-evento e confronto con
  altre semplificazioni del modello.

File generati:

- `scripts/run_sma50_trend_filter_removal.py`;
- `scripts/run_sma50_trend_filter_robustness.py`;
- `scripts/run_sma50_trend_filter_guardrails.py`;
- `reports/sma50_trend_filter_removal.md`;
- `reports/sma50_trend_filter_robustness.md`;
- `reports/sma50_trend_filter_guardrails.md`.

Verifiche:

- `python main.py --force-download`;
- `python scripts\run_sma50_trend_filter_removal.py`;
- `python scripts\run_sma50_trend_filter_robustness.py`;
- `python scripts\run_sma50_trend_filter_guardrails.py`;
- `python -m py_compile scripts\run_sma50_trend_filter_removal.py scripts\run_sma50_trend_filter_robustness.py scripts\run_sma50_trend_filter_guardrails.py`.

## Registro Operativo 2026-07-22 - Telegram esclusivamente LIVE

Obiettivo:

- eliminare il segnale DAILY dai messaggi Telegram;
- mantenere soltanto le variazioni del segnale LIVE e la risposta LIVE a
  `/segnale`;
- non modificare nessuna regola di acquisto o vendita.

Implementazione:

- rimosso dal monitor l'invio DAILY alla pubblicazione di una nuova candela;
- rimosso l'invio DAILY da `workflow_dispatch`;
- rimosso il messaggio Telegram di servizio dall'esecuzione locale di
  `main.py`;
- mantenuti controllo ogni 10 minuti, stabilizzazione LIVE di 10 minuti e
  cooldown gia esistente;
- rimosso dal Worker il fallback da `live-status.json` a `status.json` per
  `/segnale` e `/live-preview`;
- ripuliti i campi di stato usati soltanto dalle vecchie notifiche DAILY;
- aggiornati test, dashboard e documentazione operativa.

Decisione modello:

- le cinque condizioni ACQUISTA e le due condizioni VENDI sono invariate;
- soglie, calcolo degli indicatori, gestione della posizione, backtest e
  Baseline ufficiale non cambiano;
- il giornaliero resta necessario per storico, dashboard, backtest e base di
  calcolo, ma non produce piu messaggi Telegram.

## Registro Operativo 2026-07-19 - Dashboard OHLC e dismissione Render

Obiettivo:

- rendere il grafico ETH piu leggibile con candele daily rosse e verdi;
- seguire il giorno UTC corrente senza usare dati incompleti nel segnale;
- eliminare componenti infrastrutturali non piu utilizzate;
- verificare il funzionamento generale senza modificare la Baseline.

Implementazione grafico:

- `chart-data.json` esporta Open, High, Low e Close Yahoo oltre a indicatori e
  volumi;
- la dashboard disegna candele storiche chiuse e barre volume coerenti con il
  colore della giornata;
- Coinbase Exchange alimenta la candela UTC corrente, visualizzata vuota e
  tratteggiata per indicarne la natura provvisoria;
- un fallback spot aggiorna almeno Close, High e Low se l'endpoint OHLC non e
  temporaneamente disponibile;
- i dati Yahoo hanno sempre priorita e sostituiscono la riga provvisoria non
  appena la candela ufficiale viene pubblicata;
- SMA50, SMA200, RSI con soglie 40/65 e media volumi 20 giorni restano linee;
- la candela Coinbase non entra in indicatori, backtest o segnali.

Audit infrastrutturale:

- Worker ETH, health iscritti e contatore pubblico verificati online;
- dashboard GitHub Pages e workflow schedulati verificati attivi;
- pannello Render verificato con zero servizi attivi;
- rimossi backend FastAPI legacy, configurazione Render, test dedicati,
  dipendenze e guida di deploy ormai non eseguibile.

Correzioni operative:

- Yahoo viene forzato a ogni run finche la data daily attesa non risulta
  processata, eliminando il vincolo fragile del solo minuto 30;
- `run_dashboard.py` pubblica ora `docs/`, allineando dashboard locale e
  pubblica;
- aggiunta `BASELINE_SYNC_CHECKLIST.md` con i controlli trasversali obbligatori.

Decisione modello:

- nessuna condizione di ingresso o uscita e stata modificata;
- metriche e baseline restano quelle ufficiali.
# Aggiornamento 2026-07-27 - Coerenza Coinbase e baseline riproducibile

- Mantenuta senza modifiche la baseline ETH con cinque condizioni di acquisto
  e due di vendita.
- Sostituita la fonte runtime Yahoo con Coinbase Advanced Trade `ETH-USD`.
- Scelta come inizio canonico la prima serie continua, `2016-05-23`, perche le
  candele `2016-05-21` e `2016-05-22` mancano nello storico precedente.
- Congelata la baseline v1 al cutoff approvato `2026-07-26`; i run operativi
  successivi restano dinamici.
- Uniformata l'azione neutrale a `MANTIENI STATO ATTUALE`.
- Aggiunti snapshot grezzo, manifest, hash, ambiente bloccato, pubblicazione
  transazionale e riproduzione offline byte per byte.
- Dashboard, Telegram e Worker consumano gli output della pipeline unica; il
  Worker non contiene piu formule del modello.

## Promozione 2026-07-27 - Nuova Baseline ufficiale

Obiettivo:

- verificare se una o piu condizioni potessero migliorare rendimento, drawdown
  e Sharpe senza cambiare i cinque ingressi approvati;
- usare Coinbase `ETH-USD` e commissione massima 0,6% per lato;
- applicare i test all'intera storia disponibile invece di attendere 12 mesi.

Protocollo:

- ablation di condizioni e griglie locali;
- audit evento per evento e trade per trade;
- walk-forward annuale expanding dal 2021 al 2026;
- confronto con Buy & Hold;
- stress con una candela extra di ritardo;
- PBO/CSCV e Deflated Sharpe;
- 285 definizioni e 134 percorsi di segnale distinti.

Decisione:

- promuovere il candidato fisso
  `combo_trail_mom_15_sma_break_2_0`;
- mantenere invariate tutte le condizioni di acquisto;
- cambiare l'uscita SMA50 in `Close < SMA50 * 0,98`;
- cambiare la conferma momentum Trail8 da `>= -5%` a `>= -15%`;
- mantenere Trail8 all'8% e volume relativo `>= +20%`;
- non adottare la selezione annuale, perche non migliora lo Sharpe del candidato
  fisso e presenta ranking meno stabile.

Risultato sul periodo completo 2016-2026, commissione 0,6%:

- rendimento totale 56.672,64%;
- annualizzato 93,12%;
- max drawdown -43,00%;
- Sharpe 1,615;
- 30 trade completati.

Versionamento:

- il numero `v2` resta interno a manifest, tag e directory;
- nei messaggi pubblici la strategia viene chiamata Baseline ufficiale;
- `v1` diventa la vecchia baseline e resta immutabile;
- alla candela 2026-07-26 entrambe sono fuori mercato, quindi la promozione non
  genera un'operazione immediata.

Riferimenti:

- `reports/condition_ablation_coinbase_0_6.md`;
- `reports/walk_forward_coinbase_0_6.md`;
- `reports/official_baseline_implementation.md`.

## Test 2026-08-22 - Rimozione del limite superiore RSI 65

Motivazione:

- tra il 16 e il 21 agosto 2026 ETH ha registrato un rialzo molto rapido;
- la Baseline e' rimasta fuori mercato;
- e' stato richiesto di verificare se sostituire `40 <= RSI(14) <= 65` con
  il solo requisito `RSI(14) >= 40` migliori il modello.

Protocollo:

- test esclusivamente sperimentale, senza modificare i segnali ufficiali;
- mercato Coinbase `ETH-USD`, candele daily UTC chiuse;
- periodo valutato `2016-12-08` -> `2026-08-21`;
- commissione ufficiale conservativa `0,60%` per lato;
- lasciate invariate tutte le altre condizioni di acquisto;
- lasciate invariate entrambe le regole di vendita della Baseline v2;
- aggiunti stress costi, confronto annuale, audit dei nuovi ingressi e 97
  finestre mobili di 730 giorni.

Risultati periodo completo con commissione `0,60%`:

| Modello | Totale | Annualizzato | Max DD | Sharpe | PF | Trade | Win rate | Esposizione |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline `RSI 40-65` | 56.672,64% | 92,19% | -43,00% | 1,609 | 14,944 | 30 | 50,00% | 26,78% |
| Variante `RSI >= 40` | 160.216,14% | 113,88% | -42,56% | 1,665 | 19,156 | 34 | 52,94% | 29,09% |

Audit:

- la variante genera 8 nuovi ingressi effettivi;
- 4 nuovi trade sono positivi e 4 negativi;
- il vantaggio aggregato e' dominato dall'ingresso del `2017-03-11`, che
  produce `+1.395,40%` netto nel campione;
- nel 2025 la variante rende `+17,30%` contro `+29,52%` della Baseline e
  peggiora il drawdown annuale da `-29,50%` a `-36,15%`;
- solo il `40,21%` delle finestre mobili biennali migliora il rendimento;
- solo il `36,08%` migliora lo Sharpe;
- solo il `43,30%` presenta drawdown uguale o migliore.

Verifica dell'episodio agosto 2026:

- togliere soltanto il tetto RSI non produce alcun nuovo `ACQUISTA` dal 16 al
  21 agosto;
- dopo il breakout RSI sale sopra 65, ma `SMA50 > SMA200` resta falsa;
- quindi questa modifica non avrebbe intercettato il movimento che ha
  motivato il test.

Decisione:

- non promuovere la variante;
- mantenere invariata la Baseline ufficiale;
- il prossimo test dovra valutare un ingresso breakout separato e circoscritto,
  senza eliminare globalmente la protezione RSI.

File:

- `scripts/run_rsi_upper_cap_removal.py`;
- `reports/rsi_upper_cap_removal.md`.

Aggiornamento costi operativi comunicato il 2026-08-22:

- promozione VIP Coinbase attiva con commissione maker `0,07%` per lato e
  taker `0,16%` per lato;
- aggiunto al test anche lo scenario misto, equivalente a `0,115%` medio per
  lato quando un'esecuzione e' maker e l'altra taker;
- per un segnale che richiede esecuzione certa il riferimento operativo
  principale e' il taker `0,16%`;
- il maker `0,07%` resta lo scenario ottimistico, perche un ordine limite puo
  non essere eseguito;
- il `0,60%` per lato non viene rimosso dalla configurazione: resta lo scenario
  prudenziale del modello e permette confronti omogenei con i test precedenti.

Risultati con tariffa taker `0,16%` per lato:

| Modello | Totale | Annualizzato | Max DD | Sharpe | PF |
|---|---:|---:|---:|---:|---:|
| Baseline `RSI 40-65` | 73.718,82% | 97,46% | -39,87% | 1,665 | 15,995 |
| Variante `RSI >= 40` | 215.909,13% | 120,56% | -39,44% | 1,722 | 20,471 |

Le nuove tariffe migliorano le metriche nette di entrambi i modelli ma non
cambiano la conclusione qualitativa: la variante resta poco uniforme nelle
finestre mobili e non intercetta il rally di agosto 2026.

## Test 2026-08-22 - Trail9 al posto di Trail8

Ipotesi:

- verificare se allargare il trailing stop dall'8% al 9% avrebbe evitato
  l'uscita del 19 agosto 2025 e il successivo rientro;
- mantenere invariati ingressi, uscita SMA50 e conferme momentum/volume.

Risultato sull'episodio:

- massimo Close post-ingresso `4.751,46 USD` il 13 agosto 2025;
- uscita il 19 agosto a `4.075,89 USD`, pari a `-14,22%` dal massimo;
- momentum 7 giorni `-11,20%`, ancora sopra la soglia `-15%`;
- volume relativo `+37,27%`, sopra la conferma `+20%`;
- Trail8 e Trail9 vendono entrambi il 19 agosto;
- il rientro Baseline resta invariato al 25 agosto 2025.

Confronto storico completo con tariffa taker `0,16%`:

| Modello | Totale | Annualizzato | Max DD | Sharpe | PF | Trade |
|---|---:|---:|---:|---:|---:|---:|
| Trail8 ufficiale | 73.718,82% | 97,46% | -39,87% | 1,665 | 15,995 | 30 |
| Trail9 test | 73.252,37% | 97,33% | -39,87% | 1,664 | 15,989 | 30 |

Audit:

- nell'intera storia Trail9 cambia un solo segnale, quello del 2 agosto 2023;
- l'uscita viene rinviata al 4 agosto 2023;
- il rendimento netto del trade scende da `+2,41%` a `+1,77%`;
- il drawdown del trade passa da `-8,33%` a `-8,91%`.

Decisione:

- non promuovere Trail9;
- mantenere Trail8 ufficiale;
- Trail9 non risolve l'episodio per cui e' stato proposto e peggiora
  leggermente l'unico segnale storico che modifica.

File:

- `scripts/run_trailing_stop_9pct_test.py`;
- `reports/trailing_stop_8_vs_9.md`.

## Audit 2026-08-22 - Il Trail8 aggiunge valore?

Obiettivo:

- stabilire se il Trail8 e' complessivamente valido oppure interrompe troppi
  trade convenienti;
- confrontare la Baseline attuale con la stessa strategia senza trailing;
- mantenere identici ingressi e uscita `Close < SMA50 * 0,98`.

Metriche con tariffa taker `0,16%` per lato:

| Modello | Totale | Annualizzato | Max DD | Sharpe | PF | Trade | Win rate | Esposizione |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Trail8 ufficiale | 73.718,82% | 97,46% | -39,87% | 1,665 | 15,995 | 30 | 50,00% | 26,78% |
| Senza trailing | 53.714,46% | 91,13% | -48,92% | 1,451 | 18,313 | 24 | 58,33% | 31,60% |

Audit delle sequenze:

- 15 sequenze operative vengono realmente modificate dal Trail8;
- 9 sequenze migliorano e 6 peggiorano;
- principali miglioramenti: marzo 2017, maggio/settembre 2020, maggio e
  settembre 2021, febbraio e dicembre 2024;
- principali peggioramenti: dicembre 2017 e agosto 2025;
- nel segmento luglio-settembre 2025 Trail8 rende `+51,24%` contro `+62,93%`
  restando dentro, delta `-11,68` punti percentuali;
- nel segmento novembre 2017-febbraio 2018 Trail8 rende `+40,02%` contro
  `+195,26%`, delta `-155,24` punti percentuali.

Decisione:

- Trail8 e' valido a livello di portafoglio: aumenta rendimento annualizzato e
  Sharpe e riduce il max drawdown di circa 9 punti;
- non e' perfetto: divide alcuni trade e abbassa win rate e profit factor;
- non rimuovere Trail8;
- trattare i falsi stop come problema specifico da analizzare senza allargare
  indiscriminatamente la soglia.

File:

- `scripts/run_trail8_value_audit.py`;
- `reports/trail8_value_audit.md`.

## Ricerca 2026-08-22 - Guardrail selettivo per i falsi stop Trail8

Obiettivo:

- studiare una modifica della conferma Trail8 capace di migliorare le 6
  sequenze peggiorative senza perdere la protezione delle altre 9;
- usare soltanto dati disponibili alla chiusura della candela, senza look-ahead;
- lasciare invariati ingressi e uscita ufficiale `Close < SMA50 * 0,98`;
- non modificare la Baseline durante la fase di ricerca.

Protocollo:

- mercato Coinbase `ETH-USD`, daily UTC chiuso;
- periodo `2016-12-08` -> `2026-08-21`;
- riferimento operativo taker Coinbase VIP `0,16%` per lato;
- stress costi maker `0,07%`, prudenziale `0,60%` e stress `1,00%`;
- testate `274` regole su ampiezza trailing, momentum, volume, ATR,
  estensione dalla SMA50 e pendenza SMA50 a 5 giorni;
- validazione su 97 finestre mobili di 730 giorni e sui sottoperiodi
  `2017-2019`, `2020-2022` e `2023-oggi`;
- audit delle 15 sequenze realmente modificate dal trailing.

Risultato della ricerca:

- nessuna regola recupera tutte le 6 sequenze senza danneggiare almeno una
  delle 9 sequenze protettive;
- togliere il trailing recupera le 6 sequenze, ma perde tutte le 9 protezioni,
  riduce lo Sharpe a `1,451` e peggiora il max DD a `-48,92%`;
- portare globalmente il trailing al 12% aumenta il rendimento, ma peggiora il
  max DD a `-42,96%` e danneggia 3 sequenze protettive;
- modificare soltanto momentum o volume non separa in modo affidabile i falsi
  stop dalle uscite utili.

Candidato che migliora tutte le 6 sequenze:

- Trail11 quando la pendenza SMA50 a 5 giorni e' `<= 4%`;
- conferma ammessa solo con prezzo almeno `5%` sopra SMA50;
- soglia momentum portata da `-15%` a `-10%`;
- annualizzato `111,67%`, max DD `-43,53%`, Sharpe `1,739`, PF `24,073`;
- migliora tutte le 6 sequenze, ma ne recupera completamente 5;
- danneggia 2 sequenze protettive, di `-0,65` e `-9,96` punti;
- non e' considerato prudente per il peggioramento del drawdown.

Miglior compromesso prudente:

- Trail8 resta normale quando la SMA50 e' forte;
- il trailing si allarga all'11% soltanto quando la SMA50 e' salita non piu
  del `4%` negli ultimi 5 giorni;
- il trailing confermato puo vendere soltanto se il Close e' almeno `5%`
  sopra SMA50;
- momentum `>= -15%` e volume relativo `>= +20%` restano invariati;
- annualizzato `110,82%` contro `97,46%` della Baseline;
- max DD `-39,45%` contro `-39,87%`;
- Sharpe `1,748` contro `1,665`; PF `20,843` contro `15,995`;
- migliora 4 delle 6 sequenze peggiorative e ne recupera completamente 3;
- danneggia una sola sequenza protettiva, giugno-agosto 2023, per `-0,65`
  punti percentuali;
- nelle 97 finestre biennali migliora il rendimento nel `98,97%`, lo Sharpe
  nel `96,91%` e il drawdown nel `70,10%`; nessuna finestra ha rendimento
  inferiore alla Baseline.

Decisione:

- non promuovere ancora nessuna variante;
- mantenere invariata la Baseline ufficiale;
- conservare il compromesso prudente come miglior candidato di ricerca;
- il passaggio successivo richiesto prima di una promozione e' una selezione
  walk-forward realmente fuori campione, per ridurre il rischio di overfitting
  dovuto alle sole 15 sequenze disponibili.

File:

- `scripts/run_trail8_guardrail_research.py`;
- `reports/trail8_guardrail_research.md`;
- `reports/trail8_guardrail_grid.csv`;
- `reports/trail8_guardrail_events.csv`;
- `reports/trail8_guardrail_event_features.csv`.

## Validazione 2026-08-22 - Nested walk-forward dei guardrail Trail8

Obiettivo:

- proseguire la verifica del candidato prudente con selezione cronologica;
- impedire al selettore annuale di usare dati successivi all'anno di training;
- misurare il rischio di overfitting generato dalle 274 regole esplorate;
- mantenere invariata la Baseline ufficiale.

Metodo:

- dati Coinbase `ETH-USD`, daily UTC, fino al `2026-08-21`;
- primo anno di test `2020`, con training iniziale `2016-12-08` -> `2019-12-31`;
- training expanding aggiornato soltanto a fine anno;
- candidato eleggibile solo se supera la Baseline in annualizzato, max DD e
  Sharpe, completa almeno 5 trade e non aggiunge oltre 12 lati di turnover;
- 274 regole deduplicate in 70 percorsi di segnale realmente distinti;
- tre policy: gate Baseline/candidato prudente, famiglia prudente da 24
  percorsi e griglia completa da 70 percorsi;
- commissione principale taker VIP `0,16%`, stress maker `0,07%`,
  prudenziale `0,60%` e ritardo aggiuntivo di una candela;
- bootstrap circolare appaiato con blocchi da 30 e 90 giorni.

Risultato principale 2020-2026, taker `0,16%`:

| Modello | Totale | Annualizzato | Max DD | Sharpe | Trade |
|---|---:|---:|---:|---:|---:|
| Baseline | 3.249,48% | 69,64% | -39,87% | 1,460 | 23 |
| Candidato prudente / gate a due | 3.589,14% | 72,13% | -39,45% | 1,490 | 21 |
| Candidato tutte-6 | 3.734,91% | 73,13% | -43,53% | 1,476 | 19 |
| WF famiglia prudente | 2.631,48% | 64,51% | -42,96% | 1,379 | 22 |
| WF griglia completa | 3.060,99% | 68,17% | -48,92% | 1,406 | 19 |

Selezione cronologica:

- il gate limitato a Baseline e candidato prudente seleziona il candidato in
  ogni anno dal 2020 al 2026 usando solo il training precedente;
- rispetto alla Baseline migliora simultaneamente le tre metriche nel 2020,
  2023 e 2024; e' invariato nel 2021, 2022, 2025 e 2026;
- non presenta alcun anno classificato come peggiorativo;
- la riottimizzazione su 24 o 70 percorsi fallisce, soprattutto nel 2021,
  2023 e 2024: aggiungere alternative aumenta l'overfitting invece di
  migliorare la scelta.

Sensibilita' temporale:

- partenza 2021: candidato `55,77%` annualizzato, DD `-39,45%`, Sharpe
  `1,303`; Baseline `53,55%`, `-39,87%`, `1,272`;
- partenza 2023: candidato `13,74%` annualizzato, DD `-39,45%`, Sharpe
  `0,585`; Baseline `11,24%`, `-39,87%`, `0,513`;
- il vantaggio non dipende soltanto dal blocco 2020.

Costi e bootstrap:

- il candidato conserva il vantaggio con maker `0,07%`, taker `0,16%` e
  stress prudenziale `0,60%`;
- bootstrap 30 giorni: probabilita' di sovraperformance `93,70%`, vantaggio
  osservato di ricchezza finale `+10,14%`, intervallo 5%-95%
  `-0,26%` -> `+28,69%`;
- bootstrap 90 giorni: probabilita' `93,70%`, intervallo
  `-0,35%` -> `+27,57%`;
- il limite inferiore leggermente negativo non consente una confidenza piena
  al 95%.

Stress decisivo:

- con una candela ulteriore di ritardo, il candidato scende a `54,48%`
  annualizzato, DD `-44,86%`, Sharpe `1,222`;
- nello stesso stress la Baseline ottiene `57,78%`, DD `-44,38%`, Sharpe
  `1,282`;
- il vantaggio richiede quindi esecuzione coerente con il backtest alla
  candela giornaliera immediatamente successiva e non sopporta un giorno
  completo aggiuntivo di ritardo.

Interpretazione e decisione:

- il candidato prudente supera il miglior test storico cronologico disponibile;
- il test resta `pseudo out-of-sample`, non genuinamente fuori campione,
  perche la regola e l'universo sono stati definiti dopo avere osservato tutta
  la serie storica;
- nessun altro riutilizzo dei dati passati puo creare un campione davvero mai
  visto;
- non promuovere ora il candidato e non modificare la Baseline;
- congelare esattamente il candidato prudente e avviare da questa data un
  paper/shadow test prospettico: solo le candele successive al `2026-08-21`
  costituiranno vero out-of-sample.

File:

- `scripts/run_trail8_guardrail_walkforward.py`;
- `reports/trail8_guardrail_walkforward.md`;
- `reports/trail8_guardrail_walkforward_selections.csv`;
- `reports/trail8_guardrail_walkforward_metrics.csv`;
- `reports/trail8_guardrail_walkforward_yearly.csv`;
- `reports/trail8_guardrail_walkforward_bootstrap.csv`;
- `reports/trail8_guardrail_walkforward_equity.csv`.

## Gate statistico finale 2026-08-22 - Candidato guardrail Trail8

Obiettivo:

- applicare l'ultimo controllo retrospettivo prima di qualsiasi eventuale
  promozione del candidato prudente;
- misurare separatamente qualita' assoluta della strategia, vantaggio
  incrementale sulla Baseline, rischio di overfitting e stabilita' dei valori;
- mantenere invariata la Baseline ufficiale.

Protocollo:

- dati Coinbase `ETH-USD`, daily UTC chiuso, fino al `2026-08-21`;
- commissione taker VIP `0,16%` per lato;
- `274` regole provate, corrispondenti a `70` percorsi di segnale distinti;
- PBO/CSCV su 10 blocchi e 252 suddivisioni training/test;
- Sharpe corretto per selezione multipla su 70 e 274 prove;
- probabilita' che il rendimento giornaliero incrementale del candidato sia
  migliore di quello della Baseline;
- walk-forward expanding con purge di 30 e 90 giorni prima di ogni anno;
- griglia locale di 45 combinazioni: Trail `10-12%`, soglia slope SMA50
  `3,75-4,25%`, estensione sopra SMA50 `4-6%`;
- stress con un giorno completo aggiuntivo di ritardo.

Risultati principali sul periodo 2020-2026:

| Modello | Annualizzato | Max DD | Sharpe |
|---|---:|---:|---:|
| Baseline | 69,64% | -39,87% | 1,460 |
| Candidato prudente / gate a due | 72,13% | -39,45% | 1,490 |

Esito dei controlli:

- metriche aggregate: `PASS`, il candidato migliora annualizzato, drawdown e
  Sharpe;
- Deflated Sharpe corretto per 274 prove: `99,97%`, `PASS`;
- probabilita' del vantaggio incrementale sulla Baseline: `85,75%`, sotto la
  soglia prudenziale del `90%`, `FAIL`;
- PBO della griglia locale: `41,67%`, sotto il limite del `50%`, `PASS`;
- PBO della ricerca ampia: `75,40%` sui 70 percorsi e `73,41%` sulla famiglia
  conservativa, avvertimento di overfitting nella selezione ampia;
- stabilita' locale: solo il `44,44%` delle 45 combinazioni vicine migliora
  contemporaneamente annualizzato, drawdown e Sharpe, contro il minimo
  richiesto del `70%`, `FAIL`;
- walk-forward con purge 30 e 90 giorni: il candidato resta a `72,13%`,
  `-39,45%` e `1,490`, `PASS`;
- con un giorno aggiuntivo di ritardo il candidato ottiene `54,48%`
  annualizzato contro `57,78%` della Baseline e perde anche su drawdown e
  Sharpe, avvertimento operativo.

Interpretazione:

- lo Sharpe corretto molto alto conferma che la strategia nel suo complesso
  non e' un risultato casuale rispetto a zero; non dimostra pero' che la
  modifica sia superiore alla Baseline;
- il bootstrap precedente stimava una probabilita' di sovraperformance del
  `93,70%`, mentre il test probabilistico giornaliero incrementale restituisce
  `85,75%`: entrambi indicano un vantaggio probabile, ma non abbastanza stabile
  da essere considerato conclusivo;
- la fragilita' e' concentrata soprattutto intorno alla soglia slope SMA50:
  `4,00%` migliora le metriche, `4,25%` produce un peggioramento del drawdown;
- anche l'estensione al `6%` perde il vantaggio osservato con `4-5%`;
- l'ampiezza Trail tra `10%` e `12%` incide poco nello storico disponibile,
  quindi da sola non risolve il problema di selezione;
- tutte le prove restano pseudo-fuori-campione, perche' la famiglia di regole
  e' stata definita dopo aver osservato lo storico.

Decisione:

- verdetto finale del gate: **FAIL**;
- non promuovere il guardrail Trail8 e non modificare segnali, dashboard o bot;
- mantenere la Baseline ufficiale invariata;
- congelare il candidato prudente come ipotesi di ricerca, senza ulteriori
  ottimizzazioni sugli stessi dati;
- usare un confronto shadow prospettico e riesaminare il candidato dopo nuovi
  eventi in cui esso diverge realmente dalla Baseline. Un controllo a sei mesi
  puo' essere informativo, ma senza nuovi eventi Trail8 divergenti non produce
  nuova evidenza utile.

File:

- `scripts/run_trail8_guardrail_final_gate.py`;
- `reports/trail8_guardrail_final_gate.md`;
- `reports/trail8_guardrail_final_gate_checks.csv`;
- `reports/trail8_guardrail_final_gate_pbo.csv`;
- `reports/trail8_guardrail_final_gate_dsr.csv`;
- `reports/trail8_guardrail_final_gate_purged.csv`;
- `reports/trail8_guardrail_parameter_plateau.csv`.

## Ricerca 2026-08-22 - Ingresso alternativo sul breakout del 17 agosto 2026

Obiettivo:

- capire perche' la Baseline sia rimasta fuori dal rialzo iniziato il 17 agosto;
- verificare se un secondo percorso di ingresso possa intercettare accelerazioni
  simili senza rimuovere indiscriminatamente i filtri prudenziali;
- mantenere invariati ingressi ordinari, uscite ufficiali, dashboard e bot.

Caso osservato su Coinbase `ETH-USD`:

- dal Close del 16 agosto (`1.874,13 USD`) al 21 agosto (`2.515,80 USD`) il
  movimento e' stato `+34,24%`;
- il 17 agosto: Close `1.911,94`, RSI `56,61`, momentum 7g `+2,16%`, volume
  relativo `+53,06%`, SMA50 crescente `+1,69%` in 5 giorni e breakout del
  massimo precedente a 7 giorni `+1,45%`;
- il segnale e' rimasto bloccato perche' il Close era ancora `-4,80%` sotto
  SMA200 e SMA50 era sotto SMA200;
- il 19 agosto il Close ha superato SMA200 del `12,40%`, ma RSI era gia'
  `82,16`, oltre il limite d'ingresso `65`;
- rimuovere soltanto il limite RSI non avrebbe prodotto alcun acquisto;
- rimuovere SMA50>SMA200 e il limite RSI avrebbe comprato soltanto il 19
  agosto, dopo la candela principale, catturando `+11,56%` fino al cutoff.

Protocollo:

- periodo Coinbase completo fino alla candela chiusa del `2026-08-21`;
- commissioni principali taker `0,16%`, controllo maker `0,07%` e stress
  `0,60%` per lato;
- `71` configurazioni, corrispondenti a `28` percorsi di segnale distinti;
- tre famiglie: ablazione semplice dei filtri, breakout precoce sotto SMA200,
  impulso eccezionale sopra SMA200;
- metriche calcolate sia sull'intera serie sia con cutoff `2026-08-16`, in modo
  che il rialzo studiato non possa migliorare artificialmente il candidato;
- uscite identiche alla Baseline: `Close < SMA50 * 0,98` oppure Trail8
  confermato da momentum 7g `>= -15%` e volume relativo `>= +20%`;
- PBO/CSCV, Deflated Sharpe, probabilita' incrementale, bootstrap a blocchi,
  regimi storici, costi, ritardi di esecuzione e selezione ancorata al 2019.

Candidato esplorativo selezionato:

- nome ricerca: `early_lb5_vol20_near10_slope0`;
- non sostituisce l'ingresso ordinario: aggiunge un secondo percorso valido
  soltanto quando SMA50 e' ancora sotto o uguale a SMA200;
- Close sopra SMA50;
- Close non oltre il `10%` sotto SMA200 (`Close >= SMA200 * 0,90`);
- SMA50 non in calo rispetto a 5 giorni prima;
- RSI compreso tra `40` e `65`;
- momentum 7 giorni positivo;
- volume almeno `20%` sopra la media a 20 giorni;
- Close sopra il massimo dei 5 Close precedenti;
- tutte le condizioni devono essere vere sulla candela daily chiusa.

Risultato sul movimento corrente:

- segnale candidato il `2026-08-17` a `1.911,94 USD`;
- applicazione prudenziale al rendimento giornaliero successivo, senza
  look-ahead;
- rendimento simulato dal segnale al 21 agosto: `+31,37%` netto della
  commissione d'ingresso taker;
- la Baseline rimane fuori e realizza `0,00%` sullo stesso segmento;
- con una candela completa aggiuntiva di ritardo il candidato conserva
  `+31,08%`; con due candele aggiuntive cattura soltanto `+11,56%`.

Metriche con taker `0,16%`:

| Periodo | Modello | Annualizzato | Max DD | Sharpe |
|---|---|---:|---:|---:|
| Fino al 16 agosto 2026 | Baseline | 97,65% | -39,87% | 1,666 |
| Fino al 16 agosto 2026 | Candidato | 120,64% | -36,56% | 1,833 |
| Fino al 21 agosto 2026 | Baseline | 97,46% | -39,87% | 1,665 |
| Fino al 21 agosto 2026 | Candidato | 126,68% | -36,56% | 1,877 |

Audit dei segmenti divergenti:

| Segnale alternativo | Vantaggio rispetto alla Baseline | Esito |
|---|---:|---|
| 2017-02-01 | +55,10% | favorevole |
| 2019-03-27 | +18,20% | favorevole |
| 2023-01-06 | +32,00% | favorevole |
| 2024-11-06 | +36,33% | favorevole |
| 2026-01-13 | -11,92% | sfavorevole |
| 2026-08-17 | +31,37% al cutoff | aperto |

Stabilita' e controlli statistici prima dell'evento:

- 54 configurazioni della famiglia precoce e 14 percorsi distinti;
- `83,33%` delle combinazioni cattura la candela principale del 19 agosto;
- `42,59%` migliora contemporaneamente annualizzato, drawdown e Sharpe prima
  dell'evento; `40,74%` migliora le tre metriche e cattura il target;
- PBO iniziale di tutti i percorsi distinti `17,46%`; dopo la separazione
  rigorosa tra ingresso alternativo e gestione Baseline, PBO aggiornato
  `19,05%`; PBO della sola famiglia precoce invariato a `17,06%`;
- Deflated Sharpe corretto per 71 prove `100,00%`;
- probabilita' del vantaggio incrementale candidato-Baseline `99,73%`;
- bootstrap 30 giorni: probabilita' di sovraperformance `98,35%`, percentile
  5% del vantaggio `+18,63%`;
- bootstrap 90 giorni: probabilita' `97,35%`, percentile 5% `+14,39%`;
- il numero di eventi resta piccolo: prima del caso corrente vi sono soltanto
  cinque divergenze operative, quattro favorevoli e una sfavorevole.

Selezione cronologica ancorata:

- usando esclusivamente il periodo fino al `2019-12-31`, il selettore sceglie
  lo stesso candidato `early_lb5_vol20_near10_slope0`;
- sul successivo periodo `2020-01-01` -> `2026-08-16`, il candidato ottiene
  annualizzato `82,09%`, DD `-36,56%` e Sharpe `1,580`;
- sullo stesso periodo la Baseline ottiene `69,86%`, DD `-39,87%` e Sharpe
  `1,462`;
- il test e' cronologico ma resta pseudo-fuori-campione, perche' la famiglia di
  regole e' stata definita dopo aver osservato il caso del 2026.

Decisione:

- esiste un modo tecnicamente coerente per intercettare il movimento: un
  percorso di breakout precoce separato dall'ingresso ordinario;
- il risultato e' abbastanza forte da mantenere il candidato e approfondirlo,
  ma non autorizza ancora la promozione a segnale ufficiale;
- congelare esattamente la regola sopra indicata ed evitare di aggiustare RSI,
  volume o distanza SMA200 per eliminare a posteriori il solo trade negativo
  del gennaio 2026;
- Baseline, dashboard e bot restano invariati;
- prossimo controllo: riesaminare separatamente il falso ingresso del
  `2026-01-13` e confrontarlo con i quattro episodi favorevoli, senza usare il
  suo esito per scegliere nuove soglie.

File:

- `scripts/run_august_2026_breakout_entry_research.py`;
- `reports/august_2026_breakout_entry_research.md`;
- `reports/august_2026_breakout_entry_metrics.csv`;
- `reports/august_2026_breakout_entry_trades.csv`;
- `reports/august_2026_breakout_entry_segments.csv`;
- `reports/august_2026_breakout_entry_statistics.csv`;
- `reports/august_2026_breakout_entry_anchored.csv`;
- `reports/august_2026_breakout_entry_delays.csv`.

## Audit 2026-08-22 - Robustezza dei singoli ingressi breakout

Obiettivo:

- confrontare il falso ingresso del `2026-01-13` con i quattro episodi
  favorevoli precedenti e con il movimento aperto del `2026-08-17`;
- usare soltanto caratteristiche disponibili sulla candela d'ingresso;
- verificare se il vantaggio complessivo dipenda da un singolo episodio;
- non cercare nuove soglie capaci di eliminare a posteriori l'unica perdita.

Caratteristiche dei sei ingressi alternativi:

| Entry | Esito | RSI | Mom. 7g | Volume rel. | Dist. SMA200 | SMA50/SMA200 | Return 90g | Vantaggio Baseline |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2017-02-01 | favorevole | 61,05 | +1,61% | +21,26% | -0,58% | -13,52% | -1,38% | +55,10% |
| 2019-03-27 | favorevole | 56,30 | +0,25% | +41,22% | -9,18% | -13,59% | +21,33% | +18,20% |
| 2023-01-06 | favorevole | 59,16 | +5,82% | +26,52% | -8,66% | -11,88% | -3,56% | +32,00% |
| 2024-11-06 | favorevole | 61,02 | +2,49% | +204,10% | -7,90% | -14,27% | +1,52% | +36,33% |
| 2026-01-13 | negativo | 64,75 | +0,84% | +67,73% | -8,63% | -16,17% | -16,66% | -11,92% |
| 2026-08-17 | aperto | 56,61 | +2,16% | +53,06% | -4,80% | -8,22% | -9,39% | +31,37% al cutoff |

Lettura del falso ingresso di gennaio:

- RSI `64,75`, superiore al massimo `61,05` dei quattro episodi favorevoli;
- SMA50 distante `-16,17%` da SMA200, contro intervallo favorevole
  `-14,27%` -> `-11,88%`;
- rendimento a 90 giorni `-16,66%`, contro intervallo favorevole
  `-3,56%` -> `+21,33%`;
- pendenza SMA200 a 20 giorni `+1,57%`, mentre nei quattro episodi favorevoli
  era compresa tra `-8,09%` e `-1,04%`;
- questi quattro elementi descrivono un rimbalzo vicino al limite RSI dentro
  una struttura piu' deteriorata, ma provengono da un solo caso negativo e non
  costituiscono un filtro validato.

Leave-one-event-out fino al `2026-08-16`:

| Evento favorevole rimosso | Annualizzato candidato | Max DD | Sharpe | Migliora le 3 metriche |
|---|---:|---:|---:|---|
| nessuno | 120,64% | -36,56% | 1,832 | SI |
| 2017-02-01 | 110,88% | -36,56% | 1,762 | SI |
| 2019-03-27 | 116,87% | -36,56% | 1,810 | SI |
| 2023-01-06 | 114,41% | -36,56% | 1,785 | SI |
| 2024-11-06 | 113,70% | -39,87% | 1,782 | SI |

Risultato:

- il candidato continua a superare annualizzato, drawdown e Sharpe della
  Baseline anche rimuovendo uno alla volta ciascuno dei quattro episodi
  favorevoli;
- rimuovendo il caso negativo di gennaio, annualizzato e Sharpe salirebbero a
  `123,55%` e `1,861`, ma questa informazione non viene usata per modificare la
  regola.

Statistica a livello di eventi:

- eventi completati `5`, favorevoli `4`, win rate osservato `80,00%`;
- intervallo Wilson 95% del win rate `37,55%` -> `96,38%`;
- sign test unilaterale contro probabilita' 50%: p-value `18,75%`, non
  significativo al 5%;
- vantaggio composto sui cinque segmenti `+190,59%`;
- bootstrap di 20.000 campioni da cinque eventi: probabilita' di vantaggio
  positivo `98,98%`, intervallo 5%-95% `+39,90%` -> `+471,50%`;
- servirebbero nove perdite consecutive uguali al caso del 13 gennaio per
  annullare il vantaggio composto dei cinque segmenti osservati. Questa e'
  soltanto una misura di stress, non una previsione.

Decisione:

- il candidato non dipende da un singolo trade favorevole;
- il campione a livello di eventi resta troppo piccolo per una promozione
  automatica, nonostante la robustezza economica e il bootstrap favorevole;
- non introdurre filtri su RSI, distanza SMA50/SMA200, momentum a 90 giorni o
  pendenza SMA200 basandosi sul solo errore del gennaio 2026;
- mantenere congelato `early_lb5_vol20_near10_slope0` come candidato
  sperimentale e lasciare invariata la Baseline ufficiale;
- il prossimo dato davvero informativo sara' l'esito completo del trade aperto
  il `2026-08-17` oppure un nuovo segnale breakout indipendente.

File:

- `scripts/run_breakout_event_robustness_audit.py`;
- `reports/august_2026_breakout_event_audit.md`;
- `reports/august_2026_breakout_event_features.csv`;
- `reports/august_2026_breakout_bad_event_features.csv`;
- `reports/august_2026_breakout_leave_one_out.csv`;
- `reports/august_2026_breakout_event_statistics.csv`.

## Verifica 2026-08-22 - Chiusura affidata esclusivamente alla Baseline

Decisione dell'analisi:

- il nuovo percorso breakout viene valutato esclusivamente come ingresso;
- una volta aperta la posizione, la chiusura deve dipendere dalle regole
  ufficiali della Baseline, per verificare se proteggono correttamente anche
  questo tipo di movimento;
- la condizione breakout non puo' mantenere aperto il trade, sospendere il
  Trail8 o avere alcuna priorita' sulle condizioni di vendita;
- rimane invece invariata la priorita' del BUY core originale della Baseline,
  che fa gia' parte della logica ufficiale del Trail8.

Correzione e verifica tecnica:

- il runner di ricerca e' stato reso esplicito: il percorso alternativo puo'
  soltanto generare `ACQUISTA` quando la posizione e' chiusa;
- dopo l'ingresso si applicano esclusivamente `Close < SMA50 * 0,98` oppure
  Trail8 confermato da momentum 7g `>= -15%` e volume relativo `>= +20%`, con
  la priorita' BUY originale della Baseline;
- l'intera serie storica e' stata ricalcolata dopo la separazione;
- restano invariati candidato, sei eventi divergenti, metriche principali,
  leave-one-event-out e conclusioni; il PBO complessivo dei percorsi di
  controllo passa da `17,46%` a `19,05%`, mentre quello della famiglia precoce
  resta `17,06%`;
- Baseline ufficiale, dashboard e bot non sono stati modificati.

Stato del trade sperimentale alla candela chiusa del `2026-08-21`:

- ingresso candidato: `2026-08-17` a `1.911,94 USD`;
- massimo Close raggiunto: `2.515,80 USD` il `2026-08-21`;
- Trail8 dinamico: `2.314,54 USD`;
- Close corrente: `2.515,80 USD`, ancora `8,70%` sopra il Trail8;
- momentum 7g `+33,79%` e volume relativo `+209,88%`: entrambe le conferme
  del Trail8 sono vere, ma il livello di stop non e' stato raggiunto;
- livello di uscita SMA50: `1.855,71 USD`, non raggiunto;
- segnale corrente del candidato: `MANTIENI STATO ATTUALE`;
- a ogni nuovo massimo Close, il livello Trail8 verra' aggiornato; la prima
  futura uscita sara' registrata con data, prezzo, regola attivata, rendimento
  e confronto con il movimento che la Baseline non aveva acquistato.

File:

- `scripts/run_august_2026_breakout_entry_research.py`;
- `scripts/run_breakout_event_robustness_audit.py`;
- `reports/august_2026_breakout_entry_research.md`;
- `reports/august_2026_breakout_event_audit.md`;
- `reports/august_2026_breakout_exit_state.csv`.

## Ricerca 2026-08-23 - RSI e conferma prezzo del breakout precoce

Richiesta analizzata:

- sostituire `RSI 40-65` con il solo limite inferiore `RSI >= 40`;
- fondere momentum 7 giorni e massimo dei 5 Close precedenti nella regola
  `Close odierno > media dei 7 Close precedenti`;
- confrontare anche la formulazione alternativa `Close odierno > massimo dei
  7 Close precedenti`;
- indicare tutte le date nelle quali il percorso breakout avrebbe prodotto un
  ingresso effettivo.

Protocollo:

- dati `ETH-USD` Coinbase dall'inizio della serie valutabile alla candela
  chiusa del `2026-08-22`;
- commissione principale taker `0,16%` per lato; controlli maker `0,07%` e
  stress `0,60%` per lato;
- esecuzione prudenziale dalla candela successiva al segnale;
- metriche principali calcolate fino al `2026-08-16`, prima del movimento che
  ha generato la ricerca, e controllo completo fino al cutoff;
- tredici varianti tra configurazioni principali, ablazioni e sensibilita' a
  5/7/10 giorni; dieci percorsi di segnale distinti prima dell'evento;
- uscite sempre identiche alla Baseline ufficiale;
- verifica automatica della perfetta coincidenza tra replica Baseline e
  modello ufficiale e tra candidato attuale e candidato congelato.

Metriche principali pre-evento, commissione taker:

| Variante | Annualizzato | Max DD | Sharpe | Ingressi breakout | Perdite breakout | Profit factor complessivo |
|---|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | 97,65% | -39,87% | 1,666 | 0 | 0 | 15,995 |
| Attuale: RSI 40-65 + momentum7 + massimo5 | 120,64% | -36,56% | 1,833 | 6 | 1 | 16,830 |
| RSI >=40 + momentum7 + massimo5 | 125,29% | -36,56% | 1,835 | 12 | 5 | 13,005 |
| RSI 40-65 + media7 | 115,79% | -39,17% | 1,755 | 13 | 6 | 11,012 |
| RSI >=40 + media7 | 118,08% | -38,66% | 1,760 | 14 | 7 | 10,953 |
| RSI 40-65 + massimo7 | 120,64% | -36,56% | 1,833 | 6 | 1 | 16,830 |
| RSI >=40 + massimo7 | 125,29% | -36,56% | 1,835 | 12 | 5 | 13,005 |

Date degli ingressi breakout effettivi:

- candidato attuale e `RSI 40-65 + massimo7`: `2017-02-01`, `2019-03-27`,
  `2023-01-06`, `2024-11-06`, `2026-01-13`, `2026-08-17`;
- `RSI >=40 + momentum7 + massimo5` e `RSI >=40 + massimo7`:
  `2017-02-01`, `2018-05-03`, `2019-03-27`, `2020-01-15`, `2022-03-28`,
  `2023-01-06`, `2023-10-24`, `2024-11-06`, `2025-05-13`, `2025-06-10`,
  `2026-01-06`, `2026-08-17`;
- `RSI 40-65 + media7`: `2017-02-01`, `2018-05-07`, `2018-05-14`,
  `2019-03-27`, `2020-01-19`, `2020-05-07`, `2023-01-06`, `2023-11-20`,
  `2024-11-06`, `2025-05-29`, `2025-06-11`, `2026-01-13`, `2026-07-28`;
- `RSI >=40 + media7`: `2017-02-01`, `2018-05-03`, `2018-05-14`,
  `2019-03-27`, `2020-01-15`, `2020-05-07`, `2022-03-28`, `2023-01-06`,
  `2023-10-24`, `2024-11-06`, `2025-05-12`, `2025-06-10`, `2026-01-06`,
  `2026-07-28`.

Lettura della rimozione del tetto RSI:

- annualizzato pre-evento `+4,65` punti rispetto al candidato attuale;
- drawdown massimo invariato e Sharpe quasi identico (`1,833` -> `1,835`);
- gli ingressi breakout raddoppiano da 6 a 12 e le perdite passano da 1 a 5;
- nuove operazioni favorevoli: `2020-01-15` `+55,05%` e `2023-10-24`
  `+25,11%`;
- nuove operazioni sfavorevoli: `2018-05-03` `-12,85%`, `2022-03-28`
  `-5,28%`, `2025-05-13` `-10,16%`, `2025-06-10` `-8,68%`;
- l'ingresso negativo di gennaio 2026 viene anticipato dal 13 al 6 gennaio e
  passa da `-11,92%` a `-11,18%`, senza eliminare l'errore;
- PSR diretto di vantaggio sul candidato attuale `76,77%`; bootstrap 30/90
  giorni soltanto `63,10%`/`63,75%`, con percentile 5% `-39,25%`/`-41,90%`;
- il maggiore rendimento non si traduce quindi in un miglioramento robusto
  della qualita' del segnale.

Lettura della media7:

- la media7 e' molto piu' permissiva e misura un recupero di breve periodo,
  non un breakout;
- con RSI >=40 produce 14 ingressi, dei quali 7 perdenti;
- rispetto al candidato attuale peggiora annualizzato (`118,08%` contro
  `120,64%`), drawdown (`-38,66%` contro `-36,56%`) e Sharpe (`1,760` contro
  `1,833`);
- introduce fra gli altri i falsi ingressi `2018-05-14` `-20,85%` e
  `2020-05-07` `-11,93%`;
- sul movimento corrente era gia' dentro dal `2026-07-28` a `1.919,90 USD` e
  realizza `+29,23%` sul solo segmento 17-22 agosto, contro `+26,48%` del
  candidato entrato il 17 agosto; questo vantaggio locale non compensa il
  peggioramento storico;
- PSR diretto `48,31%` e bootstrap 30/90 giorni `41,00%`/`40,95%`: nessuna
  evidenza di vantaggio sul candidato attuale.

Lettura del massimo7:

- `Close > massimo dei 7 Close precedenti` assorbe logicamente il requisito
  momentum7 e, nello storico disponibile, genera esattamente gli stessi
  segnali del candidato `momentum7 + massimo5`;
- con RSI 40-65 replica tutte le sei date e tutte le metriche del candidato;
- con il solo RSI >=40 replica tutte le dodici date e le metriche della
  corrispondente variante senza tetto;
- e' quindi una formulazione piu' semplice e coerente con un breakout, ma
  rimane logicamente un poco piu' severa e non va confusa con un'identita'
  matematica universale.

Controlli di robustezza:

- PBO/CSCV sulle varianti: `82,54%`, valore elevato che segnala instabilita'
  nella selezione della configurazione apparentemente migliore;
- il candidato attuale conserva bootstrap contro la Baseline `98,35%` a 30g
  e `97,35%` a 90g;
- il solo RSI senza tetto conserva buone metriche assolute, ma il confronto
  diretto con il candidato attuale non e' abbastanza forte per sostituirlo;
- risultati coerenti sotto commissione maker/taker/stress e con ritardi di
  una o due candele; la media7 e' meno sensibile al ritardo nel caso corrente
  soltanto perche' era gia' esposta dal 28 luglio.

Decisione:

- non modificare la Baseline ufficiale, il bot o la dashboard;
- non adottare la media7 come sostituzione delle condizioni 6 e 8;
- mantenere `RSI >=40` senza tetto come variante shadow, non come nuovo
  candidato ufficiale;
- mantenere congelata la formulazione attuale del candidato per non alterare
  il test prospettico gia' iniziato;
- annotare `Close > massimo dei 7 Close precedenti` come formulazione
  equivalente osservata e piu' semplice da riesaminare alla prossima decisione,
  senza cambiare ora il candidato congelato.

File:

- `scripts/run_breakout_rsi_confirmation_research.py`;
- `reports/breakout_rsi_confirmation_research.md`;
- `reports/breakout_rsi_confirmation_metrics.csv`;
- `reports/breakout_rsi_confirmation_entries.csv`;
- `reports/breakout_rsi_confirmation_triggers.csv`;
- `reports/breakout_rsi_confirmation_yearly.csv`;
- `reports/breakout_rsi_confirmation_costs.csv`;
- `reports/breakout_rsi_confirmation_delays.csv`;
- `reports/breakout_rsi_confirmation_statistics.csv`.

## Ricerca 2026-08-23 - Guardrail per il falso breakout di gennaio 2026

Motivazione:

- le varianti breakout entrano il `2026-01-06` quando si usa `RSI >=40`
  senza tetto oppure il `2026-01-13` con `RSI 40-65`;
- entrambe escono il `2026-01-20` a `2.936,50 USD`, rispettivamente con
  `-11,18%` e `-11,92%` netti;
- il prezzo non ha recuperato i livelli di ingresso entro la candela chiusa
  del `2026-08-22`;
- obiettivo del test: evitare l'episodio usando informazioni disponibili ex
  ante, senza una regola associata alle date e senza modificare la Baseline.

Diagnosi comune alle due entrate:

| Data | Close | RSI | Slope SMA200 20g | SMA50/SMA200 | Return 90g |
|---|---:|---:|---:|---:|---:|
| 2026-01-06 | 3.295,59 | 68,55 | +1,24% | -16,50% | -27,21% |
| 2026-01-13 | 3.323,38 | 64,75 | +1,57% | -16,17% | -16,66% |

Il solo tetto RSI non e' sufficiente: rinvia l'entrata dal 6 al 13 gennaio,
ma non elimina il falso recupero. Il regime distintivo e' la combinazione tra
SMA200 ancora crescente e SMA50 molto distante sotto SMA200.

Protocollo:

- dati `ETH-USD` Coinbase dall'inizio della serie alla candela chiusa del
  `2026-08-22`;
- commissione taker `0,16%` per lato, con controlli maker `0,07%`, stress
  `0,60%` e ritardi aggiuntivi di 1-2 candele;
- 106 guardrail per ciascuno dei due sistemi breakout, per un totale di 212
  percorsi: filtri singoli, coppie e regole due-rischi-su-tre;
- soglie testate intorno a slope SMA200 20g, distanza SMA50/SMA200 e rendimento
  a 90 giorni;
- uscite e condizioni ufficiali invariate;
- confronto separato fino al `2026-01-05`, prima dell'episodio usato per
  formulare il guardrail;
- verifica di conservazione di tutti gli episodi breakout favorevoli e del
  movimento iniziato il `2026-08-17`.

Candidato principale shadow:

> Bloccare il solo ingresso breakout quando sono vere insieme entrambe:
> `SMA200 slope 20g > 0%` e `SMA50/SMA200 < -15%`.

Risultati con commissione taker:

| Sistema | Guardrail | Rendimento totale | Annualizzato | Max DD | Sharpe | Profit factor | Operazioni | Breakout loss |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| RSI 40-65, senza guardrail | no | +271.202,84% | 125,74% | -36,56% | 1,869 | 16,830 | 33 | 1 |
| RSI 40-65, guardrail | si | +307.926,92% | 128,71% | -36,56% | 1,897 | 19,020 | 32 | 0 |
| RSI >=40, senza guardrail | no | +331.993,15% | 130,49% | -36,56% | 1,870 | 13,005 | 38 | 5 |
| RSI >=40, guardrail | si | +428.934,67% | 136,65% | -36,56% | 1,928 | 15,709 | 36 | 3 |

Effetti sulle operazioni:

- elimina il falso ingresso del `2026-01-13` dal sistema RSI 40-65;
- elimina il falso ingresso del `2026-01-06` dal sistema RSI >=40;
- nella variante RSI >=40 elimina anche il precedente indipendente del
  `2018-05-03`, chiuso a `-12,85%`;
- conserva tutti gli episodi breakout favorevoli precedenti;
- conserva l'ingresso del `2026-08-17` a `1.911,94 USD`, ancora aperto al
  cutoff con `+26,47%` netto;
- il drawdown massimo complessivo resta `-36,56%`: il guardrail migliora il
  percorso e il profit factor, ma non elimina il principale drawdown storico.

Robustezza e limiti:

- tutte le nove combinazioni vicine con slope tra `-1%` e `+1%` e distanza
  tra `-16%` e `-14%` evitano gennaio, conservano agosto e non perdono episodi
  favorevoli;
- i risultati restano coerenti sotto costi maker/taker/stress e ritardi di
  una o due candele;
- fino al `2026-01-05` il sistema RSI 40-65 resta esattamente invariato;
- nel sistema RSI >=40 il guardrail migliora lo storico precedente eliminando
  il trade negativo del 2018;
- limite decisivo: nel percorso RSI 40-65 il guardrail incide storicamente su
  una sola operazione, proprio gennaio 2026; il precedente indipendente esiste
  soltanto nel percorso RSI >=40. Il campione e' quindi troppo piccolo per una
  promozione definitiva.

Decisione:

- nessuna modifica a Baseline, bot, dashboard o candidato congelato;
- registrare la regola combinata come `guardrail candidato shadow`;
- non confondere il miglioramento successivo a gennaio con una validazione
  fuori campione, poiche' il caso ha motivato la costruzione della regola;
- riesaminare il guardrail quando un nuovo ingresso breakout si presenta nello
  stesso regime oppure quando il trade aperto del 17 agosto verra' chiuso.

File:

- `scripts/run_january_2026_entry_guardrail_research.py`;
- `tests/test_january_2026_entry_guardrail.py`;
- `reports/january_2026_entry_guardrail_research.md`;
- `reports/january_2026_entry_guardrail_grid.csv`;
- `reports/january_2026_entry_guardrail_trades.csv`;
- `reports/january_2026_entry_guardrail_yearly.csv`;
- `reports/january_2026_entry_guardrail_robustness.csv`;
- `reports/january_2026_entry_guardrail_entry_features.csv`.

## Validazione 2026-08-23 - Replay cieco pre-2026 del guardrail

Domanda:

- verificare se il pacchetto `breakout RSI 40-65 + guardrail` possa essere
  promosso a Baseline ufficiale;
- evitare di scegliere una soglia soltanto perche' cancella a posteriori il
  falso ingresso del 6/13 gennaio 2026.

Protocollo temporale:

- selezione dei 105 guardrail alternativi usando esclusivamente dati chiusi
  entro il `2026-01-05`;
- nessun punteggio di selezione utilizza l'esito di gennaio 2026 o il movimento
  iniziato il 17 agosto 2026;
- vincoli pre-2026: nessun episodio breakout favorevole perso e nessun
  peggioramento di annualizzato, drawdown o Sharpe nei due sistemi analizzati;
- apertura del blocco 2026 soltanto dopo il congelamento della graduatoria;
- avvertenza metodologica: le famiglie slope SMA200, distanza SMA50/SMA200 e
  return 90g erano state individuate dopo aver osservato gennaio. Il replay e'
  cieco sulle soglie e sugli esiti 2026, ma non sulle feature iniziali.

Esito della selezione pre-2026:

- emerge al primo posto la sola distanza `SMA50/SMA200`;
- sei soglie, comprese tra `-14,5%` e `-17,0%`, sono perfettamente
  indistinguibili sul periodo di selezione;
- tutte conservano gli episodi favorevoli e riducono le perdite breakout
  aggregate pre-2026 da entrambe le varianti;
- il guardrail combinato `SMA200 slope20 > 0%` e `SMA50/SMA200 < -15%` e'
  ammissibile ma occupa il rank 33, perche' e' meno aggressivo e lascia vive
  piu' operazioni negative della variante RSI senza tetto.

Apertura del holdout 2026:

- soglie distanza `-14,5%`, `-15,0%`, `-15,5%` e `-16,0%` bloccano sia il 6
  sia il 13 gennaio;
- soglie `-16,5%` e `-17,0%`, equivalenti nel periodo di selezione, non
  bloccano gennaio;
- esito del gate per la classe cieca: `4/6` evitano gennaio;
- tutte le sei soglie (`6/6`) conservano l'ingresso del `2026-08-17`;
- il guardrail combinato evita entrambe le entrate di gennaio, conserva agosto
  e resta identico al candidato RSI 40-65 in tutto il periodo pre-2026.

Lettura:

- il replay conferma che la distanza eccessiva tra SMA50 e SMA200 contiene
  informazione utile gia' prima del caso gennaio 2026;
- non identifica pero' una soglia unica: selezionare `-15%` dopo aver aperto il
  2026 conserverebbe una componente di scelta a posteriori;
- il gate retrospettivo e' quindi superato soltanto in parte;
- la regola combinata e' preferita come shadow perche' blocca soltanto quando
  alla distanza profonda si aggiunge SMA200 ancora crescente, riducendo il
  rischio di eliminare recuperi validi.

Decisione congelata:

> Shadow breakout bloccato soltanto quando `SMA200Slope20 > 0%` e
> `SMA50VsSMA200 < -15%` sono vere contemporaneamente.

- stato: `shadow_frozen` dal `2026-08-23`;
- nessuna modifica a Baseline, bot, dashboard, entrate o uscite ufficiali;
- nessuna promozione immediata a Baseline;
- promozione riesaminabile alla prima nuova attivazione indipendente del
  guardrail, senza un'attesa prefissata in mesi;
- in quella occasione si dovra' registrare il breakout bloccato, il successivo
  andamento fino all'uscita che sarebbe stata applicata, il drawdown evitato o
  subito e il costo opportunita' rispetto all'ingresso non eseguito.

File:

- `scripts/run_january_2026_guardrail_blind_validation.py`;
- `reports/january_2026_guardrail_blind_validation.md`;
- `reports/january_2026_guardrail_blind_selection.csv`;
- `reports/january_2026_guardrail_blind_holdout.csv`;
- `reports/january_2026_guardrail_blind_periods.csv`;
- `reports/january_2026_guardrail_blind_trades.csv`;
- `reports/january_2026_guardrail_shadow_spec.json`.

## Follow-up 2026-08-28 - Rialzo ancora escluso dalla Baseline

Domanda:

- verificare perche' la Baseline non abbia ancora prodotto `ACQUISTA` durante
  il rialzo iniziato il 17 agosto;
- stabilire se il problema dipenda da `RSI <= 65`, da `SMA50 > SMA200` o
  dalla loro interazione;
- aggiornare il controllo del candidato breakout senza modificare i segnali
  operativi.

Dati:

- `ETH-USD` Coinbase daily UTC;
- ultima candela chiusa `2026-08-27`;
- costi maker `0,07%`, taker `0,16%` e stress `0,60%` per lato;
- regole di uscita ufficiali invariate.

Diagnosi:

- il 17 e 18 agosto RSI, momentum e volume erano validi, ma Close e SMA50
  erano ancora sotto SMA200;
- dal 19 agosto Close era sopra SMA200, ma RSI era gia' a `82,16` e SMA50
  restava sotto SMA200;
- le condizioni ufficiali non sono state vere insieme in alcuna candela;
- rimuovere soltanto il tetto RSI oppure soltanto il gate SMA50 non avrebbe
  prodotto un ingresso nel movimento;
- rimuovere entrambi avrebbe generato un ingresso tardivo il `2026-08-19` a
  `2.251,69 USD`, ma porta le operazioni storiche da 30 a 42 e peggiora il
  max drawdown da `-39,87%` a `-43,03%`.

Aggiornamento del candidato shadow protetto:

- ingresso breakout `2026-08-17` a `1.911,94 USD`;
- Close al cutoff `2.511,67 USD`;
- rendimento netto provvisorio taker `+31,16%`;
- massimo drawdown del trade `-3,73%`;
- posizione ancora aperta, nessuna uscita ufficiale o Trail8;
- il guardrail conserva agosto ed elimina il falso ingresso del
  `2026-01-13` chiuso a `-11,92%` senza protezione.

Confronto storico taker:

| Sistema | Annualizzato | Max DD | Sharpe | Profit factor | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline ufficiale | 97,23% | -39,87% | 1,664 | 15,995 | 30 |
| Breakout protetto | 129,30% | -36,56% | 1,903 | 19,020 | 32 |

Decisione:

- nessuna rimozione globale di RSI o SMA50 e nessun inseguimento tardivo del
  prezzo;
- Baseline, bot, dashboard e Telegram restano invariati;
- il percorso breakout protetto resta il candidato principale per risolvere
  questo tipo di movimento;
- l'esito del trade corrente rafforza il candidato ma non e' una validazione
  indipendente, poiche' agosto e' l'evento che ne ha motivato lo sviluppo;
- riesame alla chiusura del trade shadow con le uscite ufficiali oppure alla
  prima nuova attivazione indipendente;
- valutare come prossimo passo la visualizzazione separata dello stato shadow
  nella dashboard, senza promozione automatica ad `ACQUISTA`.

File:

- `reports/august_2026_missed_rally_followup.md`.

## Decisione 2026-08-28 - Promozione del breakout protetto

Decisione dell'utente:

- promuovere il candidato breakout protetto a secondo percorso ufficiale di
  ingresso;
- conservare integralmente il percorso standard;
- non modificare le due condizioni di vendita;
- non eseguire un acquisto retroattivo relativo al 17 agosto.

Nuova logica ufficiale:

> `ACQUISTA = percorso standard completo OR breakout protetto completo`.

Percorso standard, tutte vere:

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `40 <= RSI14 <= 65`;
4. `Close > Close.shift(7)`;
5. `Volume > VolumeAvg20`.

Breakout protetto, tutte vere:

1. `SMA50 <= SMA200`;
2. `Close > SMA50` e `Close >= SMA200 * 0,90`;
3. `SMA50 >= SMA50.shift(5)`;
4. `40 <= RSI14 <= 65`;
5. `Close > Close.shift(7)`;
6. `Volume >= VolumeAvg20 * 1,20`;
7. `Close` sopra il massimo dei cinque Close precedenti;
8. guardrail superato: non devono essere vere insieme slope SMA200 a 20
   giorni positiva e distanza SMA50/SMA200 inferiore a `-15%`.

Uscite confermate senza variazioni:

- `Close < SMA50 * 0,98`;
- Trail8 dal massimo Close post-ingresso, con momentum 7 giorni `>= -15%` e
  volume relativo `>= +20%`.

Risultati congelati al `2026-08-27`, costo prudenziale `0,60%` per lato:

| Metrica | Baseline v3 | Buy & Hold |
|---|---:|---:|
| Totale | +240.310,55% | +30.163,66% |
| Annualizzato | 122,70% | 79,95% |
| Max drawdown | -39,05% | -94,01% |
| Sharpe | 1,845 | 1,097 |
| Profit factor | 17,813 | n/a |
| Trade completati | 32 | n/a |

Separazione tra ricerca e operativita':

- il replay storico completo entra sul breakout del `2026-08-17` a
  `1.911,94 USD` e al cutoff mantiene il trade aperto;
- quel risultato rimane nel backtest per misurare la regola su tutta la serie;
- lo stato operativo riparte `FUORI`;
- il nuovo percorso e' abilitato dalle candele chiuse del `2026-08-28`;
- nessun segnale passato viene ricostruito come acquisto reale;
- il prossimo ingresso operativo richiede una nuova candela che completi uno
  dei due percorsi.

Implementazione:

- `strategy/signals.py`: secondo percorso, guardrail, data di attivazione e
  stato operativo senza backfill;
- `pipeline.py`: separazione tra replay storico e stato operativo;
- `reports/generate.py` e `reports/publication.py`: contratto dati v3;
- dashboard, Telegram, monitor orario e Cloudflare Worker: visualizzazione dei
  due percorsi e dello stato `DENTRO/FUORI`;
- test automatici dedicati ad attivazione, guardrail, messaggi e JSON;
- pacchetto congelato:
  `docs/runs/baseline-v3-2026-08-27/manifest.json`.

Reversibilita':

- le baseline v1 e v2 restano archiviate e immutabili;
- il dossier completo della decisione e' in
  `reports/breakout_official_promotion_2026-08-28.md`;
- ogni futura attivazione del breakout dovra essere registrata con ingresso,
  uscita, rendimento, drawdown e confronto con il percorso standard.

## Pubblicazione 2026-08-28 - Baseline v3 operativa

Versionamento e push:

- commit del modello: `b95ce23` - `Promuove il breakout protetto nella Baseline`;
- tag annotato pubblicato: `baseline-v3-2026-08-27`;
- integrati senza sovrascrittura i pacchetti automatici gia presenti sul
  remoto;
- commit del pacchetto operativo: `d77fc29` -
  `Pubblica pacchetto operativo Baseline v3`;
- branch remoto `master` allineato al pacchetto v3.

Pacchetto pubblico verificato:

- run operativo: `20260828T100344Z-600cfc99`;
- ultima candela chiusa: `2026-08-27`;
- azione DAILY e LIVE: `MANTIENI STATO ATTUALE`;
- stato operativo: `FUORI`;
- gruppi pubblicati: 5 condizioni standard, 8 breakout e 2 vendita;
- dashboard GitHub Pages caricata senza errori con metriche v3 e i due
  percorsi `ACQUISTA`;
- test CI e deploy GitHub Pages conclusi con successo sul commit `d77fc29`.

Telegram e Worker:

- Cloudflare Worker `eth-prudential-signal` pubblicato;
- Version ID: `b7c329dc-4c46-492f-8a63-3b65c37e7696`;
- `/live-preview`, `/subscribers/health` e `/subscribers/count` verificati con
  risposta HTTP 200;
- Supabase configurato sulla tabella `telegram_subscribers_eth`;
- conteggio al controllo: un iscritto attivo;
- il messaggio LIVE mostra azione, stato `DENTRO/FUORI`, cinque condizioni
  standard, otto breakout, due vendite e collegamento alla dashboard.
