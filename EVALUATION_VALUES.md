# Valutazione baseline ETH-USD v1

Fonte canonica: `docs/runs/baseline-v1-2026-07-26/manifest.json`.

- storico Coinbase continuo: `2016-05-23`–`2026-07-26`;
- warm-up: fino al `2016-12-07`;
- valutazione: `2016-12-08`–`2026-07-26`;
- osservazioni e giorni di calendario: `3518`;
- strategia: rendimento totale `186.63524277301624`, annualizzato
  `0.7215842468567129`, max drawdown `-0.45887949067964284`, Sharpe
  `1.3573838337263227`, 36 trade completati, win rate
  `0.3611111111111111`, profit factor `14.00916695086703`;
- Buy & Hold: rendimento totale `237.16219512195124`, annualizzato
  `0.7647197288654111`, max drawdown `-0.940116304238034`, Sharpe
  `1.0755007254180986`.

La strategia riduce fortemente il drawdown e migliora lo Sharpe rispetto al Buy
& Hold, ma nel periodo completo ottiene un rendimento totale e annualizzato
inferiore. Il basso win rate e compensato da pochi trade vincenti molto ampi;
questo rende importante non interpretare il profit factor storico come garanzia
futura.

Costi, spread, slippage, imposte e rendimento della liquidita non sono inclusi.
Non esiste un vero out-of-sample separato. I risultati possono riflettere
overfitting e dipendono dall'integrita dello storico Coinbase.
