"""
시각화 모듈
matplotlib, seaborn, plotly를 활용한 차트 생성
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Visualizer:
    """데이터 시각화 클래스"""

    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """
        Visualizer 초기화

        Args:
            style: matplotlib 스타일
        """
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')

        sns.set_palette("husl")

    @staticmethod
    def plot_price_and_volume(
        df: pd.DataFrame,
        title: str = "Price and Volume",
        figsize: Tuple[int, int] = (14, 8)
    ) -> None:
        """
        가격 및 거래량 차트

        Args:
            df: OHLCV 데이터프레임
            title: 차트 제목
            figsize: 그림 크기
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

        # 가격 차트
        ax1.plot(df.index, df['Close'], label='Close', linewidth=2)
        if 'SMA_20' in df.columns:
            ax1.plot(df.index, df['SMA_20'], label='SMA 20', alpha=0.7)
        if 'SMA_50' in df.columns:
            ax1.plot(df.index, df['SMA_50'], label='SMA 50', alpha=0.7)

        ax1.set_ylabel('Price ($)')
        ax1.set_title(title)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 거래량 차트
        ax2.bar(df.index, df['Volume'], alpha=0.5)
        ax2.set_ylabel('Volume')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_candlestick(
        df: pd.DataFrame,
        title: str = "Candlestick Chart",
        show_volume: bool = True
    ) -> None:
        """
        캔들스틱 차트 (plotly 사용)

        Args:
            df: OHLCV 데이터프레임
            title: 차트 제목
            show_volume: 거래량 표시 여부
        """
        if show_volume:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3]
            )

            # 캔들스틱
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='OHLC'
                ),
                row=1, col=1
            )

            # 거래량
            fig.add_trace(
                go.Bar(x=df.index, y=df['Volume'], name='Volume'),
                row=2, col=1
            )

            fig.update_layout(
                title=title,
                xaxis_rangeslider_visible=False,
                height=600
            )
        else:
            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close']
                    )
                ]
            )
            fig.update_layout(title=title, xaxis_rangeslider_visible=False)

        fig.show()

    @staticmethod
    def plot_returns_distribution(
        df: pd.DataFrame,
        figsize: Tuple[int, int] = (12, 5)
    ) -> None:
        """
        수익률 분포 시각화

        Args:
            df: 수익률이 포함된 데이터프레임
            figsize: 그림 크기
        """
        if 'Returns' not in df.columns:
            df['Returns'] = df['Close'].pct_change()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # 히스토그램
        df['Returns'].dropna().hist(bins=50, ax=ax1, edgecolor='black')
        ax1.set_title('Returns Distribution')
        ax1.set_xlabel('Returns')
        ax1.set_ylabel('Frequency')
        ax1.axvline(0, color='red', linestyle='--', alpha=0.5)

        # Q-Q plot
        from scipy import stats
        stats.probplot(df['Returns'].dropna(), dist="norm", plot=ax2)
        ax2.set_title('Q-Q Plot')

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_backtest_results(
        df: pd.DataFrame,
        title: str = "Backtest Results",
        figsize: Tuple[int, int] = (14, 10)
    ) -> None:
        """
        백테스트 결과 시각화

        Args:
            df: 백테스트 결과 데이터프레임
            title: 차트 제목
            figsize: 그림 크기
        """
        fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)

        # 포트폴리오 가치
        if 'Portfolio_Value' in df.columns:
            axes[0].plot(df.index, df['Portfolio_Value'], label='Portfolio Value', linewidth=2)
            axes[0].set_ylabel('Portfolio Value ($)')
            axes[0].set_title(title)
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)

        # 수익률
        if 'Strategy_Returns' in df.columns:
            axes[1].plot(df.index, df['Strategy_Returns'].cumsum(), label='Cumulative Returns', linewidth=2)
            axes[1].axhline(0, color='red', linestyle='--', alpha=0.5)
            axes[1].set_ylabel('Cumulative Returns')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)

        # 포지션
        if 'Position' in df.columns:
            axes[2].fill_between(df.index, 0, df['Position'], alpha=0.3, label='Position')
            axes[2].set_ylabel('Position')
            axes[2].set_xlabel('Date')
            axes[2].legend()
            axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_indicator(
        df: pd.DataFrame,
        indicator_name: str,
        price: bool = True,
        figsize: Tuple[int, int] = (14, 8)
    ) -> None:
        """
        특정 지표 시각화

        Args:
            df: 데이터프레임
            indicator_name: 지표 이름
            price: 가격도 함께 표시할지 여부
            figsize: 그림 크기
        """
        if indicator_name not in df.columns:
            raise ValueError(f"{indicator_name} not found in dataframe")

        if price:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

            # 가격
            ax1.plot(df.index, df['Close'], label='Close Price', linewidth=2)
            ax1.set_ylabel('Price ($)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # 지표
            ax2.plot(df.index, df[indicator_name], label=indicator_name, linewidth=2, color='orange')
            ax2.set_ylabel(indicator_name)
            ax2.set_xlabel('Date')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        else:
            fig, ax = plt.subplots(figsize=figsize)
            ax.plot(df.index, df[indicator_name], label=indicator_name, linewidth=2)
            ax.set_ylabel(indicator_name)
            ax.set_xlabel('Date')
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_correlation_matrix(
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (10, 8)
    ) -> None:
        """
        상관관계 행렬 히트맵

        Args:
            df: 데이터프레임
            columns: 분석할 컬럼 리스트 (None이면 숫자 컬럼 전체)
            figsize: 그림 크기
        """
        if columns:
            corr = df[columns].corr()
        else:
            corr = df.select_dtypes(include=[np.number]).corr()

        plt.figure(figsize=figsize)
        sns.heatmap(
            corr,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1
        )
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_comparison(
        data_dict: dict,
        title: str = "Symbol Comparison",
        normalize: bool = True,
        figsize: Tuple[int, int] = (14, 7)
    ) -> None:
        """
        여러 심볼 비교 차트

        Args:
            data_dict: {symbol: DataFrame} 딕셔너리
            title: 차트 제목
            normalize: 정규화 여부 (시작점을 100으로)
            figsize: 그림 크기
        """
        plt.figure(figsize=figsize)

        for symbol, df in data_dict.items():
            if normalize:
                normalized = (df['Close'] / df['Close'].iloc[0]) * 100
                plt.plot(df.index, normalized, label=symbol, linewidth=2)
            else:
                plt.plot(df.index, df['Close'], label=symbol, linewidth=2)

        plt.ylabel('Normalized Price' if normalize else 'Price ($)')
        plt.xlabel('Date')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
