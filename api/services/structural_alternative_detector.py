from __future__ import annotations

import sqlglot
from sqlglot import exp

from api.schemas.structural_optimization import (
    CandidateStatus,
    EvidenceStatus,
    SemanticSafetyStatus,
    StructuralAlternativeCandidate,
    StructuralAlternativeResult,
    StructuralLayer,
    SubqueryAlternativeType,
)


class StructuralAlternativeDetector:
    """Detect subquery-related structural alternatives from SQL.

    This service is analytical only. It does not:

    - rewrite SQL,
    - claim semantic equivalence,
    - validate semantic safety,
    - execute SQL,
    - benchmark alternatives,
    - modify database objects, or
    - make production decisions.

    Detection is based exclusively on the SQLGlot AST produced using
    the PostgreSQL dialect.
    """

    def detect(self, original_sql: str) -> StructuralAlternativeResult:
        """Detect supported subquery structures in the supplied SQL.

        The original SQL is preserved exactly in every generated candidate.
        Candidate ordering follows deterministic AST traversal order.
        """

        expression = sqlglot.parse_one(
            original_sql,
            dialect="postgres",
        )

        candidates: list[StructuralAlternativeCandidate] = []
        candidate_number = 1

        for node in expression.walk():
            alternative_type = self._classify_node(node)

            if alternative_type is None:
                continue

            candidates.append(
                self._build_candidate(
                    candidate_number=candidate_number,
                    alternative_type=alternative_type,
                    original_sql=original_sql,
                    node=node,
                )
            )
            candidate_number += 1

        return StructuralAlternativeResult(candidates=candidates)

    @staticmethod
    def _classify_node(
        node: exp.Expression,
    ) -> SubqueryAlternativeType | None:
        """Return the structural alternative type represented by a node."""

        if isinstance(node, exp.Exists):
            return SubqueryAlternativeType.EXISTS

        if isinstance(node, exp.In):
            query = node.args.get("query")

            if isinstance(query, exp.Subquery):
                return SubqueryAlternativeType.IN

            return None

        if isinstance(node, exp.Any):
            subquery = node.args.get("this")

            if isinstance(subquery, exp.Subquery):
                return SubqueryAlternativeType.ANY

            return None

        if isinstance(node, exp.Subquery):
            if isinstance(node.parent, exp.From):
                return SubqueryAlternativeType.DERIVED_TABLE

        return None

    @staticmethod
    def _build_candidate(
        candidate_number: int,
        alternative_type: SubqueryAlternativeType,
        original_sql: str,
        node: exp.Expression,
    ) -> StructuralAlternativeCandidate:
        """Build a detection-only structural alternative candidate."""

        source_layer = (
            StructuralLayer.SUBQUERY
            if alternative_type != SubqueryAlternativeType.DERIVED_TABLE
            else StructuralLayer.FROM
        )

        titles = {
            SubqueryAlternativeType.EXISTS:
                "EXISTS subquery alternative",
            SubqueryAlternativeType.IN:
                "IN subquery alternative",
            SubqueryAlternativeType.ANY:
                "ANY subquery alternative",
            SubqueryAlternativeType.DERIVED_TABLE:
                "Derived-table alternative",
        }

        rationales = {
            SubqueryAlternativeType.EXISTS:
                "An EXISTS subquery structure was detected and is eligible "
                "for later semantic-safety analysis.",
            SubqueryAlternativeType.IN:
                "An IN subquery structure was detected and is eligible "
                "for later semantic-safety analysis.",
            SubqueryAlternativeType.ANY:
                "An ANY subquery structure was detected and is eligible "
                "for later semantic-safety analysis.",
            SubqueryAlternativeType.DERIVED_TABLE:
                "A derived-table structure was detected in the FROM layer "
                "and is eligible for later semantic-safety analysis.",
        }

        return StructuralAlternativeCandidate(
            candidate_id=f"ALT-{candidate_number:04d}",
            alternative_type=alternative_type,
            status=CandidateStatus.CANDIDATE,
            semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
            evidence_status=EvidenceStatus.COMPLETE,
            title=titles[alternative_type],
            rationale=rationales[alternative_type],
            source_layer=source_layer,
            original_sql=original_sql,
            alternative_sql=None,
        )
