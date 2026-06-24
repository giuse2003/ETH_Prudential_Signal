# ETH Model Improvement Roadmap

Ultimo aggiornamento: 2026-06-24

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
- risultato: `55` test eseguiti, `OK`.

Copertura rilevante:

- esclusione della candela giornaliera corrente;
- gestione indici con e senza timezone;
- annualizzazione crypto su `365` giorni;
- conteggio dei soli trade completati;
- esclusione delle posizioni ancora aperte dal win rate;
- regole `ACQUISTA`, `MANTIENI`, `VENDI`;
- salvataggio `backtest.json`;
- allineamento backtest dalla prima data comune reale `ETH-USD` / `ETH-EUR`.

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

## Test Da Fare

### 1. Costi operativi

Obiettivo: trasformare il backtest da lordo a piu' realistico.

Test:

- commissioni 0,10% per operazione;
- commissioni 0,25% per operazione;
- spread/slippage 0,10%;
- spread/slippage 0,25%;
- scenario stress: commissioni + slippage 0,50% complessivo.

Metriche da confrontare:

- rendimento annualizzato;
- max drawdown;
- Sharpe Ratio;
- profit factor;
- numero operazioni.

### 2. Profit factor e qualita' trade

Obiettivo: rendere visibile se la strategia vince per robustezza o per pochi
eventi estremi.

Test:

- profit factor;
- rendimento medio trade vincente;
- perdita media trade perdente;
- trade migliore e trade peggiore;
- durata media e mediana dei trade;
- distribuzione dei rendimenti per trade.

### 3. Filtri volatilita'

Obiettivo: aumentare lo Sharpe riducendo entrate in fasi troppo instabili.

Varianti da testare:

- evitare `ACQUISTA` se ATR percentuale e' sopra una soglia;
- evitare `ACQUISTA` se volatilita' rolling 20 giorni e' sopra una soglia;
- ridurre esposizione quando ATR aumenta rapidamente;
- confrontare ATR su 14, 20 e 30 giorni.

Soglie iniziali:

- ATR / Close > 5%;
- ATR / Close > 7%;
- volatilita' rolling 20 giorni sopra percentile 75;
- volatilita' rolling 20 giorni sopra percentile 85.

### 4. Trend filter piu' selettivo

Obiettivo: ridurre falsi ingressi e migliorare Sharpe.

Varianti da testare:

- `SMA200` crescente negli ultimi 10 giorni;
- `SMA200` crescente negli ultimi 20 giorni;
- `SMA50` crescente negli ultimi 5 o 10 giorni;
- prezzo sopra `SMA200` con margine minimo del 2%;
- prezzo sopra `SMA200` con margine minimo del 5%.

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

Varianti:

- trailing stop sotto massimo a 10 giorni;
- trailing stop sotto massimo a 20 giorni;
- uscita se prezzo sotto `SMA50` per 1 giorno;
- uscita se prezzo sotto `SMA50` per 2 giorni, regola attuale;
- uscita se RSI scende sotto 35;
- uscita se Close perde piu' del 10% dall'ingresso.

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

Test:

- backtest per sottoperiodi annuali;
- bull market vs bear market;
- walk-forward semplice;
- train/test split temporale;
- confronto pre-2021, 2021-2022, post-2022.

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

- aggiungere costi, slippage e profit factor al motore di backtest;
- salvare le nuove metriche in `backtest.json`;
- mostrare almeno profit factor e periodo backtest in dashboard.

Priorita' 2:

- testare filtro volatilita' ATR / Close;
- testare `SMA200` crescente;
- confrontare le varianti contro la baseline in una tabella unica.

Priorita' 3:

- introdurre esposizione 50% / 100%;
- testare uscite dinamiche;
- fare walk-forward per controllare overfitting.
