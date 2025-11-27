# 로컬 데이터베이스 기능 가이드

## 개요

이제 수집된 데이터를 SQLite 데이터베이스에 저장하고 재사용할 수 있습니다. API 호출을 최소화하고 데이터를 영구적으로 보관할 수 있습니다.

## 주요 기능

### 1. 자동 데이터 저장
- yfinance API로 수집한 데이터를 자동으로 SQLite DB에 저장
- 프로그램 종료 후에도 데이터 유지

### 2. 스마트 데이터 재사용
- 동일한 데이터 요청 시 DB에서 즉시 로드 (API 호출 없음)
- 최신 데이터가 필요한 경우에만 자동으로 API 호출
- 누락된 기간만 추가로 수집

### 3. 효율적인 저장소 관리
- 심볼별, 간격별 데이터 관리
- 통계 조회 및 데이터 삭제 기능
- 데이터베이스 최적화 지원

## 사용 방법

### 기본 사용

```python
from src.data import DataFetcher

# DB 사용 모드로 DataFetcher 생성 (기본값)
fetcher = DataFetcher(db_path="market_data.db", use_db=True)

# 첫 번째 호출: API에서 수집 + DB에 저장
data = fetcher.fetch_data('TQQQ', period='1y')

# 두 번째 호출: DB에서 즉시 로드 (API 호출 없음)
data_cached = fetcher.fetch_data('TQQQ', period='1y')
```

### DB 통계 확인

```python
# 저장된 데이터 통계 조회
stats = fetcher.get_db_stats()
print(stats)

# 출력 예시:
#   symbol  interval  first_date  last_date  record_count  last_updated
#   TQQQ    1d        2023-11-27  2024-11-27  252          2024-11-27 12:00:00
#   SOXL    1d        2024-05-27  2024-11-27  126          2024-11-27 12:05:00
```

### 강제 업데이트

```python
# DB를 무시하고 최신 데이터를 강제로 수집
data = fetcher.fetch_data('TQQQ', period='1mo', force_update=True)

# 또는 편의 메서드 사용
data = fetcher.update_symbol('TQQQ', period='1mo')
```

### 특정 날짜 범위 조회

```python
# DB에 데이터가 있으면 DB에서, 없으면 API에서 수집
data = fetcher.fetch_data(
    'TQQQ',
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

### 데이터 삭제

```python
# 특정 심볼의 데이터 삭제
deleted_count = fetcher.delete_symbol_data('TQQQ', interval='1d')
print(f"{deleted_count}개 레코드 삭제됨")
```

### DB 비활성화 (기존 방식)

```python
# 메모리 캐시만 사용 (DB 저장 안함)
fetcher = DataFetcher(use_db=False)
data = fetcher.fetch_data('TQQQ', period='1y')
```

## MarketDataDB 직접 사용

DataFetcher 없이 DB만 직접 사용할 수도 있습니다:

```python
from src.data import MarketDataDB
import pandas as pd

# DB 연결
db = MarketDataDB(db_path="market_data.db")

# 데이터 저장
df = pd.DataFrame({...})  # OHLCV 데이터
db.save_data('TQQQ', df, interval='1d')

# 데이터 조회
data = db.get_data('TQQQ', start_date='2024-01-01', interval='1d')

# 날짜 범위 확인
date_range = db.get_date_range('TQQQ', interval='1d')
print(f"저장된 기간: {date_range[0]} ~ {date_range[1]}")

# 통계 조회
stats = db.get_stats()

# 데이터 삭제
db.delete_data('TQQQ', interval='1d')

# DB 최적화
db.vacuum()
```

## 데이터베이스 구조

### market_data 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 |
| symbol | TEXT | 티커 심볼 (예: TQQQ) |
| date | TEXT | 날짜/시간 |
| open | REAL | 시가 |
| high | REAL | 고가 |
| low | REAL | 저가 |
| close | REAL | 종가 |
| volume | INTEGER | 거래량 |
| interval | TEXT | 데이터 간격 (1d, 1h 등) |
| created_at | TIMESTAMP | 생성 시간 |

### metadata 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| symbol | TEXT | 티커 심볼 (기본 키) |
| interval | TEXT | 데이터 간격 |
| first_date | TEXT | 최초 날짜 |
| last_date | TEXT | 마지막 날짜 |
| record_count | INTEGER | 레코드 수 |
| last_updated | TIMESTAMP | 마지막 업데이트 |

## 예제 실행

### 전체 통합 예제
```bash
# requirements 설치 (필요한 경우)
pip install -r requirements.txt

# 전체 기능 테스트
python examples/database_example.py
```

### DB 모듈만 테스트
```bash
# pandas만 설치되어 있으면 실행 가능
python examples/database_test_standalone.py
```

## 성능 향상

### Before (DB 없이)
```
첫 번째 실행: API 호출 (5-10초)
두 번째 실행: API 호출 (5-10초)
세 번째 실행: API 호출 (5-10초)
...
```

### After (DB 사용)
```
첫 번째 실행: API 호출 + DB 저장 (5-10초)
두 번째 실행: DB에서 로드 (0.1초 미만)
세 번째 실행: DB에서 로드 (0.1초 미만)
...
```

## 파일 위치

- **데이터베이스**: `market_data.db` (프로젝트 루트 또는 지정된 경로)
- **DB 모듈**: `src/data/database.py`
- **통합 모듈**: `src/data/data_fetcher.py`
- **예제**: `examples/database_example.py`

## 주의사항

1. **데이터 최신성**: 기본적으로 2일 이상 오래된 데이터는 자동으로 업데이트됩니다
2. **디스크 공간**: 1년치 일봉 데이터는 심볼당 약 100KB 정도 사용
3. **동시성**: SQLite는 단일 writer를 지원하므로 멀티스레드 사용 시 주의 필요

## 트러블슈팅

### DB 파일이 너무 큰 경우
```python
# 오래된 데이터 삭제
fetcher.delete_symbol_data('OLD_SYMBOL', interval='1d')

# DB 최적화로 공간 회수
fetcher.db.vacuum()
```

### 데이터 불일치 발생 시
```python
# 해당 심볼 데이터 삭제 후 재수집
fetcher.delete_symbol_data('TQQQ', interval='1d')
fetcher.fetch_data('TQQQ', period='2y', force_update=True)
```

### DB 초기화
```bash
# DB 파일 삭제 후 재시작
rm market_data.db
python examples/database_example.py
```
