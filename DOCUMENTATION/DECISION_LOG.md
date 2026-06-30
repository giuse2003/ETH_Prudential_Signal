# Decision Log

Registro sintetico delle decisioni che influenzano segnali e metriche.

## 2026-06-30 - Decisione su uscita SMA50 a 1 giorno

**Decisione:** accettare il compromesso e promuovere come nuova regola di
uscita ufficiale:

- `Close < SMA50` gia' dopo 1 giorno;
- resta invariato il trailing stop 8% confermato da momentum e volume;
- restano invariati tutti i criteri di acquisto.

**Regola sostituita:** `Close < SMA50` per 2 giorni consecutivi.

**Motivo specifico della decisione:** la scelta e' stata presa per privilegiare
la protezione del capitale acquisito e la riduzione del drawdown, anche
accettando alcuni falsi stop storici. Il candidato migliora le metriche
aggregate piu' rilevanti sull'intero periodo testato:

- rendimento annualizzato: 47,94% vs 43,58%;
- max drawdown: -40,97% vs -44,93%;
- Sharpe: 1,179 vs 1,084;
- profit factor: 7,117 vs 5,889;
- stress costi superato in tutti gli scenari testati;
- segmenti modificati: 16 migliorano, 8 peggiorano.

**Compromesso accettato:** il rendimento annuale non migliora in modo uniforme:
negli anni attivi il candidato migliora 3 anni e peggiora 3 anni. In
particolare il 2019-2020 resta il punto debole storico. Il compromesso viene
accettato perche' il miglioramento complessivo su drawdown, Sharpe, profit
factor, costi e periodo recente 2023-2025 e' ritenuto piu' importante della
maggiore stabilita' della vecchia conferma a 2 giorni.

**Varianti non promosse:** nessuna conferma aggiuntiva testata sopra
`Close < SMA50` a 1 giorno viene promossa. In particolare:

- filtro rottura almeno -1%: piu' prudente ma meno efficiente;
- volume relativo >= -10%: leggero vantaggio su rendimento e profit factor, ma
  non migliora lo Sharpe rispetto alla regola pura;
- filtri su RSI, momentum, distanza SMA50, candela rossa e combinazioni: utili
  come storico, ma non superiori alla regola pura.

**Stato operativo:** decisione approvata, registrata agli atti e implementata
come nuova regola ufficiale della Baseline. Calcolo segnali, report,
dashboard, messaggi Telegram e documentazione corrente devono restare
allineati a questa regola.

**Riferimenti:** `ETH_MODEL_RESEARCH_DIARY.md`,
`reports/sma50_one_day_promotion_gate.md`,
`reports/sma50_exit_confirmation_grid.md`,
`reports/sma50_exit_timing_audit.md`.

## 2026-06-28 - Promozione nuova Baseline ufficiale

**Decisione:** promuovere il candidato combinato a nuova Baseline ufficiale
del modello ETH.

**Regole ufficiali di acquisto:**

- `Close > SMA200`;
- `SMA50 > SMA200`;
- `RSI(14) >= 40`;
- `RSI(14) <= 65` solo sui nuovi ingressi;
- `Close > Close_7d_ago`;
- `Volume > VolumeAvg20`.

**Regole ufficiali di vendita:**

- `Close < SMA50` per 2 giorni consecutivi;
- oppure trailing stop 8% dal massimo `Close` post-ingresso, confermato da:
  - momentum 7 giorni >= -5%;
  - volume relativo >= +20% rispetto alla media 20 giorni.

**Decisioni collegate:**

- `RSI <= 65` non e' una regola di uscita: se la posizione e' gia' aperta,
  il superamento di RSI 65 non vende da solo.
- La variante `trade return >= 15%` non viene promossa per rischio overfit su
  un solo evento.
- Le varianti `momentum -6%`, `RSI <= 62`, `volume +10%` e trailing dinamico
  15%/8% restano storiche/sperimentali, non operative.

**Motivazione:** il candidato combinato migliora rendimento annualizzato,
drawdown, Sharpe e profit factor rispetto alla Baseline precedente, mantenendo
regole semplici e verificabili.

**Riferimenti:** `ETH_MODEL_RESEARCH_DIARY.md`,
`reports/final_promotion_gate.md`,
`reports/official_baseline_implementation.md`.

## 2026-06-11 - Iscrizione visibile nella dashboard

**Decisione:** aggiungere alla dashboard pubblica una card Telegram con deep
link e numero aggregato degli iscritti attivi.

**Impatto:**

- il link pubblico usa `@ETH_Prudential_Signal_bot`;
- `/start iscrivimi` viene trattato come `/iscrivimi`;
- `GET /subscribers/count` conta server-side soltanto le righe attive;
- nessun dato personale viene restituito dal nuovo endpoint;
- la dashboard mostra un fallback neutro se Render non risponde;
- CORS accetta soltanto GitHub Pages e gli indirizzi locali di sviluppo;
- nessun secret Supabase o Telegram e presente nel frontend.

## 2026-06-10 - Iscrizioni Telegram persistenti

**Decisione:** consentire l'uso del bot in ogni chat privata e memorizzare le
iscrizioni in Supabase.

