from pydantic import BaseModel, Field


class ContentPlan(BaseModel):
    topic: str
    target_audience: str
    key_points: list[str] = Field(min_length=1)
    angle: str