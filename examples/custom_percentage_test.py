"""
커스텀 퍼센트 조건 테스트
사용자가 직접 매수/매도 조건을 설정하여 테스트
"""

import sys
sys.path.append('..')

from src.data.data_fetcher import DataFetcher
from src.strategies.percentage_strategy import (
    PercentageDropBuyStrategy,
    PyramidingStrategy,
    CombinedPercentageStrategy
)
from src.backtesting.backtester import Backtester


def test_simple_drop_buy():
    """
    간단한 하락률 매수 전략 테스트
    사용자가 원하는 하락률과 상승률을 설정
    """
    print("=" * 80)
    print("간단한 하락률 매수 전략 테스트")
    print("=" * 80)
    print()

    # 사용자 설정
    SYMBOL = 'TQQQ'           # 거래할 심볼
    PERIOD = '2y'             # 데이터 기간
    DROP_PERCENT = 7.0        # 매수 기준: 7% 하락
    SELL_PERCENT = 5.0        # 매도 기준: 5% 상승
    INITIAL_CAPITAL = 10000   # 초기 자본

    print(f"테스트 조건:")
    print(f"  - 심볼: {SYMBOL}")
    print(f"  - 기간: {PERIOD}")
    print(f"  - 매수 조건: {DROP_PERCENT}% 하락")
    print(f"  - 매도 조건: {SELL_PERCENT}% 상승")
    print(f"  - 초기 자본: ${INITIAL_CAPITAL:,}")
    print()

    # 데이터 수집
    print("데이터 수집 중...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data(SYMBOL, period=PERIOD)
    print(f"수집 완료: {len(data)} 일")
    print()

    # 전략 실행
    strategy = PercentageDropBuyStrategy(
        drop_percent=DROP_PERCENT,
        sell_profit_percent=SELL_PERCENT
    )

    backtester = Backtester(initial_capital=INITIAL_CAPITAL)
    backtester.run(strategy, data)

    # 결과 출력
    backtester.print_summary()

    print()
    comparison = backtester.compare_with_buy_and_hold()
    print("[ Buy & Hold 전략 대비 ]")
    print(f"  Buy & Hold 최종 가치: ${comparison['Buy & Hold Final Value']:,.2f}")
    print(f"  전략 최종 가치: ${comparison['Strategy Final Value']:,.2f}")
    print(f"  차이: ${comparison['Strategy Final Value'] - comparison['Buy & Hold Final Value']:,.2f}")
    print()


def test_pyramiding():
    """
    피라미딩 전략 테스트
    하락폭에 따라 다른 비중으로 매수
    """
    print("=" * 80)
    print("피라미딩 전략 테스트 (하락 시 비중 늘리기)")
    print("=" * 80)
    print()

    # 사용자 설정
    SYMBOL = 'SOXL'
    PERIOD = '2y'
    INITIAL_CAPITAL = 10000

    # 매수 레벨 설정
    BUY_LEVELS = [
        (2.0, 0.15),   # 2% 하락 → 15% 투자
        (4.0, 0.20),   # 4% 하락 → 20% 투자
        (6.0, 0.25),   # 6% 하락 → 25% 투자
        (10.0, 0.40),  # 10% 하락 → 40% 투자
    ]

    SELL_PROFIT = 8.0  # 8% 수익 시 전량 매도

    print(f"테스트 조건:")
    print(f"  - 심볼: {SYMBOL}")
    print(f"  - 기간: {PERIOD}")
    print(f"  - 초기 자본: ${INITIAL_CAPITAL:,}")
    print()
    print("매수 조건 (하락폭에 따른 비중 배분):")
    total_weight = 0
    for drop, weight in BUY_LEVELS:
        print(f"  - {drop}% 하락 → {weight*100}% 투자")
        total_weight += weight
    print(f"  총 투자 비중: {total_weight*100}%")
    print(f"\n매도 조건: {SELL_PROFIT}% 상승 시 전량 매도")
    print()

    # 데이터 수집
    print("데이터 수집 중...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data(SYMBOL, period=PERIOD)
    print(f"수집 완료: {len(data)} 일")
    print()

    # 전략 실행
    strategy = PyramidingStrategy(
        buy_levels=BUY_LEVELS,
        sell_profit_percent=SELL_PROFIT
    )

    backtester = Backtester(initial_capital=INITIAL_CAPITAL)
    backtester.run(strategy, data)

    # 결과 출력
    backtester.print_summary()

    print()
    comparison = backtester.compare_with_buy_and_hold()
    print("[ Buy & Hold 전략 대비 ]")
    print(f"  초과 수익률: {comparison['Excess Return (%)']:+.2f}%")
    print()


def test_combined_strategy():
    """
    복합 퍼센트 전략
    여러 하락/상승 구간에서 각각 다른 비중으로 매매
    """
    print("=" * 80)
    print("복합 퍼센트 전략 테스트")
    print("=" * 80)
    print()

    # 사용자 설정
    SYMBOL = 'TQQQ'
    PERIOD = '1y'
    INITIAL_CAPITAL = 10000

    # 매수 조건: (하락률, 매수비중)
    BUY_CONDITIONS = [
        (5.0, 0.4),    # 5% 하락 → 40% 매수
        (10.0, 0.6),   # 10% 하락 → 60% 매수
        (15.0, 1.0),   # 15% 하락 → 100% 매수
    ]

    # 매도 조건: (상승률, 매도비중)
    SELL_CONDITIONS = [
        (8.0, 0.5),    # 8% 상승 → 50% 매도
        (15.0, 1.0),   # 15% 상승 → 100% 매도
    ]

    print(f"테스트 조건:")
    print(f"  - 심볼: {SYMBOL}")
    print(f"  - 기간: {PERIOD}")
    print(f"  - 초기 자본: ${INITIAL_CAPITAL:,}")
    print()

    print("[ 매수 조건 ]")
    for drop, buy_size in BUY_CONDITIONS:
        print(f"  {drop}% 하락 → {buy_size*100}% 매수")

    print()
    print("[ 매도 조건 ]")
    for rise, sell_size in SELL_CONDITIONS:
        print(f"  {rise}% 상승 → {sell_size*100}% 매도")
    print()

    # 데이터 수집
    print("데이터 수집 중...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data(SYMBOL, period=PERIOD)
    print(f"수집 완료: {len(data)} 일")
    print()

    # 전략 실행
    strategy = CombinedPercentageStrategy(
        buy_conditions=BUY_CONDITIONS,
        sell_conditions=SELL_CONDITIONS
    )

    backtester = Backtester(initial_capital=INITIAL_CAPITAL)
    backtester.run(strategy, data)

    # 결과 출력
    backtester.print_summary()

    print()
    comparison = backtester.compare_with_buy_and_hold()
    print("[ Buy & Hold 전략 대비 ]")
    print(f"  초과 수익률: {comparison['Excess Return (%)']:+.2f}%")

    # 거래 내역
    print()
    print("[ 최근 거래 내역 (10개) ]")
    print("-" * 80)
    trade_log = backtester.get_trade_log()
    if not trade_log.empty:
        print(trade_log.tail(10).to_string())
    else:
        print("거래 내역이 없습니다.")

    print()


def main():
    """메인 함수"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "커스텀 퍼센트 전략 테스트" + " " * 33 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # 1. 간단한 하락률 매수 전략
    test_simple_drop_buy()

    print("\n" + "▼" * 80 + "\n")

    # 2. 피라미딩 전략
    test_pyramiding()

    print("\n" + "▼" * 80 + "\n")

    # 3. 복합 전략
    test_combined_strategy()

    print()
    print("=" * 80)
    print("모든 테스트 완료!")
    print("=" * 80)
    print()
    print("💡 팁:")
    print("  - 파일 상단의 설정값을 수정하여 다양한 조건을 테스트해보세요")
    print("  - DROP_PERCENT, SELL_PERCENT 등의 값을 조정하면 됩니다")
    print("  - BUY_LEVELS, SELL_CONDITIONS를 변경하여 비중을 조절할 수 있습니다")
    print()


if __name__ == "__main__":
    main()
