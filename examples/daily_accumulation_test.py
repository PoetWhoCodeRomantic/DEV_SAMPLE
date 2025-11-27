"""
일일 DCA + 회차별 익절 전략 테스트
매일 종가 기준으로 하락 시 매수, 상승 시 수익난 회차만 익절
"""

import sys
sys.path.append('..')

from src.data.data_fetcher import DataFetcher
from src.strategies.percentage_strategy import DailyDCAStrategy
from src.backtesting.backtester import Backtester
from src.utils.config import Config


def test_daily_accumulation():
    """일일 DCA 전략 (회차별 개별 익절)"""
    print("=" * 80)
    print("[ 일일 DCA + 회차별 익절 전략 ]")
    print("=" * 80)
    print()
    print("전략 설명:")
    print("  1. 매일 종가 체크")
    print("  2. 첫날 무조건 1회 매수")
    print("  3. 전일 종가보다 낮으면 추가 매수")
    print("  4. 전일 종가보다 높으면 각 회차별로 수익난 것만 매도")
    print("  5. ⭐ 평균 매수가 대비 하락 깊이에 따라 매수 수량 자동 증가")
    print()

    # 설정 파일 로드
    config = Config()
    data_config = config.get_data_config()
    backtest_config = config.get_backtest_config()
    strategy_config = config.get_daily_dca_config()

    print("[ 설정 정보 ]")
    print(f"  종목: {data_config['default_symbol']}")
    print(f"  기간: {data_config['period']}")
    print(f"  초기 자본: ${backtest_config['initial_capital']:,}")
    print(f"  최대 회차: {strategy_config['max_positions']}회")
    print(f"  익절 목표: {strategy_config['profit_target_percent']}%")
    print()

    # 데이터 수집
    print(f"{data_config['default_symbol']} 데이터 수집 중...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data(
        data_config['default_symbol'],
        period=data_config['period']
    )
    print(f"데이터 수집 완료: {len(data)} 일")
    print(f"기간: {data.index[0].date()} ~ {data.index[-1].date()}")
    print()

    # 전략 설정 (config.yaml에서 로드)
    strategy = DailyDCAStrategy(**strategy_config)

    # 백테스트 실행
    print("백테스트 실행 중...")
    backtester = Backtester(
        initial_capital=backtest_config['initial_capital'],
        commission=backtest_config['commission'],
        slippage=backtest_config['slippage']
    )
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
    print("[ 파라미터 비교 ] 프리셋별 성과 비교")
    print("=" * 80)
    print()

    # 설정 로드
    config = Config()
    data_config = config.get_data_config()
    backtest_config = config.get_backtest_config()

    # 데이터 수집
    fetcher = DataFetcher()
    data = fetcher.fetch_data(
        data_config['default_symbol'],
        period=data_config['period']
    )

    # 프리셋별 비교
    presets = ['fixed', 'conservative', 'balanced', 'aggressive']
    preset_names = {
        'fixed': '스케일링 OFF (고정)',
        'conservative': '보수적',
        'balanced': '균형잡힌',
        'aggressive': '공격적'
    }
    results_summary = []

    for preset in presets:
        print(f"테스트 중: {preset_names[preset]}...")

        strategy_config = config.get_daily_dca_config(preset)
        strategy = DailyDCAStrategy(**strategy_config)

        backtester = Backtester(
            initial_capital=backtest_config['initial_capital'],
            commission=backtest_config['commission'],
            slippage=backtest_config['slippage']
        )
        test_results = backtester.run(strategy, data)
        metrics = backtester.calculate_metrics()

        # 매수 통계
        buy_signals = test_results[test_results['Signal'] == 1]
        total_quantity = buy_signals['Buy_Quantity'].sum()
        avg_quantity = buy_signals['Buy_Quantity'].mean()
        max_quantity = buy_signals['Buy_Quantity'].max()

        results_summary.append({
            'Config': preset_names[preset],
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
    print("  - 프리셋은 config.yaml에서 설정 가능")
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
