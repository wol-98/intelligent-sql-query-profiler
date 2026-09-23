"""M21.15 dynamic optimization blueprint generation.

The blueprint follows the five-section reporting structure defined by
Project Execution Plan v2.0:

1. Structural Performance Evaluation
2. Matrix Comparison
3. Optimized Structural SQL Code
4. Indexing Blueprint
5. Architectural Recommendations and Trade-offs

This service formats evidence and candidates. It does not execute SQL,
create indexes, establish semantic equivalence, or claim global optimality.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlglot import parse_one
from sqlglot.errors import ParseError

from api.schemas.structural_optimization import OptimizationCandidate


class DynamicBlueprintGenerator:
    """Generate the M21.15 five-section optimization blueprint."""

    def build_blueprint(
        self,
        raw_sql: str,
        parsed_metadata: Dict[str, Any],
        candidates: List[OptimizationCandidate],
        benchmark_result: Optional[Dict[str, Any]] = None,
        structural_analysis: Any = None,
    ) -> Dict[str, Any]:
        """Build the complete M21.15 blueprint."""
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sections": [
                self._format_structural_performance_evaluation(
                    raw_sql,
                    parsed_metadata,
                    candidates,
                    benchmark_result,
                    structural_analysis,
                ),
                self._format_matrix_comparison(
                    candidates,
                ),
                self._format_optimized_structural_sql(
                    candidates,
                    benchmark_result,
                ),
                self._format_indexing_blueprint(
                    candidates,
                ),
                self._format_architectural_recommendations(
                    candidates,
                    structural_analysis,
                    benchmark_result,
                ),
            ],
        }

    @staticmethod
    def _field(
        value: Any,
        name: str,
        default: Any = None,
    ) -> Any:
        """Read a field from either a Pydantic model or a dictionary."""
        if value is None:
            return default

        if isinstance(value, dict):
            return value.get(name, default)

        return getattr(value, name, default)

    @staticmethod
    def _enum_value(value: Any) -> Any:
        """Return Enum.value when applicable."""
        return getattr(value, "value", value)

    def _format_structural_performance_evaluation(
        self,
        raw_sql: str,
        parsed_metadata: Dict[str, Any],
        candidates: List[OptimizationCandidate],
        benchmark_result: Optional[Dict[str, Any]],
        structural_analysis: Any,
    ) -> Dict[str, Any]:
        """Format structural findings, layers and optimization opportunities."""
        findings = []

        if structural_analysis is not None:
            for finding in self._field(
                structural_analysis,
                "findings",
                [],
            ) or []:
                findings.append(
                    {
                        "layer": self._enum_value(
                            self._field(finding, "layer")
                        ),
                        "finding_type": self._field(
                            finding,
                            "finding_type",
                        ),
                        "description": self._field(
                            finding,
                            "description",
                        ),
                        "evidence": self._field(
                            finding,
                            "evidence",
                        ),
                    }
                )

        layers = []

        if structural_analysis is not None:
            layers = [
                self._enum_value(layer)
                for layer in (
                    self._field(
                        structural_analysis,
                        "layers_detected",
                        [],
                    )
                    or []
                )
            ]

        opportunities = [
            {
                "candidate_id": candidate.candidate_id,
                "title": candidate.title,
                "candidate_type": self._enum_value(
                    candidate.alternative_type
                ),
                "source_layer": self._enum_value(
                    candidate.source_layer
                ),
                "rationale": candidate.rationale,
                "status": self._enum_value(candidate.status),
            }
            for candidate in candidates
        ]

        evidence_status = (
            benchmark_result.get("evidence_status")
            if benchmark_result
            else "INSUFFICIENT"
        )

        if evidence_status == "MEASURED":
            performance_note = (
                "Measured benchmark evidence is available for a "
                "candidate alternative. Semantic equivalence still "
                "requires explicit validation."
            )
        elif evidence_status == "SIMULATED":
            performance_note = (
                "Only simulated benchmark evidence is available. "
                "It must not be treated as measured performance evidence."
            )
        else:
            performance_note = (
                "No measured alternative-query performance evidence "
                "is currently available."
            )

        return {
            "section": "1. Structural Performance Evaluation",
            "query": raw_sql.strip(),
            "query_type": self._field(
                structural_analysis,
                "query_type",
                parsed_metadata.get("query_type"),
            ),
            "tables": (
                self._field(
                    structural_analysis,
                    "tables",
                    None,
                )
                or parsed_metadata.get("tables", [])
            ),
            "query_layers": layers,
            "structural_findings": findings,
            "optimization_opportunities": opportunities,
            "performance_evidence_status": evidence_status,
            "performance_note": performance_note,
        }

    def _format_matrix_comparison(
        self,
        candidates: List[OptimizationCandidate],
    ) -> Dict[str, Any]:
        """Format the original-versus-alternative comparison matrix."""
        rows = [
            {
                "variant": "Original Query",
                "strategy": "Baseline",
                "structural_changes": "None",
                "expected_index_requirement": "None",
                "status": "BASELINE",
            }
        ]

        rewrite_candidates = [
            candidate
            for candidate in candidates
            if candidate.optimized_sql
        ]

        if rewrite_candidates:
            for candidate in rewrite_candidates:
                rows.append(
                    {
                        "variant": "Optimized Alternative",
                        "strategy": candidate.title,
                        "structural_changes": candidate.rationale,
                        "expected_index_requirement": (
                            "See Indexing Blueprint"
                            if candidate.index_ddl
                            else "Only where justified"
                        ),
                        "status": self._enum_value(candidate.status),
                    }
                )
        else:
            rows.append(
                {
                    "variant": "Optimized Alternative",
                    "strategy": "Not available",
                    "structural_changes": (
                        "No executable structural SQL rewrite "
                        "is currently available."
                    ),
                    "expected_index_requirement": "Not established",
                    "status": "NOT_AVAILABLE",
                }
            )

        index_candidates = [
            candidate
            for candidate in candidates
            if self._enum_value(candidate.alternative_type) == "INDEX"
        ]

        return {
            "section": "2. Matrix Comparison",
            "columns": [
                "Variant",
                "Strategy",
                "Structural changes",
                "Expected index requirement",
            ],
            "rows": rows,
            "index_candidate_count": len(index_candidates),
            "comparison_note": (
                "Structural alternatives remain candidates until "
                "semantic safety and performance evidence are established."
            ),
        }

    def _validate_sql_syntax(
        self,
        sql_code: str,
    ) -> str:
        """Validate candidate SQL syntax without executing it."""
        try:
            parse_one(
                sql_code,
                dialect="postgres",
            )
        except ParseError:
            return "INVALID"
        except Exception:
            return "INVALID"

        return "VALID"

    def _format_optimized_structural_sql(
        self,
        candidates: List[OptimizationCandidate],
        benchmark_result: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Format executable structural SQL candidates when available."""
        rewrite_candidates = [
            candidate
            for candidate in candidates
            if self._enum_value(candidate.alternative_type)
            == "SQL_REWRITE"
            and candidate.optimized_sql
        ]

        if not rewrite_candidates:
            return {
                "section": "3. Optimized Structural SQL Code",
                "status": "NOT_AVAILABLE",
                "sql_code": None,
                "syntax_status": "NOT_AVAILABLE",
                "evidence_status": (
                    benchmark_result.get("evidence_status")
                    if benchmark_result
                    else "INSUFFICIENT"
                ),
                "message": (
                    "No executable structural SQL rewrite is currently "
                    "available from the candidate-generation stage."
                ),
            }

        alternatives = []

        for candidate in rewrite_candidates:
            syntax_status = self._validate_sql_syntax(
                candidate.optimized_sql,
            )

            sql_code = (
                f"-- Structural candidate: {candidate.title}\n"
                f"-- Rationale: {candidate.rationale}\n"
                f"{candidate.optimized_sql.strip()}"
            )

            alternatives.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "title": candidate.title,
                    "syntax_status": syntax_status,
                    "sql_code": sql_code,
                    "semantic_safety": "NOT_ASSESSED",
                    "status": self._enum_value(candidate.status),
                }
            )

        evidence_status = (
            benchmark_result.get("evidence_status")
            if benchmark_result
            else "INSUFFICIENT"
        )

        if evidence_status == "MEASURED":
            status = "BENCHMARKED"
        elif evidence_status == "SIMULATED":
            status = "SIMULATED_NOT_DECISIONAL"
        else:
            status = "CANDIDATE_NOT_VALIDATED"

        return {
            "section": "3. Optimized Structural SQL Code",
            "status": status,
            "alternatives": alternatives,
            "evidence_status": evidence_status,
            "global_optimality_claim": False,
        }

    def _format_indexing_blueprint(
        self,
        candidates: List[OptimizationCandidate],
    ) -> Dict[str, Any]:
        """Format candidate index DDL without overstating evidence."""
        index_candidates = [
            candidate
            for candidate in candidates
            if (
                self._enum_value(candidate.alternative_type) == "INDEX"
                and candidate.index_ddl
            )
        ]

        if not index_candidates:
            return {
                "section": "4. Indexing Blueprint",
                "status": "NOT_AVAILABLE",
                "indexes": [],
                "message": (
                    "No index DDL candidate is currently available."
                ),
            }

        indexes = [
            {
                "candidate_id": candidate.candidate_id,
                "title": candidate.title,
                "ddl": candidate.index_ddl,
                "evidence_status": "INSUFFICIENT",
                "support_note": (
                    "Candidate DDL only. Execution evidence supporting "
                    "this index has not been established by the current "
                    "M21.15 pipeline."
                ),
            }
            for candidate in index_candidates
        ]

        return {
            "section": "4. Indexing Blueprint",
            "status": "CANDIDATE_DDL",
            "indexes": indexes,
            "evidence_status": "INSUFFICIENT",
            "global_optimality_claim": False,
        }

    def _format_architectural_recommendations(
        self,
        candidates: List[OptimizationCandidate],
        structural_analysis: Any,
        benchmark_result: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Format architectural options and explicit trade-offs."""
        recommendations = []
        seen = set()

        for candidate in candidates:
            recommendation = candidate.architectural_recommendation

            if recommendation:
                key = (
                    "explicit",
                    recommendation,
                )

                if key not in seen:
                    seen.add(key)
                    recommendations.append(
                        {
                            "type": "Candidate-specific",
                            "recommendation": recommendation,
                            "trade_offs": [
                                "Semantic correctness must be established.",
                                "Performance evidence must be established.",
                                "Operational complexity should be assessed.",
                            ],
                        }
                    )

        layers = set()

        if structural_analysis is not None:
            layers.update(
                self._enum_value(layer)
                for layer in (
                    self._field(
                        structural_analysis,
                        "layers_detected",
                        [],
                    )
                    or []
                )
            )

        for candidate in candidates:
            source_layer = self._enum_value(
                candidate.source_layer
            )

            if source_layer:
                layers.add(source_layer)

        layer_recommendations = {
            "CTE": (
                "CTE structure may be considered where decomposition "
                "improves clarity or reuse.",
                [
                    "Review materialization behavior.",
                    "Review freshness requirements.",
                    "Validate semantic equivalence and performance.",
                ],
            ),
            "JOIN": (
                "JOIN structure should be reviewed for relationship and "
                "filtering behavior before adopting a structural change.",
                [
                    "Validate join semantics.",
                    "Benchmark alternative structures.",
                    "Review supporting indexes separately.",
                ],
            ),
            "WINDOW": (
                "Window-function structure may be considered where ranking "
                "or analytical processing is required.",
                [
                    "Preserve ordering and partition semantics.",
                    "Validate row-level results.",
                    "Benchmark before adoption.",
                ],
            ),
            "SUBQUERY": (
                "Subquery structure may be considered for an alternative "
                "query formulation where semantic safety can be established.",
                [
                    "Validate semantic equivalence.",
                    "Check correlated-query behavior.",
                    "Benchmark the alternative.",
                ],
            ),
        }

        for layer in sorted(layers):
            if layer not in layer_recommendations:
                continue

            recommendation, trade_offs = layer_recommendations[layer]

            recommendations.append(
                {
                    "type": layer,
                    "recommendation": recommendation,
                    "trade_offs": trade_offs,
                }
            )

        recommendations.extend(
            [
                {
                    "type": "View / Materialized View",
                    "recommendation": (
                        "No view or materialized-view candidate is "
                        "currently attached to this blueprint."
                    ),
                    "trade_offs": [
                        "Storage and refresh requirements must be assessed.",
                        "Freshness requirements must be assessed.",
                        "Repeated-query benefit requires evidence.",
                    ],
                },
                {
                    "type": "Function / Procedure",
                    "recommendation": (
                        "No database-function or stored-procedure candidate "
                        "is currently attached to this blueprint."
                    ),
                    "trade_offs": [
                        "Procedural complexity should be justified by the workload.",
                        "Semantic behavior must remain clear.",
                        "Performance evidence is required before adoption.",
                    ],
                },
            ]
        )

        evidence_status = (
            benchmark_result.get("evidence_status")
            if benchmark_result
            else "INSUFFICIENT"
        )

        if evidence_status == "MEASURED":
            decision_note = (
                "Measured benchmark evidence is available, but the report "
                "does not claim global optimality and semantic validation "
                "remains required."
            )
        elif evidence_status == "SIMULATED":
            decision_note = (
                "Benchmark data is simulated; it is not sufficient for a "
                "performance recommendation."
            )
        else:
            decision_note = (
                "Current evidence is insufficient for a performance-based "
                "adoption decision."
            )

        return {
            "section": (
                "5. Architectural Recommendations and Trade-offs"
            ),
            "recommendations": recommendations,
            "evidence_status": evidence_status,
            "decision_note": decision_note,
            "global_optimality_claim": False,
        }


def build_blueprint(
    query_record: Dict[str, Any],
    original_sql: str,
    combined_candidates: List[OptimizationCandidate],
    benchmark_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Backward-compatible module-level wrapper."""
    return DynamicBlueprintGenerator().build_blueprint(
        raw_sql=original_sql,
        parsed_metadata=query_record,
        candidates=combined_candidates,
        benchmark_result=benchmark_result,
    )


def blueprint_to_text(
    blueprint: Dict[str, Any],
) -> str:
    """Render a blueprint into a simple text representation."""
    lines = [
        f"OPTIMIZATION BLUEPRINT — generated {blueprint['generated_at']}",
        "=" * 70,
    ]

    for section in blueprint["sections"]:
        title = section["section"]
        lines.append(f"\n{title}")
        lines.append("-" * len(title))

        for key, value in section.items():
            if key == "section":
                continue

            lines.append(f"  {key}: {value}")

    return "\n".join(lines)
