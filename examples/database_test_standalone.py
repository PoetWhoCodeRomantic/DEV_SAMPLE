"""
SQLite 데이터베이스 모듈 단독 테스트

이 테스트는 yfinance 없이 MarketDataDB만 테스트합니다.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.database import MarketDataDB


def create_sample_data(days=100):
    """샘플 OHLCV 데이터 생성"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    data = {
        'Open': [100 + i * 0.5 for i in range(days)],
        'High': [102 + i * 0.5 for i in range(days)],
        'Low': [98 + i * 0.5 for i in range(days)],
        'Close': [101 + i * 0.5 for i in range(days)],
        'Volume': [1000000 + i * 10000 for i in range(days)]
    }

    df = pd.DataFrame(data, index=dates)
    df.index.name = 'Date'
    return df


def main():
    print("=" * 80)
    print("SQLite 데이터베이스 모듈 테스트")
    print("=" * 80)

    # 테스트용 DB 생성
    db = MarketDataDB(db_path="test_market_data.db")

    print("\n[1단계] 샘플 데이터 생성")
    print("-" * 80)

    sample_data = create_sample_data(100)
    print(f"✓ 샘플 데이터 생성: {len(sample_data)} 레코드")
    print(f"\n첫 5개 레코드:")
    print(sample_data.head())

    print("\n[2단계] 데이터베이스에 저장")
    print("-" * 80)

    saved_count = db.save_data('TEST_SYMBOL', sample_data, interval='1d')
    print(f"✓ 저장 완료: {saved_count} 레코드")

    print("\n[3단계] 데이터베이스에서 조회")
    print("-" * 80)

    retrieved_data = db.get_data('TEST_SYMBOL', interval='1d')
    if retrieved_data is not None:
        print(f"✓ 조회 완료: {len(retrieved_data)} 레코드")
        print(f"  날짜 범위: {retrieved_data.index.min()} ~ {retrieved_data.index.max()}")
        print(f"\n마지막 5개 레코드:")
        print(retrieved_data.tail())
    else:
        print("✗ 데이터를 찾을 수 없습니다")

    print("\n[4단계] 날짜 범위 조회")
    print("-" * 80)

    date_range = db.get_date_range('TEST_SYMBOL', interval='1d')
    if date_range:
        print(f"✓ 저장된 날짜 범위:")
        print(f"  시작: {date_range[0]}")
        print(f"  종료: {date_range[1]}")

    print("\n[5단계] 특정 기간 데이터 조회")
    print("-" * 80)

    # 최근 30일 데이터만 조회
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    partial_data = db.get_data('TEST_SYMBOL', start_date=start_date, end_date=end_date, interval='1d')
    if partial_data is not None:
        print(f"✓ 최근 30일 데이터 조회: {len(partial_data)} 레코드")

    print("\n[6단계] 추가 심볼 저장")
    print("-" * 80)

    # 다른 심볼도 저장
    symbols = ['SYMBOL_A', 'SYMBOL_B', 'SYMBOL_C']
    for symbol in symbols:
        sample = create_sample_data(50)
        count = db.save_data(symbol, sample, interval='1d')
        print(f"✓ {symbol}: {count} 레코드 저장")

    print("\n[7단계] 전체 통계 조회")
    print("-" * 80)

    stats = db.get_stats()
    print("\n저장된 모든 데이터:")
    print(stats.to_string(index=False))

    print("\n[8단계] 심볼 목록 조회")
    print("-" * 80)

    all_symbols = db.get_all_symbols()
    print(f"✓ 저장된 심볼: {', '.join(all_symbols)}")

    print("\n[9단계] 데이터 삭제 테스트")
    print("-" * 80)

    deleted_count = db.delete_data('SYMBOL_A', interval='1d')
    print(f"✓ SYMBOL_A 삭제: {deleted_count} 레코드")

    remaining_symbols = db.get_all_symbols()
    print(f"✓ 남은 심볼: {', '.join(remaining_symbols)}")

    print("\n[10단계] 데이터베이스 최적화")
    print("-" * 80)

    db.vacuum()
    print("✓ 데이터베이스 최적화 완료")

    print("\n" + "=" * 80)
    print("테스트 완료!")
    print("=" * 80)
    print(f"\n📁 테스트 DB 파일: test_market_data.db")
    print("  → sqlite3 test_market_data.db 명령으로 직접 확인 가능")


if __name__ == "__main__":
    main()
