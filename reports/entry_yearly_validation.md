# Entry Yearly Validation

Periodo: `2017-11-11` -> `2026-06-27`.

Confronto solo sugli ingressi: Baseline ufficiale vs Baseline + filtro `RSI <= 65`.
L'uscita resta invariata: `VENDI` sotto SMA50 per 2 giorni consecutivi.

## Tabella Annuale

| Anno | Baseline Ret | RSI65 Ret | Delta Ret | Baseline DD | RSI65 DD | Delta DD | Baseline Sharpe | RSI65 Sharpe | Entry B/R | Chiusi B/R | Delta chiusi |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a | 0/0 | 0/0 | 0 |
| 2018 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a | 0/0 | 0/0 | 0 |
| 2019 | 60.32% | 60.32% | 0.00% | -19.32% | -19.32% | 0.00% | 1.316 | 1.316 | 1/1 | 1/1 | 0 |
| 2020 | 69.85% | 136.42% | 66.57% | -38.20% | -29.21% | 8.99% | 1.205 | 1.930 | 5/4 | 4/3 | -1 |
| 2021 | 201.42% | 201.42% | 0.00% | -45.09% | -45.09% | 0.00% | 1.719 | 1.719 | 5/5 | 6/6 | 0 |
| 2022 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a | 0/0 | 0/0 | 0 |
| 2023 | 0.09% | 0.09% | -0.00% | -22.67% | -22.67% | -0.00% | 0.148 | 0.148 | 6/6 | 5/5 | 0 |
| 2024 | -14.58% | -10.22% | 4.36% | -47.85% | -45.19% | 2.66% | -0.230 | -0.130 | 7/7 | 8/8 | 0 |
| 2025 | 35.98% | 35.98% | -0.00% | -26.08% | -26.08% | -0.00% | 1.046 | 1.046 | 4/4 | 4/4 | 0 |
| 2026 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | n/a | n/a | 0/0 | 0/0 | 0 |

## Lettura

- Anni in cui cambia il numero di operazioni: 2020.
- Anni in cui cambia il rendimento in modo reale: 2020, 2024.
- Anni con rendimento RSI65 migliore della Baseline: 2.
- Anni con rendimento RSI65 peggiore della Baseline: 0.
- Anni con drawdown annuale meno profondo usando RSI65: 2.
- `Entry B/R` significa ingressi Baseline / ingressi RSI65 nello stesso anno.
- `Chiusi B/R` significa trade chiusi Baseline / trade chiusi RSI65 nello stesso anno.
- Delta DD positivo significa drawdown meno negativo, quindi miglioramento.
