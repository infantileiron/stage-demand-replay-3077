from pydantic import BaseModel, Field

class PlanCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    run_id: int = Field(gt=0)
