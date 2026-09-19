from enum import Enum


class EvidenceStatus(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"


class DecisionState(str, Enum):
    RECOMMEND = "RECOMMEND"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class GuardrailStatus(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class ProvenanceStatus(str, Enum):
    LINKED = "LINKED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


class ValidationOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    NEUTRAL = "NEUTRAL"
    UNSUCCESSFUL = "UNSUCCESSFUL"
    UNSAFE = "UNSAFE"
