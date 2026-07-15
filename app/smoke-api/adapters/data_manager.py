from typing import Dict, List, Optional

from domain.contracts import ItemRepository
from domain.dtos import ItemDTO


class InMemoryItemRepository(ItemRepository):
    def __init__(self) -> None:
        self._items: Dict[int, ItemDTO] = {}
        self._next_id = 1

    def save(self, item: ItemDTO) -> ItemDTO:
        item.id = self._next_id
        self._items[self._next_id] = item
        self._next_id += 1
        return item

    def list(self) -> List[ItemDTO]:
        return list(self._items.values())

    def get(self, item_id: int) -> Optional[ItemDTO]:
        return self._items.get(item_id)
