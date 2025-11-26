"""
기술적 지표 계산 모듈
pandas-ta를 기반으로 다양한 기술적 지표 제공
"""

import pandas as pd
import numpy as np
from typing import Optional


class TechnicalIndicators:
    """기술적 지표 계산 클래스"""

    @staticmethod
    def calculate_sma(data: pd.Series, period: int = 20) -> pd.Series:
        """
        단순 이동평균 (Simple Moving Average)

        Args:
            data: 가격 데이터
            period: 이동평균 기간

        Returns:
            Series: SMA 값
        """
        return data.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(data: pd.Series, period: int = 20) -> pd.Series:
        """
        지수 이동평균 (Exponential Moving Average)

        Args:
            data: 가격 데이터
            period: 이동평균 기간

        Returns:
            Series: EMA 값
        """
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        상대강도지수 (Relative Strength Index)

        Args:
            data: 가격 데이터
            period: RSI 기간

        Returns:
            Series: RSI 값 (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_macd(
        data: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> pd.DataFrame:
        """
        MACD (Moving Average Convergence Divergence)

        Args:
            data: 가격 데이터
            fast: 빠른 EMA 기간
            slow: 느린 EMA 기간
            signal: 시그널 라인 기간

        Returns:
            DataFrame: MACD, Signal, Histogram
        """
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()

        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return pd.DataFrame({
            'MACD': macd,
            'Signal': signal_line,
            'Histogram': histogram
        })

    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> pd.DataFrame:
        """
        볼린저 밴드 (Bollinger Bands)

        Args:
            data: 가격 데이터
            period: 이동평균 기간
            std_dev: 표준편차 배수

        Returns:
            DataFrame: Upper, Middle, Lower 밴드
        """
        middle = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return pd.DataFrame({
            'BB_Upper': upper,
            'BB_Middle': middle,
            'BB_Lower': lower
        })

    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        평균 진폭 범위 (Average True Range)

        Args:
            high: 고가 데이터
            low: 저가 데이터
            close: 종가 데이터
            period: ATR 기간

        Returns:
            Series: ATR 값
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr

    @staticmethod
    def calculate_stochastic(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> pd.DataFrame:
        """
        스토캐스틱 오실레이터 (Stochastic Oscillator)

        Args:
            high: 고가 데이터
            low: 저가 데이터
            close: 종가 데이터
            k_period: %K 기간
            d_period: %D 기간

        Returns:
            DataFrame: %K, %D
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()

        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()

        return pd.DataFrame({
            'Stoch_K': k,
            'Stoch_D': d
        })

    @staticmethod
    def calculate_adx(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        평균 방향성 지수 (Average Directional Index)

        Args:
            high: 고가 데이터
            low: 저가 데이터
            close: 종가 데이터
            period: ADX 기간

        Returns:
            Series: ADX 값
        """
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = tr.rolling(window=period).mean()

        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx

    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        온 밸런스 볼륨 (On-Balance Volume)

        Args:
            close: 종가 데이터
            volume: 거래량 데이터

        Returns:
            Series: OBV 값
        """
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv

    @staticmethod
    def calculate_vwap(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series
    ) -> pd.Series:
        """
        거래량 가중 평균 가격 (Volume Weighted Average Price)

        Args:
            high: 고가 데이터
            low: 저가 데이터
            close: 종가 데이터
            volume: 거래량 데이터

        Returns:
            Series: VWAP 값
        """
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()

        return vwap

    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        모든 주요 지표를 데이터프레임에 추가

        Args:
            df: OHLCV 데이터프레임

        Returns:
            DataFrame: 지표가 추가된 데이터프레임
        """
        df = df.copy()

        # 이동평균
        df['SMA_20'] = TechnicalIndicators.calculate_sma(df['Close'], 20)
        df['SMA_50'] = TechnicalIndicators.calculate_sma(df['Close'], 50)
        df['EMA_12'] = TechnicalIndicators.calculate_ema(df['Close'], 12)
        df['EMA_26'] = TechnicalIndicators.calculate_ema(df['Close'], 26)

        # RSI
        df['RSI'] = TechnicalIndicators.calculate_rsi(df['Close'])

        # MACD
        macd_df = TechnicalIndicators.calculate_macd(df['Close'])
        df = pd.concat([df, macd_df], axis=1)

        # 볼린저 밴드
        bb_df = TechnicalIndicators.calculate_bollinger_bands(df['Close'])
        df = pd.concat([df, bb_df], axis=1)

        # ATR
        df['ATR'] = TechnicalIndicators.calculate_atr(
            df['High'], df['Low'], df['Close']
        )

        # 스토캐스틱
        stoch_df = TechnicalIndicators.calculate_stochastic(
            df['High'], df['Low'], df['Close']
        )
        df = pd.concat([df, stoch_df], axis=1)

        # OBV
        df['OBV'] = TechnicalIndicators.calculate_obv(df['Close'], df['Volume'])

        # VWAP
        df['VWAP'] = TechnicalIndicators.calculate_vwap(
            df['High'], df['Low'], df['Close'], df['Volume']
        )

        return df
