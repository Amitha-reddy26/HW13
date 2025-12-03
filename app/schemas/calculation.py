from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class CalculationCreate(BaseModel):
    operation: str = Field(..., examples=["add", "subtract", "multiply", "divide"])
    a: float
    b: float


class CalculationRead(BaseModel):
    id: UUID
    operation: str
    a: float
    b: float
    result: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)