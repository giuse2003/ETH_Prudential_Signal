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

Costruire una tabella di tutte le entrate dal 2022 al 2026-06-27 con:

- indicatori al momento dell'ingresso;
- esito del trade;
- drawdown interno;
- durata;
- confronto fra entrate vincenti e perdenti.

Obiettivo:

- identificare il primo filtro di ingresso davvero testabile;
- ridurre il win rate basso della Baseline;
- migliorare lo Sharpe senza peggiorare la capacita' di protezione del modello.
