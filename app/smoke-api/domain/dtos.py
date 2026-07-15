from pydantic import BaseModel
from typing import Optional


class CreateItemDTO(BaseModel):
    name: str
    description: Optional[str] = None


class ItemDTO(CreateItemDTO):
    id: int
