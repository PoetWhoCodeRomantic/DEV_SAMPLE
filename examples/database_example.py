"""
데이터베이스 저장 및 재사용 기능 테스트 예제

이 예제는 다음을 시연합니다:
1. 데이터 수집 및 자동 DB 저장
2. DB에서 데이터 재사용 (API 호출 없이)
3. DB 통계 조회
4. 데이터 업데이트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data import DataFetcher
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    print("=" * 80)
    print("데이터베이스 저장 및 재사용 기능 테스트")
    print("=" * 80)

    # DataFetcher 생성 (DB 사용 모드)
    fetcher = DataFetcher(db_path="market_data.db", use_db=True)

    print("\n[1단계] 첫 번째 데이터 수집 (API 호출 + DB 저장)")
    print("-" * 80)

    # TQQQ 데이터 수집 (API에서 가져와서 DB에 저장)
    tqqq_data = fetcher.fetch_data('TQQQ', period='1y')
    print(f"✓ TQQQ 데이터 수집 완료: {len(tqqq_data)} 레코드")
    print(f"  날짜 범위: {tqqq_data.index.min()} ~ {tqqq_data.index.max()}")
    print(f"\n최근 5일 데이터:")
    print(tqqq_data.tail())

    print("\n[2단계] 동일한 데이터 재조회 (DB에서 즉시 로드)")
    print("-" * 80)

    # 동일한 데이터를 다시 요청 - DB에서 가져옴 (API 호출 없음)
    tqqq_cached = fetcher.fetch_data('TQQQ', period='1y')
    print(f"✓ TQQQ 데이터 재조회 완료: {len(tqqq_cached)} 레코드")
    print("  → API 호출 없이 DB에서 즉시 로드됨!")

    print("\n[3단계] 여러 심볼 수집")
    print("-" * 80)

    symbols = ['SOXL', 'UPRO']
    data_dict = fetcher.fetch_multiple(symbols, period='6mo')

    for symbol, df in data_dict.items():
        print(f"✓ {symbol}: {len(df)} 레코드")

    print("\n[4단계] DB 통계 확인")
    print("-" * 80)

    stats = fetcher.get_db_stats()
    if stats is not None:
        print("\n저장된 데이터 통계:")
        print(stats.to_string(index=False))
    else:
        print("DB 통계를 가져올 수 없습니다")

    print("\n[5단계] 특정 날짜 범위 조회 (DB에서)")
    print("-" * 80)

    # 특정 기간만 조회 - DB에 있으면 DB에서 가져옴
    recent_data = fetcher.fetch_data(
        'TQQQ',
        start_date='2024-01-01',
        end_date='2024-12-31'
    )
    print(f"✓ TQQQ 2024년 데이터: {len(recent_data)} 레코드")
    print(f"  날짜 범위: {recent_data.index.min()} ~ {recent_data.index.max()}")

    print("\n[6단계] 강제 업데이트 (DB 무시하고 API 재수집)")
    print("-" * 80)

    updated_data = fetcher.update_symbol('TQQQ', period='1mo')
    print(f"✓ TQQQ 최신 데이터 업데이트: {len(updated_data)} 레코드")

    print("\n[7단계] 최종 DB 통계")
    print("-" * 80)

    final_stats = fetcher.get_db_stats()
    if final_stats is not None:
        print("\n최종 저장된 데이터:")
        print(final_stats.to_string(index=False))

    print("\n" + "=" * 80)
    print("테스트 완료!")
    print("=" * 80)
    print("\n💡 주요 특징:")
    print("  • 데이터는 자동으로 market_data.db에 저장됩니다")
    print("  • 동일한 데이터 요청 시 API 호출 없이 DB에서 즉시 로드")
    print("  • 최신 데이터가 필요한 경우 자동으로 업데이트")
    print("  • force_update=True로 강제 재수집 가능")
    print("\n📁 데이터베이스 파일: market_data.db")
    print("  → 프로그램 종료 후에도 데이터 유지됨")


if __name__ == "__main__":
    main()
