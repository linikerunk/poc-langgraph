from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional

from domain.dtos import ItemDTO


class ItemRepository(ABC):
    """Contract for item persistence adapters."""

    @abstractmethod
    def save(self, item: ItemDTO) -> ItemDTO:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[ItemDTO]:
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: int) -> Optional[ItemDTO]:
        raise NotImplementedError
