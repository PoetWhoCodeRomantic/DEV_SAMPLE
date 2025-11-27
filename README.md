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

7. **일일 DCA + 회차별 익절 + 트레일링 매수 + 포지션 스케일링** (DailyDCAStrategy) ⭐ NEW
   - **스마트 매수**: ① 전일 대비 하락 OR ② 최근 고점 대비 N% 하락
   - **상승장 대응**: 상승 추세에서도 조정 구간마다 자동 매수
   - **포지션 스케일링**: 하락 깊이에 따라 매수 수량 자동 증가 (5% 하락→1주, 10% 하락→2주, 15% 하락→3주...)
   - **회차별 익절**: 각 매수 회차별로 3% 이상 수익난 것만 개별 매도
   - **평균 단가 개선**: 큰 하락에 더 많이 사서 평균 단가 빠르게 낮춤
   - 레버리지 ETF의 높은 변동성에 최적화된 전략

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
├── config.yaml                          # ⭐ 설정 파일
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_fetcher.py          # 데이터 수집
│   │   └── database.py              # SQLite 데이터베이스
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
│       ├── config.py                # ⭐ 설정 로더
│       ├── indicators.py            # 기술적 지표 (레거시)
│       └── visualization.py         # 시각화
├── examples/
│   ├── daily_accumulation_test.py       # ⭐ 일일 DCA 전략 (config 사용)
│   ├── percentage_strategy_example.py   # 퍼센트 전략 예제
│   ├── custom_percentage_test.py        # 커스텀 조건 테스트
│   ├── basic_example.py                 # 기본 예제
│   ├── strategy_comparison.py           # 전략 비교
│   └── parameter_optimization.py        # 파라미터 최적화
├── tests/
├── requirements.txt
├── README.md
├── DCA_STRATEGY_GUIDE.md            # DailyDCA 전략 가이드
└── DATABASE_GUIDE.md                # 데이터베이스 가이드
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

### 4. 설정 파일 확인 및 수정
`config.yaml` 파일에서 종목, 기간, 전략 파라미터 등을 설정할 수 있습니다.

```yaml
# config.yaml
data:
  default_symbol: TQQQ  # 기본 종목
  period: 1y            # 데이터 기간
  symbols:              # 수집할 종목 리스트
    - TQQQ
    - SOXL
    - UPRO

backtest:
  initial_capital: 10000  # 초기 자본
  commission: 0.001       # 수수료
  slippage: 0.001         # 슬리피지

strategies:
  daily_dca:
    max_positions: 10
    profit_target_percent: 3.0
    # ... 기타 파라미터
```

## 사용 방법

### ⭐ 설정 파일 기반 사용 (추천)

#### 1. config.yaml 설정

프로젝트 루트의 `config.yaml` 파일에서 모든 설정을 관리할 수 있습니다:

```yaml
# 데이터 수집 설정
data:
  default_symbol: TQQQ    # 테스트할 종목
  period: 1y              # 1년치 데이터

# 백테스트 설정
backtest:
  initial_capital: 10000  # 초기 자본 $10,000

# 전략 설정
strategies:
  daily_dca:
    max_positions: 10
    profit_target_percent: 3.0
    position_scaling: true
    depth_threshold: 5.0
```

#### 2. 프리셋 사용

`config.yaml`에는 미리 정의된 4가지 프리셋이 있습니다:
- `balanced`: 균형잡힌 설정 (추천)
- `aggressive`: 공격적 설정
- `conservative`: 보수적 설정
- `fixed`: 스케일링 OFF

```python
from src.utils.config import Config
from src.strategies.percentage_strategy import DailyDCAStrategy

# Config 로드
config = Config()

# 프리셋 사용
strategy_config = config.get_daily_dca_config('aggressive')
strategy = DailyDCAStrategy(**strategy_config)
```

#### 3. 예제 실행

설정 파일을 사용하는 예제:

```bash
cd examples
python daily_accumulation_test.py  # config.yaml 설정 자동 사용
```

### 퍼센트 기반 전략 예제 (코드에서 직접 설정)

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

### ⭐ 일일 DCA + 회차별 익절 + 트레일링 매수 + 포지션 스케일링 (NEW!)

