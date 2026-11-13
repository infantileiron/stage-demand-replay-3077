from dataclasses import dataclass, asdict
from typing import ClassVar

@dataclass(frozen=True)
class Report:
    """Persisted domain document; identity and timestamps are repository metadata."""
    table: ClassVar[str] = "reports"
    title: str
    plan_id: int
    venue: str
    days: list[dict]
    status: str

    def payload(self):
        return asdict(self)
