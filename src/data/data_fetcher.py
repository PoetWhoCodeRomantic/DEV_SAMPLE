"""
레버리지 ETF 데이터 수집 모듈
yfinance를 사용하여 TQQQ, SOXL 등의 과거 데이터를 수집
SQLite DB에 저장하여 재사용
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Union
import logging
from .database import MarketDataDB

logger = logging.getLogger(__name__)


class DataFetcher:
    """레버리지 ETF 데이터를 수집하는 클래스"""

    # 주요 레버리지 ETF 목록
    LEVERAGE_ETFS = {
        'TQQQ': 'ProShares UltraPro QQQ (3x)',
        'SOXL': 'Direxion Daily Semiconductor Bull 3X',
        'UPRO': 'ProShares UltraPro S&P500 (3x)',
        'TNA': 'Direxion Daily Small Cap Bull 3X',
        'FNGU': 'MicroSectors FANG+ Index 3X',
        'TECL': 'Direxion Daily Technology Bull 3X',
        'CURE': 'Direxion Daily Healthcare Bull 3X',
        'LABU': 'Direxion Daily S&P Biotech Bull 3X',
        'DFEN': 'Direxion Daily Aerospace & Defense Bull 3X',
        'SPXL': 'Direxion Daily S&P 500 Bull 3X',
    }

    def __init__(self, db_path: str = "market_data.db", use_db: bool = True):
        """
        DataFetcher 초기화

        Args:
            db_path: SQLite 데이터베이스 파일 경로
            use_db: DB 사용 여부 (False시 메모리 캐시만 사용)
        """
        self.data_cache = {}
        self.use_db = use_db
        self.db = MarketDataDB(db_path) if use_db else None

    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        period: str = "2y",
        interval: str = "1d",
        force_update: bool = False
    ) -> pd.DataFrame:
        """
        지정된 심볼의 주가 데이터를 수집 (DB 우선 조회)

        Args:
            symbol: 티커 심볼 (예: 'TQQQ', 'SOXL')
            start_date: 시작 날짜 (선택사항)
            end_date: 종료 날짜 (선택사항)
            period: 기간 (예: '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            interval: 간격 (예: '1m', '5m', '1h', '1d', '1wk', '1mo')
            force_update: True시 DB 무시하고 API에서 재수집

        Returns:
            DataFrame: OHLCV 데이터
        """
        # 날짜 범위 계산
        if start_date:
            start_str = pd.to_datetime(start_date).strftime('%Y-%m-%d')
        else:
            start_str = None

        if end_date:
            end_str = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        else:
            end_str = None

        # DB 사용 모드이고 강제 업데이트가 아닌 경우
        if self.use_db and not force_update:
            # DB에서 데이터 조회 시도
            db_data = self.db.get_data(symbol, start_str, end_str, interval)

            if db_data is not None and not db_data.empty:
                # DB에 충분한 데이터가 있는지 확인
                if self._is_data_sufficient(db_data, start_date, end_date, period):
                    logger.info(f"{symbol}: DB에서 {len(db_data)}개 레코드 조회")
                    self.data_cache[symbol] = db_data
                    return db_data
                else:
                    logger.info(f"{symbol}: DB 데이터 부족, API에서 추가 수집")

        # API에서 데이터 수집
        try:
            ticker = yf.Ticker(symbol)

            if start_date and end_date:
                df = ticker.history(start=start_date, end=end_date, interval=interval)
            else:
                df = ticker.history(period=period, interval=interval)

            if df.empty:
                raise ValueError(f"{symbol} 데이터를 가져올 수 없습니다.")

            # DB에 저장
            if self.use_db:
                saved_count = self.db.save_data(symbol, df, interval)
                logger.info(f"{symbol}: API에서 수집 후 DB에 {saved_count}개 저장")
            else:
                logger.info(f"{symbol}: API에서 {len(df)}개 레코드 수집 (메모리 전용)")

            # 캐시에 저장
            self.data_cache[symbol] = df

            return df

        except Exception as e:
            raise RuntimeError(f"{symbol} 데이터 수집 중 오류 발생: {str(e)}")

    def _is_data_sufficient(
        self,
        df: pd.DataFrame,
        start_date: Optional[Union[str, datetime]],
        end_date: Optional[Union[str, datetime]],
        period: str
    ) -> bool:
        """
        DB의 데이터가 요청 범위를 충족하는지 확인

        Args:
            df: DB에서 조회한 데이터
            start_date: 요청 시작 날짜
            end_date: 요청 종료 날짜
            period: 요청 기간

        Returns:
            bool: 충분 여부
        """
        if df.empty:
            return False

        db_start = df.index.min()
        db_end = df.index.max()

        # 날짜 범위가 명시된 경우
        if start_date and end_date:
            req_start = pd.to_datetime(start_date)
            req_end = pd.to_datetime(end_date)
            return db_start <= req_start and db_end >= req_end

        # period로 요청한 경우 - 최근 데이터가 있는지만 확인
        # (과거 데이터는 변하지 않으므로 최신성만 중요)
        days_diff = (datetime.now() - db_end).days

        # 최신 데이터가 2일 이내면 충분하다고 판단
        return days_diff <= 2

    def fetch_multiple(
        self,
        symbols: List[str],
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        period: str = "2y",
        interval: str = "1d"
    ) -> dict:
        """
        여러 심볼의 데이터를 동시에 수집

        Args:
            symbols: 티커 심볼 리스트
            start_date: 시작 날짜
            end_date: 종료 날짜
            period: 기간
            interval: 간격

        Returns:
            dict: {symbol: DataFrame} 형태의 딕셔너리
        """
        data_dict = {}

        for symbol in symbols:
            try:
                data_dict[symbol] = self.fetch_data(
                    symbol, start_date, end_date, period, interval
                )
                print(f"✓ {symbol} 데이터 수집 완료")
            except Exception as e:
                print(f"✗ {symbol} 데이터 수집 실패: {str(e)}")

        return data_dict

    def get_etf_info(self, symbol: str) -> dict:
        """
        ETF 정보 조회

        Args:
            symbol: 티커 심볼

        Returns:
            dict: ETF 정보
        """
        ticker = yf.Ticker(symbol)

        try:
            info = ticker.info
            return {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'description': self.LEVERAGE_ETFS.get(symbol, 'N/A'),
                'currency': info.get('currency', 'N/A'),
                'exchange': info.get('exchange', 'N/A'),
                'marketCap': info.get('marketCap', 'N/A'),
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'description': self.LEVERAGE_ETFS.get(symbol, 'N/A'),
                'error': str(e)
            }

    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        수익률 계산

        Args:
            df: OHLCV 데이터프레임

        Returns:
            DataFrame: 수익률이 추가된 데이터프레임
        """
        df = df.copy()
        df['Returns'] = df['Close'].pct_change()
        df['Cumulative_Returns'] = (1 + df['Returns']).cumprod()

        return df

    def resample_data(self, df: pd.DataFrame, freq: str = 'W') -> pd.DataFrame:
        """
        데이터 리샘플링 (예: 일봉 -> 주봉)

        Args:
            df: OHLCV 데이터프레임
            freq: 리샘플링 빈도 ('D', 'W', 'M', 'Q', 'Y')

        Returns:
            DataFrame: 리샘플링된 데이터
        """
        resampled = df.resample(freq).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })

        return resampled.dropna()

    @classmethod
    def list_available_etfs(cls) -> pd.DataFrame:
        """
        사용 가능한 레버리지 ETF 목록 반환

        Returns:
            DataFrame: ETF 목록
        """
        data = [
            {'Symbol': symbol, 'Description': desc}
            for symbol, desc in cls.LEVERAGE_ETFS.items()
        ]
        return pd.DataFrame(data)

    def get_db_stats(self) -> Optional[pd.DataFrame]:
        """
        데이터베이스 통계 조회

        Returns:
            DataFrame: 심볼별 통계 또는 None (DB 미사용시)
        """
        if not self.use_db:
            logger.warning("DB를 사용하지 않는 모드입니다")
            return None

        return self.db.get_stats()

    def clear_cache(self):
        """메모리 캐시 초기화"""
        self.data_cache.clear()
        logger.info("메모리 캐시 초기화 완료")

    def update_symbol(self, symbol: str, interval: str = "1d", period: str = "1mo") -> pd.DataFrame:
        """
        특정 심볼의 최신 데이터 업데이트

        Args:
            symbol: 티커 심볼
            interval: 데이터 간격
            period: 업데이트할 기간

        Returns:
            DataFrame: 업데이트된 데이터
        """
        logger.info(f"{symbol}: 최신 데이터 업데이트 시작")
        return self.fetch_data(symbol, interval=interval, period=period, force_update=True)

    def delete_symbol_data(self, symbol: str, interval: str = "1d") -> int:
        """
        특정 심볼의 데이터 삭제

        Args:
            symbol: 티커 심볼
            interval: 데이터 간격

        Returns:
            int: 삭제된 레코드 수
        """
        if not self.use_db:
            logger.warning("DB를 사용하지 않는 모드입니다")
            return 0

        return self.db.delete_data(symbol, interval)
