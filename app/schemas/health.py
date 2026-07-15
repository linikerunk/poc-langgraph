from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["HEALTHY", "WARNING", "CRITICAL"]


class HealthAssessment(BaseModel):
    status: Severity
    summary: str
    probable_cause: str
    impact: str
    remedies: list[str]
    confidence: float = Field(ge=0, le=1)


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
