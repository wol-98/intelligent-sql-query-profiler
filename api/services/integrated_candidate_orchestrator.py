"""M21.13 integration layer for structural and index candidates.

This service combines:
    - structural candidates produced by StructuralAnalysisEnricher
    - index candidates produced by collector.index_candidate_generator

It does not:
    - rewrite SQL
    - execute index DDL
    - benchmark candidates
    - claim semantic equivalence
    - make optimization decisions

Executable SQL rewrites remain eligible for M21.14 only when a later
transformation stage supplies concrete alternative SQL.
"""

from __future__ import annotations

import uuid
from typing import Any, Callable, Dict, List

from api.schemas.structural_optimization import (
    AlternativeType,
    CandidateStatus,
    OptimizationCandidate,
)

from collector.index_candidate_generator import (
    generate_index_candidates,
)
from collector.recommendation_repository import (
    generate_index_sql,
)


class IntegratedCandidateOrchestrator:
    """Combine production structural and index candidate sources."""

    def __init__(
        self,
        structural_enricher,
        index_generator: Callable[
            [Dict[str, Any], Dict[str, Any]], List[Dict[str, Any]]
        ] = generate_index_candidates,
    ) -> None:
        self.structural_enricher = structural_enricher
        self.index_generator = index_generator

    def generate_unified_candidates(
        self,
        raw_sql: str,
        parsed_metadata: Dict[str, Any],
        features: Dict[str, Any],
        analysis,
    ) -> List[OptimizationCandidate]:
        """Return a unified M21.13 candidate collection.

        Structural candidates are obtained from the production
        StructuralAnalysisEnricher.

        Index candidates are obtained from the existing collector-level
        generate_index_candidates() function and converted into the
        OptimizationCandidate schema.

        No candidate is rewritten or executed here.
        """
        candidates: List[OptimizationCandidate] = []

        # ---------------------------------------------------------
        # 1. Production structural candidates
        # ---------------------------------------------------------
        structural_candidates = (
            self.structural_enricher.generate_candidates(
                analysis,
                raw_sql,
            )
        )

        candidates.extend(structural_candidates)

        # ---------------------------------------------------------
        # 2. Existing index candidate subsystem
        # ---------------------------------------------------------
        index_candidates = self.index_generator(
            features,
            parsed_metadata,
        )

        for number, index_candidate in enumerate(
            index_candidates,
            start=1,
        ):
            table_name = index_candidate.get("table_name")
            column_name = index_candidate.get("column_name")
            index_type = index_candidate.get(
                "index_type",
                "B-tree",
            )
            reason = index_candidate.get(
                "reason",
                "Index candidate generated from query structure.",
            )
            source = index_candidate.get("source")

            if not table_name or not column_name:
                continue

            index_ddl = generate_index_sql(
                table_name,
                column_name,
                index_type,
            )

            source_type = index_candidate.get("source_type")
            candidate_type = index_candidate.get("candidate_type")

            rationale_parts = [reason]

            if source:
                rationale_parts.append(f"Source: {source}.")

            if source_type:
                rationale_parts.append(
                    f"Source type: {source_type}."
                )

            if candidate_type:
                rationale_parts.append(
                    f"Candidate type: {candidate_type}."
                )

            candidates.append(
                OptimizationCandidate(
                    candidate_id=(
                        f"INDEX-CAND-{number:04d}-"
                        f"{uuid.uuid4().hex[:8]}"
                    ),
                    alternative_type=AlternativeType.INDEX,
                    status=CandidateStatus.CANDIDATE,
                    title=(
                        f"Index candidate on "
                        f"{table_name}({column_name})"
                    ),
                    rationale=" ".join(rationale_parts),
                    original_sql=raw_sql,
                    optimized_sql=None,
                    index_ddl=index_ddl,
                    architectural_recommendation=None,
                )
            )

        return candidates
