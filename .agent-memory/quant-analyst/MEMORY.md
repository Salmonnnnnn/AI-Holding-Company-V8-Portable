# 📈 Quantitative Analyst & Trading Memory

## 📊 Market Model & Instrument
- **Primary Asset**: Gold (`XAUUSD` / `GC=F`)
- **Correlations**: US Dollar Index (`DX-Y.NYB`), US 10-Year Treasury Yield (`^TNX`)
- **Timeframes**: Multi-Timeframe Analysis (`D1` Trend, `H4` Structure, `H1` Entry)

## 🤖 Committee Specialist Agents (`agents/`)
- `technical_agent.py`: EMA (20/50/200), RSI (14), ATR (14), Support/Resistance pivots.
- `macro_agent.py`: DXY inverted correlation, Fed interest rate sentiment, geopolitical risk score.
- `debate_agent.py`: Bull vs Bear adversarial synthesis.
- `risk_agent.py`: Fractional Kelly Criterion sizing, volatility veto, maximum drawdown circuit breaker.
- `cio_agent.py`: Chief Investment Officer final consensus decision (`STRONG_BUY`, `BUY`, `NEUTRAL`, `SELL`, `STRONG_SELL`).

## ⚙️ Sizing & Risk Formulae
- **Kelly Sizing**: `f* = (p * b - q) / b`, scaled by conservative fraction (typically 0.20 - 0.25).
- **Max Stop Loss**: 1.5% - 2.0% equity risk per trade based on 2x ATR.
- **Circuit Breaker**: If 3 consecutive losses occur or market volatility > 3.5σ, position sizing reduces by 50%.
