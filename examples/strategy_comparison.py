"""
여러 전략 비교 예제
TQQQ, SOXL에 대해 다양한 전략의 성과를 비교
"""

import sys
sys.path.append('..')

import pandas as pd
from src.data.data_fetcher import DataFetcher
from src.strategies.momentum_strategy import MomentumStrategy
from src.strategies.mean_reversion_strategy import MeanReversionStrategy
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.macd_strategy import MACDStrategy
from src.backtesting.backtester import Backtester


def main():
    print("=" * 80)
    print("레버리지 ETF 퀀트 트레이딩 - 전략 비교 예제")
    print("=" * 80)
    print()

    # 1. 데이터 수집
    print("1. 데이터 수집 중...")
    fetcher = DataFetcher()
    symbols = ['TQQQ', 'SOXL']
    data_dict = fetcher.fetch_multiple(symbols, period='2y')
    print()

    # 2. 전략 정의
    strategies = [
        MomentumStrategy(short_window=20, long_window=50, use_ema=True),
        MeanReversionStrategy(period=20, std_dev=2.0),
        RSIStrategy(period=14, oversold=30, overbought=70),
        MACDStrategy(fast=12, slow=26, signal=9),
    ]

    # 3. 각 심볼 및 전략별 백테스트
    results_summary = []

    for symbol in symbols:
        print(f"\n{'=' * 80}")
        print(f"심볼: {symbol}")
        print(f"{'=' * 80}\n")

        data = data_dict[symbol]

        for strategy in strategies:
            print(f"전략 테스트 중: {strategy.name}")

            # 백테스트 실행
            backtester = Backtester(initial_capital=10000)
            backtester.run(strategy, data)
            metrics = backtester.calculate_metrics()

            # 결과 저장
            results_summary.append({
                'Symbol': symbol,
                'Strategy': strategy.name,
                'Total Return (%)': metrics['Total Return (%)'],
                'Sharpe Ratio': metrics['Sharpe Ratio'],
                'Max Drawdown (%)': metrics['Max Drawdown (%)'],
                'Win Rate (%)': metrics['Win Rate (%)'],
                'Number of Trades': metrics['Number of Trades'],
            })

            print(f"  ✓ 완료 - 수익률: {metrics['Total Return (%)']:.2f}%")

    # 4. 결과 비교
    print(f"\n{'=' * 80}")
    print("전략 성과 비교")
    print(f"{'=' * 80}\n")

    results_df = pd.DataFrame(results_summary)

    # 심볼별로 그룹화하여 출력
    for symbol in symbols:
        print(f"\n[ {symbol} ]")
        symbol_results = results_df[results_df['Symbol'] == symbol].copy()
        symbol_results = symbol_results.sort_values('Total Return (%)', ascending=False)
        print(symbol_results.to_string(index=False))
        print()

    # 5. 최고 성과 전략
    print(f"{'=' * 80}")
    print("최고 성과 전략")
    print(f"{'=' * 80}\n")

    best_by_return = results_df.loc[results_df['Total Return (%)'].idxmax()]
    best_by_sharpe = results_df.loc[results_df['Sharpe Ratio'].idxmax()]

    print("수익률 기준:")
    print(f"  심볼: {best_by_return['Symbol']}")
    print(f"  전략: {best_by_return['Strategy']}")
    print(f"  수익률: {best_by_return['Total Return (%)']:.2f}%")
    print()

    print("샤프 비율 기준:")
    print(f"  심볼: {best_by_sharpe['Symbol']}")
    print(f"  전략: {best_by_sharpe['Strategy']}")
    print(f"  샤프 비율: {best_by_sharpe['Sharpe Ratio']:.2f}")
    print()

    # 6. Excel로 내보내기
    output_file = 'strategy_comparison_results.xlsx'
    results_df.to_excel(output_file, index=False)
    print(f"결과가 '{output_file}'로 저장되었습니다.")

    print("\n" + "=" * 80)
    print("전략 비교 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
