"""
기본 트레이딩 전략 클래스
모든 전략의 베이스 클래스
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseStrategy(ABC):
    """
    추상 기본 전략 클래스
    모든 트레이딩 전략은 이 클래스를 상속받아야 함
    """

    def __init__(self, name: str = "BaseStrategy"):
        """
        BaseStrategy 초기화

        Args:
            name: 전략 이름
        """
        self.name = name
        self.signals = None
        self.positions = None

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        트레이딩 시그널 생성 (추상 메서드)

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        pass

    def calculate_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """
        시그널을 기반으로 포지션 계산

        Args:
            signals: 시그널 데이터프레임

        Returns:
            DataFrame: 포지션이 추가된 데이터프레임
        """
        df = signals.copy()

        # Signal: 1 = 매수, -1 = 매도, 0 = 관망
        df['Position'] = df['Signal'].fillna(0)

        # 포지션 변화 감지
        df['Position_Change'] = df['Position'].diff()

        return df

    def get_trade_log(self, positions: pd.DataFrame) -> pd.DataFrame:
        """
        거래 로그 생성

        Args:
            positions: 포지션 데이터프레임

        Returns:
            DataFrame: 거래 로그
        """
        # 포지션 변화가 있는 시점만 추출
        trades = positions[positions['Position_Change'] != 0].copy()

        if len(trades) == 0:
            return pd.DataFrame()

        trades['Action'] = trades['Position_Change'].apply(
            lambda x: 'BUY' if x > 0 else 'SELL' if x < 0 else 'HOLD'
        )

        return trades[['Close', 'Position', 'Position_Change', 'Action']]

    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        데이터 유효성 검증

        Args:
            data: 검증할 데이터프레임

        Returns:
            bool: 유효성 여부
        """
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Required column '{col}' not found in data")

        if data.empty:
            raise ValueError("Data is empty")

        if data.isnull().any().any():
            print("Warning: Data contains NaN values")

        return True

    def apply_strategy(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        전략 적용 (시그널 생성 + 포지션 계산)

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 전략이 적용된 데이터프레임
        """
        self.validate_data(data)

        # 시그널 생성
        signals = self.generate_signals(data)
        self.signals = signals

        # 포지션 계산
        positions = self.calculate_positions(signals)
        self.positions = positions

        return positions

    def get_performance_summary(self, positions: pd.DataFrame) -> Dict:
        """
        전략 성과 요약

        Args:
            positions: 포지션 데이터프레임

        Returns:
            dict: 성과 지표
        """
        if 'Returns' not in positions.columns:
            positions['Returns'] = positions['Close'].pct_change()

        # 전략 수익률 계산
        positions['Strategy_Returns'] = positions['Position'].shift(1) * positions['Returns']

        total_return = positions['Strategy_Returns'].sum()
        num_trades = len(positions[positions['Position_Change'] != 0])

        winning_trades = positions[positions['Strategy_Returns'] > 0]
        losing_trades = positions[positions['Strategy_Returns'] < 0]

        win_rate = len(winning_trades) / num_trades if num_trades > 0 else 0

        summary = {
            'strategy_name': self.name,
            'total_return': total_return,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'avg_win': winning_trades['Strategy_Returns'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['Strategy_Returns'].mean() if len(losing_trades) > 0 else 0,
        }

        return summary

    def __str__(self):
        return f"Strategy: {self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"
