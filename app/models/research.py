
from typing import Literal
from pydantic import BaseModel


class Source(BaseModel):
    title: str
    url: str
    evidence: str


class ResearchResult(BaseModel):
    claims: list[str]
    sources: list[Source]


class ClaimCheck(BaseModel):
    claim: str
    status: Literal["supported", "unsupported", "uncertain"]
    evidence: str
    source_urls: list[str]


class FactCheckResult(BaseModel):
    checks: list[ClaimCheck]
