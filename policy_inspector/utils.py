from typing import Callable

from pydantic import BaseModel


# It's just make use of pydantic because it's available ;)
class Example(BaseModel):
    name: str
    args: list
    cmd: Callable
