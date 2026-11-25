
from pydantic import BaseModel
from typing import Literal


class ResearchClaim(BaseModel):
    claim: str
    evidence: str
    source_urls: list[str]


class ResearchResult(BaseModel):
    claims: list[ResearchClaim]


class ClaimCheck(BaseModel):
    claim: str
    status: Literal["supported", "unsupported", "uncertain"]
    evidence: str
    source_urls: list[str]
    draft_quote: str


class FactCheckResult(BaseModel):
    checks: list[ClaimCheck]
