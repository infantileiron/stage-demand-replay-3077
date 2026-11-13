from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

Venue = Literal["大剧场", "黑匣子", "实验厅"]

class AttendanceRow(BaseModel):
    date: date
    venue: Venue
    attendance: int = Field(ge=0, le=2000)
    capacity: int = Field(ge=1, le=2000)
    event: int = Field(default=0, ge=0, le=1)

class DatasetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    filename: str = Field(min_length=3, max_length=150)
    rows: list[AttendanceRow] = Field(min_length=42, max_length=5000)
