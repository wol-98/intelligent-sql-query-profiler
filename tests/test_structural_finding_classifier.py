from api.schemas.structural_optimization import (
    EvidenceQuality,
    EvidenceStatus,
    OptimizationRelevance,
    StructuralFinding,
    StructuralFindingClassificationType,
    StructuralLayer,
)
from api.services.structural_finding_classifier import (
    StructuralFindingClassifier,
)


def finding(
    layer: StructuralLayer,
    finding_type: str,
    evidence: str | None,
) -> StructuralFinding:
    return StructuralFinding(
        layer=layer,
        finding_type=finding_type,
        severity="INFO",
        description="Test structural finding.",
        evidence=evidence,
    )


def test_where_is_classified_as_predicate_and_potentially_relevant():
    result = StructuralFindingClassifier().classify(
        [
            finding(
                StructuralLayer.WHERE,
                "FILTER",
                "query_block=1; where=WHERE customer_id = 845",
            )
        ]
    )

    classification = result.classifications[0]

    assert classification.finding_index == 0
    assert (
        classification.classification
        == StructuralFindingClassificationType.PREDICATE
    )
    assert classification.evidence_status == EvidenceStatus.COMPLETE
    assert classification.evidence_quality == EvidenceQuality.EXACT
    assert (
        classification.optimization_relevance
        == OptimizationRelevance.POTENTIALLY_RELEVANT
    )


def test_join_is_classified_as_relationship():
    result = StructuralFindingClassifier().classify(
        [
            finding(
                StructuralLayer.JOIN,
                "JOIN",
                "query_block=1; join=JOIN customers AS c "
                "ON o.customer_id = c.customer_id",
            )
        ]
    )

    classification = result.classifications[0]

    assert (
        classification.classification
        == StructuralFindingClassificationType.RELATIONSHIP
    )
    assert classification.evidence_status == EvidenceStatus.COMPLETE
    assert classification.evidence_quality == EvidenceQuality.EXACT


def test_select_is_contextual():
    result = StructuralFindingClassifier().classify(
        [
            finding(
                StructuralLayer.SELECT,
                "SELECT_LIST",
                "query_block=1; expressions=customer_id, total_amount",
            )
        ]
    )

    classification = result.classifications[0]

    assert (
        classification.classification
        == StructuralFindingClassificationType.DIRECT_OPERATION
    )
    assert (
        classification.optimization_relevance
        == OptimizationRelevance.CONTEXTUAL
    )


def test_from_is_source_definition():
    result = StructuralFindingClassifier().classify(
        [
            finding(
                StructuralLayer.FROM,
                "TABLE_SOURCE",
                "query_block=1; from=FROM orders",
            )
        ]
    )

    classification = result.classifications[0]

    assert (
        classification.classification
        == StructuralFindingClassificationType.SOURCE_DEFINITION
    )
    assert (
        classification.optimization_relevance
        == OptimizationRelevance.CONTEXTUAL
    )


def test_group_by_and_having_are_aggregation():
    result = StructuralFindingClassifier().classify(
        [
            finding(
                StructuralLayer.GROUP_BY,
                "GROUPING",
                "query_block=1; group_by=GROUP BY customer_id",
            ),
            finding(
                StructuralLayer.HAVING,
                "AGGREGATE_FILTER",
                "query_block=1; having=HAVING COUNT(*) > 2",
            ),
        ]
    )

    classifications = result.classifications

    assert all(
        item.classification
        == StructuralFindingClassificationType.AGGREGATION
        for item in classifications
    )
    assert all(
        item.optimization_relevance
        == OptimizationRelevance.POTENTIALLY_RELEVANT
        for item in classifications
    )


