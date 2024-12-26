from dataclasses import dataclass
from typing import Any, List

@dataclass
class Joke:
    id: str
    categories: List[str]
    createdAt: str
    joke: str

    @staticmethod
    def from_dict(obj: Any):
        _id = str(obj.get("id"))
        _categories = obj.get("categories")
        _createdAt = obj.get("created_at")
        _joke = str(obj.get("value"))
        return Joke(_id, _categories, _createdAt, _joke)
