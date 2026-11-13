from pydantic import BaseModel, Field

class RunCreate(BaseModel):
    scenario_id: int = Field(gt=0)

class VerifyCreate(BaseModel):
    dataset_id: int = Field(gt=0)