**Impatto:**

- `/iscrivimi` crea o riattiva l'iscrizione senza duplicati;
- `/disiscrivimi` disattiva gli invii senza cancellare la registrazione;
- `/privacy` descrive i dati conservati;
- gruppi e supergruppi vengono ignorati;
- il numero di cellulare non viene richiesto;
- la service role resta nelle variabili protette del backend;
- la notifica collettiva al cambio segnale o rischio resta nella Fase 4.

## 2026-06-09 - Webhook Render attivato

**Stato:** operativo e verificato.

**Configurazione:**

- servizio pubblico:
  `https://eth-prudential-signal.onrender.com`;
- endpoint Telegram:
  `https://eth-prudential-signal.onrender.com/webhook`;
- health check verificato con `{"status":"ok"}`;
- registrazione Telegram verificata tramite `getWebhookInfo`;
- `/segnale` verificato con risposta immediata.

**Decisione operativa:**

- mantenere attivo `Hourly ETH monitor (Telegram)`;
- mantenere disabilitato `Telegram command listener`;
- usare il listener `getUpdates` soltanto come fallback dopo aver eseguito
  `deleteWebhook`.

## 2026-06-09 - Webhook Telegram FastAPI

**Decisione:** aggiungere un servizio FastAPI separato, distribuibile su
Render, per ricevere direttamente gli update Telegram.

**Motivazione:** eliminare la latenza dello scheduler GitHub Actions senza
spostare o modificare il calcolo dei segnali.

**Impatto:**

- `POST /webhook` gestisce `/segnale`, `/start` e `/help`;
- ogni `/segnale` scarica il JSON dal GitHub Raw URL pubblico;
- nessun database, copia locale o autenticazione GitHub;
- accesso limitato a `TELEGRAM_CHAT_ID`;
- supporto opzionale a `TELEGRAM_WEBHOOK_SECRET`;
- il listener `getUpdates` resta come fallback, ma deve essere disabilitato
  mentre il webhook e registrato.

## 2026-06-09 - Comando Telegram `/segnale`

**Decisione:** aggiungere un listener GitHub Actions separato che controlla
Telegram ogni 5 minuti.

**Motivazione:** permettere la richiesta manuale del segnale direttamente
dalla chat senza avviare il workflow dal sito GitHub.

**Impatto:**

- `/segnale` restituisce segnale, rischio, prezzo EUR live e indicazione;
- `/start` e `/help` mostrano il comando disponibile;
- rispondono soltanto i messaggi provenienti da `TELEGRAM_CHAT_ID`;
- la risposta puo essere ritardata dallo scheduler GitHub Actions;
- non e richiesto un server esterno sempre attivo.

## 2026-06-09 - Notifica Telegram essenziale

**Decisione:** mostrare nella notifica soltanto il prezzo ETH in euro ed
eliminare la sezione `Sintesi`.

**Motivazione:** il doppio prezzo e il riepilogo tecnico rendevano il messaggio
meno immediato.

**Impatto:**

- nessun prezzo USD nel messaggio Telegram;
- restano segnale, rischio, prezzo EUR e indicazione;
- il prezzo storico `ETH-EUR` viene usato se Coinbase non e disponibile.
- l'avvio manuale del workflow invia lo stesso formato dei cambi di segnale,
  senza aggiornare lo stato delle notifiche automatiche.

## 2026-06-08 - Calendario crypto a 365 giorni

**Decisione:** usare `365` periodi annui per Ethereum.

**Motivazione:** Ethereum viene negoziato tutti i giorni; il calendario
tradizionale da 252 sedute sottostima la finestra annuale e altera rendimento
annualizzato e Sharpe Ratio.

**Impatto:**

- `CFG.periods_per_year = 365`;
- finestra 52 settimane pari a 365 osservazioni;
- annualizzazione e Sharpe basati su 365 periodi.

## 2026-06-08 - Segnali solo su candele concluse

**Decisione:** escludere sempre la candela giornaliera UTC corrente.

**Motivazione:** durante il giorno prezzo, volume e indicatori della candela
sono incompleti e possono produrre cambi di segnale non confermati.

**Impatto:**

- funzione condivisa `keep_closed_daily_candles`;
- comportamento coerente tra analisi locale e monitor GitHub Actions;
- prezzo spot Coinbase resta live, ma non entra nel calcolo del segnale
  giornaliero.

## 2026-06-08 - Operazione definita come trade chiuso

**Decisione:** contare come operazione soltanto una sequenza completa di
entrata long e successiva uscita.

**Motivazione:** contare ogni variazione di esposizione mescolava ingressi e
uscite, producendo un denominatore incoerente per il win rate.

**Impatto:**

- `num_operations` rappresenta i trade completati;
- `win_rate` e il rapporto tra trade chiusi positivi e trade chiusi totali;
- una posizione aperta a fine backtest resta esclusa da entrambe le metriche.

## Decisioni rinviate

- Costi di transazione, spread e slippage.
- Versionamento bloccato delle dipendenze.
- Revisione generale di manutenibilita, workflow e duplicazione frontend.
