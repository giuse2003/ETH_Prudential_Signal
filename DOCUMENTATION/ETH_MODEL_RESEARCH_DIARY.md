# ETH Model Research Diary

Ultimo aggiornamento: 2026-06-28

Questo file e' il diario operativo del lavoro sul miglioramento del modello
ETH Prudential Signal.

Nota cronologica:

- le sezioni iniziali riassumono lo stato ufficiale corrente dopo la
  promozione del 2026-06-28;
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

## Strategia Ufficiale Corrente

La strategia ufficiale corrente e' la Baseline prudenziale.

Segnale `ACQUISTA` quando tutte le condizioni sono vere:

- Close > SMA200;
- SMA50 > SMA200;
- RSI >= 40;
- Close > Close di 7 giorni prima;
- Volume > VolumeAvg20.

Segnale `VENDI` quando:

- Close < SMA50 per 2 giorni consecutivi.

`MANTIENI` conserva l'esposizione precedente.

Nota importante: gli esperimenti su trailing stop, ATR, RSI e filtri di
ingresso/uscita non sono regole operative ufficiali.

## Baseline Completa

Periodo dati completo disponibile nei segnali:

- inizio: 2017-11-11;
- ultima candela chiusa: 2026-06-27.

Metriche Baseline complete:

| Metrica | Valore |
|---|---:|
| Rendimento totale | +980,86% |
| Rendimento annualizzato | +31,76% |
| Max drawdown | -52,57% |
| Sharpe ratio | 0,849 |
| Profit factor | 4,327 |
| Operazioni chiuse | 28 |
| Win rate | 39,29% |
| Esposizione media | 28,75% |
| Turnover | 56 cambi esposizione |

Interpretazione:

- la Baseline batte Buy & Hold sul periodo completo;
- lo Sharpe resta sotto 1, quindi il rapporto rendimento/volatilita' va ancora
  migliorato;
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
  1. prezzo sotto SMA50 per 2 giorni consecutivi;
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
