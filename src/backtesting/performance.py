"""
성과 분석 모듈
백테스트 결과의 상세 분석 및 리포트 생성
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from scipy import stats


class PerformanceAnalyzer:
    """백테스트 성과 분석 클래스"""

    def __init__(self, results: pd.DataFrame, initial_capital: float = 10000.0):
        """
        PerformanceAnalyzer 초기화

        Args:
            results: 백테스트 결과 데이터프레임
            initial_capital: 초기 자본금
        """
        self.results = results
        self.initial_capital = initial_capital

    def calculate_returns_statistics(self) -> Dict:
        """
        수익률 통계 계산

        Returns:
            dict: 수익률 통계
        """
        returns = self.results['Strategy_Returns'].dropna()

        stats_dict = {
            'Mean Return': returns.mean(),
            'Median Return': returns.median(),
            'Std Return': returns.std(),
            'Min Return': returns.min(),
            'Max Return': returns.max(),
            'Skewness': returns.skew(),
            'Kurtosis': returns.kurtosis(),
        }

        return stats_dict

    def calculate_risk_metrics(self) -> Dict:
        """
        리스크 지표 계산

        Returns:
            dict: 리스크 메트릭스
        """
        returns = self.results['Strategy_Returns'].dropna()

        # VaR (Value at Risk) - 95%, 99%
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)

        # CVaR (Conditional VaR)
        cvar_95 = returns[returns <= var_95].mean()
        cvar_99 = returns[returns <= var_99].mean()

        # 최대 연속 손실
        consecutive_losses = 0
        max_consecutive_losses = 0
        for ret in returns:
            if ret < 0:
                consecutive_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            else:
                consecutive_losses = 0

        # 변동성 (연율화)
        volatility = returns.std() * np.sqrt(252)

        risk_metrics = {
            'VaR 95%': var_95,
            'VaR 99%': var_99,
            'CVaR 95%': cvar_95,
            'CVaR 99%': cvar_99,
            'Max Consecutive Losses': max_consecutive_losses,
            'Annual Volatility': volatility,
        }

        return risk_metrics

    def calculate_drawdown_analysis(self) -> Dict:
        """
        드로우다운 분석

        Returns:
            dict: 드로우다운 분석 결과
        """
        portfolio_value = self.results['Portfolio_Value']
        peak = self.results['Peak']
        drawdown = self.results['Drawdown']

        # 최대 드로우다운
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()

        # 드로우다운 기간
        dd_periods = []
        in_dd = False
        dd_start = None

        for idx, dd in drawdown.items():
            if dd < 0 and not in_dd:
                dd_start = idx
                in_dd = True
            elif dd == 0 and in_dd:
                dd_periods.append((dd_start, idx))
                in_dd = False

        # 평균 드로우다운 기간
        if dd_periods:
            avg_dd_duration = np.mean([
                (end - start).days for start, end in dd_periods
            ])
        else:
            avg_dd_duration = 0

        dd_analysis = {
            'Max Drawdown': max_dd,
            'Max Drawdown Date': max_dd_date,
            'Number of Drawdown Periods': len(dd_periods),
            'Avg Drawdown Duration (days)': avg_dd_duration,
        }

        return dd_analysis

    def calculate_trade_analysis(self) -> Dict:
        """
        거래 분석

        Returns:
            dict: 거래 분석 결과
        """
        trades = self.results[self.results['Trade'] > 0].copy()

        if len(trades) == 0:
            return {'Message': 'No trades executed'}

        # 거래 간격
        trade_intervals = trades.index.to_series().diff().dt.days
        avg_trade_interval = trade_intervals.mean()

        # 포지션 보유 기간
        position_changes = self.results[self.results['Position'].diff() != 0]
        holding_periods = []

        for i in range(len(position_changes) - 1):
            if position_changes['Position'].iloc[i] != 0:
                duration = (
                    position_changes.index[i+1] - position_changes.index[i]
                ).days
                holding_periods.append(duration)

        avg_holding_period = np.mean(holding_periods) if holding_periods else 0

        trade_analysis = {
            'Total Trades': len(trades),
            'Avg Trade Interval (days)': avg_trade_interval,
            'Avg Holding Period (days)': avg_holding_period,
        }

        return trade_analysis

    def calculate_monthly_returns(self) -> pd.DataFrame:
        """
        월별 수익률 계산

        Returns:
            DataFrame: 월별 수익률
        """
        monthly = self.results['Strategy_Returns'].resample('M').sum()
        monthly_df = pd.DataFrame({
            'Month': monthly.index.strftime('%Y-%m'),
            'Return (%)': monthly.values * 100
        })

        return monthly_df

    def calculate_yearly_returns(self) -> pd.DataFrame:
        """
        연도별 수익률 계산

        Returns:
            DataFrame: 연도별 수익률
        """
        yearly = self.results['Strategy_Returns'].resample('Y').sum()
        yearly_df = pd.DataFrame({
            'Year': yearly.index.year,
            'Return (%)': yearly.values * 100
        })

        return yearly_df

    def generate_report(self) -> str:
        """
        종합 성과 리포트 생성

        Returns:
            str: 리포트 텍스트
        """
        report = []
        report.append("=" * 80)
        report.append("백테스트 성과 분석 리포트")
        report.append("=" * 80)
        report.append("")

        # 수익률 통계
        report.append("[ 수익률 통계 ]")
        returns_stats = self.calculate_returns_statistics()
        for key, value in returns_stats.items():
            report.append(f"  {key:.<40} {value:>15.4f}")
        report.append("")

        # 리스크 지표
        report.append("[ 리스크 지표 ]")
        risk_metrics = self.calculate_risk_metrics()
        for key, value in risk_metrics.items():
            if isinstance(value, (int, np.integer)):
                report.append(f"  {key:.<40} {value:>15}")
            else:
                report.append(f"  {key:.<40} {value:>15.4f}")
        report.append("")

        # 드로우다운 분석
        report.append("[ 드로우다운 분석 ]")
        dd_analysis = self.calculate_drawdown_analysis()
        for key, value in dd_analysis.items():
            if isinstance(value, (int, np.integer, float, np.floating)):
                report.append(f"  {key:.<40} {value:>15.2f}")
            else:
                report.append(f"  {key:.<40} {str(value):>15}")
        report.append("")

        # 거래 분석
        report.append("[ 거래 분석 ]")
        trade_analysis = self.calculate_trade_analysis()
        for key, value in trade_analysis.items():
            if isinstance(value, (int, np.integer)):
                report.append(f"  {key:.<40} {value:>15}")
            elif isinstance(value, (float, np.floating)):
                report.append(f"  {key:.<40} {value:>15.2f}")
            else:
                report.append(f"  {key:.<40} {str(value):>15}")
        report.append("")

        report.append("=" * 80)

        return "\n".join(report)

    def print_report(self) -> None:
        """리포트 출력"""
        print(self.generate_report())

    def export_to_excel(self, filename: str = "backtest_results.xlsx") -> None:
        """
        결과를 Excel 파일로 내보내기

        Args:
            filename: 저장할 파일명
        """
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 전체 결과
            self.results.to_excel(writer, sheet_name='Full Results')

            # 월별 수익률
            monthly_returns = self.calculate_monthly_returns()
            monthly_returns.to_excel(writer, sheet_name='Monthly Returns', index=False)

            # 연도별 수익률
            yearly_returns = self.calculate_yearly_returns()
            yearly_returns.to_excel(writer, sheet_name='Yearly Returns', index=False)

            # 통계 요약
            stats_df = pd.DataFrame([
                self.calculate_returns_statistics(),
                self.calculate_risk_metrics(),
                self.calculate_trade_analysis()
            ])
            stats_df.to_excel(writer, sheet_name='Statistics')

        print(f"결과가 '{filename}'로 저장되었습니다.")

    def calculate_rolling_metrics(
        self,
        window: int = 30,
        metric: str = 'sharpe'
    ) -> pd.Series:
        """
        롤링 메트릭 계산

        Args:
            window: 롤링 윈도우 크기
            metric: 계산할 메트릭 ('sharpe', 'sortino', 'volatility')

        Returns:
            Series: 롤링 메트릭 값
        """
        returns = self.results['Strategy_Returns']

        if metric == 'sharpe':
            rolling_mean = returns.rolling(window=window).mean()
            rolling_std = returns.rolling(window=window).std()
            rolling_metric = (rolling_mean / rolling_std) * np.sqrt(252)

        elif metric == 'sortino':
            rolling_mean = returns.rolling(window=window).mean()
            downside_returns = returns.copy()
            downside_returns[downside_returns > 0] = 0
            rolling_downside_std = downside_returns.rolling(window=window).std()
            rolling_metric = (rolling_mean / rolling_downside_std) * np.sqrt(252)

        elif metric == 'volatility':
            rolling_metric = returns.rolling(window=window).std() * np.sqrt(252)

        else:
            raise ValueError(f"Unknown metric: {metric}")

        return rolling_metric