```python
from src.strategies.percentage_strategy import DailyDCAStrategy

# 균형잡힌 설정 (추천) ⭐ 포지션 스케일링 활성화
strategy = DailyDCAStrategy(
    max_positions=10,              # 최대 10회까지 매수
    profit_target_percent=3.0,     # 각 회차별 3% 익절
    first_day_buy=True,            # 첫날 무조건 매수
    lookback_days=7,               # 최근 7일 고점 추적
    pullback_percent=3.0,          # 고점 대비 3% 하락 시 매수
    position_scaling=True,         # ⭐ 포지션 스케일링 활성화
    base_quantity=1,               # 기본 1주
    depth_threshold=5.0,           # 평균가 대비 5%마다 수량 증가
    max_quantity_multiplier=5      # 최대 5배
)

# 공격적 설정 (빈번한 매수 + 빠른 스케일링)
strategy_aggressive = DailyDCAStrategy(
    max_positions=15,
    profit_target_percent=2.0,
    lookback_days=5,
    pullback_percent=2.0,
    position_scaling=True,
    depth_threshold=3.0,           # 평균가 대비 3%마다 수량 증가
    max_quantity_multiplier=10     # 최대 10배
)

# 보수적 설정 (선별적 매수 + 느린 스케일링)
strategy_conservative = DailyDCAStrategy(
    max_positions=10,
    profit_target_percent=5.0,
    lookback_days=10,
    pullback_percent=5.0,
    position_scaling=True,
    depth_threshold=10.0,          # 평균가 대비 10%마다 수량 증가
    max_quantity_multiplier=3      # 최대 3배
)

# 스케일링 OFF (고정 수량)
strategy_fixed = DailyDCAStrategy(
    max_positions=10,
    profit_target_percent=3.0,
    position_scaling=False,        # 스케일링 비활성화
    base_quantity=1                # 항상 1주씩만 매수
)

# 동작 방식 (평균 매수가 기준 포지션 스케일링):
# - 1일차: $100에 1주 매수 (평균가 $100)
# - 2일차: $95 → 평균($100) 대비 5% 하락 → 2주 매수 (평균가 $96.67)
# - 3일차: $90 → 평균($96.67) 대비 6.9% 하락 → 2주 매수 (평균가 $93.75)
# - 4일차: $97 (+7.7%) → 3% 이상 수익난 회차 개별 매도 (1일차, 2일차 매도)
# - 5일차: $93 → 남은 평균가 대비 조정 → 수량 재계산하여 매수
# - 각 회차별 매수가를 개별 추적하여 수익난 회차만 먼저 매도
# - ⭐ 평균 매수가 대비 하락 깊이로 수량 자동 증가 → 평균 단가 빠르게 낮춤
```

### 예제 스크립트 실행

```bash
cd examples

# ⭐ 일일 누적 매수 전략 테스트 (NEW!)
python daily_accumulation_test.py

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

## 🎯 그리드 트레이딩 전략 상세 가이드

### 📖 그리드 트레이딩이란?

그리드 트레이딩은 **일정한 가격 간격(%)으로 매수/매도 주문을 미리 배치**하는 전략입니다. 마치 그물망(Grid)처럼 여러 가격대에 주문을 걸어놓고, 가격이 움직일 때마다 자동으로 매매가 체결되는 방식입니다.

### 💡 작동 원리

```
중심 가격: $100

매도 그리드:
├─ $115 (15% ↑) ─ 매도 주문
├─ $112 (12% ↑) ─ 매도 주문
├─ $109 (9% ↑)  ─ 매도 주문
├─ $106 (6% ↑)  ─ 매도 주문
├─ $103 (3% ↑)  ─ 매도 주문
│
└─ $100 (중심)
│
매수 그리드:
├─ $97  (3% ↓)  ─ 매수 주문
├─ $94  (6% ↓)  ─ 매수 주문
├─ $91  (9% ↓)  ─ 매수 주문
├─ $88  (12% ↓) ─ 매수 주문
└─ $85  (15% ↓) ─ 매수 주문
```

가격이 $97로 하락하면 자동 매수 → 다시 $103으로 상승하면 자동 매도 → 6% 수익!

### ✅ 장점

1. **변동성을 수익으로 전환**
   - 레버리지 ETF의 높은 변동성을 활용
   - 방향 예측 불필요, 단순히 움직임만 있으면 수익

2. **감정 배제**
   - 미리 정해진 규칙대로 자동 매매
   - 패닉 매도나 욕심으로 인한 실수 방지

3. **지속적인 수익 창출**
   - 횡보장에서 특히 효과적
   - 매일 작은 수익을 누적

4. **리스크 분산**
   - 여러 가격대에 분할 매수/매도
   - 한 번에 올인하지 않음

### ⚠️ 주의사항

1. **강한 추세장에서는 불리**
   - 지속적인 상승장: 일찍 매도하여 기회 손실
   - 지속적인 하락장: 계속 매수하다가 자금 고갈

2. **자금 관리 중요**
   - 각 그리드에 투입할 자금 미리 계산
   - 너무 많은 그리드는 자금 부족 위험

3. **적절한 간격 설정 필요**
   - 간격이 너무 좁으면: 빈번한 거래, 수수료 손실
   - 간격이 너무 넓으면: 거래 기회 감소

### 🚀 레버리지 ETF에 최적인 이유

레버리지 ETF는 **하루에도 5~10% 이상 움직이는 경우가 많습니다**. 이런 높은 변동성이 그리드 트레이딩의 최고의 먹잇감입니다!

```python
# TQQQ 예시 (실제 데이터 기반)
# 하루 변동폭: 평균 7~12%
# 한 주 변동폭: 20~30%

