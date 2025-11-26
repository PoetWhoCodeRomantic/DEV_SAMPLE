# 레버리지 ETF 퀀트 트레이딩 시뮬레이션

TQQQ, SOXL 등 변동성이 큰 레버리지 ETF의 과거 데이터를 분석하고, 효율적인 퀀트 트레이딩 전략을 시뮬레이션하고 검증하는 프로그램입니다.

## 주요 기능

### 📊 데이터 수집
- yfinance를 활용한 레버리지 ETF 실시간 데이터 수집
- TQQQ, SOXL, UPRO, TNA, FNGU 등 주요 3배 레버리지 ETF 지원
- 다양한 기간 및 인터벌 설정 가능

### 📈 기술적 지표
- **이동평균**: SMA, EMA
- **모멘텀 지표**: RSI, MACD, Stochastic, ADX
- **변동성 지표**: Bollinger Bands, ATR
- **거래량 지표**: OBV, VWAP

### 🎯 트레이딩 전략
1. **모멘텀 전략**
   - 이동평균선 크로스오버
   - 골든/데드 크로스 기반 매매

2. **평균 회귀 전략**
   - 볼린저 밴드 기반
   - Z-Score 기반

3. **RSI 전략**
   - 과매수/과매도 구간 매매
   - RSI 다이버전스 전략

4. **MACD 전략**
   - MACD 크로스오버
   - 히스토그램 전략
   - 제로선 크로스

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
│   │   ├── momentum_strategy.py     # 모멘텀 전략
│   │   ├── mean_reversion_strategy.py  # 평균 회귀 전략
│   │   ├── rsi_strategy.py          # RSI 전략
│   │   └── macd_strategy.py         # MACD 전략
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── backtester.py            # 백테스팅 엔진
│   │   └── performance.py           # 성과 분석
│   └── utils/
│       ├── __init__.py
│       ├── indicators.py            # 기술적 지표
│       └── visualization.py         # 시각화
├── examples/
│   ├── basic_example.py             # 기본 사용 예제
│   ├── strategy_comparison.py       # 전략 비교
│   └── parameter_optimization.py    # 파라미터 최적화
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

### 기본 예제

```python
from src.data.data_fetcher import DataFetcher
from src.strategies.momentum_strategy import MomentumStrategy
from src.backtesting.backtester import Backtester

# 1. 데이터 수집
fetcher = DataFetcher()
data = fetcher.fetch_data('TQQQ', period='2y')

# 2. 전략 설정
strategy = MomentumStrategy(short_window=20, long_window=50)

# 3. 백테스트 실행
backtester = Backtester(initial_capital=10000)
results = backtester.run(strategy, data)

# 4. 결과 출력
backtester.print_summary()
```

### 예제 스크립트 실행

```bash
# 기본 예제 실행
cd examples
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

```python
from src.strategies.base_strategy import BaseStrategy
import pandas as pd

class MyCustomStrategy(BaseStrategy):
    def __init__(self, param1, param2):
        super().__init__(name="MyCustomStrategy")
        self.param1 = param1
        self.param2 = param2

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # 여기에 시그널 생성 로직 구현
        # df['Signal'] = 1 (매수), -1 (매도), 0 (관망)

        return df
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
