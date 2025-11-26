"""
평균 회귀 전략
볼린저 밴드 기반 평균 회귀 트레이딩 전략
"""

import pandas as pd
from .base_strategy import BaseStrategy
from ..utils.indicators import TechnicalIndicators


class MeanReversionStrategy(BaseStrategy):
    """
    평균 회귀 전략
    가격이 볼린저 밴드 하단을 이탈하면 매수, 상단을 이탈하면 매도
    """

    def __init__(
        self,
        period: int = 20,
        std_dev: float = 2.0,
        use_close_signal: bool = True
    ):
        """
        MeanReversionStrategy 초기화

        Args:
            period: 볼린저 밴드 기간
            std_dev: 표준편차 배수
            use_close_signal: 중간선 도달 시 포지션 종료 여부
        """
        super().__init__(name=f"MeanReversion(BB{period})")
        self.period = period
        self.std_dev = std_dev
        self.use_close_signal = use_close_signal

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        평균 회귀 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 볼린저 밴드 계산
        bb_df = TechnicalIndicators.calculate_bollinger_bands(
            df['Close'], self.period, self.std_dev
        )
        df = pd.concat([df, bb_df], axis=1)

        # 시그널 생성
        df['Signal'] = 0

        # 하단 밴드 이탈 시 매수 (과매도)
        df.loc[df['Close'] < df['BB_Lower'], 'Signal'] = 1

        # 상단 밴드 이탈 시 매도 (과매수)
        df.loc[df['Close'] > df['BB_Upper'], 'Signal'] = -1

        # 중간선 복귀 시 포지션 종료
        if self.use_close_signal:
            # 이전 시그널 확인
            prev_signal = df['Signal'].shift(1)

            # 매수 포지션에서 중간선 도달 시 종료
            close_long = (prev_signal > 0) & (df['Close'] >= df['BB_Middle'])
            df.loc[close_long, 'Signal'] = 0

            # 매도 포지션에서 중간선 도달 시 종료
            close_short = (prev_signal < 0) & (df['Close'] <= df['BB_Middle'])
            df.loc[close_short, 'Signal'] = 0

        return df


class ZScoreStrategy(BaseStrategy):
    """
    Z-Score 기반 평균 회귀 전략
    가격의 Z-Score를 계산하여 극단값에서 매매
    """

    def __init__(
        self,
        period: int = 20,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5
    ):
        """
        ZScoreStrategy 초기화

        Args:
            period: 평균 및 표준편차 계산 기간
            entry_threshold: 진입 임계값 (Z-Score)
            exit_threshold: 청산 임계값 (Z-Score)
        """
        super().__init__(name=f"ZScore({period})")
        self.period = period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Z-Score 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 이동평균 및 표준편차 계산
        df['MA'] = df['Close'].rolling(window=self.period).mean()
        df['Std'] = df['Close'].rolling(window=self.period).std()

        # Z-Score 계산
        df['ZScore'] = (df['Close'] - df['MA']) / df['Std']

        # 시그널 생성
        df['Signal'] = 0

        # Z-Score < -entry_threshold: 과매도 -> 매수
        df.loc[df['ZScore'] < -self.entry_threshold, 'Signal'] = 1

        # Z-Score > entry_threshold: 과매수 -> 매도
        df.loc[df['ZScore'] > self.entry_threshold, 'Signal'] = -1

        # 0에 가까워지면 포지션 종료
        df.loc[abs(df['ZScore']) < self.exit_threshold, 'Signal'] = 0

        return df
