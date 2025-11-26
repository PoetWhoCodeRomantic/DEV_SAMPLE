# 레버리지 ETF 퀀트 트레이딩 시뮬레이션

TQQQ, SOXL 등 변동성이 큰 레버리지 ETF의 과거 데이터를 분석하고, **퍼센트 기반의 실용적인 트레이딩 전략**을 시뮬레이션하고 검증하는 프로그램입니다.

## 💡 핵심 특징

복잡한 기술적 지표 대신, **가격 변동률(%)을 기반으로 한 명확하고 단순한 매매 전략**을 제공합니다.
- "N% 하락 시 매수, M% 상승 시 매도"와 같은 직관적인 조건
- 하락폭에 따른 비중 조절 (피라미딩)
- 레버리지 ETF의 높은 변동성에 최적화된 전략

## 주요 기능

### 📊 데이터 수집
- yfinance를 활용한 레버리지 ETF 실시간 데이터 수집
- TQQQ, SOXL, UPRO, TNA, FNGU 등 주요 3배 레버리지 ETF 지원
- 다양한 기간 및 인터벌 설정 가능

### 🎯 퍼센트 기반 트레이딩 전략 (주요 전략)

1. **하락률 매수 전략** (PercentageDropBuyStrategy)
   - N% 하락 시 매수
   - M% 상승 시 매도
   - 예: 5% 하락 시 매수, 3% 상승 시 매도

2. **피라미딩 전략** (PyramidingStrategy)
   - 하락폭에 따라 매수 비중 증가
   - 예: 3% 하락 → 20% 투자, 5% 하락 → 30% 투자, 10% 하락 → 50% 투자
   - 목표 수익률 도달 시 전량 매도

3. **그리드 트레이딩** (GridTradingStrategy)
   - 일정 간격(%)으로 매수/매도 주문 배치
   - 예: 3% 간격으로 10개 그리드 설정
   - 변동성 장세에서 효과적

4. **정액 적립식 투자** (DollarCostAveragingStrategy)
   - 일정 기간마다 자동 매수
   - 목표 수익률 도달 시 매도
   - 장기 투자에 적합

5. **변동성 돌파 전략** (VolatilityBreakoutStrategy)
   - 전일 변동폭의 N% 돌파 시 매수
   - 손절/익절 기준 설정 가능

6. **복합 퍼센트 전략** (CombinedPercentageStrategy)
   - 여러 하락/상승 구간에서 각각 다른 비중으로 매매
   - 예: 3% 하락 시 30% 매수, 7% 하락 시 70% 매수
   - 매도도 단계별로 설정 가능

### 📈 기술적 지표 기반 전략 (레거시)

<details>
<summary>클릭하여 펼치기</summary>

- **모멘텀 전략**: 이동평균선 크로스오버
- **평균 회귀 전략**: 볼린저 밴드, Z-Score
- **RSI 전략**: 과매수/과매도
- **MACD 전략**: 크로스오버

기술적 지표 계산 유틸리티:
- 이동평균: SMA, EMA
- 모멘텀: RSI, MACD, Stochastic, ADX
- 변동성: Bollinger Bands, ATR
- 거래량: OBV, VWAP

</details>

### 🔬 백테스팅 엔진
- 실제 거래 비용 (수수료, 슬리피지) 반영
- 포트폴리오 가치 추적
- 드로우다운 분석
- Buy & Hold 전략과 비교

### 📊 성과 분석
- **수익률 분석**: 총 수익률, 연율화 수익률, 월별/연도별 수익률
- **리스크 지표**: Sharpe Ratio, Sortino Ratio, Calmar Ratio
- **드로우다운**: 최대 드로우다운, 평균 드로우다운 기간
- **거래 분석**: 승률, 손익비, 평균 승/패, 거래 횟수
- **리스크 메트릭**: VaR, CVaR, 변동성

### 📉 시각화
- 가격 및 거래량 차트
- 캔들스틱 차트 (Plotly 인터랙티브)
- 백테스트 결과 시각화
- 기술적 지표 차트
- 상관관계 히트맵

## 프로젝트 구조

