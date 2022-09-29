# this file just holds a stuct to parse reviews from json
from msgspec.json import decode, encode
from msgspec import Struct
from typing import Optional

class Review(Struct):
    book_id: str
    has_spoiler: bool
    review_sentences: list[list]
    user_id: str
    rating: int
    preprocessed_sentences: Optional[list[list]] = [[]]
    partition: Optional[str] = "NONE"