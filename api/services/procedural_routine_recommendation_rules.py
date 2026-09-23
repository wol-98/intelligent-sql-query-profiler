from __future__ import annotations

from dataclasses import dataclass

from api.schemas.structural_optimization import (
    DatabaseRoutineRecommendationType,
    EvidenceStatus,
    ProceduralWorkloadOpportunityType,
)


@dataclass(frozen=True)
class ProceduralRoutineRecommendationRule:
    """
    Deterministic mapping from a procedural workload opportunity to a
    database function or stored-procedure recommendation type.

    The rule is architectural only. It does not establish semantic
    equivalence, behavioral correctness, performance improvement, or
    production suitability.
    """

    opportunity_type: ProceduralWorkloadOpportunityType
    recommendation_type: DatabaseRoutineRecommendationType
    required_evidence_status: EvidenceStatus
    requires_behavioral_validation: bool
    rationale: str


class ProceduralRoutineRecommendationRuleEngine:
    """
    Resolve deterministic function-vs-procedure recommendation rules.

    The engine does not:
      - generate SQL,
      - generate CREATE FUNCTION statements,
      - generate CREATE PROCEDURE statements,
      - execute database routines,
      - benchmark alternatives, or
      - make production decisions.
    """

    _RULES = {
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION: (
            ProceduralRoutineRecommendationRule(
                opportunity_type=(
                    ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
                ),
                recommendation_type=(
                    DatabaseRoutineRecommendationType.FUNCTION
                ),
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_behavioral_validation=True,
                rationale=(
                    "A structurally reusable computation may warrant "
                    "architectural analysis as a database function because "
                    "the detected workload pattern represents reusable "
                    "computation. Behavioral validation is required before "
                    "acceptance."
                ),
            )
        ),
        ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION: (
            ProceduralRoutineRecommendationRule(
                opportunity_type=(
                    ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION
                ),
                recommendation_type=(
                    DatabaseRoutineRecommendationType.FUNCTION
                ),
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_behavioral_validation=True,
                rationale=(
                    "A parameterized operation may warrant architectural "
                    "analysis as a database function because the detected "
                    "workload contains an explicit parameterized operation. "
                    "Behavioral validation is required before acceptance."
                ),
            )
        ),
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION: (
            ProceduralRoutineRecommendationRule(
                opportunity_type=(
                    ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION
                ),
                recommendation_type=(
                    DatabaseRoutineRecommendationType.PROCEDURE
                ),
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_behavioral_validation=True,
                rationale=(
                    "A multi-step data operation may warrant architectural "
                    "analysis as a stored procedure because the detected "
                    "structure represents staged data processing. "
                    "Behavioral validation is required before acceptance."
                ),
            )
        ),
        ProceduralWorkloadOpportunityType.DATA_MUTATION_WORKFLOW: (
            ProceduralRoutineRecommendationRule(
                opportunity_type=(
                    ProceduralWorkloadOpportunityType.DATA_MUTATION_WORKFLOW
                ),
                recommendation_type=(
                    DatabaseRoutineRecommendationType.PROCEDURE
                ),
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_behavioral_validation=True,
                rationale=(
                    "A data-mutation workflow may warrant architectural "
                    "analysis as a stored procedure because the workload "
                    "pattern is workflow-oriented. Behavioral validation "
                    "is required before acceptance."
                ),
            )
        ),
        ProceduralWorkloadOpportunityType.COMPLEX_PROCEDURAL_LOGIC: (
            ProceduralRoutineRecommendationRule(
                opportunity_type=(
                    ProceduralWorkloadOpportunityType.COMPLEX_PROCEDURAL_LOGIC
                ),
                recommendation_type=(
                    DatabaseRoutineRecommendationType.PROCEDURE
                ),
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_behavioral_validation=True,
                rationale=(
                    "Complex procedural logic may warrant architectural "
                    "analysis as a stored procedure because the workload "
                    "pattern is procedural in nature. Behavioral validation "
                    "is required before acceptance."
                ),
            )
        ),
        ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW: (
            ProceduralRoutineRecommendationRule(
                opportunity_type=(
                    ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW
                ),
                recommendation_type=(
                    DatabaseRoutineRecommendationType.PROCEDURE
                ),
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_behavioral_validation=True,
                rationale=(
                    "A side-effecting workflow may warrant architectural "
                    "analysis as a stored procedure because the detected "
                    "workload pattern is workflow-oriented. Behavioral "
                    "validation is required before acceptance."
                ),
            )
        ),
    }

    def get_rule(
        self,
        opportunity_type: ProceduralWorkloadOpportunityType,
    ) -> ProceduralRoutineRecommendationRule:
        try:
            return self._RULES[opportunity_type]
        except KeyError as exc:
            raise ValueError(
                "No procedural routine recommendation rule exists for "
                f"{opportunity_type}"
            ) from exc
