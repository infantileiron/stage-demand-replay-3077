from dataclasses import dataclass, asdict
from typing import ClassVar

@dataclass(frozen=True)
class Dataset:
    """Persisted domain document; identity and timestamps are repository metadata."""
    table: ClassVar[str] = "datasets"
    name: str
    filename: str
    rows: list[dict]
    row_count: int
    venues: list[str]

    def payload(self):
        return asdict(self)
