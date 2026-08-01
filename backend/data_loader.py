# backend/data_loader.py
"""
وحدة جلب بيانات السوق والأسهم (Market Data Loader Module)
تتحكم في جلب البيانات من Yahoo Finance وتنظيفها وتجهيزها للمعالجة الفنية
"""

from typing import Dict, Any, Optional
import functools
import pandas as pd
import yfinance as yf


class DataLoader:
    """كلاس متكامل لجلب وتجهيز بيانات الأسهم والمؤشرات المالية"""

    @staticmethod
    def get_stock_data(
        ticker: str, period: str = "6mo", interval: str = "1d"
    ) -> pd.DataFrame:
        """جلب بيانات السهم التاريخية وتنظيفها بشكل آمن

        Args:
            ticker (str): رمز السهم (مثال: 'AAPL', 'NVDA')
            period (str): الفترة الزمنية (مثال: '1mo', '6mo', '1y')
            interval (str): فاصل الشموع (مثال: '1d', '1wk')

        Returns:
            pd.DataFrame: جدول يحتوي على الأعمدة النمطية [open, high, low, close, volume]
        """
        if not ticker or not isinstance(ticker, str):
            return pd.DataFrame()

        clean_ticker = ticker.strip().upper()

        try:
            stock = yf.Ticker(clean_ticker)
            df = stock.history(period=period, interval=interval)

            if df is None or df.empty:
                print(f"⚠️ لا توجد بيانات متاحة للرمز: {clean_ticker}")
                return pd.DataFrame()

            # 1. التخلص من أسماء الأعمدة المتعددة المستويات (MultiIndex) إن وجدت
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # 2. توحيد أسماء الأعمدة للحروف الصغيرة النمطية
            df = df.rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                    "Adj Close": "adj_close",
                }
            )

            # 3. التأكد من وجود الأعمدة الفنية المطلوبة
            required_cols = ["open", "high", "low", "close", "volume"]
            for col in required_cols:
                if col not in df.columns:
                    print(
                        f"⚠️ العمود المطلوب '{col}' غير متوفر لـ {clean_ticker}"
                    )
                    return pd.DataFrame()

            # 4. تنظيف البيانات من القيم المفقودة والتأكد من ترتيب التاريخ
            df = df[required_cols].dropna()
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)

            return df

        except Exception as e:
            print(f"⚠️ خطأ في جلب بيانات السهم {clean_ticker}: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_stock_info(ticker: str) -> Dict[str, Any]:
        """جلب البيانات الأساسية للشركة (القطاع، القيمة السوقية، الاسم)

        Args:
            ticker (str): رمز السهم

        Returns:
            dict: قاموس يحتوي على تفاصيل الشركة الأساسية
        """
        if not ticker or not isinstance(ticker, str):
            return {}

        clean_ticker = ticker.strip().upper()

        try:
            stock = yf.Ticker(clean_ticker)
            info = stock.info

            if not info or not isinstance(info, dict):
                return {"symbol": clean_ticker, "name": clean_ticker}

            return {
                "symbol": clean_ticker,
                "name": info.get("shortName")
                or info.get("longName")
                or clean_ticker,
                "sector": info.get("sector", "غير محدد"),
                "industry": info.get("industry", "غير محدد"),
                "market_cap": info.get("marketCap", 0),
                "currency": info.get("currency", "USD"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", 0.0),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow", 0.0),
            }

        except Exception as e:
            print(f"⚠️ تعذر جلب معلومات السهم {clean_ticker}: {e}")
            return {"symbol": clean_ticker, "name": clean_ticker}

    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """التحقق السريع من صحة وجود رمز السهم في السوق"""
        if not ticker or not isinstance(ticker, str):
            return False

        df = DataLoader.get_stock_data(ticker, period="5d")
        return not df.empty
