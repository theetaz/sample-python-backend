from typing import TypeVar, Generic, Union, List, Optional
from pydantic.generics import GenericModel
from pydantic import BaseModel

DataT = TypeVar('DataT')

class PageMeta(BaseModel):
    page: int
    page_size: int
    total_pages: int
    total_items: int

class CommonResponse(GenericModel, Generic[DataT]):
    message: str
    success: bool
    payload: Optional[Union[DataT, List[DataT]]]
    meta: Optional[PageMeta]