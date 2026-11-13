from pydantic import BaseModel, Field
from typing import Literal

class ScenarioCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    dataset_id: int = Field(gt=0)
    venue: Literal["大剧场", "黑匣子", "实验厅"] = "大剧场"
    horizon: Literal[7, 14] = 7
    weekend_event: bool = False
    people_per_usher: int = Field(default=65, ge=20, le=150)
