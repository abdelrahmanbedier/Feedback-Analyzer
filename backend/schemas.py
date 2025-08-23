from pydantic import BaseModel
from datetime import datetime
from typing import List

class FeedbackBase(BaseModel):
    original_text: str
    product: str | None = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    original_language: str | None = None
    translated_text: str | None = None 
    sentiment: str | None = None
    was_reviewed: bool #
    status: str # <-- ADD THIS LINE
    created_at: datetime

class Config:
    from_attributes = True # Renamed from orm_mode in Pydantic v2

class StatsResponse(BaseModel):
    positive_count: int
    negative_count: int
    neutral_count: int
    total_count: int
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float


class FeedbackUpdate(BaseModel):
    translated_text: str
    sentiment: str


class PaginatedFeedbackResponse(BaseModel):
    total_count: int
    items: List[Feedback]    