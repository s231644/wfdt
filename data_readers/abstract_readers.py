from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, List

from src import LexItem, WFToken, Inventory


class ReaderAbstract(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def build_inventory(self, *args, **kwargs) -> Inventory:
        raise NotImplementedError

    @abstractmethod
    def read_dataset(self, *args, **kwargs) -> Dict[LexItem, Any]:
        raise NotImplementedError

    @abstractmethod
    def read_sample(self, *args, **kwargs) -> Tuple[LexItem, Any]:
        raise NotImplementedError


class AnalysesReaderAbstract(ReaderAbstract, ABC):
    @abstractmethod
    def read_dataset(self, *args, **kwargs) -> Dict[LexItem, WFToken]:
        raise NotImplementedError

    @abstractmethod
    def read_sample(self, *args, **kwargs) -> List[Tuple[LexItem, WFToken]]:
        raise NotImplementedError
