"""
파라미터 최적화 예제
RSI 전략의 최적 파라미터를 그리드 서치로 찾기
"""

import sys
sys.path.append('..')

from src.data.data_fetcher import DataFetcher
from src.strategies.rsi_strategy import RSIStrategy
from src.backtesting.backtester import Backtester


def main():
    print("=" * 80)
    print("파라미터 최적화 예제 - RSI 전략")
    print("=" * 80)
    print()

    # 1. 데이터 수집
    print("1. TQQQ 데이터 수집 중...")
    fetcher = DataFetcher()
    data = fetcher.fetch_data('TQQQ', period='2y')
    print(f"   데이터 수집 완료: {len(data)} 행")
    print()

    # 2. 파라미터 그리드 정의
    print("2. 파라미터 그리드 정의")
    param_grid = {
        'period': [10, 14, 20],
        'oversold': [20, 25, 30],
        'overbought': [70, 75, 80],
    }

    print("   테스트할 파라미터 조합:")
    for key, values in param_grid.items():
        print(f"     {key}: {values}")

    total_combinations = 1
    for values in param_grid.values():
        total_combinations *= len(values)
    print(f"   총 {total_combinations}개 조합")
    print()

    # 3. 최적화 실행
    print("3. 그리드 서치 실행 중...")
    backtester = Backtester(initial_capital=10000)

    optimization_result = backtester.optimize_parameters(
        strategy_class=RSIStrategy,
        data=data,
        param_grid=param_grid,
        metric='Sharpe Ratio'
    )

    print("   최적화 완료!")
    print()

    # 4. 결과 출력
    print("4. 최적화 결과")
    print("=" * 80)
    print()

    best_params = optimization_result['best_params']
    best_score = optimization_result['best_score']
    best_metrics = optimization_result['best_metrics']

    print("[ 최적 파라미터 ]")
    for key, value in best_params.items():
        print(f"  {key:.<30} {value:>10}")
    print()

    print(f"[ 최적 스코어 (Sharpe Ratio) ]")
    print(f"  {best_score:.4f}")
    print()

    print("[ 상세 성과 지표 ]")
    for key, value in best_metrics.items():
        if isinstance(value, float):
            if 'Ratio' in key or 'Factor' in key:
                print(f"  {key:.<40} {value:>10.2f}")
            elif '%' in key:
                print(f"  {key:.<40} {value:>10.2f}%")
            else:
                print(f"  {key:.<40} ${value:>10,.2f}")
        else:
            print(f"  {key:.<40} {value:>10}")

    # 5. 최적 전략으로 재실행 및 시각화
    print("\n5. 최적 전략으로 재실행")
    print("-" * 80)

    optimal_strategy = RSIStrategy(**best_params)
    backtester_final = Backtester(initial_capital=10000)
    final_results = backtester_final.run(optimal_strategy, data)

    print(f"전략: {optimal_strategy.name}")
    print()
    backtester_final.print_summary()

    print("\n" + "=" * 80)
    print("최적화 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
