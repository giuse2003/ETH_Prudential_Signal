# ETH Model Research Diary

Ultimo aggiornamento: 2026-06-28

Questo file e' il diario operativo del lavoro sul miglioramento del modello
ETH Prudential Signal.

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
