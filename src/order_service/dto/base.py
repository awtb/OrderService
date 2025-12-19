from dataclasses import dataclass
from typing import Generic
from typing import TypeVar


@dataclass
class BaseDTO:
    """Base data-transfer object."""


T = TypeVar("T", bound=BaseDTO)


@dataclass
class PageDTO(Generic[T], BaseDTO):
    items: list[T]
    page_size: int
    total_pages: int
    total_items: int
    page: int
