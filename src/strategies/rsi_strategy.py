"""
RSI 전략
상대강도지수 기반 트레이딩 전략
"""

import pandas as pd
from .base_strategy import BaseStrategy
from ..utils.indicators import TechnicalIndicators


class RSIStrategy(BaseStrategy):
    """
    RSI 기반 트레이딩 전략
    RSI가 과매도 구간에서 매수, 과매수 구간에서 매도
    """

    def __init__(
        self,
        period: int = 14,
        oversold: int = 30,
        overbought: int = 70,
        neutral_zone: tuple = (40, 60)
    ):
        """
        RSIStrategy 초기화

        Args:
            period: RSI 계산 기간
            oversold: 과매도 임계값
            overbought: 과매수 임계값
            neutral_zone: 중립 구간 (청산 신호)
        """
        super().__init__(name=f"RSI({period})")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.neutral_zone = neutral_zone

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        RSI 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # RSI 계산
        df['RSI'] = TechnicalIndicators.calculate_rsi(df['Close'], self.period)

        # 시그널 초기화
        df['Signal'] = 0

        # 과매도 구간: 매수 신호
        df.loc[df['RSI'] < self.oversold, 'Signal'] = 1

        # 과매수 구간: 매도 신호
        df.loc[df['RSI'] > self.overbought, 'Signal'] = -1

        # 중립 구간: 포지션 청산
        if self.neutral_zone:
            neutral_low, neutral_high = self.neutral_zone
            neutral = (df['RSI'] >= neutral_low) & (df['RSI'] <= neutral_high)
            df.loc[neutral, 'Signal'] = 0

        return df


class RSIDivergenceStrategy(BaseStrategy):
    """
    RSI 다이버전스 전략
    가격과 RSI의 괴리를 이용한 전략
    """

    def __init__(
        self,
        period: int = 14,
        lookback: int = 5
    ):
        """
        RSIDivergenceStrategy 초기화

        Args:
            period: RSI 계산 기간
            lookback: 다이버전스 확인 기간
        """
        super().__init__(name=f"RSI_Divergence({period})")
        self.period = period
        self.lookback = lookback

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        RSI 다이버전스 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # RSI 계산
        df['RSI'] = TechnicalIndicators.calculate_rsi(df['Close'], self.period)

        # 가격 및 RSI의 최근 고점/저점
        df['Price_High'] = df['Close'].rolling(window=self.lookback).max()
        df['Price_Low'] = df['Close'].rolling(window=self.lookback).min()
        df['RSI_High'] = df['RSI'].rolling(window=self.lookback).max()
        df['RSI_Low'] = df['RSI'].rolling(window=self.lookback).min()

        # 시그널 초기화
        df['Signal'] = 0

        # 강세 다이버전스: 가격은 저점 낮아지는데 RSI는 저점 높아짐 (매수)
        bullish_div = (
            (df['Close'] == df['Price_Low']) &
            (df['RSI'] > df['RSI_Low'].shift(self.lookback))
        )
        df.loc[bullish_div, 'Signal'] = 1

        # 약세 다이버전스: 가격은 고점 높아지는데 RSI는 고점 낮아짐 (매도)
        bearish_div = (
            (df['Close'] == df['Price_High']) &
            (df['RSI'] < df['RSI_High'].shift(self.lookback))
        )
        df.loc[bearish_div, 'Signal'] = -1

        return df
