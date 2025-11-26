"""
퍼센트 기반 전략 예제
하락/상승률 기반의 단순하고 실용적인 매매 전략 테스트
"""

import sys
sys.path.append('..')

from src.data.data_fetcher import DataFetcher
from src.strategies.percentage_strategy import (
    PercentageDropBuyStrategy,
    PyramidingStrategy,
    GridTradingStrategy,
    DollarCostAveragingStrategy,
    VolatilityBreakoutStrategy,
    CombinedPercentageStrategy
)
from src.backtesting.backtester import Backtester


def main():
    print("=" * 80)
    print("퍼센트 기반 트레이딩 전략 테스트")
    print("=" * 80)
    print()

    # 1. 데이터 수집
    print("1. TQQQ 데이터 수집 중...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data('TQQQ', period='1y')
    print(f"   데이터 수집 완료: {len(data)} 행")
    print(f"   기간: {data.index[0].date()} ~ {data.index[-1].date()}")
    print()

    # 2. 하락률 매수 전략
    print("=" * 80)
    print("[ 전략 1 ] 하락률 매수 전략")
    print("=" * 80)
    print("조건: 5% 하락 시 매수, 3% 상승 시 매도")
    print()

    strategy1 = PercentageDropBuyStrategy(
        drop_percent=5.0,
        sell_profit_percent=3.0,
        lookback_days=1
    )

    backtester1 = Backtester(initial_capital=10000)
    backtester1.run(strategy1, data)
    backtester1.print_summary()

    comparison1 = backtester1.compare_with_buy_and_hold()
    print("\n[ Buy & Hold 대비 ]")
    print(f"  Buy & Hold 수익률: {comparison1['Buy & Hold Return (%)']:.2f}%")
    print(f"  전략 수익률: {comparison1['Strategy Return (%)']:.2f}%")
    print(f"  초과 수익률: {comparison1['Excess Return (%)']:.2f}%")
    print()

    # 3. 피라미딩 전략 (하락 시 비중 늘리기)
    print("=" * 80)
    print("[ 전략 2 ] 피라미딩 전략 (하락 시 비중 늘리기)")
    print("=" * 80)
    print("조건:")
    print("  - 3% 하락 → 20% 투자")
    print("  - 5% 하락 → 30% 투자")
    print("  - 8% 하락 → 30% 투자")
    print("  - 12% 하락 → 20% 투자")
    print("  - 5% 상승 시 전량 매도")
    print()

    strategy2 = PyramidingStrategy(
        buy_levels=[
            (3.0, 0.2),   # 3% 하락 시 20% 투자
            (5.0, 0.3),   # 5% 하락 시 30% 투자
            (8.0, 0.3),   # 8% 하락 시 30% 투자
            (12.0, 0.2)   # 12% 하락 시 20% 투자
        ],
        sell_profit_percent=5.0
    )

    backtester2 = Backtester(initial_capital=10000)
    backtester2.run(strategy2, data)
    backtester2.print_summary()

    comparison2 = backtester2.compare_with_buy_and_hold()
    print("\n[ Buy & Hold 대비 ]")
    print(f"  Buy & Hold 수익률: {comparison2['Buy & Hold Return (%)']:.2f}%")
    print(f"  전략 수익률: {comparison2['Strategy Return (%)']:.2f}%")
    print(f"  초과 수익률: {comparison2['Excess Return (%)']:.2f}%")
    print()

    # 4. 그리드 트레이딩 전략
    print("=" * 80)
    print("[ 전략 3 ] 그리드 트레이딩 전략")
    print("=" * 80)
    print("조건: 3% 간격으로 10개 그리드 설정")
    print()

    strategy3 = GridTradingStrategy(
        grid_size=3.0,
        num_grids=10
    )

    backtester3 = Backtester(initial_capital=10000)
    backtester3.run(strategy3, data)
    backtester3.print_summary()

    comparison3 = backtester3.compare_with_buy_and_hold()
    print("\n[ Buy & Hold 대비 ]")
    print(f"  Buy & Hold 수익률: {comparison3['Buy & Hold Return (%)']:.2f}%")
    print(f"  전략 수익률: {comparison3['Strategy Return (%)']:.2f}%")
    print(f"  초과 수익률: {comparison3['Excess Return (%)']:.2f}%")
    print()

    # 5. 정액 적립식 투자 (DCA)
    print("=" * 80)
    print("[ 전략 4 ] 정액 적립식 투자 (DCA)")
    print("=" * 80)
    print("조건: 7일마다 일정 금액 매수, 10% 수익 시 매도")
    print()

    strategy4 = DollarCostAveragingStrategy(
        investment_interval=7,
        sell_profit_percent=10.0
    )

    backtester4 = Backtester(initial_capital=10000)
    backtester4.run(strategy4, data)
    backtester4.print_summary()

    comparison4 = backtester4.compare_with_buy_and_hold()
    print("\n[ Buy & Hold 대비 ]")
    print(f"  Buy & Hold 수익률: {comparison4['Buy & Hold Return (%)']:.2f}%")
    print(f"  전략 수익률: {comparison4['Strategy Return (%)']:.2f}%")
    print(f"  초과 수익률: {comparison4['Excess Return (%)']:.2f}%")
    print()

    # 6. 복합 퍼센트 전략
    print("=" * 80)
    print("[ 전략 5 ] 복합 퍼센트 전략")
    print("=" * 80)
    print("조건:")
    print("  [ 매수 ]")
    print("  - 3% 하락 → 30% 매수")
    print("  - 7% 하락 → 70% 매수")
    print("  [ 매도 ]")
    print("  - 5% 상승 → 50% 매도")
    print("  - 10% 상승 → 100% 매도")
    print()

    strategy5 = CombinedPercentageStrategy(
        buy_conditions=[
            (3.0, 0.3),   # 3% 하락 시 30% 매수
            (7.0, 0.7)    # 7% 하락 시 70% 매수
        ],
        sell_conditions=[
            (5.0, 0.5),   # 5% 상승 시 50% 매도
            (10.0, 1.0)   # 10% 상승 시 100% 매도
        ]
    )

    backtester5 = Backtester(initial_capital=10000)
    backtester5.run(strategy5, data)
    backtester5.print_summary()

    comparison5 = backtester5.compare_with_buy_and_hold()
    print("\n[ Buy & Hold 대비 ]")
    print(f"  Buy & Hold 수익률: {comparison5['Buy & Hold Return (%)']:.2f}%")
    print(f"  전략 수익률: {comparison5['Strategy Return (%)']:.2f}%")
    print(f"  초과 수익률: {comparison5['Excess Return (%)']:.2f}%")
    print()

    # 7. 전략 성과 비교 요약
    print("=" * 80)
    print("전체 전략 성과 비교")
    print("=" * 80)
    print()

    strategies_summary = [
        ("하락률 매수 (5%↓/3%↑)", backtester1.calculate_metrics()),
        ("피라미딩", backtester2.calculate_metrics()),
        ("그리드 트레이딩", backtester3.calculate_metrics()),
        ("정액 적립식 (DCA)", backtester4.calculate_metrics()),
        ("복합 퍼센트", backtester5.calculate_metrics()),
    ]

    print(f"{'전략명':<25} {'수익률':>12} {'샤프비율':>12} {'최대낙폭':>12} {'거래횟수':>12}")
    print("-" * 80)

    for name, metrics in strategies_summary:
        print(f"{name:<25} {metrics['Total Return (%)']:>11.2f}% "
              f"{metrics['Sharpe Ratio']:>12.2f} "
              f"{metrics['Max Drawdown (%)']:>11.2f}% "
              f"{metrics['Number of Trades']:>12}")

    print()
    print("=" * 80)
    print("테스트 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