```
.
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   └── data_fetcher.py          # 데이터 수집
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base_strategy.py         # 기본 전략 클래스
│   │   ├── percentage_strategy.py   # ⭐ 퍼센트 기반 전략 (주요)
│   │   ├── momentum_strategy.py     # 모멘텀 전략 (레거시)
│   │   ├── mean_reversion_strategy.py  # 평균 회귀 전략 (레거시)
│   │   ├── rsi_strategy.py          # RSI 전략 (레거시)
│   │   └── macd_strategy.py         # MACD 전략 (레거시)
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── backtester.py            # 백테스팅 엔진
│   │   └── performance.py           # 성과 분석
│   └── utils/
│       ├── __init__.py
│       ├── indicators.py            # 기술적 지표 (레거시)
│       └── visualization.py         # 시각화
├── examples/
│   ├── percentage_strategy_example.py   # ⭐ 퍼센트 전략 예제 (추천)
│   ├── custom_percentage_test.py        # ⭐ 커스텀 조건 테스트 (추천)
│   ├── basic_example.py                 # 기본 예제
│   ├── strategy_comparison.py           # 전략 비교
│   └── parameter_optimization.py        # 파라미터 최적화
├── tests/
├── requirements.txt
└── README.md
```

## 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd DEV_SAMPLE
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

## 사용 방법

### ⭐ 퍼센트 기반 전략 예제 (추천)

```python
from src.data.data_fetcher import DataFetcher
from src.strategies.percentage_strategy import PercentageDropBuyStrategy
from src.backtesting.backtester import Backtester

# 1. 데이터 수집
fetcher = DataFetcher()
data = fetcher.fetch_data('TQQQ', period='2y')

# 2. 전략 설정: 5% 하락 시 매수, 3% 상승 시 매도
strategy = PercentageDropBuyStrategy(
    drop_percent=5.0,      # 5% 하락 시 매수
    sell_profit_percent=3.0  # 3% 상승 시 매도
)

# 3. 백테스트 실행
backtester = Backtester(initial_capital=10000)
results = backtester.run(strategy, data)

# 4. 결과 출력
backtester.print_summary()
```

### 💰 피라미딩 전략 (하락 시 비중 늘리기)

```python
from src.strategies.percentage_strategy import PyramidingStrategy

# 하락폭에 따라 단계적으로 비중 증가
strategy = PyramidingStrategy(
    buy_levels=[
        (3.0, 0.2),   # 3% 하락 → 20% 투자
        (5.0, 0.3),   # 5% 하락 → 30% 투자
        (8.0, 0.3),   # 8% 하락 → 30% 투자
        (12.0, 0.2)   # 12% 하락 → 20% 투자
    ],
    sell_profit_percent=5.0  # 5% 수익 시 전량 매도
)
```

### 📊 복합 전략 (매수/매도 단계별 조절)

```python
from src.strategies.percentage_strategy import CombinedPercentageStrategy

strategy = CombinedPercentageStrategy(
    buy_conditions=[
        (5.0, 0.4),    # 5% 하락 → 40% 매수
        (10.0, 0.6),   # 10% 하락 → 60% 매수
        (15.0, 1.0)    # 15% 하락 → 100% 매수
    ],
    sell_conditions=[
        (8.0, 0.5),    # 8% 상승 → 50% 매도
        (15.0, 1.0)    # 15% 상승 → 100% 매도
    ]
)
```

### 예제 스크립트 실행

```bash
cd examples

# ⭐ 퍼센트 전략 종합 테스트 (추천)
python percentage_strategy_example.py

# ⭐ 커스텀 조건으로 테스트 (추천)
python custom_percentage_test.py

# 기본 예제
python basic_example.py

# 여러 전략 비교
python strategy_comparison.py

# 파라미터 최적화
python parameter_optimization.py
```

## 지원하는 레버리지 ETF

| 심볼 | 설명 | 레버리지 |
|------|------|----------|
| TQQQ | ProShares UltraPro QQQ | 3x |
| SOXL | Direxion Daily Semiconductor Bull | 3x |
| UPRO | ProShares UltraPro S&P500 | 3x |
| TNA | Direxion Daily Small Cap Bull | 3x |
| FNGU | MicroSectors FANG+ Index | 3x |
| TECL | Direxion Daily Technology Bull | 3x |
| CURE | Direxion Daily Healthcare Bull | 3x |
| LABU | Direxion Daily S&P Biotech Bull | 3x |
| DFEN | Direxion Daily Aerospace & Defense Bull | 3x |
| SPXL | Direxion Daily S&P 500 Bull | 3x |

