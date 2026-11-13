from dataclasses import dataclass, asdict
from typing import ClassVar

@dataclass(frozen=True)
class Run:
    """Persisted domain document; identity and timestamps are repository metadata."""
    table: ClassVar[str] = "runs"
    scenario_id: int
    status: str
    result: dict | None
    error: str | None

    def payload(self):
        return asdict(self)
