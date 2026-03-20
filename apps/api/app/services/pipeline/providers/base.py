from abc import ABC, abstractmethod
from typing import Any

from app.core.enums import SourceType


class NewsProvider(ABC):
    name: str
    source_type: SourceType

    @abstractmethod
    def fetch(self) -> list[dict[str, Any]]:
        raise NotImplementedError