## 커스텀 전략 만들기

### 퍼센트 기반 커스텀 전략

```python
from src.strategies.base_strategy import BaseStrategy
import pandas as pd

class MyPercentageStrategy(BaseStrategy):
    """
    나만의 퍼센트 전략
    예: 연속 2일 하락 후 추가 3% 하락 시 매수
    """
    def __init__(self, drop_threshold=3.0):
        super().__init__(name="MyPercentageStrategy")
        self.drop_threshold = drop_threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # 일일 변동률 계산
        df['Daily_Change'] = df['Close'].pct_change() * 100

        # 2일 연속 하락 확인
        df['Consecutive_Drop'] = (
            (df['Daily_Change'] < 0) &
            (df['Daily_Change'].shift(1) < 0)
        )

        # 시그널 생성
        df['Signal'] = 0

        # 연속 하락 후 threshold 이상 하락 시 매수
        buy_condition = (
            df['Consecutive_Drop'] &
            (df['Daily_Change'] <= -self.drop_threshold)
        )
        df.loc[buy_condition, 'Signal'] = 1

        # 5% 수익 시 매도
        df['Returns_From_Entry'] = (df['Close'] / df['Close'].shift(1) - 1) * 100
        df.loc[df['Returns_From_Entry'] >= 5.0, 'Signal'] = -1

        return df
```

### 실전 예제: 나만의 조건 설정

```python
# 예제 1: 급락 구간 물타기 전략
from src.strategies.percentage_strategy import PyramidingStrategy

my_strategy = PyramidingStrategy(
    buy_levels=[
        (5.0, 0.25),    # 5% 하락 → 자본의 25% 투자
        (10.0, 0.35),   # 10% 하락 → 추가 35% 투자
        (15.0, 0.40),   # 15% 하락 → 추가 40% 투자 (총 100%)
    ],
    sell_profit_percent=7.0  # 7% 수익 시 전량 매도
)

# 예제 2: 보수적 전략
from src.strategies.percentage_strategy import PercentageDropBuyStrategy

conservative_strategy = PercentageDropBuyStrategy(
    drop_percent=10.0,       # 큰 폭 하락 시에만 매수
    sell_profit_percent=5.0  # 작은 수익에도 매도
)

# 예제 3: 공격적 전략
aggressive_strategy = PercentageDropBuyStrategy(
    drop_percent=3.0,        # 작은 하락에도 매수
    sell_profit_percent=10.0 # 큰 수익 노리기
)
```

## 성과 지표

### 수익률 지표
- **Total Return**: 총 수익률
- **Sharpe Ratio**: 위험 대비 수익률 (연율화)
- **Sortino Ratio**: 하방 위험 대비 수익률
- **Calmar Ratio**: 최대 드로우다운 대비 수익률

### 리스크 지표
- **Max Drawdown**: 최대 낙폭
- **Volatility**: 변동성 (연율화)
- **VaR (Value at Risk)**: 손실 위험 값
- **CVaR (Conditional VaR)**: 조건부 손실 위험 값

### 거래 지표
- **Win Rate**: 승률
- **Profit Factor**: 손익비
- **Number of Trades**: 총 거래 횟수
- **Average Win/Loss**: 평균 승/패

## 주의사항

⚠️ **면책 조항**

이 프로그램은 교육 및 연구 목적으로만 제작되었습니다.
- 실제 투자 결정에 사용하기 전에 반드시 충분한 검토가 필요합니다
- 과거 성과가 미래 수익을 보장하지 않습니다
- 레버리지 ETF는 높은 변동성과 리스크를 가지고 있습니다
- 실제 투자 시 반드시 전문가와 상담하시기 바랍니다

## 라이선스

MIT License

## 기여하기

이슈와 Pull Request를 환영합니다!

## 문의

프로젝트 관련 문의사항은 Issues를 통해 남겨주세요.

---

**Happy Trading! 📈**
