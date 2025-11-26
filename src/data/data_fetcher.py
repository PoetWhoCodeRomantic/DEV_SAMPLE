"""
레버리지 ETF 데이터 수집 모듈
yfinance를 사용하여 TQQQ, SOXL 등의 과거 데이터를 수집
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Union


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

    def __init__(self):
        """DataFetcher 초기화"""
        self.data_cache = {}

    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        period: str = "2y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        지정된 심볼의 주가 데이터를 수집

        Args:
            symbol: 티커 심볼 (예: 'TQQQ', 'SOXL')
            start_date: 시작 날짜 (선택사항)
            end_date: 종료 날짜 (선택사항)
            period: 기간 (예: '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            interval: 간격 (예: '1m', '5m', '1h', '1d', '1wk', '1mo')

        Returns:
            DataFrame: OHLCV 데이터
        """
        ticker = yf.Ticker(symbol)

        try:
            if start_date and end_date:
                df = ticker.history(start=start_date, end=end_date, interval=interval)
            else:
                df = ticker.history(period=period, interval=interval)

            if df.empty:
                raise ValueError(f"{symbol} 데이터를 가져올 수 없습니다.")

            # 캐시에 저장
            self.data_cache[symbol] = df

            return df

        except Exception as e:
            raise RuntimeError(f"{symbol} 데이터 수집 중 오류 발생: {str(e)}")

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
