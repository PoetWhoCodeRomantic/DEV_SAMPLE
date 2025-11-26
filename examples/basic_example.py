"""
기본 사용 예제
TQQQ 데이터를 수집하고 간단한 모멘텀 전략을 백테스트
"""

import sys
sys.path.append('..')

from src.data.data_fetcher import DataFetcher
from src.strategies.momentum_strategy import MomentumStrategy
from src.backtesting.backtester import Backtester
from src.backtesting.performance import PerformanceAnalyzer


def main():
    print("=" * 60)
    print("레버리지 ETF 퀀트 트레이딩 시뮬레이션 - 기본 예제")
    print("=" * 60)
    print()

    # 1. 데이터 수집
    print("1. TQQQ 데이터 수집 중...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data('TQQQ', period='2y')
    print(f"   데이터 수집 완료: {len(data)} 행")
    print(f"   기간: {data.index[0]} ~ {data.index[-1]}")
    print()

    # 2. 전략 설정
    print("2. 모멘텀 전략 설정...")
    strategy = MomentumStrategy(short_window=20, long_window=50, use_ema=True)
    print(f"   전략: {strategy.name}")
    print()

    # 3. 백테스트 실행
    print("3. 백테스트 실행 중...")
    backtester = Backtester(
        initial_capital=10000,
        commission=0.001,
        slippage=0.001
    )
    results = backtester.run(strategy, data)
    print("   백테스트 완료!")
    print()

    # 4. 결과 출력
    print("4. 결과 분석")
    print()
    backtester.print_summary()
    print()

    # 5. Buy & Hold와 비교
    print("5. Buy & Hold 전략과 비교")
    print("-" * 60)
    comparison = backtester.compare_with_buy_and_hold()
    for key, value in comparison.items():
        if isinstance(value, float):
            if '%' in key:
                print(f"{key:.<40} {value:>10.2f}%")
            else:
                print(f"{key:.<40} ${value:>10,.2f}")
    print()

    # 6. 상세 성과 분석
    print("6. 상세 성과 분석")
    print()
    analyzer = PerformanceAnalyzer(results, initial_capital=10000)
    analyzer.print_report()

    # 7. 거래 로그 (최근 10개)
    print("\n7. 최근 거래 내역 (최근 10개)")
    print("-" * 60)
    trade_log = backtester.get_trade_log()
    if not trade_log.empty:
        print(trade_log.tail(10).to_string())
    else:
        print("거래 내역이 없습니다.")

    print("\n" + "=" * 60)
    print("예제 실행 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
