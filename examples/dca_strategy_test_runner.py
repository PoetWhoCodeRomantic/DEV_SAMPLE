"""
DCA 전략 가이드 종합 테스트 실행 파일

DCA_STRATEGY_GUIDE.md에 작성된 모든 테스트 시나리오를 순차적으로 실행합니다:
1. 기본 설정 테스트 (균형잡힌 설정)
2. 4개 프리셋 비교 (균형잡힌, 공격적, 보수적, 스케일링 OFF)
3. 여러 ETF 비교 (TQQQ, SOXL, UPRO)
4. 파라미터별 상세 비교 (profit_target, depth_threshold 등)
5. 종합 결과 요약 및 권장사항
"""

import sys
sys.path.append('..')

from src.data.data_fetcher import DataFetcher
from src.strategies.percentage_strategy import DailyDCAStrategy
from src.backtesting.backtester import Backtester
from src.utils.config import Config
import pandas as pd
from typing import Dict, List, Any


class DCAStrategyTestRunner:
    """DCA 전략 종합 테스트 러너"""

    def __init__(self):
        """초기화"""
        self.config = Config()
        self.data_config = self.config.get_data_config()
        self.backtest_config = self.config.get_backtest_config()
        self.all_results = []

    def print_header(self, title: str, width: int = 100):
        """섹션 헤더 출력"""
        print("\n" + "=" * width)
        print(f"{title:^{width}}")
        print("=" * width + "\n")

    def print_subheader(self, title: str, width: int = 100):
        """서브 섹션 헤더 출력"""
        print("\n" + "-" * width)
        print(f"  {title}")
        print("-" * width + "\n")

    def run_single_test(
        self,
        symbol: str,
        strategy_config: Dict[str, Any],
        test_name: str,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        단일 테스트 실행

        Args:
            symbol: 종목 심볼
            strategy_config: 전략 설정
            test_name: 테스트 이름
            verbose: 상세 출력 여부

        Returns:
            테스트 결과 딕셔너리
        """
        # 데이터 수집
        fetcher = DataFetcher()
        data = fetcher.fetch_data(symbol, period=self.data_config['period'])

        # 전략 생성
        strategy = DailyDCAStrategy(**strategy_config)

        # 백테스트 실행
        backtester = Backtester(
            initial_capital=self.backtest_config['initial_capital'],
            commission=self.backtest_config['commission'],
            slippage=self.backtest_config['slippage']
        )
        results = backtester.run(strategy, data)
        metrics = backtester.calculate_metrics()

        # 거래 통계 수집
        buy_signals = results[results['Signal'] == 1]
        sell_signals = results[results['Signal'] == -1]

        total_bought = buy_signals['Buy_Quantity'].sum() if len(buy_signals) > 0 else 0
        avg_buy_qty = buy_signals['Buy_Quantity'].mean() if len(buy_signals) > 0 else 0
        max_buy_qty = buy_signals['Buy_Quantity'].max() if len(buy_signals) > 0 else 0

        # Buy & Hold 비교
        comparison = backtester.compare_with_buy_and_hold()

        result = {
            'Test Name': test_name,
            'Symbol': symbol,
            'Total Return (%)': metrics['Total Return (%)'],
            'Sharpe Ratio': metrics['Sharpe Ratio'],
            'Sortino Ratio': metrics['Sortino Ratio'],
            'Max Drawdown (%)': metrics['Max Drawdown (%)'],
            'Win Rate (%)': metrics['Win Rate (%)'],
            'Profit Factor': metrics['Profit Factor'],
            'Buy & Hold Return (%)': comparison['Buy & Hold Return (%)'],
            'Excess Return (%)': comparison['Excess Return (%)'],
            'Max Positions': results['Position_Count'].max(),
            'Avg Positions': results['Position_Count'].mean(),
            'Total Buy Days': len(buy_signals),
            'Total Sell Days': len(sell_signals),
            'Total Bought Qty': total_bought,
            'Avg Buy Qty': avg_buy_qty,
            'Max Buy Qty': max_buy_qty,
            'Strategy Config': strategy_config
        }

        if verbose:
            print(f"  종목: {symbol}")
            print(f"  총 수익률: {metrics['Total Return (%)']:>10.2f}%")
            print(f"  샤프 비율: {metrics['Sharpe Ratio']:>10.2f}")
            print(f"  최대 낙폭: {metrics['Max Drawdown (%)']:>10.2f}%")
            print(f"  승률:      {metrics['Win Rate (%)']:>10.1f}%")
            print()

        return result

    def test_1_basic_setup(self):
        """테스트 1: 기본 설정 (균형잡힌 프리셋)"""
        self.print_header("테스트 1: 기본 설정 테스트 (균형잡힌 프리셋)")

        print("[ 전략 설명 ]")
        print("  - 일일 DCA + 회차별 익절 + 트레일링 매수 + 포지션 스케일링")
        print("  - 매일 가격 체크하여 조건 충족 시 자동 매수")
        print("  - 각 회차별 개별 익절 (수익난 회차만 선별 매도)")
        print("  - 평균 매수가 대비 하락 깊이에 따라 매수 수량 자동 증가")
        print()

        strategy_config = self.config.get_daily_dca_config('balanced')

        print("[ 전략 파라미터 ]")
        print(f"  최대 회차:           {strategy_config['max_positions']}회")
        print(f"  익절 목표:           {strategy_config['profit_target_percent']}%")
        print(f"  고점 추적 기간:      {strategy_config['lookback_days']}일")
        print(f"  조정 매수 기준:      {strategy_config['pullback_percent']}%")
        print(f"  포지션 스케일링:     {strategy_config['position_scaling']}")
        print(f"  기본 수량:           {strategy_config['base_quantity']}주")
        print(f"  수량 증가 기준:      {strategy_config['depth_threshold']}%마다")
        print(f"  최대 수량 배수:      {strategy_config['max_quantity_multiplier']}배")
        print()

        print(f"[ 데이터 수집 ]")
        print(f"  종목: {self.data_config['default_symbol']}")
        print(f"  기간: {self.data_config['period']}")
        print(f"  초기 자본: ${self.backtest_config['initial_capital']:,}")
        print()

        result = self.run_single_test(
            self.data_config['default_symbol'],
            strategy_config,
            "기본 설정 (균형잡힌)",
            verbose=False
        )

        self.all_results.append(result)

        # 상세 결과 출력
        print("[ 백테스트 결과 ]")
        print(f"  초기 자본:           ${self.backtest_config['initial_capital']:>10,.2f}")
        print(f"  최종 자본:           ${self.backtest_config['initial_capital'] * (1 + result['Total Return (%)'] / 100):>10,.2f}")
        print(f"  총 수익:             ${self.backtest_config['initial_capital'] * result['Total Return (%)'] / 100:>10,.2f}")
        print(f"  수익률:              {result['Total Return (%)']:>10.2f}%")
        print(f"  샤프 비율:           {result['Sharpe Ratio']:>10.2f}")
        print(f"  소르티노 비율:       {result['Sortino Ratio']:>10.2f}")
        print(f"  최대 낙폭:           {result['Max Drawdown (%)']:>10.2f}%")
        print(f"  승률:                {result['Win Rate (%)']:>10.1f}%")
        print(f"  손익비:              {result['Profit Factor']:>10.2f}")
        print()

        print("[ Buy & Hold 전략 대비 ]")
        print(f"  Buy & Hold 수익률:   {result['Buy & Hold Return (%)']:>10.2f}%")
        print(f"  전략 수익률:         {result['Total Return (%)']:>10.2f}%")
        print(f"  초과 수익률:         {result['Excess Return (%)']:>+10.2f}%")
        print()

        print("[ 거래 통계 ]")
        print(f"  최대 보유 회차:      {result['Max Positions']:>10.0f}회")
        print(f"  평균 보유 회차:      {result['Avg Positions']:>10.1f}회")
        print(f"  총 매수일:           {result['Total Buy Days']:>10.0f}일")
        print(f"  총 매도일:           {result['Total Sell Days']:>10.0f}일")
        print(f"  총 매수 수량:        {result['Total Bought Qty']:>10.0f}주")
        print(f"  평균 매수 수량:      {result['Avg Buy Qty']:>10.1f}주/회")
        print(f"  최대 매수 수량:      {result['Max Buy Qty']:>10.0f}주/회")
        print()

        # 결과 해석
        self._interpret_results(result)

    def test_2_preset_comparison(self):
        """테스트 2: 4개 프리셋 비교"""
        self.print_header("테스트 2: 프리셋별 성과 비교")

        print("[ 비교 대상 프리셋 ]")
        print("  1. 스케일링 OFF (고정) - 전통적 DCA, 항상 고정 수량")
        print("  2. 보수적 - 안정성 중시, 느린 스케일링")
        print("  3. 균형잡힌 - 대부분의 투자자에게 추천")
        print("  4. 공격적 - 고위험 고수익, 빠른 스케일링")
        print()

        presets = ['fixed', 'conservative', 'balanced', 'aggressive']
        preset_names = {
            'fixed': '스케일링 OFF (고정)',
            'conservative': '보수적',
            'balanced': '균형잡힌',
            'aggressive': '공격적'
        }

        preset_results = []

        for preset in presets:
            print(f"테스트 중: {preset_names[preset]}...")
            strategy_config = self.config.get_daily_dca_config(preset)

            result = self.run_single_test(
                self.data_config['default_symbol'],
                strategy_config,
                preset_names[preset],
                verbose=False
            )

            preset_results.append(result)
            self.all_results.append(result)

        # 결과 테이블 출력
        print()
        print(f"{'프리셋':^20} {'수익률':>10} {'샤프':>8} {'낙폭':>10} {'승률':>8} {'총수량':>8} {'평균':>6} {'최대':>6}")
        print("-" * 100)

        for result in preset_results:
            print(f"{result['Test Name']:^20} "
                  f"{result['Total Return (%)']:>9.2f}% "
                  f"{result['Sharpe Ratio']:>8.2f} "
                  f"{result['Max Drawdown (%)']:>9.2f}% "
                  f"{result['Win Rate (%)']:>7.1f}% "
                  f"{result['Total Bought Qty']:>8.0f}주 "
                  f"{result['Avg Buy Qty']:>5.1f}주 "
                  f"{result['Max Buy Qty']:>5.0f}주")

        print()
        print("💡 해석:")
        print("  - 스케일링 ON: 하락 깊이에 따라 매수 수량 자동 증가")
        print("  - 더 공격적일수록 총수량, 평균, 최대 수량이 증가")
        print("  - 공격적 설정은 더 높은 수익 가능성과 더 큰 변동성")
        print("  - 자신의 리스크 성향과 자금 규모에 맞는 프리셋 선택")
        print()

    def test_3_multi_symbol_comparison(self):
        """테스트 3: 여러 ETF 비교"""
        self.print_header("테스트 3: 레버리지 ETF별 성과 비교")

        print("[ 비교 대상 ETF ]")
        print("  - TQQQ: ProShares UltraPro QQQ (나스닥 100 3배)")
        print("  - SOXL: Direxion Daily Semiconductor Bull (반도체 3배)")
        print("  - UPRO: ProShares UltraPro S&P500 (S&P 500 3배)")
        print()
        print("동일한 전략 설정(균형잡힌)으로 각 ETF의 성과를 비교합니다.")
        print()

        symbols = self.data_config['symbols']
        strategy_config = self.config.get_daily_dca_config('balanced')

        symbol_results = []

        for symbol in symbols:
            print(f"테스트 중: {symbol}...")
            result = self.run_single_test(
                symbol,
                strategy_config,
                f"{symbol} (균형잡힌)",
                verbose=False
            )

            symbol_results.append(result)
            self.all_results.append(result)

        # 결과 테이블 출력
        print()
        print(f"{'종목':^10} {'수익률':>10} {'샤프':>8} {'소르티노':>10} {'낙폭':>10} {'승률':>8} {'손익비':>8} {'초과수익':>10}")
        print("-" * 110)

        for result in symbol_results:
            print(f"{result['Symbol']:^10} "
                  f"{result['Total Return (%)']:>9.2f}% "
                  f"{result['Sharpe Ratio']:>8.2f} "
                  f"{result['Sortino Ratio']:>10.2f} "
                  f"{result['Max Drawdown (%)']:>9.2f}% "
                  f"{result['Win Rate (%)']:>7.1f}% "
                  f"{result['Profit Factor']:>8.2f} "
                  f"{result['Excess Return (%)']:>9.2f}%")

        print()
        print("💡 해석:")
        print("  - TQQQ: 가장 인기 있는 레버리지 ETF, 적절한 변동성")
        print("  - SOXL: 반도체 섹터, 높은 변동성으로 더 큰 수익/손실 가능")
        print("  - UPRO: S&P 500 추종, 상대적으로 안정적")
        print("  - 초과수익(+): 전략이 Buy & Hold보다 우수")
        print("  - 초과수익(-): Buy & Hold가 더 우수")
        print()

    def test_4_parameter_sensitivity(self):
        """테스트 4: 파라미터 민감도 분석"""
        self.print_header("테스트 4: 파라미터 민감도 분석")

        # 4-1: profit_target 비교
        self.print_subheader("4-1: 익절 목표 수익률 비교")
        print("익절 목표가 전략 성과에 미치는 영향을 분석합니다.")
        print()

        base_config = self.config.get_daily_dca_config('balanced')
        profit_targets = [1.0, 2.0, 3.0, 5.0, 10.0]

        profit_results = []

        for target in profit_targets:
            config = base_config.copy()
            config['profit_target_percent'] = target

            print(f"테스트 중: 익절 목표 {target}%...")
            result = self.run_single_test(
                self.data_config['default_symbol'],
                config,
                f"익절목표 {target}%",
                verbose=False
            )
            profit_results.append(result)
            self.all_results.append(result)

        print()
        print(f"{'익절목표':>12} {'수익률':>10} {'샤프':>8} {'승률':>8} {'매도일':>8} {'회전율':>8}")
        print("-" * 80)

        for result in profit_results:
            turnover = result['Total Sell Days'] / (result['Total Buy Days'] + 0.001)
            print(f"{result['Test Name']:>12} "
                  f"{result['Total Return (%)']:>9.2f}% "
                  f"{result['Sharpe Ratio']:>8.2f} "
                  f"{result['Win Rate (%)']:>7.1f}% "
                  f"{result['Total Sell Days']:>8.0f} "
                  f"{turnover:>7.2f}x")

        print()
        print("💡 해석:")
        print("  - 낮은 목표(1~2%): 빠른 회전, 높은 승률, 더 많은 수수료")
        print("  - 중간 목표(3~5%): 균형잡힌 설정, 대부분의 상황에 적합")
        print("  - 높은 목표(10%+): 느린 회전, 큰 수익 기대, 변동성 증가")
        print()

        # 4-2: depth_threshold 비교
        self.print_subheader("4-2: 포지션 스케일링 속도 비교")
        print("하락 시 수량 증가 속도가 성과에 미치는 영향을 분석합니다.")
        print()

        depth_thresholds = [3.0, 5.0, 7.0, 10.0]

        depth_results = []

        for threshold in depth_thresholds:
            config = base_config.copy()
            config['depth_threshold'] = threshold

            print(f"테스트 중: {threshold}%마다 수량 증가...")
            result = self.run_single_test(
                self.data_config['default_symbol'],
                config,
                f"{threshold}%마다 증가",
                verbose=False
            )
            depth_results.append(result)
            self.all_results.append(result)

        print()
        print(f"{'스케일링속도':>16} {'수익률':>10} {'샤프':>8} {'낙폭':>10} {'총수량':>8} {'평균':>6} {'최대':>6}")
        print("-" * 100)

        for result in depth_results:
            print(f"{result['Test Name']:>16} "
                  f"{result['Total Return (%)']:>9.2f}% "
                  f"{result['Sharpe Ratio']:>8.2f} "
                  f"{result['Max Drawdown (%)']:>9.2f}% "
                  f"{result['Total Bought Qty']:>8.0f}주 "
                  f"{result['Avg Buy Qty']:>5.1f}주 "
                  f"{result['Max Buy Qty']:>5.0f}주")

        print()
        print("💡 해석:")
        print("  - 작은 임계값(3%): 빠른 스케일링, 많은 자금 필요, 공격적")
        print("  - 중간 임계값(5%): 균형잡힌 스케일링, 대부분에게 적합")
        print("  - 큰 임계값(10%): 느린 스케일링, 보수적, 적은 자금")
        print()

    def test_5_summary_and_recommendations(self):
        """테스트 5: 종합 결과 요약 및 권장사항"""
        self.print_header("테스트 5: 종합 결과 요약 및 권장사항")

        if not self.all_results:
            print("실행된 테스트가 없습니다.")
            return

        # 최고 성과 분석
        print("[ 최고 성과 분석 ]")
        print()

        # 최고 수익률
        best_return = max(self.all_results, key=lambda x: x['Total Return (%)'])
        print(f"✅ 최고 수익률:")
        print(f"   테스트: {best_return['Test Name']}")
        print(f"   종목: {best_return['Symbol']}")
        print(f"   수익률: {best_return['Total Return (%)']:.2f}%")
        print(f"   샤프 비율: {best_return['Sharpe Ratio']:.2f}")
        print()

        # 최고 샤프 비율
        best_sharpe = max(self.all_results, key=lambda x: x['Sharpe Ratio'])
        print(f"✅ 최고 샤프 비율 (위험 대비 수익):")
        print(f"   테스트: {best_sharpe['Test Name']}")
        print(f"   종목: {best_sharpe['Symbol']}")
        print(f"   샤프 비율: {best_sharpe['Sharpe Ratio']:.2f}")
        print(f"   수익률: {best_sharpe['Total Return (%)']:.2f}%")
        print()

        # 최소 낙폭
        best_drawdown = min(self.all_results, key=lambda x: abs(x['Max Drawdown (%)']))
        print(f"✅ 최소 낙폭 (안정성):")
        print(f"   테스트: {best_drawdown['Test Name']}")
        print(f"   종목: {best_drawdown['Symbol']}")
        print(f"   최대 낙폭: {best_drawdown['Max Drawdown (%)']:.2f}%")
        print(f"   수익률: {best_drawdown['Total Return (%)']:.2f}%")
        print()

        # 최고 승률
        best_winrate = max(self.all_results, key=lambda x: x['Win Rate (%)'])
        print(f"✅ 최고 승률:")
        print(f"   테스트: {best_winrate['Test Name']}")
        print(f"   종목: {best_winrate['Symbol']}")
        print(f"   승률: {best_winrate['Win Rate (%)']:.1f}%")
        print(f"   수익률: {best_winrate['Total Return (%)']:.2f}%")
        print()

        # 투자자 유형별 권장사항
        print("=" * 100)
        print("[ 투자자 유형별 권장사항 ]")
        print("=" * 100)
        print()

        print("🟢 초보 투자자 / 보수적 투자자")
        print("   프리셋: 보수적")
        print("   종목: TQQQ 또는 UPRO")
        print("   자금: $1,000 ~ $10,000")
        print("   특징:")
        print("     - 안정적인 수익 추구")
        print("     - 낮은 변동성")
        print("     - 느린 포지션 스케일링")
        print()

        print("🟡 일반 투자자")
        print("   프리셋: 균형잡힌")
        print("   종목: TQQQ")
        print("   자금: $5,000 ~ $20,000")
        print("   특징:")
        print("     - 리스크와 수익의 균형")
        print("     - 대부분의 시장 환경에 적합")
        print("     - 중간 속도 스케일링")
        print()

        print("🔴 경험 많은 투자자 / 공격적 투자자")
        print("   프리셋: 공격적")
        print("   종목: TQQQ 또는 SOXL")
        print("   자금: $20,000+")
        print("   특징:")
        print("     - 고위험 고수익")
        print("     - 높은 변동성 감내")
        print("     - 빠른 포지션 스케일링")
        print()

        print("⚪ 전통적 DCA 선호자")
        print("   프리셋: 스케일링 OFF (고정)")
        print("   종목: TQQQ 또는 UPRO")
        print("   자금: 제한 없음")
        print("   특징:")
        print("     - 예측 가능한 자금 소모")
        print("     - 단순한 전략")
        print("     - 일정한 매수 수량")
        print()

        # 주의사항
        print("=" * 100)
        print("[ ⚠️  중요 주의사항 ]")
        print("=" * 100)
        print()

        print("1. 백테스트 한계:")
        print("   - 과거 성과가 미래 수익을 보장하지 않습니다")
        print("   - 실전에서는 슬리피지, 체결 지연 등 추가 비용 발생")
        print()

        print("2. 레버리지 ETF 리스크:")
        print("   - 높은 변동성으로 큰 손실 가능")
        print("   - 변동성 감쇠(Volatility Decay) 현상")
        print("   - 극단적 시장 상황에서 예상치 못한 손실")
        print()

        print("3. 실전 운용 팁:")
        print("   - 소액으로 시작하여 전략 검증")
        print("   - 정기적인 모니터링 필수")
        print("   - 손절선 설정 (백테스트 최대 낙폭의 1.5배 권장)")
        print("   - 감정적인 파라미터 변경 금지")
        print()

        print("4. 자금 관리:")
        print("   - 필요 자금 = base_qty × 가격 × max_pos × max_mult × 1.5")
        print("   - 충분한 여유 자금 확보")
        print("   - 분산 투자 고려 (여러 ETF)")
        print()

    def _interpret_results(self, result: Dict[str, Any]):
        """결과 해석 및 평가"""
        print("[ 결과 해석 ]")

        # 수익률 평가
        if result['Total Return (%)'] >= 30:
            print(f"  ✅ 수익률 {result['Total Return (%)']:.2f}% - 우수! (연 30%+ 목표 달성)")
        elif result['Total Return (%)'] >= 20:
            print(f"  ✅ 수익률 {result['Total Return (%)']:.2f}% - 좋음! (연 20%+ 목표 달성)")
        elif result['Total Return (%)'] >= 10:
            print(f"  ⚠️  수익률 {result['Total Return (%)']:.2f}% - 보통 (개선 여지 있음)")
        else:
            print(f"  ❌ 수익률 {result['Total Return (%)']:.2f}% - 낮음 (파라미터 조정 필요)")

        # 샤프 비율 평가
        if result['Sharpe Ratio'] >= 2.0:
            print(f"  ✅ 샤프 비율 {result['Sharpe Ratio']:.2f} - 매우 좋음! (위험 대비 수익 우수)")
        elif result['Sharpe Ratio'] >= 1.5:
            print(f"  ✅ 샤프 비율 {result['Sharpe Ratio']:.2f} - 좋음!")
        elif result['Sharpe Ratio'] >= 1.0:
            print(f"  ⚠️  샤프 비율 {result['Sharpe Ratio']:.2f} - 보통")
        else:
            print(f"  ❌ 샤프 비율 {result['Sharpe Ratio']:.2f} - 낮음 (변동성 대비 수익 부족)")

        # 최대 낙폭 평가
        if abs(result['Max Drawdown (%)']) <= 15:
            print(f"  ✅ 최대 낙폭 {result['Max Drawdown (%)']:.2f}% - 우수! (레버리지 대비 낮음)")
        elif abs(result['Max Drawdown (%)']) <= 25:
            print(f"  ⚠️  최대 낙폭 {result['Max Drawdown (%)']:.2f}% - 보통 (감내 가능)")
        else:
            print(f"  ❌ 최대 낙폭 {result['Max Drawdown (%)']:.2f}% - 높음 (리스크 크다)")

        # 승률 평가
        if result['Win Rate (%)'] >= 70:
            print(f"  ✅ 승률 {result['Win Rate (%)']:.1f}% - 매우 좋음!")
        elif result['Win Rate (%)'] >= 60:
            print(f"  ✅ 승률 {result['Win Rate (%)']:.1f}% - 좋음!")
        else:
            print(f"  ⚠️  승률 {result['Win Rate (%)']:.1f}% - 개선 필요")

        print()

        # 종합 평가
        good_count = 0
        if result['Total Return (%)'] >= 20:
            good_count += 1
        if result['Sharpe Ratio'] >= 1.5:
            good_count += 1
        if abs(result['Max Drawdown (%)']) <= 20:
            good_count += 1
        if result['Win Rate (%)'] >= 65:
            good_count += 1

        if good_count >= 3:
            print("  ✨ 종합 평가: 우수! 이 파라미터로 실전 운용 가능")
        elif good_count >= 2:
            print("  💡 종합 평가: 양호. 약간의 조정으로 개선 가능")
        else:
            print("  ⚠️  종합 평가: 파라미터 조정 필요")
            print("     권장 조정 방향:")
            if result['Sharpe Ratio'] < 1.0:
                print("       - max_positions 줄이기 (리스크 감소)")
                print("       - depth_threshold 높이기 (스케일링 속도 늦추기)")
            if abs(result['Max Drawdown (%)']) > 25:
                print("       - profit_target 낮추기 (빠른 익절)")
                print("       - max_quantity_multiplier 줄이기")

        print()

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n")
        print("╔" + "═" * 118 + "╗")
        print("║" + " " * 30 + "DCA 전략 가이드 종합 테스트 실행 프로그램" + " " * 46 + "║")
        print("║" + " " * 35 + "DCA_STRATEGY_GUIDE.md 기반" + " " * 55 + "║")
        print("╚" + "═" * 118 + "╝")

        # 테스트 1: 기본 설정
        self.test_1_basic_setup()

        # 테스트 2: 프리셋 비교
        print("\n" + "▼" * 100 + "\n")
        self.test_2_preset_comparison()

        # 테스트 3: 여러 ETF 비교
        print("\n" + "▼" * 100 + "\n")
        self.test_3_multi_symbol_comparison()

        # 테스트 4: 파라미터 민감도
        print("\n" + "▼" * 100 + "\n")
        self.test_4_parameter_sensitivity()

        # 테스트 5: 종합 요약
        print("\n" + "▼" * 100 + "\n")
        self.test_5_summary_and_recommendations()

        # 완료 메시지
        print()
        print("=" * 100)
        print("모든 테스트 완료!")
        print("=" * 100)
        print()
        print(f"총 {len(self.all_results)}개 테스트 실행 완료")
        print()
        print("💡 다음 단계:")
        print("  1. 위 결과를 바탕으로 자신에게 맞는 프리셋 선택")
        print("  2. config.yaml에서 해당 프리셋 활성화")
        print("  3. 소액으로 실전 테스트 시작")
        print("  4. 정기적인 모니터링 및 조정")
        print()
        print("📚 추가 정보:")
        print("  - 전략 상세 설명: DCA_STRATEGY_GUIDE.md")
        print("  - 설정 파일 가이드: config.yaml")
        print("  - 데이터베이스 가이드: DATABASE_GUIDE.md")
        print()


def main():
    """메인 함수"""
    runner = DCAStrategyTestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()
