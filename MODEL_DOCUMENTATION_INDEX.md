# Model Documentation Index

Ultimo aggiornamento: 2026-06-28

Questo file indica dove sono memorizzate le informazioni che riguardano la
costruzione, i test, le decisioni e lo stato ufficiale del modello ETH
Prudential Signal.

## Stato Ufficiale Corrente

- `README.md`: descrizione pubblica del progetto e regole operative correnti.
- `PROJECT_OVERVIEW.md`: documento tecnico generale per capire dati,
  indicatori, segnali, backtest, dashboard e Telegram.
- `PROJECT_STATUS.md`: stato operativo aggiornato del progetto.
- `reports/official_baseline_implementation.md`: report canonico della
  promozione della nuova Baseline ufficiale.

## Diario e Decisioni

- `ETH_MODEL_RESEARCH_DIARY.md`: diario cronologico completo delle analisi sul
  modello, incluse ipotesi, test, scarti, decisioni e allineamenti dashboard.
- `DECISION_LOG.md`: registro sintetico delle decisioni che modificano segnali
  o metriche.
- `MODEL_IMPROVEMENT_ROADMAP.md`: roadmap di miglioramento del modello, con
  storico dei test e riepilogo della Baseline promossa.
- `ETH_PROJECT_ROADMAP.md`: roadmap operativa del progetto, inclusi
  infrastruttura, dashboard, Telegram e documentazione.

## Report di Validazione

- `reports/final_promotion_gate.md`: gate finale che ha stabilito la
  promuovibilita' del candidato principale.
- `reports/final_combined_candidate_validation.md`: confronto finale tra
  Baseline precedente e candidato combinato.
- `reports/combined_walkforward_validation.md`: validazione cronologica e
  confronto con variante `trade return >= 15%`.
- `reports/residual_2023_exit_audit.md`: audit dell'unica uscita residua
  sottoperformante del 2023.
- `reports/signal_component_analysis.md`: separazione tra modelli di ingresso,
  uscita e combinazioni.

## Cronologia Sintetica

| Data | Fase | Dove leggere i dettagli |
|---|---|---|
| 2026-06-23 | Creazione progetto ETH, dashboard, primo backtest e correzione metriche copiate dal progetto BTC | `ETH_PROJECT_ROADMAP.md`, `PROJECT_OVERVIEW.md` |
| 2026-06-24 | Configurazione Worker Cloudflare, Telegram, Supabase e automazioni operative | `ETH_PROJECT_ROADMAP.md`, `PROJECT_STATUS.md`, `DECISION_LOG.md` |
| 2026-06-26 | Prime analisi di miglioramento: costi, qualita' trade, filtri ingresso, uscite protettive, stop e trailing | `MODEL_IMPROVEMENT_ROADMAP.md`, `reports/` |
| 2026-06-27 | Analisi trailing/ATR/RSI piu' avanzate e scarto delle varianti deboli o troppo complesse | `MODEL_IMPROVEMENT_ROADMAP.md`, `reports/` |
| 2026-06-28 | Analisi separata ingressi/uscite, validazione combinata, gate finale e promozione nuova Baseline ufficiale | `ETH_MODEL_RESEARCH_DIARY.md`, `reports/final_promotion_gate.md`, `reports/official_baseline_implementation.md`, `DECISION_LOG.md` |
| 2026-06-28 | Allineamento Telegram `/conditions`, dashboard, legenda RSI 40/65 e documentazione cronologica | `ETH_MODEL_RESEARCH_DIARY.md`, `README.md`, `PROJECT_OVERVIEW.md`, `PROJECT_STATUS.md` |

## Regole Ufficiali Del Modello

### Acquisto

Per generare `ACQUISTA` devono essere vere tutte le condizioni:

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `RSI(14) >= 40`;
4. `RSI(14) <= 65`;
5. `Close > Close_7d_ago`;
6. `Volume > VolumeAvg20`.

Nota: `RSI <= 65` filtra solo nuovi ingressi e non forza la vendita di una
posizione gia' aperta.

### Vendita

Per generare `VENDI` deve essere vera almeno una condizione:

1. `Close < SMA50` per 2 giorni consecutivi;
2. trailing stop 8% dal massimo `Close` post-ingresso, confermato da:
   - momentum 7 giorni >= -5%;
   - volume relativo >= +20% rispetto alla media 20 giorni.

## Regole Non Promosse

Restano documentate ma non operative:

- `trade return >= 15%` come ulteriore conferma del trailing;
- `momentum >= -6%`;
- `RSI <= 62`;
- volume relativo `+10%`;
- trailing dinamico 15%/8%;
- trailing stop puro senza conferma momentum/volume;
- stop loss fisso da ingresso.

## Principio Di Reversibilita'

Ogni modifica al modello deve lasciare traccia in almeno uno di questi file:

- diario cronologico: `ETH_MODEL_RESEARCH_DIARY.md`;
- decisione sintetica: `DECISION_LOG.md`;
- report tecnico in `reports/`;
- stato corrente: `PROJECT_STATUS.md`;
- se diventa ufficiale, anche `README.md` e `PROJECT_OVERVIEW.md`.
