"""
백테스팅 엔진
트레이딩 전략의 과거 성과를 시뮬레이션
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict
from ..strategies.base_strategy import BaseStrategy


class Backtester:
    """
    백테스팅 엔진 클래스
    전략의 과거 성과를 시뮬레이션하고 분석
    """

    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.001
    ):
        """
        Backtester 초기화

        Args:
            initial_capital: 초기 자본금
            commission: 거래 수수료 (0.001 = 0.1%)
            slippage: 슬리피지 (0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.results = None

    def run(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        position_size: float = 1.0
    ) -> pd.DataFrame:
        """
        백테스트 실행

        Args:
            strategy: 트레이딩 전략
            data: OHLCV 데이터
            position_size: 포지션 크기 (1.0 = 100%)

        Returns:
            DataFrame: 백테스트 결과
        """
        # 전략 적용
        df = strategy.apply_strategy(data)

        # 수익률 계산
        df['Returns'] = df['Close'].pct_change()

        # 포지션 크기 조정
        df['Position_Size'] = df['Position'] * position_size

        # 거래 비용 계산
        df['Trade'] = df['Position'].diff().abs()
        df['Commission_Cost'] = df['Trade'] * self.commission
        df['Slippage_Cost'] = df['Trade'] * self.slippage
        df['Total_Cost'] = df['Commission_Cost'] + df['Slippage_Cost']

        # 전략 수익률 (비용 포함)
        df['Strategy_Returns'] = (
            df['Position_Size'].shift(1) * df['Returns'] - df['Total_Cost']
        )

        # 누적 수익률
        df['Cumulative_Returns'] = (1 + df['Strategy_Returns']).cumprod()

        # 포트폴리오 가치
        df['Portfolio_Value'] = self.initial_capital * df['Cumulative_Returns']

        # 드로우다운 계산
        df['Peak'] = df['Portfolio_Value'].cummax()
        df['Drawdown'] = (df['Portfolio_Value'] - df['Peak']) / df['Peak']

        self.results = df

        return df

    def get_trade_log(self) -> pd.DataFrame:
        """
        거래 로그 가져오기

        Returns:
            DataFrame: 거래 내역
        """
        if self.results is None:
            raise ValueError("백테스트를 먼저 실행해주세요 (run 메서드)")

        trades = self.results[self.results['Trade'] > 0].copy()

        if len(trades) == 0:
            return pd.DataFrame()

        trades['Action'] = trades['Position'].apply(
            lambda x: 'BUY' if x > 0 else 'SELL' if x < 0 else 'CLOSE'
        )

        trades['Price'] = trades['Close']
        trades['Cost'] = trades['Total_Cost'] * trades['Price']

        return trades[['Price', 'Position', 'Action', 'Cost', 'Portfolio_Value']]

    def calculate_metrics(self) -> Dict:
        """
        성과 지표 계산

        Returns:
            dict: 성과 메트릭스
        """
        if self.results is None:
            raise ValueError("백테스트를 먼저 실행해주세요 (run 메서드)")

        df = self.results

        # 기본 메트릭스
        total_return = (df['Portfolio_Value'].iloc[-1] / self.initial_capital - 1)
        num_trades = int(df['Trade'].sum())

        # 승률 계산
        winning_trades = df[df['Strategy_Returns'] > 0]
        losing_trades = df[df['Strategy_Returns'] < 0]
        total_trading_days = len(df[df['Strategy_Returns'] != 0])

        win_rate = len(winning_trades) / total_trading_days if total_trading_days > 0 else 0

        # 샤프 비율 (연율화, 252 거래일 가정)
        returns_mean = df['Strategy_Returns'].mean()
        returns_std = df['Strategy_Returns'].std()
        sharpe_ratio = (returns_mean / returns_std) * np.sqrt(252) if returns_std != 0 else 0

        # 소르티노 비율
        downside_returns = df[df['Strategy_Returns'] < 0]['Strategy_Returns']
        downside_std = downside_returns.std()
        sortino_ratio = (returns_mean / downside_std) * np.sqrt(252) if downside_std != 0 else 0

        # 최대 드로우다운
        max_drawdown = df['Drawdown'].min()

        # 칼마 비율
        calmar_ratio = (total_return / abs(max_drawdown)) if max_drawdown != 0 else 0

        # 평균 승리/손실
        avg_win = winning_trades['Strategy_Returns'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['Strategy_Returns'].mean() if len(losing_trades) > 0 else 0

        # 손익비
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0

        # 총 거래 비용
        total_costs = df['Total_Cost'].sum() * df['Close'].mean()

        metrics = {
            'Initial Capital': self.initial_capital,
            'Final Value': df['Portfolio_Value'].iloc[-1],
            'Total Return (%)': total_return * 100,
            'Number of Trades': num_trades,
            'Win Rate (%)': win_rate * 100,
            'Average Win (%)': avg_win * 100,
            'Average Loss (%)': avg_loss * 100,
            'Profit Factor': profit_factor,
            'Sharpe Ratio': sharpe_ratio,
            'Sortino Ratio': sortino_ratio,
            'Max Drawdown (%)': max_drawdown * 100,
            'Calmar Ratio': calmar_ratio,
            'Total Costs': total_costs,
        }

        return metrics

    def print_summary(self) -> None:
        """성과 요약 출력"""
        metrics = self.calculate_metrics()

        print("=" * 60)
        print("백테스트 결과 요약")
        print("=" * 60)

        for key, value in metrics.items():
            if isinstance(value, float):
                if 'Ratio' in key or 'Factor' in key:
                    print(f"{key:.<30} {value:>10.2f}")
                elif '%' in key:
                    print(f"{key:.<30} {value:>10.2f}%")
                else:
                    print(f"{key:.<30} ${value:>10,.2f}")
            else:
                print(f"{key:.<30} {value:>10}")

        print("=" * 60)

    def compare_with_buy_and_hold(self) -> Dict:
        """
        Buy & Hold 전략과 비교

        Returns:
            dict: 비교 결과
        """
        if self.results is None:
            raise ValueError("백테스트를 먼저 실행해주세요 (run 메서드)")

        df = self.results

        # Buy & Hold 수익률
        bh_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1)
        bh_final_value = self.initial_capital * (1 + bh_return)

        # 전략 수익률
        strategy_return = (df['Portfolio_Value'].iloc[-1] / self.initial_capital - 1)

        # 초과 수익률
        excess_return = strategy_return - bh_return

        comparison = {
            'Buy & Hold Return (%)': bh_return * 100,
            'Buy & Hold Final Value': bh_final_value,
            'Strategy Return (%)': strategy_return * 100,
            'Strategy Final Value': df['Portfolio_Value'].iloc[-1],
            'Excess Return (%)': excess_return * 100,
        }

        return comparison

    def optimize_parameters(
        self,
        strategy_class,
        data: pd.DataFrame,
        param_grid: Dict,
        metric: str = 'Sharpe Ratio'
    ) -> Dict:
        """
        그리드 서치를 통한 파라미터 최적화

        Args:
            strategy_class: 전략 클래스
            data: OHLCV 데이터
            param_grid: 파라미터 그리드
            metric: 최적화 기준 메트릭

        Returns:
            dict: 최적 파라미터 및 결과
        """
        best_score = -np.inf
        best_params = None
        best_metrics = None

        # 파라미터 조합 생성
        from itertools import product

        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())

        for values in product(*param_values):
            params = dict(zip(param_names, values))

            # 전략 생성 및 백테스트
            strategy = strategy_class(**params)
            self.run(strategy, data)
            metrics = self.calculate_metrics()

            # 최적 파라미터 업데이트
            score = metrics.get(metric, -np.inf)
            if score > best_score:
                best_score = score
                best_params = params
                best_metrics = metrics

        return {
            'best_params': best_params,
            'best_score': best_score,
            'best_metrics': best_metrics
        }
