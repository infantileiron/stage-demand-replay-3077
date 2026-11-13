from dataclasses import dataclass,asdict
from typing import ClassVar

@dataclass(frozen=True)
class DeliverySchedule:
    table: ClassVar[str] = "schedules"
    name: str
    source_report_id: int | None
    daily_time: str
    enabled: bool
    next_run: str
    last_run: str | None = None
    last_error: str | None = None

    def payload(self): return asdict(self)
