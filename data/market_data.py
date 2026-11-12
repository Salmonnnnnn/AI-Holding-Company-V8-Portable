"""
Multi-Timeframe Market Data Engine for Gold (XAUUSD / GC=F) and Macro Indicators (DXY, 10Y Yield)
Supports Daily (D1) Major Structure and Hourly (H1) Intraday Execution + Quantitative Indicators.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / (loss + 1e-9)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return float(rsi.iloc[-1])


def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    val = atr.iloc[-1]
    if pd.isna(val) or val <= 0:
        val = float(high_low.tail(period).mean())
    return float(val)


def calculate_macd(series: pd.Series) -> dict:
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    hist = macd_line - signal_line
    macd_val = round(float(macd_line.iloc[-1]), 2)
    sig_val = round(float(signal_line.iloc[-1]), 2)
    hist_val = round(float(hist.iloc[-1]), 2)
    prev_hist = round(float(hist.iloc[-2]), 2) if len(hist) > 1 else hist_val
    momentum = "BULLISH_EXPANDING" if hist_val > 0 and hist_val >= prev_hist else (
        "BULLISH_WEAKENING" if hist_val > 0 else (
            "BEARISH_EXPANDING" if hist_val < 0 and hist_val <= prev_hist else "BEARISH_WEAKENING"
        )
    )
    return {
        "macd": macd_val,
        "signal": sig_val,
        "histogram": hist_val,
        "state": "BULLISH" if macd_val > sig_val else "BEARISH",
        "momentum": momentum
    }


def calculate_bollinger(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> dict:
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    u_val = round(float(upper.iloc[-1]), 2) if not pd.isna(upper.iloc[-1]) else round(float(series.iloc[-1]) * 1.01, 2)
    m_val = round(float(sma.iloc[-1]), 2) if not pd.isna(sma.iloc[-1]) else round(float(series.iloc[-1]), 2)
    l_val = round(float(lower.iloc[-1]), 2) if not pd.isna(lower.iloc[-1]) else round(float(series.iloc[-1]) * 0.99, 2)
    return {
        "upper": u_val,
        "middle": m_val,
        "lower": l_val
    }


class MarketDataEngine:
    def __init__(self, symbol: str = "GC=F"):
        self.gold_symbol = symbol
        self.last_h1_df = None
        self.last_d1_df = None

    def get_market_snapshot(self) -> dict:
        """ดึงข้อมูลราคาและตัวชี้วัดทางเทคนิคแบบ Multi-Timeframe (D1 + H1) และข้อมูลเศรษฐกิจมหภาค"""
        try:
            gold_ticker = yf.Ticker(self.gold_symbol)
            d1_hist = gold_ticker.history(period="3mo", interval="1d")
            h1_hist = gold_ticker.history(period="1mo", interval="1h")

            if d1_hist.empty or len(d1_hist) < 20:
                gold_ticker = yf.Ticker("XAUUSD=X")
                d1_hist = gold_ticker.history(period="3mo", interval="1d")
                h1_hist = gold_ticker.history(period="1mo", interval="1h")

            if d1_hist.empty:
                logger.warning("Live data unavailable, using simulated real-market snapshot.")
                return self._get_fallback_data()

            self.last_d1_df = d1_hist.copy()
            self.last_h1_df = h1_hist.copy() if not h1_hist.empty and len(h1_hist) >= 30 else d1_hist.copy()

            current_price = round(float(self.last_h1_df['Close'].iloc[-1]), 2)
            prev_d1_close = round(float(d1_hist['Close'].iloc[-2]), 2)
            change_pct = round(((current_price - prev_d1_close) / prev_d1_close) * 100, 2)

            # คำนวณ Indicators บน D1 (Major Trend)
            d1_ema20 = round(float(d1_hist['Close'].ewm(span=20, adjust=False).mean().iloc[-1]), 2)
            d1_ema50 = round(float(d1_hist['Close'].ewm(span=50, adjust=False).mean().iloc[-1]), 2)
            d1_rsi = round(calculate_rsi(d1_hist['Close']), 2)
            d1_atr = round(calculate_atr(d1_hist), 2)
            d1_trend = "BULLISH" if current_price > d1_ema20 and d1_ema20 > d1_ema50 else (
                "BEARISH" if current_price < d1_ema20 and d1_ema20 < d1_ema50 else "SIDEWAY"
            )

            # คำนวณ Indicators บน H1 (Intraday Execution)
            h1_df = self.last_h1_df
            h1_ema20 = round(float(h1_df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]), 2)
            h1_ema50 = round(float(h1_df['Close'].ewm(span=50, adjust=False).mean().iloc[-1]), 2)
            h1_ema200 = round(float(h1_df['Close'].ewm(span=200, adjust=False).mean().iloc[-1]), 2)
            h1_rsi = round(calculate_rsi(h1_df['Close']), 2)
            h1_atr = round(calculate_atr(h1_df), 2)
            # ป้องกันกรณี H1 Fallback ไปใช้ D1 แล้ว ATR ใหญ่เกินไปสำหรับ Intraday
            if h1_hist.empty or len(h1_hist) < 30:
                h1_atr = round(d1_atr * 0.25, 2)

            h1_macd = calculate_macd(h1_df['Close'])
            h1_bb = calculate_bollinger(h1_df['Close'])
            h1_trend = "BULLISH" if current_price > h1_ema20 and h1_ema20 > h1_ema50 else (
                "BEARISH" if current_price < h1_ema20 and h1_ema20 < h1_ema50 else "SIDEWAY"
            )

            # แนวรับแนวต้าน Intraday (H1 - 48 แท่งล่าสุด ~ 2 วันทำการ) และ Major (D1 - 10 วัน)
            h1_recent = h1_df.tail(48)
            intraday_support = round(float(h1_recent['Low'].min()), 2)
            intraday_resistance = round(float(h1_recent['High'].max()), 2)

            major_support = round(float(d1_hist['Low'].tail(10).min()), 2)
            major_resistance = round(float(d1_hist['High'].tail(10).max()), 2)

            # คำนวณ Fibonacci Retracement จาก Swing ล่าสุดบน H1
            swing_range = max(intraday_resistance - intraday_support, 1.0)
            fib_382 = round(intraday_resistance - (swing_range * 0.382), 2)
            fib_500 = round(intraday_resistance - (swing_range * 0.500), 2)
            fib_618 = round(intraday_resistance - (swing_range * 0.618), 2)

            # ข้อมูล Macro: DXY และ Bond Yield
            macro_info = self._get_macro_snapshot()

            return {
                "symbol": "XAUUSD / Gold",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "current_price": current_price,
                "change_pct": change_pct,
                # Legacy compatibility keys (mapped to H1/D1 appropriately)
                "ema20": h1_ema20,
                "ema50": h1_ema50,
                "ema200": h1_ema200,
                "trend": h1_trend,
                "d1_trend": d1_trend,
                "d1_ema20": d1_ema20,
                "d1_ema50": d1_ema50,
                "d1_rsi": d1_rsi,
                "d1_atr": d1_atr,
                "rsi14": h1_rsi,
                "atr14": h1_atr,
                "macd": h1_macd,
                "bollinger": h1_bb,
                "support": intraday_support,
                "resistance": intraday_resistance,
                "major_support": major_support,
                "major_resistance": major_resistance,
                "fib_levels": {
                    "fib_382": fib_382,
                    "fib_500": fib_500,
                    "fib_618": fib_618
                },
                "dxy_index": macro_info["dxy"],
                "dxy_change_pct": macro_info["dxy_change_pct"],
                "us10y_yield": macro_info["us10y"],
                "us10y_change_pct": macro_info["us10y_change_pct"],
                "source": "Yahoo Finance Multi-Timeframe (Live D1 + H1)"
            }
        except Exception as e:
            logger.error(f"Error fetching live data: {e}. Falling back to default data.")
            return self._get_fallback_data()

    def _get_macro_snapshot(self) -> dict:
        dxy = 104.20
        dxy_change = 0.05
        yield_10y = 4.35
        yield_change = 0.02
        try:
            dxy_ticker = yf.Ticker("DX-Y.NYB")
            dxy_hist = dxy_ticker.history(period="5d", interval="1d")
            if not dxy_hist.empty:
                dxy = round(float(dxy_hist['Close'].iloc[-1]), 2)
                if len(dxy_hist) > 1:
                    prev = float(dxy_hist['Close'].iloc[-2])
                    dxy_change = round(((dxy - prev) / prev) * 100, 2)
        except Exception:
            pass

        try:
            tnx_ticker = yf.Ticker("^TNX")
            tnx_hist = tnx_ticker.history(period="5d", interval="1d")
            if not tnx_hist.empty:
                raw_tnx = float(tnx_hist['Close'].iloc[-1])
                # ^TNX on Yahoo Finance is quoted as 43.5 for 4.35% or 4.35 directly
                yield_10y = round(raw_tnx / 10.0, 2) if raw_tnx > 15.0 else round(raw_tnx, 2)
                if len(tnx_hist) > 1:
                    prev_raw = float(tnx_hist['Close'].iloc[-2])
                    prev_y = prev_raw / 10.0 if prev_raw > 15.0 else prev_raw
                    yield_change = round(((yield_10y - prev_y) / prev_y) * 100, 2)
        except Exception:
            pass

        return {
            "dxy": dxy,
            "dxy_change_pct": dxy_change,
            "us10y": yield_10y,
            "us10y_change_pct": yield_change
        }

    def _get_fallback_data(self) -> dict:
        return {
            "symbol": "XAUUSD / Gold",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_price": 2685.50,
            "change_pct": 0.45,
            "ema20": 2680.10,
            "ema50": 2672.30,
            "ema200": 2650.00,
            "trend": "BULLISH",
            "d1_trend": "BULLISH",
            "d1_ema20": 2665.00,
            "d1_ema50": 2630.00,
            "d1_rsi": 58.4,
            "d1_atr": 32.0,
            "rsi14": 56.2,
            "atr14": 8.50,
            "macd": {
                "macd": 2.45,
                "signal": 1.80,
                "histogram": 0.65,
                "state": "BULLISH",
                "momentum": "BULLISH_EXPANDING"
            },
            "bollinger": {
                "upper": 2698.00,
                "middle": 2680.00,
                "lower": 2662.00
            },
            "support": 2668.00,
            "resistance": 2702.00,
            "major_support": 2640.00,
            "major_resistance": 2725.00,
            "fib_levels": {
                "fib_382": 2689.00,
                "fib_500": 2685.00,
                "fib_618": 2681.00
            },
            "dxy_index": 104.15,
            "dxy_change_pct": -0.18,
            "us10y_yield": 4.32,
            "us10y_change_pct": -0.25,
            "source": "Snapshot Data (Resilient Multi-TF Fallback)"
        }


if __name__ == "__main__":
    engine = MarketDataEngine()
    data = engine.get_market_snapshot()
    print("Market Snapshot:", data)
