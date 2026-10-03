from pydantic import BaseModel


class Source(BaseModel):
    title: str
    url: str
    evidence: str


class ResearchResult(BaseModel):
    claims: list[str]
    sources: list[Source]