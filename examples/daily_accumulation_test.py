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
    print("  5. ⭐ 하락 깊이에 따라 매수 수량 자동 증가 (5%마다 2배, 3배...)")
    print()

    # 데이터 수집
    print("TQQQ 데이터 수집 중...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data('TQQQ', period='1y')
    print(f"데이터 수집 완료: {len(data)} 일")
    print(f"기간: {data.index[0].date()} ~ {data.index[-1].date()}")
    print()

    # 전략 설정 (포지션 스케일링 활성화)
    strategy = DailyDCAStrategy(
        max_positions=30,              # 최대 30회 매수
        profit_target_percent=3.0,     # 3% 익절
        lookback_days=7,               # 최근 7일 고점 추적
        pullback_percent=3.0,          # 고점 대비 3% 하락 시 매수
        position_scaling=True,         # ⭐ 포지션 스케일링 활성화
        base_quantity=1,               # 기본 1주
        depth_threshold=5.0,           # 5%마다 수량 증가
        max_quantity_multiplier=5      # 최대 5배
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
    print(f"  최대 보유 수량: {results['Total_Quantity'].max():.0f}주")
    print(f"  평균 보유 수량: {results['Total_Quantity'].mean():.1f}주")

    # 매수/매도 횟수
    buy_days = len(results[results['Signal'] == 1])
    sell_days = len(results[results['Signal'] == -1])
    total_bought = results[results['Signal'] == 1]['Buy_Quantity'].sum()
    print(f"  총 매수일: {buy_days}일")
    print(f"  총 매수 수량: {total_bought:.0f}주")
    print(f"  총 매도일: {sell_days}일")

    # 포지션 스케일링 통계
    if 'Buy_Quantity' in results.columns:
        buy_quantities = results[results['Signal'] == 1]['Buy_Quantity']
        if len(buy_quantities) > 0:
            print(f"  평균 매수 수량: {buy_quantities.mean():.1f}주/회")
            print(f"  최대 매수 수량: {buy_quantities.max():.0f}주/회")
    print()


def test_parameter_comparison():
    """파라미터별 성과 비교"""
    print("=" * 80)
    print("[ 파라미터 비교 ] 포지션 스케일링 ON/OFF")
    print("=" * 80)
    print()

    # 데이터 수집
    fetcher = DataFetcher()
    data = fetcher.fetch_data('TQQQ', period='1y')

    # 포지션 스케일링 ON/OFF 비교
    test_configs = [
        {
            'scaling': False,
            'name': '스케일링 OFF (고정 1주)'
        },
        {
            'scaling': True,
            'depth_threshold': 10.0,
            'name': '스케일링 ON (보수적: 10%마다)'
        },
        {
            'scaling': True,
            'depth_threshold': 5.0,
            'name': '스케일링 ON (균형: 5%마다)'
        },
        {
            'scaling': True,
            'depth_threshold': 3.0,
            'name': '스케일링 ON (공격적: 3%마다)'
        }
    ]
    results_summary = []

    for config in test_configs:
        print(f"테스트 중: {config['name']}...")

        strategy = DailyDCAStrategy(
            max_positions=30,
            profit_target_percent=3.0,
            lookback_days=7,
            pullback_percent=3.0,
            position_scaling=config['scaling'],
            base_quantity=1,
            depth_threshold=config.get('depth_threshold', 5.0),
            max_quantity_multiplier=5
        )

        backtester = Backtester(initial_capital=10000)
        test_results = backtester.run(strategy, data)
        metrics = backtester.calculate_metrics()

        # 매수 통계
        buy_signals = test_results[test_results['Signal'] == 1]
        total_quantity = buy_signals['Buy_Quantity'].sum()
        avg_quantity = buy_signals['Buy_Quantity'].mean()
        max_quantity = buy_signals['Buy_Quantity'].max()

        results_summary.append({
            'Config': config['name'],
            'Total Return (%)': metrics['Total Return (%)'],
            'Sharpe Ratio': metrics['Sharpe Ratio'],
            'Max Drawdown (%)': metrics['Max Drawdown (%)'],
            'Win Rate (%)': metrics['Win Rate (%)'],
            'Total Qty': total_quantity,
            'Avg Qty': avg_quantity,
            'Max Qty': max_quantity
        })

    # 결과 출력
    print()
    print(f"{'설정':>30} {'수익률':>10} {'샤프':>8} {'낙폭':>10} {'승률':>8} {'총수량':>8} {'평균':>6} {'최대':>6}")
    print("-" * 100)

    for result in results_summary:
        print(f"{result['Config']:>30} "
              f"{result['Total Return (%)']:>9.2f}% "
              f"{result['Sharpe Ratio']:>8.2f} "
              f"{result['Max Drawdown (%)']:>9.2f}% "
              f"{result['Win Rate (%)']:>7.1f}% "
              f"{result['Total Qty']:>8.0f}주 "
              f"{result['Avg Qty']:>5.1f}주 "
              f"{result['Max Qty']:>5.0f}주")

    print()
    print("💡 해석:")
    print("  - 스케일링 ON: 하락 깊이에 따라 매수 수량 자동 증가")
    print("  - 큰 하락에 더 많이 사서 평균 단가 빠르게 낮춤")
    print("  - 총수량/평균/최대 수량으로 공격성 확인 가능")
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
    print("  - ⭐ 포지션 스케일링: 하락 깊이에 따라 매수 수량 자동 증가")
    print("  - 상승장 대응: 트레일링 매수로 조정 구간마다 진입")
    print("  - 레버리지 ETF의 높은 변동성에 최적화")
    print("  - 하락장에서 지속적으로 매수, 상승장에서 수익 실현")
    print()


if __name__ == "__main__":
    main()
