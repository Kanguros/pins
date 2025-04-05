import logging
from typing import ClassVar, Literal, Optional

from pydantic import BaseModel

AnyObj = "any"
AnyObjType = set[Literal["any"]]
AppDefault = "application-default"
AppDefaultType = set[Literal["application-default"]]
SetStr = set[str]
Action = Literal["allow", "deny", "monitor"]
logger = logging.getLogger(__name__)


class MainModel(BaseModel):
    """Base class for all models."""

    singular: ClassVar[Optional[str]] = None
    """Display name of a single model."""
    plural: ClassVar[Optional[str]] = None
    """Display name of a many models."""
