from typing import List

from domain.contracts import ItemRepository
from domain.dtos import CreateItemDTO, ItemDTO


class ItemService:
    """Business logic layer for item operations."""

    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    def create_item(self, payload: CreateItemDTO) -> ItemDTO:
        item = ItemDTO(id=0, name=payload.name, description=payload.description)
        return self._repository.save(item)

    def list_items(self) -> List[ItemDTO]:
        return self._repository.list()

    def get_common_names(self) -> List[str]:
        return [
            "Alice",
            "Bob",
            "Charlie",
            "Diana",
            "Ethan",
            "Fiona",
            "George",
            "Hannah",
        ]

    def get_item(self, item_id: int) -> ItemDTO:
        item = self._repository.get(item_id)
        if item is None:
            raise ValueError(f"Item with id {item_id} not found")
        return item
