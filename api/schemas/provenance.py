from pydantic import BaseModel

from api.schemas.common import EvidenceStatus, ProvenanceStatus


class ProvenanceResponse(BaseModel):
    recommendation_id: int
    query_fingerprint: str | None = None
    index_name: str | None = None
    linked_experiment_id: str | None = None

    status: ProvenanceStatus
    evidence_status: EvidenceStatus
