from dataclasses import dataclass, asdict
from typing import ClassVar

@dataclass(frozen=True)
class Scenario:
    """Persisted domain document; identity and timestamps are repository metadata."""
    table: ClassVar[str] = "scenarios"
    name: str
    dataset_id: int
    venue: str
    horizon: int
    weekend_event: bool
    people_per_usher: int

    def payload(self):
        return asdict(self)
