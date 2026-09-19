from pydantic import BaseModel

from api.schemas.common import (
    DecisionState,
    EvidenceStatus,
    GuardrailStatus,
)


class GuardrailCheck(BaseModel):
    name: str
    status: GuardrailStatus
    detail: str | None = None


class ProductionDecisionResponse(BaseModel):
    recommendation_id: int

    state: DecisionState
    reason: str | None = None

    guardrail_status: GuardrailStatus
    guardrail_checks: list[GuardrailCheck]

    evidence_status: EvidenceStatus
