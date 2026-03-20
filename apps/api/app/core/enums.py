from enum import Enum


class SourceType(str, Enum):
    DOMESTIC = "domestic"
    FOREIGN = "foreign"


class MarketScope(str, Enum):
    KOREA = "korea"
    GLOBAL = "global"
    MIXED = "mixed"


class ClusterStatus(str, Enum):
    ACTIVE = "active"
    COOLING = "cooling"
    ARCHIVED = "archived"


class ImpactDirection(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class ForecastHorizon(str, Enum):
    INTRADAY = "intraday"
    CLOSE = "close"
    T1 = "t1"


class RankingScope(str, Enum):
    THEME = "theme"
    CLUSTER = "cluster"
    DASHBOARD = "dashboard"


class MarketCode(str, Enum):
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"
    KONEX = "KONEX"

