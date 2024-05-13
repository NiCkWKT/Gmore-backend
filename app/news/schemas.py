from pydantic import BaseModel
from typing import List, Union


class News(BaseModel):
    id: str
    title: str
    published_at: str
    image_url: Union[str, None]
    source: str
    source_url: str
    category: str
    summary: List[str]
