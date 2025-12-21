from typing import Generic
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


T = TypeVar("T", bound=BaseModel)


class Page(Generic[T], BaseSchema):
    page_size: int
    total_pages: int
    total_items: int
    page: int
    items: list[T]