# 3% 간격 그리드 설정 시
# → 하루에 2~4회 거래 발생 가능
# → 각 거래마다 3~6% 수익
```

### 📊 실전 예제

#### 예제 1: 기본 그리드 트레이딩

```python
from src.data.data_fetcher import DataFetcher
from src.strategies.percentage_strategy import GridTradingStrategy
from src.backtesting.backtester import Backtester

# 데이터 수집
fetcher = DataFetcher()
data = fetcher.fetch_data('TQQQ', period='1y')

# 그리드 전략 설정
strategy = GridTradingStrategy(
    grid_size=3.0,      # 3% 간격
    num_grids=10,       # 10개 그리드 (상/하 각 5개)
    center_price=None   # None이면 시작 가격을 중심으로
)

# 백테스트 실행
backtester = Backtester(initial_capital=10000)
results = backtester.run(strategy, data)
backtester.print_summary()
```

#### 예제 2: 보수적 설정 (큰 간격)

```python
# 큰 변동에만 반응 - 안정적이지만 거래 빈도 낮음
strategy = GridTradingStrategy(
    grid_size=5.0,      # 5% 간격 (보수적)
    num_grids=8,        # 8개 그리드
)
```

#### 예제 3: 공격적 설정 (작은 간격)

```python
# 작은 변동에도 반응 - 거래 빈도 높음, 수수료 주의
strategy = GridTradingStrategy(
    grid_size=2.0,      # 2% 간격 (공격적)
    num_grids=15,       # 15개 그리드
)
```

#### 예제 4: 중심 가격 고정

```python
# 현재 가격이 $50이라고 가정
strategy = GridTradingStrategy(
    grid_size=3.0,
    num_grids=10,
    center_price=50.0   # $50을 중심으로 그리드 생성
)
```

### 🎨 파라미터 선택 가이드

#### grid_size (그리드 간격)

| 간격 | 특성 | 추천 대상 |
|------|------|-----------|
| 1~2% | 매우 공격적, 거래 빈번 | 초단타 트레이더, 수수료 낮은 경우 |
| 3~4% | 균형잡힌 설정 | **대부분의 투자자 추천** |
| 5~7% | 보수적, 안정적 | 장기 투자자, 큰 변동만 노리는 경우 |
| 8%+ | 매우 보수적 | 극단적 변동만 활용 |

#### num_grids (그리드 개수)

| 개수 | 자금 활용 | 추천 자본 |
|------|-----------|-----------|
| 5~8개 | 낮음 (50~60%) | 소액 ($1,000 미만) |
| 10~15개 | 중간 (70~80%) | 중액 ($1,000~10,000) |
| 15~20개 | 높음 (90%+) | 고액 ($10,000+) |

### 💰 수익 계산 예시

```
초기 자본: $10,000
그리드 간격: 3%
그리드 개수: 10개 (상/하 각 5개)
각 그리드 투자금: $1,000

시나리오:
1. 가격 3% 하락 → $1,000 매수
2. 가격 6% 상승 → $1,000 매도
3. 수익: $1,000 × 0.06 = $60

하루 2회 거래 × 20 거래일 = 월 40회
월 예상 수익: $60 × 40 = $2,400 (24%)

※ 실제로는 수수료, 슬리피지, 시장 상황에 따라 변동
```

### 🔧 최적화 팁

1. **백테스트로 최적 간격 찾기**
   ```python
   # parameter_optimization.py 참고
   # 다양한 grid_size를 테스트하여 최적값 탐색
   ```

2. **변동성에 따라 조정**
   - 변동성 높을 때: 간격 넓히기 (4~5%)
   - 변동성 낮을 때: 간격 좁히기 (2~3%)

3. **부분 청산 전략**
   - 큰 수익 발생 시 일부 그리드 청산
   - 남은 자금으로 새로운 중심가 설정

4. **손절선 설정**
   - 중심가에서 ±20~30% 이상 벗어나면 전략 재설정 고려

### 📈 실전 운용 예시

```python
# 실전 추천 설정 (TQQQ 기준)
strategy = GridTradingStrategy(
    grid_size=3.5,      # 3.5% 간격 (적당한 거래 빈도)
    num_grids=12,       # 12개 그리드 (충분한 대응 범위)
    center_price=None   # 시작 가격을 중심으로
)

# 초기 자본 $10,000 기준
# - 각 그리드: 약 $833
# - 최대 하락 대응: 21% (3.5% × 6)
# - 최대 상승 대응: 21% (3.5% × 6)
# - 예상 월 거래: 30~50회
# - 목표 월 수익률: 10~20%
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
