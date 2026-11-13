from pydantic import BaseModel, Field

class RunCreate(BaseModel):
    scenario_id: int = Field(gt=0)
