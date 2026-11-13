from dataclasses import dataclass, asdict
from typing import ClassVar

@dataclass(frozen=True)
class Plan:
    """Persisted domain document; identity and timestamps are repository metadata."""
    table: ClassVar[str] = "plans"
    name: str
    run_id: int
    venue: str
    days: list[dict]
    status: str
    approved_by: str | None

    def payload(self):
        return asdict(self)