def test_window_order_and_limit_are_potentially_relevant():
    findings = [
        finding(
            StructuralLayer.WINDOW,
            "WINDOW_FUNCTION",
            "query_block=1; window=ROW_NUMBER() OVER (...)",
        ),
        finding(
            StructuralLayer.ORDER_BY,
            "ORDERING",
            "query_block=1; order_by=ORDER BY order_date DESC",
        ),
        finding(
            StructuralLayer.LIMIT_OFFSET,
            "ROW_LIMITING",
            "query_block=1; limit=LIMIT 10; offset=OFFSET 5",
        ),
    ]

    result = StructuralFindingClassifier().classify(findings)

    assert [
        item.classification for item in result.classifications
    ] == [
        StructuralFindingClassificationType.WINDOW_OPERATION,
        StructuralFindingClassificationType.ORDERING,
        StructuralFindingClassificationType.ROW_LIMITING,
    ]

    assert all(
        item.optimization_relevance
        == OptimizationRelevance.POTENTIALLY_RELEVANT
        for item in result.classifications
    )


def test_subquery_summary_is_partial_summary_evidence():
    result = StructuralFindingClassifier().classify(
        [
            finding(
                StructuralLayer.SUBQUERY,
                "SUBQUERY",
                "subquery_count=1",
            )
        ]
    )

    classification = result.classifications[0]

    assert (
        classification.classification
        == StructuralFindingClassificationType.NESTED_QUERY
    )
    assert classification.evidence_status == EvidenceStatus.PARTIAL
    assert classification.evidence_quality == EvidenceQuality.SUMMARY
    assert (
        classification.optimization_relevance
        == OptimizationRelevance.POTENTIALLY_RELEVANT
    )


def test_set_operation_is_contextual():
    result = StructuralFindingClassifier().classify(
        [
            finding(
                StructuralLayer.SET_OPERATION,
                "SET_OPERATION",
                "UNION",
            )
        ]
    )

    classification = result.classifications[0]

    assert (
        classification.classification
        == StructuralFindingClassificationType.SET_OPERATION
    )
    assert (
        classification.optimization_relevance
        == OptimizationRelevance.CONTEXTUAL
    )


def test_missing_evidence_becomes_insufficient_and_not_assessed():
    result = StructuralFindingClassifier().classify(
        [
            finding(
                StructuralLayer.WHERE,
                "FILTER",
                None,
            )
        ]
    )

    classification = result.classifications[0]

    assert classification.evidence_status == EvidenceStatus.INSUFFICIENT
    assert classification.evidence_quality == EvidenceQuality.MISSING
    assert (
        classification.optimization_relevance
        == OptimizationRelevance.NOT_ASSESSED
    )


def test_empty_evidence_becomes_insufficient_and_not_assessed():
    result = StructuralFindingClassifier().classify(
        [
            finding(
                StructuralLayer.WHERE,
                "FILTER",
                "   ",
            )
        ]
    )

    classification = result.classifications[0]

    assert classification.evidence_status == EvidenceStatus.INSUFFICIENT
    assert classification.evidence_quality == EvidenceQuality.MISSING
    assert (
        classification.optimization_relevance
        == OptimizationRelevance.NOT_ASSESSED
    )


def test_finding_order_and_indexes_are_preserved():
    findings = [
        finding(
            StructuralLayer.SELECT,
            "SELECT_LIST",
            "query_block=1; expressions=customer_id",
        ),
        finding(
            StructuralLayer.WHERE,
            "FILTER",
            "query_block=1; where=WHERE customer_id = 845",
        ),
        finding(
            StructuralLayer.ORDER_BY,
            "ORDERING",
            "query_block=1; order_by=ORDER BY customer_id",
        ),
    ]

    result = StructuralFindingClassifier().classify(findings)

    assert [
        item.finding_index for item in result.classifications
    ] == [0, 1, 2]


def test_classifier_does_not_make_performance_claims():
    result = StructuralFindingClassifier().classify(
        [
            finding(
                StructuralLayer.WHERE,
                "FILTER",
                "query_block=1; where=WHERE customer_id = 845",
            )
        ]
    )

    rationale = result.classifications[0].rationale.lower()

    assert "make a recommendation" not in rationale
    assert "recommendation to optimize" not in rationale
    assert "slow" not in rationale
    assert "performance" not in rationale
    assert "index" not in rationale
    assert "problem" in rationale
