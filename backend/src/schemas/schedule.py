from pydantic import BaseModel,Field

class ScheduleCreate(BaseModel):
    name: str = Field(min_length=2,max_length=100)
    source_report_id: int | None = Field(default=None,gt=0)
    daily_time: str = Field(default="08:30",pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    enabled: bool = True

class ScheduleToggle(BaseModel):
    enabled: bool
