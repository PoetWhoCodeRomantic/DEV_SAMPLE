"""
일일 DCA + 회차별 익절 전략 테스트
매일 종가 기준으로 하락 시 매수, 상승 시 수익난 회차만 익절
"""

import sys
sys.path.append('..')

from src.data.data_fetcher import DataFetcher
from src.strategies.percentage_strategy import DailyDCAStrategy
from src.backtesting.backtester import Backtester


def test_daily_accumulation():
    """일일 DCA 전략 (회차별 개별 익절)"""
    print("=" * 80)
    print("[ 일일 DCA + 회차별 익절 전략 ]")
    print("=" * 80)
    print()
    print("전략 설명:")
    print("  1. 매일 종가 체크")
    print("  2. 첫날 무조건 1회 매수")
    print("  3. 전일 종가보다 낮으면 추가 매수 (최대 30회)")
    print("  4. 전일 종가보다 높으면 각 회차별로 3% 이상 수익난 것만 매도")
    print()

    # 데이터 수집
    print("TQQQ 데이터 수집 중...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data('TQQQ', period='1y')
    print(f"데이터 수집 완료: {len(data)} 일")
    print(f"기간: {data.index[0].date()} ~ {data.index[-1].date()}")
    print()

    # 전략 설정
    strategy = DailyDCAStrategy(
        max_positions=30,        # 최대 30회 매수
        profit_target_percent=3.0  # 3% 익절
    )

    # 백테스트 실행
    print("백테스트 실행 중...")
    backtester = Backtester(initial_capital=10000)
    results = backtester.run(strategy, data)
    print()

    # 결과 출력
    backtester.print_summary()

    # Buy & Hold 비교
    print()
    comparison = backtester.compare_with_buy_and_hold()
    print("[ Buy & Hold 전략 대비 ]")
    print(f"  Buy & Hold 수익률: {comparison['Buy & Hold Return (%)']:>10.2f}%")
    print(f"  전략 수익률:       {comparison['Strategy Return (%)']:>10.2f}%")
    print(f"  초과 수익률:       {comparison['Excess Return (%)']:>+10.2f}%")
    print()

    # 거래 통계
    print("[ 거래 통계 ]")
    print(f"  최대 보유 회차: {results['Position_Count'].max():.0f}회")
    print(f"  평균 보유 회차: {results['Position_Count'].mean():.1f}회")

    # 매수/매도 횟수
    buy_days = len(results[results['Signal'] == 1])
    sell_days = len(results[results['Signal'] == -1])
    print(f"  총 매수일: {buy_days}일")
    print(f"  총 매도일: {sell_days}일")
    print()


def test_parameter_comparison():
    """파라미터별 성과 비교"""
    print("=" * 80)
    print("[ 파라미터 비교 ] 최대 매수 회차에 따른 성과")
    print("=" * 80)
    print()

    # 데이터 수집
    fetcher = DataFetcher()
    data = fetcher.fetch_data('TQQQ', period='1y')

    # 다양한 max_positions 테스트
    test_params = [10, 20, 30, 50]
    results_summary = []

    for max_pos in test_params:
        print(f"테스트 중: 최대 {max_pos}회 매수...")

        strategy = DailyDCAStrategy(
            max_positions=max_pos,
            profit_target_percent=3.0
        )

        backtester = Backtester(initial_capital=10000)
        backtester.run(strategy, data)
        metrics = backtester.calculate_metrics()

        results_summary.append({
            'Max Positions': max_pos,
            'Total Return (%)': metrics['Total Return (%)'],
            'Sharpe Ratio': metrics['Sharpe Ratio'],
            'Max Drawdown (%)': metrics['Max Drawdown (%)'],
            'Win Rate (%)': metrics['Win Rate (%)']
        })

    # 결과 출력
    print()
    print(f"{'최대회차':>10} {'수익률':>12} {'샤프비율':>12} {'최대낙폭':>12} {'승률':>10}")
    print("-" * 80)

    for result in results_summary:
        print(f"{result['Max Positions']:>10} "
              f"{result['Total Return (%)']:>11.2f}% "
              f"{result['Sharpe Ratio']:>12.2f} "
              f"{result['Max Drawdown (%)']:>11.2f}% "
              f"{result['Win Rate (%)']:>9.1f}%")

    print()


def main():
    """메인 함수"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 18 + "일일 DCA + 회차별 익절 전략 테스트" + " " * 25 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # 1. 일일 DCA 전략
    test_daily_accumulation()

    print("\n" + "▼" * 80 + "\n")

    # 2. 파라미터 비교
    test_parameter_comparison()

    print()
    print("=" * 80)
    print("테스트 완료!")
    print("=" * 80)
    print()
    print("💡 전략 특징:")
    print()
    print("  [ DailyDCAStrategy ]")
    print("  - 각 매수 회차별로 개별 익절")
    print("  - 수익난 회차만 먼저 매도")
    print("  - 레버리지 ETF의 높은 변동성에 최적화")
    print("  - 하락장에서 지속적으로 매수, 상승장에서 수익 실현")
    print()


if __name__ == "__main__":
    main()
