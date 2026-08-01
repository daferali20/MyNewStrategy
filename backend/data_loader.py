import yfinance as yf
import pandas as pd

class DataLoader:
    @staticmethod
    def get_stock_data(ticker: str, period: str = "6mo") -> pd.DataFrame:
        """جلب بيانات السهم من yfinance بشكل آمن"""
        try:
            df = yf.Ticker(ticker).history(period=period)
            if df.empty:
                return pd.DataFrame()
            return df
        except Exception as e:
            print(f"⚠️ خطأ في جلب بيانات {ticker}: {e}")
            return pd.DataFrame()
