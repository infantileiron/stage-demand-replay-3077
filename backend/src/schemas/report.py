from pydantic import BaseModel, Field

class ReportCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    plan_id: int = Field(gt=0)
