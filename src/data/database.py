"""
SQLite 기반 시장 데이터 저장 모듈
수집된 OHLCV 데이터를 로컬 DB에 저장하고 재사용
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class MarketDataDB:
    """시장 데이터를 SQLite에 저장하고 관리하는 클래스"""

    def __init__(self, db_path: str = "market_data.db"):
        """
        MarketDataDB 초기화

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """데이터베이스 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 시장 데이터 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    interval TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date, interval)
                )
            """)

            # 인덱스 생성 (조회 성능 향상)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_date
                ON market_data(symbol, date)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_interval
                ON market_data(symbol, interval)
            """)

            # 메타데이터 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    symbol TEXT PRIMARY KEY,
                    interval TEXT NOT NULL,
                    first_date TEXT,
                    last_date TEXT,
                    record_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.info(f"데이터베이스 초기화 완료: {self.db_path}")

    def save_data(self, symbol: str, df: pd.DataFrame, interval: str = "1d") -> int:
        """
        시장 데이터를 데이터베이스에 저장

        Args:
            symbol: 티커 심볼
            df: OHLCV 데이터프레임 (인덱스는 날짜)
            interval: 데이터 간격 ('1d', '1h' 등)

        Returns:
            int: 저장된 레코드 수
        """
        if df.empty:
            logger.warning(f"{symbol}: 저장할 데이터가 없습니다")
            return 0

        df = df.copy()
        df.reset_index(inplace=True)

        # 날짜 컬럼명 확인 (Date 또는 Datetime)
        date_col = 'Date' if 'Date' in df.columns else 'Datetime'

        # 필요한 컬럼만 선택
        required_cols = [date_col, 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df[required_cols]

        # 날짜를 문자열로 변환
        df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d %H:%M:%S')

        # 데이터베이스에 저장
        with sqlite3.connect(self.db_path) as conn:
            saved_count = 0

            for _, row in df.iterrows():
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO market_data
                        (symbol, date, open, high, low, close, volume, interval)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol,
                        row[date_col],
                        float(row['Open']),
                        float(row['High']),
                        float(row['Low']),
                        float(row['Close']),
                        int(row['Volume']),
                        interval
                    ))
                    saved_count += 1
                except sqlite3.Error as e:
                    logger.error(f"데이터 저장 오류: {e}")

            # 메타데이터 업데이트
            first_date = df[date_col].min()
            last_date = df[date_col].max()

            conn.execute("""
                INSERT OR REPLACE INTO metadata
                (symbol, interval, first_date, last_date, record_count, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                interval,
                first_date,
                last_date,
                saved_count,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            logger.info(f"{symbol}: {saved_count}개 레코드 저장 완료")

        return saved_count

    def get_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        데이터베이스에서 시장 데이터 조회

        Args:
            symbol: 티커 심볼
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            interval: 데이터 간격

        Returns:
            DataFrame 또는 None
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT date, open, high, low, close, volume
                FROM market_data
                WHERE symbol = ? AND interval = ?
            """
            params = [symbol, interval]

            if start_date:
                query += " AND date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND date <= ?"
                params.append(end_date)

            query += " ORDER BY date"

            df = pd.read_sql_query(query, conn, params=params)

            if df.empty:
                return None

            # 날짜를 인덱스로 설정
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

            # 컬럼명을 대문자로 변경 (yfinance 형식과 일치)
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

            logger.info(f"{symbol}: {len(df)}개 레코드 조회 완료")
            return df

    def get_date_range(self, symbol: str, interval: str = "1d") -> Optional[Tuple[str, str]]:
        """
        저장된 데이터의 날짜 범위 조회

        Args:
            symbol: 티커 심볼
            interval: 데이터 간격

        Returns:
            (first_date, last_date) 튜플 또는 None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT first_date, last_date
                FROM metadata
                WHERE symbol = ? AND interval = ?
            """, (symbol, interval))

            result = cursor.fetchone()
            return result if result else None

    def has_data(self, symbol: str, interval: str = "1d") -> bool:
        """
        특정 심볼의 데이터가 존재하는지 확인

        Args:
            symbol: 티커 심볼
            interval: 데이터 간격

        Returns:
            bool: 데이터 존재 여부
        """
        return self.get_date_range(symbol, interval) is not None

    def delete_data(self, symbol: str, interval: str = "1d") -> int:
        """
        특정 심볼의 데이터 삭제

        Args:
            symbol: 티커 심볼
            interval: 데이터 간격

        Returns:
            int: 삭제된 레코드 수
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM market_data
                WHERE symbol = ? AND interval = ?
            """, (symbol, interval))

            deleted_count = cursor.rowcount

            conn.execute("""
                DELETE FROM metadata
                WHERE symbol = ? AND interval = ?
            """, (symbol, interval))

            conn.commit()
            logger.info(f"{symbol}: {deleted_count}개 레코드 삭제 완료")

        return deleted_count

    def get_all_symbols(self) -> List[str]:
        """
        저장된 모든 심볼 목록 조회

        Returns:
            List[str]: 심볼 리스트
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT DISTINCT symbol FROM metadata")
            return [row[0] for row in cursor.fetchall()]

    def get_stats(self) -> pd.DataFrame:
        """
        데이터베이스 통계 조회

        Returns:
            DataFrame: 심볼별 통계
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT
                    symbol,
                    interval,
                    first_date,
                    last_date,
                    record_count,
                    last_updated
                FROM metadata
                ORDER BY symbol, interval
            """
            df = pd.read_sql_query(query, conn)
            return df

    def vacuum(self):
        """데이터베이스 최적화 (공간 회수)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM")
            logger.info("데이터베이스 최적화 완료")
