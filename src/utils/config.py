"""
설정 파일 로더
config.yaml 파일을 읽어 설정값 제공
"""

import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """
    설정 관리 클래스
    config.yaml 파일을 읽어서 설정값을 제공
    """

    _instance = None
    _config = None

    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Config 초기화"""
        if self._config is None:
            self.load_config()

    def load_config(self, config_path: Optional[str] = None):
        """
        설정 파일 로드

        Args:
            config_path: 설정 파일 경로 (None이면 프로젝트 루트의 config.yaml 사용)
        """
        if config_path is None:
            # 프로젝트 루트 경로 찾기
            current_dir = Path(__file__).resolve().parent
            project_root = current_dir.parent.parent
            config_path = project_root / "config.yaml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        설정값 가져오기 (점 표기법 지원)

        Args:
            key: 설정 키 (예: 'data.default_symbol', 'backtest.initial_capital')
            default: 기본값 (키가 없을 때 반환)

        Returns:
            설정값

        Examples:
            >>> config = Config()
            >>> config.get('data.default_symbol')
            'TQQQ'
            >>> config.get('backtest.initial_capital')
            10000
        """
        if self._config is None:
            self.load_config()

        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_data_config(self) -> Dict[str, Any]:
        """데이터 수집 설정 가져오기"""
        return self.get('data', {})

    def get_backtest_config(self) -> Dict[str, Any]:
        """백테스트 설정 가져오기"""
        return self.get('backtest', {})

    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """
        특정 전략 설정 가져오기

        Args:
            strategy_name: 전략 이름 (예: 'daily_dca', 'pyramiding')

        Returns:
            전략 설정 딕셔너리
        """
        return self.get(f'strategies.{strategy_name}', {})

    def get_daily_dca_config(self, preset: Optional[str] = None) -> Dict[str, Any]:
        """
        DailyDCA 전략 설정 가져오기

        Args:
            preset: 프리셋 이름 (None, 'balanced', 'aggressive', 'conservative', 'fixed')

        Returns:
            전략 파라미터 딕셔너리

        Examples:
            >>> config = Config()
            >>> # 기본 설정
            >>> params = config.get_daily_dca_config()
            >>> # 공격적 프리셋
            >>> params = config.get_daily_dca_config('aggressive')
        """
        if preset:
            preset_config = self.get(f'strategies.daily_dca.presets.{preset}')
            if preset_config:
                return preset_config
            else:
                print(f"⚠️  프리셋 '{preset}'을 찾을 수 없습니다. 기본 설정을 사용합니다.")

        # 기본 설정 (프리셋 제외)
        base_config = self.get('strategies.daily_dca', {})
        # presets 키 제외
        return {k: v for k, v in base_config.items() if k not in ['presets', 'name']}

    def get_database_config(self) -> Dict[str, Any]:
        """데이터베이스 설정 가져오기"""
        return self.get('database', {})

    def get_output_config(self) -> Dict[str, Any]:
        """출력 설정 가져오기"""
        return self.get('output', {})

    def get_risk_config(self) -> Dict[str, Any]:
        """리스크 관리 설정 가져오기"""
        return self.get('risk', {})

    def get_all(self) -> Dict[str, Any]:
        """전체 설정 가져오기"""
        if self._config is None:
            self.load_config()
        return self._config.copy()

    def reload(self):
        """설정 파일 다시 로드"""
        self._config = None
        self.load_config()

    def __repr__(self):
        """문자열 표현"""
        return f"Config(loaded={self._config is not None})"


# 편의 함수들
def get_config() -> Config:
    """
    Config 인스턴스 가져오기 (싱글톤)

    Returns:
        Config 인스턴스
    """
    return Config()


def load_config(config_path: Optional[str] = None) -> Config:
    """
    설정 파일 로드 및 Config 인스턴스 반환

    Args:
        config_path: 설정 파일 경로

    Returns:
        Config 인스턴스
    """
    config = Config()
    if config_path:
        config.load_config(config_path)
    return config


# 사용 예시
if __name__ == "__main__":
    # Config 인스턴스 생성
    config = Config()

    # 설정값 출력
    print("=" * 80)
    print("설정 파일 로드 테스트")
    print("=" * 80)
    print()

    # 데이터 설정
    print("[ 데이터 설정 ]")
    print(f"  기본 종목: {config.get('data.default_symbol')}")
    print(f"  수집 기간: {config.get('data.period')}")
    print(f"  데이터 간격: {config.get('data.interval')}")
    print(f"  종목 리스트: {config.get('data.symbols')}")
    print()

    # 백테스트 설정
    print("[ 백테스트 설정 ]")
    backtest_config = config.get_backtest_config()
    print(f"  초기 자본: ${backtest_config['initial_capital']:,}")
    print(f"  수수료: {backtest_config['commission']*100}%")
    print(f"  슬리피지: {backtest_config['slippage']*100}%")
    print()

    # DailyDCA 전략 설정
    print("[ DailyDCA 전략 - 기본 설정 ]")
    dca_config = config.get_daily_dca_config()
    for key, value in dca_config.items():
        print(f"  {key}: {value}")
    print()

    # DailyDCA 전략 - 공격적 프리셋
    print("[ DailyDCA 전략 - 공격적 프리셋 ]")
    aggressive_config = config.get_daily_dca_config('aggressive')
    for key, value in aggressive_config.items():
        print(f"  {key}: {value}")
    print()

    # 점 표기법 테스트
    print("[ 점 표기법 테스트 ]")
    print(f"  strategies.daily_dca.max_positions: {config.get('strategies.daily_dca.max_positions')}")
    print(f"  strategies.pyramiding.sell_profit_percent: {config.get('strategies.pyramiding.sell_profit_percent')}")
    print(f"  존재하지 않는 키: {config.get('nonexistent.key', 'DEFAULT_VALUE')}")
    print()
