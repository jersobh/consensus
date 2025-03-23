from pydantic import BaseModel
from typing import List

class ModelResponse(BaseModel):
    answer: str
    reason: str

class RoundResult(BaseModel):
    round_number: int
    responses: List[ModelResponse]
