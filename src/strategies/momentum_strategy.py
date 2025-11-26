"""
모멘텀 전략
이동평균선 크로스오버 기반 트레이딩 전략
"""

import pandas as pd
from .base_strategy import BaseStrategy
from ..utils.indicators import TechnicalIndicators


class MomentumStrategy(BaseStrategy):
    """
    모멘텀 기반 트레이딩 전략
    단기 이동평균선이 장기 이동평균선을 상향 돌파 시 매수, 하향 돌파 시 매도
    """

    def __init__(
        self,
        short_window: int = 20,
        long_window: int = 50,
        use_ema: bool = False
    ):
        """
        MomentumStrategy 초기화

        Args:
            short_window: 단기 이동평균 기간
            long_window: 장기 이동평균 기간
            use_ema: EMA 사용 여부 (False이면 SMA 사용)
        """
        super().__init__(name=f"Momentum({short_window}/{long_window})")
        self.short_window = short_window
        self.long_window = long_window
        self.use_ema = use_ema

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        모멘텀 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 이동평균선 계산
        if self.use_ema:
            df['Short_MA'] = TechnicalIndicators.calculate_ema(
                df['Close'], self.short_window
            )
            df['Long_MA'] = TechnicalIndicators.calculate_ema(
                df['Close'], self.long_window
            )
        else:
            df['Short_MA'] = TechnicalIndicators.calculate_sma(
                df['Close'], self.short_window
            )
            df['Long_MA'] = TechnicalIndicators.calculate_sma(
                df['Close'], self.long_window
            )

        # 시그널 생성
        df['Signal'] = 0

        # 골든 크로스: 단기 MA가 장기 MA를 상향 돌파 (매수)
        df.loc[df['Short_MA'] > df['Long_MA'], 'Signal'] = 1

        # 데드 크로스: 단기 MA가 장기 MA를 하향 돌파 (매도)
        df.loc[df['Short_MA'] < df['Long_MA'], 'Signal'] = -1

        return df


class TripleMomentumStrategy(BaseStrategy):
    """
    삼중 이동평균선 전략
    세 개의 이동평균선을 사용하여 더 정교한 시그널 생성
    """

    def __init__(
        self,
        fast_window: int = 10,
        medium_window: int = 20,
        slow_window: int = 50
    ):
        """
        TripleMomentumStrategy 초기화

        Args:
            fast_window: 빠른 이동평균 기간
            medium_window: 중간 이동평균 기간
            slow_window: 느린 이동평균 기간
        """
        super().__init__(
            name=f"TripleMomentum({fast_window}/{medium_window}/{slow_window})"
        )
        self.fast_window = fast_window
        self.medium_window = medium_window
        self.slow_window = slow_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        삼중 모멘텀 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 세 개의 이동평균선 계산
        df['Fast_MA'] = TechnicalIndicators.calculate_ema(
            df['Close'], self.fast_window
        )
        df['Medium_MA'] = TechnicalIndicators.calculate_ema(
            df['Close'], self.medium_window
        )
        df['Slow_MA'] = TechnicalIndicators.calculate_ema(
            df['Close'], self.slow_window
        )

        # 시그널 생성
        df['Signal'] = 0

        # 강한 매수 신호: Fast > Medium > Slow
        strong_buy = (
            (df['Fast_MA'] > df['Medium_MA']) &
            (df['Medium_MA'] > df['Slow_MA'])
        )
        df.loc[strong_buy, 'Signal'] = 1

        # 강한 매도 신호: Fast < Medium < Slow
        strong_sell = (
            (df['Fast_MA'] < df['Medium_MA']) &
            (df['Medium_MA'] < df['Slow_MA'])
        )
        df.loc[strong_sell, 'Signal'] = -1

        return df
