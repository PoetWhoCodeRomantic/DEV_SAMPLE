# DCA 전략 종합 테스트 실행 가이드

## 개요

`dca_strategy_test_runner.py`는 DCA_STRATEGY_GUIDE.md에 작성된 모든 테스트 시나리오를 순차적으로 실행하는 종합 테스트 프로그램입니다.

## 실행 방법

### 전체 테스트 실행

```bash
cd examples
python dca_strategy_test_runner.py
```

이 명령은 다음 5가지 테스트를 순차적으로 실행합니다:

## 테스트 구성

### 테스트 1: 기본 설정 테스트
- **목적**: 균형잡힌 프리셋의 기본 성능 확인
- **대상**: TQQQ (기본 설정)
- **출력**:
  - 백테스트 결과 (수익률, 샤프 비율, 최대 낙폭, 승률 등)
  - Buy & Hold 비교
  - 거래 통계
  - 결과 해석 및 평가

### 테스트 2: 프리셋별 성과 비교
- **목적**: 4개 프리셋의 성능 비교
- **비교 대상**:
  1. 스케일링 OFF (고정) - 전통적 DCA
  2. 보수적 - 안정성 중시
  3. 균형잡힌 - 기본 추천
  4. 공격적 - 고위험 고수익
- **출력**: 프리셋별 성능 비교 테이블

### 테스트 3: 여러 ETF 비교
- **목적**: 다양한 레버리지 ETF의 성능 비교
- **비교 대상**:
  - TQQQ: ProShares UltraPro QQQ (나스닥 100 3배)
  - SOXL: Direxion Daily Semiconductor Bull (반도체 3배)
  - UPRO: ProShares UltraPro S&P500 (S&P 500 3배)
- **출력**: ETF별 성능 비교 테이블

### 테스트 4: 파라미터 민감도 분석
- **목적**: 주요 파라미터 변경이 성능에 미치는 영향 분석
- **4-1: 익절 목표 수익률 비교**
  - 1%, 2%, 3%, 5%, 10% 비교
  - 회전율과 승률 분석
- **4-2: 포지션 스케일링 속도 비교**
  - depth_threshold: 3%, 5%, 7%, 10% 비교
  - 총 매수 수량 및 평균 매수 수량 분석

### 테스트 5: 종합 결과 요약 및 권장사항
- **목적**: 모든 테스트 결과 종합 분석
- **출력**:
  - 최고 성과 분석 (최고 수익률, 샤프 비율, 안정성, 승률)
  - 투자자 유형별 권장사항
  - 중요 주의사항
  - 실전 운용 팁

## 예상 실행 시간

- 전체 테스트: 약 3~5분 (네트워크 속도에 따라 변동)
- 각 테스트별: 30초~1분

## 출력 결과 이해하기

### 주요 지표 설명

#### 수익률 (Total Return)
- 전략의 총 수익률
- **목표**: 20% 이상 (연간)

#### 샤프 비율 (Sharpe Ratio)
- 위험 대비 수익성 측정
- **해석**:
  - < 1.0: 낮음
  - 1.0 ~ 2.0: 좋음
  - \> 2.0: 매우 좋음

#### 소르티노 비율 (Sortino Ratio)
- 하방 위험 대비 수익성
- 샤프 비율보다 하락 리스크에 집중

#### 최대 낙폭 (Max Drawdown)
- 최고점 대비 최대 하락률
- **목표**: -15% 이내 (레버리지 ETF 기준)

#### 승률 (Win Rate)
- 전체 거래 중 수익 거래 비율
- **목표**: 60% 이상

#### 손익비 (Profit Factor)
- 총 수익 / 총 손실
- **해석**:
  - < 1.0: 손실
  - 1.0 ~ 1.5: 보통
  - \> 2.0: 매우 좋음

## 테스트 결과 활용 방법

### 1. 자신에게 맞는 프리셋 선택
테스트 2의 결과를 보고 자신의 리스크 성향에 맞는 프리셋을 선택합니다.

### 2. 최적 ETF 선택
테스트 3의 결과를 보고 투자할 ETF를 선택합니다.

### 3. 파라미터 미세 조정
테스트 4의 결과를 참고하여 필요시 파라미터를 조정합니다.

### 4. config.yaml 수정
선택한 설정을 config.yaml에 반영합니다.

```yaml
strategies:
  daily_dca:
    # 선택한 프리셋의 파라미터 적용
    max_positions: 10
    profit_target_percent: 3.0
    # ... 나머지 설정
```

### 5. 실전 적용
1. 소액으로 시작
2. 정기적 모니터링
3. 결과 분석 및 조정

## 문제 해결

### "ModuleNotFoundError" 오류
```bash
# 프로젝트 루트 디렉토리에서 실행
cd /home/user/DEV_SAMPLE
python examples/dca_strategy_test_runner.py
```

### 데이터 수집 오류
- 인터넷 연결 확인
- yfinance 패키지 업데이트: `pip install --upgrade yfinance`

### 메모리 부족 오류
- 테스트 범위 축소 (period를 6mo로 변경)
- config.yaml에서 period 조정

## 추가 정보

- **전략 가이드**: DCA_STRATEGY_GUIDE.md
- **설정 파일**: config.yaml
- **데이터베이스 가이드**: DATABASE_GUIDE.md

## 커스터마이징

특정 테스트만 실행하려면 코드를 수정할 수 있습니다:

```python
# dca_strategy_test_runner.py 끝부분

def main():
    runner = DCAStrategyTestRunner()

    # 원하는 테스트만 실행
    runner.test_1_basic_setup()
    # runner.test_2_preset_comparison()
    # runner.test_3_multi_symbol_comparison()
    # runner.test_4_parameter_sensitivity()
    # runner.test_5_summary_and_recommendations()

if __name__ == "__main__":
    main()
```

## 주의사항

1. **백테스트 한계**: 과거 성과가 미래 수익을 보장하지 않습니다
2. **레버리지 리스크**: 높은 변동성으로 큰 손실 가능
3. **실전 차이**: 슬리피지, 체결 지연 등 실전 비용 발생
4. **자금 관리**: 충분한 여유 자금 확보 필수

## 라이센스 및 면책

본 테스트는 교육 및 정보 제공 목적으로만 작성되었습니다. 투자 권유가 아니며, 투자 결정은 본인의 책임입니다.
