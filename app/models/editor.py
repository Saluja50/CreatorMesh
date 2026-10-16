from pydantic import BaseModel


class EditorResult(BaseModel):
    approved: bool
    feedback: list[str]