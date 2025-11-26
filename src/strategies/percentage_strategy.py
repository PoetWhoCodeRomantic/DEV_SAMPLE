"""
퍼센트 기반 트레이딩 전략
가격 변동률(%)을 기반으로 매매 결정
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from typing import List, Tuple, Optional


class PercentageDropBuyStrategy(BaseStrategy):
    """
    하락률 기반 매수 전략
    N% 하락 시 매수, M% 상승 시 매도
    """

    def __init__(
        self,
        drop_percent: float = 5.0,
        sell_profit_percent: float = 3.0,
        lookback_days: int = 1
    ):
        """
        PercentageDropBuyStrategy 초기화

        Args:
            drop_percent: 매수 기준 하락률 (%)
            sell_profit_percent: 매도 기준 상승률 (%)
            lookback_days: 기준 가격 lookback 기간 (일)
        """
        super().__init__(name=f"DropBuy({drop_percent}%)")
        self.drop_percent = drop_percent
        self.sell_profit_percent = sell_profit_percent
        self.lookback_days = lookback_days

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        하락률 기반 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 기준 가격 (N일 전 종가)
        df['Reference_Price'] = df['Close'].shift(self.lookback_days)

        # 현재 가격 대비 변동률
        df['Price_Change_Pct'] = ((df['Close'] - df['Reference_Price']) / df['Reference_Price']) * 100

        # 시그널 초기화
        df['Signal'] = 0

        # 하락률이 drop_percent 이상이면 매수
        df.loc[df['Price_Change_Pct'] <= -self.drop_percent, 'Signal'] = 1

        # 상승률이 sell_profit_percent 이상이면 매도
        df.loc[df['Price_Change_Pct'] >= self.sell_profit_percent, 'Signal'] = -1

        return df


class PyramidingStrategy(BaseStrategy):
    """
    피라미딩 전략 (하락 시 비중 늘리기)
    하락폭에 따라 단계적으로 매수 비중 증가
    """

    def __init__(
        self,
        buy_levels: List[Tuple[float, float]] = None,
        sell_profit_percent: float = 5.0,
        lookback_days: int = 1
    ):
        """
        PyramidingStrategy 초기화

        Args:
            buy_levels: [(하락률, 투자비중), ...] 예: [(3, 0.2), (5, 0.3), (10, 0.5)]
            sell_profit_percent: 매도 기준 상승률 (%)
            lookback_days: 기준 가격 lookback 기간
        """
        if buy_levels is None:
            buy_levels = [(3.0, 0.2), (5.0, 0.3), (8.0, 0.3), (12.0, 0.2)]

        super().__init__(name="Pyramiding")
        self.buy_levels = sorted(buy_levels, key=lambda x: x[0])  # 하락률 순 정렬
        self.sell_profit_percent = sell_profit_percent
        self.lookback_days = lookback_days

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        피라미딩 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 기준 가격
        df['Reference_Price'] = df['Close'].shift(self.lookback_days)

        # 변동률 계산
        df['Price_Change_Pct'] = ((df['Close'] - df['Reference_Price']) / df['Reference_Price']) * 100

        # 시그널 및 비중 초기화
        df['Signal'] = 0
        df['Position_Size'] = 0.0

        # 각 하락 레벨에 따라 매수 비중 결정
        for drop_pct, weight in self.buy_levels:
            mask = df['Price_Change_Pct'] <= -drop_pct
            df.loc[mask, 'Signal'] = 1
            df.loc[mask, 'Position_Size'] = weight

        # 목표 수익률 도달 시 전량 매도
        df.loc[df['Price_Change_Pct'] >= self.sell_profit_percent, 'Signal'] = -1

        return df


class GridTradingStrategy(BaseStrategy):
    """
    그리드 트레이딩 전략
    일정 간격으로 매수/매도 주문 배치
    """

    def __init__(
        self,
        grid_size: float = 3.0,
        num_grids: int = 10,
        center_price: Optional[float] = None
    ):
        """
        GridTradingStrategy 초기화

        Args:
            grid_size: 그리드 간격 (%)
            num_grids: 그리드 개수
            center_price: 중심 가격 (None이면 첫 종가 사용)
        """
        super().__init__(name=f"GridTrading({grid_size}%)")
        self.grid_size = grid_size
        self.num_grids = num_grids
        self.center_price = center_price

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        그리드 트레이딩 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 중심 가격 설정
        if self.center_price is None:
            center = df['Close'].iloc[0]
        else:
            center = self.center_price

        # 그리드 레벨 생성
        buy_levels = []
        sell_levels = []

        for i in range(1, self.num_grids + 1):
            buy_level = center * (1 - (self.grid_size / 100) * i)
            sell_level = center * (1 + (self.grid_size / 100) * i)
            buy_levels.append(buy_level)
            sell_levels.append(sell_level)

        # 시그널 초기화
        df['Signal'] = 0
        df['Grid_Level'] = 0

        # 각 행마다 그리드 레벨 확인
        for idx, row in df.iterrows():
            price = row['Close']

            # 매수 레벨 체크
            for level_idx, buy_price in enumerate(buy_levels):
                if price <= buy_price:
                    df.loc[idx, 'Signal'] = 1
                    df.loc[idx, 'Grid_Level'] = -(level_idx + 1)
                    break

            # 매도 레벨 체크
            for level_idx, sell_price in enumerate(sell_levels):
                if price >= sell_price:
                    df.loc[idx, 'Signal'] = -1
                    df.loc[idx, 'Grid_Level'] = (level_idx + 1)
                    break

        return df


class DollarCostAveragingStrategy(BaseStrategy):
    """
    정액 적립식 투자 (DCA)
    일정 기간마다 일정 금액 매수
    """

    def __init__(
        self,
        investment_interval: int = 7,  # 일
        sell_profit_percent: float = 10.0
    ):
        """
        DollarCostAveragingStrategy 초기화

        Args:
            investment_interval: 투자 간격 (일)
            sell_profit_percent: 매도 기준 수익률 (%)
        """
        super().__init__(name=f"DCA({investment_interval}d)")
        self.investment_interval = investment_interval
        self.sell_profit_percent = sell_profit_percent

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        DCA 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 시그널 초기화
        df['Signal'] = 0
        df['Days_Since_Start'] = range(len(df))

        # 일정 간격마다 매수
        df.loc[df['Days_Since_Start'] % self.investment_interval == 0, 'Signal'] = 1

        # 평균 매수가 계산
        df['Avg_Buy_Price'] = 0.0
        cumulative_shares = 0
        cumulative_cost = 0

        for idx in df.index:
            if df.loc[idx, 'Signal'] == 1:
                # 매수
                cumulative_shares += 1
                cumulative_cost += df.loc[idx, 'Close']

            if cumulative_shares > 0:
                df.loc[idx, 'Avg_Buy_Price'] = cumulative_cost / cumulative_shares

        # 수익률 계산 및 매도 시그널
        df['Profit_Pct'] = ((df['Close'] - df['Avg_Buy_Price']) / df['Avg_Buy_Price']) * 100

        # 목표 수익률 도달 시 전량 매도
        df.loc[df['Profit_Pct'] >= self.sell_profit_percent, 'Signal'] = -1

        return df


class VolatilityBreakoutStrategy(BaseStrategy):
    """
    변동성 돌파 전략
    전일 변동폭의 N% 돌파 시 매수
    """

    def __init__(
        self,
        breakout_ratio: float = 0.5,
        profit_target: float = 5.0,
        stop_loss: float = 3.0
    ):
        """
        VolatilityBreakoutStrategy 초기화

        Args:
            breakout_ratio: 돌파 기준 비율 (0.5 = 전일 변동폭의 50%)
            profit_target: 목표 수익률 (%)
            stop_loss: 손절 기준 (%)
        """
        super().__init__(name=f"VolBreakout({breakout_ratio})")
        self.breakout_ratio = breakout_ratio
        self.profit_target = profit_target
        self.stop_loss = stop_loss

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        변동성 돌파 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 전일 변동폭
        df['Prev_Range'] = (df['High'] - df['Low']).shift(1)

        # 돌파 가격 = 전일 종가 + (전일 변동폭 × breakout_ratio)
        df['Breakout_Price'] = df['Close'].shift(1) + (df['Prev_Range'] * self.breakout_ratio)

        # 시그널 초기화
        df['Signal'] = 0
        df['Entry_Price'] = 0.0

        # 매수 진입 가격 추적
        in_position = False
        entry_price = 0

        for idx in df.index:
            current_price = df.loc[idx, 'Close']
            breakout_price = df.loc[idx, 'Breakout_Price']

            if not in_position:
                # 돌파 시 매수
                if current_price > breakout_price and not pd.isna(breakout_price):
                    df.loc[idx, 'Signal'] = 1
                    entry_price = current_price
                    df.loc[idx, 'Entry_Price'] = entry_price
                    in_position = True
            else:
                df.loc[idx, 'Entry_Price'] = entry_price

                # 수익률 계산
                profit_pct = ((current_price - entry_price) / entry_price) * 100

                # 목표 수익률 도달 또는 손절
                if profit_pct >= self.profit_target or profit_pct <= -self.stop_loss:
                    df.loc[idx, 'Signal'] = -1
                    in_position = False
                    entry_price = 0

        return df


class CombinedPercentageStrategy(BaseStrategy):
    """
    복합 퍼센트 전략
    여러 하락/상승 구간에서 각각 다른 액션
    """

    def __init__(
        self,
        buy_conditions: List[Tuple[float, float]] = None,
        sell_conditions: List[Tuple[float, float]] = None,
        lookback_days: int = 1
    ):
        """
        CombinedPercentageStrategy 초기화

        Args:
            buy_conditions: [(하락률, 매수비중), ...] 예: [(3, 0.3), (7, 0.7)]
            sell_conditions: [(상승률, 매도비중), ...] 예: [(5, 0.5), (10, 1.0)]
            lookback_days: 기준 가격 lookback 기간
        """
        if buy_conditions is None:
            buy_conditions = [(3.0, 0.3), (7.0, 0.7)]
        if sell_conditions is None:
            sell_conditions = [(5.0, 0.5), (10.0, 1.0)]

        super().__init__(name="CombinedPct")
        self.buy_conditions = sorted(buy_conditions, key=lambda x: x[0], reverse=True)
        self.sell_conditions = sorted(sell_conditions, key=lambda x: x[0])
        self.lookback_days = lookback_days

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        복합 퍼센트 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 기준 가격
        df['Reference_Price'] = df['Close'].shift(self.lookback_days)

        # 변동률 계산
        df['Price_Change_Pct'] = ((df['Close'] - df['Reference_Price']) / df['Reference_Price']) * 100

        # 시그널 초기화
        df['Signal'] = 0
        df['Position_Size'] = 0.0

        # 매수 조건 체크
        for drop_pct, buy_size in self.buy_conditions:
            mask = df['Price_Change_Pct'] <= -drop_pct
            df.loc[mask, 'Signal'] = 1
            df.loc[mask, 'Position_Size'] = buy_size

        # 매도 조건 체크
        for rise_pct, sell_size in self.sell_conditions:
            mask = df['Price_Change_Pct'] >= rise_pct
            df.loc[mask, 'Signal'] = -1
            df.loc[mask, 'Position_Size'] = sell_size

        return df


class DailyAccumulationStrategy(BaseStrategy):
    """
    일일 누적 매수 + 회차별 익절 전략

    매수 규칙:
    - 매일 종가에 매수 (최대 30회)
    - 1일차: 무조건 1회 매수
    - 2일차 이후: 당일 종가가 전일 종가보다 낮으면 추가 매수

    매도 규칙:
    - 당일 종가가 전일 종가보다 높을 때
    - 각 매수 회차별로 3% 이상 수익이 난 회차만 매도
    """

    def __init__(
        self,
        max_positions: int = 30,
        profit_target_percent: float = 3.0
    ):
        """
        DailyAccumulationStrategy 초기화

        Args:
            max_positions: 최대 매수 회차 (기본값: 30)
            profit_target_percent: 익절 기준 수익률 (기본값: 3%)
        """
        super().__init__(name=f"DailyAccumulation(max={max_positions})")
        self.max_positions = max_positions
        self.profit_target_percent = profit_target_percent

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        일일 누적 매수 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 시그널 및 매매 정보 초기화
        df['Signal'] = 0
        df['Buy_Count'] = 0  # 현재까지 누적 매수 회차
        df['Sell_Count'] = 0  # 당일 매도 회차
        df['Avg_Buy_Price'] = 0.0  # 평균 매수가
        df['Total_Positions'] = 0  # 보유 포지션 수

        # 각 매수 회차별 매수가 저장 (최대 30개)
        buy_prices = []  # [(날짜, 매수가), ...]

        prev_close = None

        for idx in df.index:
            current_close = df.loc[idx, 'Close']

            # 첫날 또는 이전 종가보다 낮을 때 매수
            if prev_close is None:
                # 첫날: 무조건 매수
                if len(buy_prices) < self.max_positions:
                    df.loc[idx, 'Signal'] = 1
                    df.loc[idx, 'Buy_Count'] = 1
                    buy_prices.append((idx, current_close))
            else:
                # 현재 종가 vs 전일 종가 비교
                if current_close < prev_close:
                    # 하락: 추가 매수
                    if len(buy_prices) < self.max_positions:
                        df.loc[idx, 'Signal'] = 1
                        df.loc[idx, 'Buy_Count'] = len(buy_prices) + 1
                        buy_prices.append((idx, current_close))
                elif current_close > prev_close:
                    # 상승: 수익 난 회차 매도 체크
                    sell_count = 0
                    positions_to_remove = []

                    for i, (buy_date, buy_price) in enumerate(buy_prices):
                        profit_pct = ((current_close - buy_price) / buy_price) * 100

                        if profit_pct >= self.profit_target_percent:
                            sell_count += 1
                            positions_to_remove.append(i)

                    if sell_count > 0:
                        df.loc[idx, 'Signal'] = -1
                        df.loc[idx, 'Sell_Count'] = sell_count

                        # 매도한 포지션 제거 (역순으로 제거)
                        for i in sorted(positions_to_remove, reverse=True):
                            buy_prices.pop(i)

            # 현재 보유 포지션 및 평균 매수가 기록
            df.loc[idx, 'Total_Positions'] = len(buy_prices)
            if len(buy_prices) > 0:
                df.loc[idx, 'Avg_Buy_Price'] = sum(price for _, price in buy_prices) / len(buy_prices)

            prev_close = current_close

        return df


class DailyDCAStrategy(BaseStrategy):
    """
    간소화된 일일 DCA + 익절 전략

    매수: 매일 종가가 전일 종가보다 낮으면 매수 (최대 30회)
    매도: 평균 매수가 대비 3% 이상 수익 시 전량 매도
    """

    def __init__(
        self,
        max_positions: int = 30,
        profit_target_percent: float = 3.0,
        first_day_buy: bool = True
    ):
        """
        DailyDCAStrategy 초기화

        Args:
            max_positions: 최대 매수 회차
            profit_target_percent: 익절 기준 (%)
            first_day_buy: 첫날 무조건 매수 여부
        """
        super().__init__(name=f"DailyDCA({max_positions}회)")
        self.max_positions = max_positions
        self.profit_target_percent = profit_target_percent
        self.first_day_buy = first_day_buy

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        일일 DCA 시그널 생성

        Args:
            data: OHLCV 데이터프레임

        Returns:
            DataFrame: 시그널이 추가된 데이터프레임
        """
        df = data.copy()

        # 전일 종가
        df['Prev_Close'] = df['Close'].shift(1)

        # 시그널 초기화
        df['Signal'] = 0
        df['Position_Count'] = 0
        df['Avg_Price'] = 0.0

        # 상태 추적
        position_count = 0
        total_cost = 0.0
        avg_price = 0.0

        for idx in df.index:
            current_close = df.loc[idx, 'Close']
            prev_close = df.loc[idx, 'Prev_Close']

            # 첫날 처리
            if pd.isna(prev_close):
                if self.first_day_buy:
                    df.loc[idx, 'Signal'] = 1
                    position_count = 1
                    total_cost = current_close
                    avg_price = current_close
            else:
                # 현재가 vs 전일 종가
                if current_close < prev_close and position_count < self.max_positions:
                    # 하락: 매수
                    df.loc[idx, 'Signal'] = 1
                    position_count += 1
                    total_cost += current_close
                    avg_price = total_cost / position_count

                elif current_close > prev_close and position_count > 0:
                    # 상승: 익절 체크
                    profit_pct = ((current_close - avg_price) / avg_price) * 100

                    if profit_pct >= self.profit_target_percent:
                        # 전량 매도
                        df.loc[idx, 'Signal'] = -1
                        position_count = 0
                        total_cost = 0.0
                        avg_price = 0.0

            # 현재 상태 기록
            df.loc[idx, 'Position_Count'] = position_count
            df.loc[idx, 'Avg_Price'] = avg_price

        return df
