"""
MACD 전략
MACD 지표 기반 트레이딩 전략
"""

import pandas as pd
from .base_strategy import BaseStrategy
from ..utils.indicators import TechnicalIndicators


class MACDStrategy(BaseStrategy):
    """
    MACD 크로스오버 전략
    MACD 라인이 시그널 라인을 상향 돌파 시 매수, 하향 돌파 시 매도
    """

    def __init__(
        self,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ):
        """
        MACDStrategy 초기화

        Args:
            fast: 빠른 EMA 기간
            slow: 느린 EMA 기간
            signal: 시그널 라인 기간
        """
        super().__init__(name=f"MACD({fast}/{slow}/{signal})")
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        MACD 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # MACD 계산
        macd_df = TechnicalIndicators.calculate_macd(
            df['Close'], self.fast, self.slow, self.signal
        )
        df = pd.concat([df, macd_df], axis=1)

        # 시그널 초기화
        df['Signal'] = 0

        # MACD > Signal: 매수
        df.loc[df['MACD'] > df['Signal'], 'Signal'] = 1

        # MACD < Signal: 매도
        df.loc[df['MACD'] < df['Signal'], 'Signal'] = -1

        return df


class MACDHistogramStrategy(BaseStrategy):
    """
    MACD 히스토그램 전략
    히스토그램의 방향 전환을 이용한 전략
    """

    def __init__(
        self,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
        histogram_threshold: float = 0.0
    ):
        """
        MACDHistogramStrategy 초기화

        Args:
            fast: 빠른 EMA 기간
            slow: 느린 EMA 기간
            signal: 시그널 라인 기간
            histogram_threshold: 히스토그램 임계값
        """
        super().__init__(name=f"MACD_Histogram({fast}/{slow}/{signal})")
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.histogram_threshold = histogram_threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        MACD 히스토그램 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # MACD 계산
        macd_df = TechnicalIndicators.calculate_macd(
            df['Close'], self.fast, self.slow, self.signal
        )
        df = pd.concat([df, macd_df], axis=1)

        # 히스토그램 변화
        df['Histogram_Change'] = df['Histogram'].diff()

        # 시그널 초기화
        df['Signal'] = 0

        # 히스토그램이 음수에서 양수로 전환 (상승 모멘텀 시작)
        bullish = (
            (df['Histogram'] > self.histogram_threshold) &
            (df['Histogram'].shift(1) <= self.histogram_threshold)
        )
        df.loc[bullish, 'Signal'] = 1

        # 히스토그램이 양수에서 음수로 전환 (하락 모멘텀 시작)
        bearish = (
            (df['Histogram'] < self.histogram_threshold) &
            (df['Histogram'].shift(1) >= self.histogram_threshold)
        )
        df.loc[bearish, 'Signal'] = -1

        return df


class MACDZeroCrossStrategy(BaseStrategy):
    """
    MACD 제로선 크로스 전략
    MACD가 0선을 돌파하는 시점에 매매
    """

    def __init__(
        self,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ):
        """
        MACDZeroCrossStrategy 초기화

        Args:
            fast: 빠른 EMA 기간
            slow: 느린 EMA 기간
            signal: 시그널 라인 기간
        """
        super().__init__(name=f"MACD_ZeroCross({fast}/{slow}/{signal})")
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        MACD 제로선 크로스 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # MACD 계산
        macd_df = TechnicalIndicators.calculate_macd(
            df['Close'], self.fast, self.slow, self.signal
        )
        df = pd.concat([df, macd_df], axis=1)

        # 시그널 초기화
        df['Signal'] = 0

        # MACD가 0선 상향 돌파: 매수
        bullish_cross = (df['MACD'] > 0) & (df['MACD'].shift(1) <= 0)
        df.loc[bullish_cross, 'Signal'] = 1

        # MACD가 0선 하향 돌파: 매도
        bearish_cross = (df['MACD'] < 0) & (df['MACD'].shift(1) >= 0)
        df.loc[bearish_cross, 'Signal'] = -1

        return df
