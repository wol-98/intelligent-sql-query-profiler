from api.schemas.structural_optimization import (
    DatabaseRoutineRecommendationType,
    SemanticSafetyStatus,
)
from api.services.structural_database_routine_semantic_precondition_analyzer import (
    StructuralDatabaseRoutineSemanticPreconditionAnalyzer,
)


def test_parameterized_function_requires_validation():
    sql = """
        SELECT customer_id
        FROM orders
        WHERE customer_id = $1
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.FUNCTION,
        )
    )

    assert (
        result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )

    names = [
        finding.name
        for finding in result.findings
    ]

    assert "PARAMETER_SIGNATURE" in names

    parameter_finding = next(
        finding
        for finding in result.findings
        if finding.name == "PARAMETER_SIGNATURE"
    )

    assert parameter_finding.detected is True


def test_function_detects_result_and_table_dependencies():
    sql = """
        SELECT customer_id, COUNT(*)
        FROM orders
        GROUP BY customer_id
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.FUNCTION,
        )
    )

    findings = {
        finding.name: finding.detected
        for finding in result.findings
    }

    assert findings["RETURN_VALUE_SEMANTICS"] is True
    assert findings["INPUT_DATA_DEPENDENCIES"] is True


def test_function_detects_null_and_type_constructs():
    sql = """
        SELECT CAST(customer_id AS INTEGER)
        FROM orders
        WHERE deleted_at IS NULL
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.FUNCTION,
        )
    )

    finding = next(
        finding
        for finding in result.findings
        if finding.name == "NULL_AND_TYPE_SEMANTICS"
    )

    assert finding.detected is True


def test_function_detects_known_volatility_construct():
    sql = """
        SELECT random()
        FROM orders
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.FUNCTION,
        )
    )

    finding = next(
        finding
        for finding in result.findings
        if finding.name == "DETERMINISM_VOLATILITY"
    )

    assert finding.detected is True


def test_function_does_not_assume_volatility_from_plain_select():
    sql = """
        SELECT customer_id
        FROM orders
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.FUNCTION,
        )
    )

    finding = next(
        finding
        for finding in result.findings
        if finding.name == "DETERMINISM_VOLATILITY"
    )

    assert finding.detected is False
    assert "not established" in finding.rationale


def test_function_detects_security_construct():
    sql = """
        SELECT CURRENT_USER
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.FUNCTION,
        )
    )

    finding = next(
        finding
        for finding in result.findings
        if finding.name == "SECURITY_CONTEXT"
    )

    assert finding.detected is True


def test_procedure_detects_multi_step_execution():
    sql = """
        WITH customer_orders AS (
            SELECT customer_id, COUNT(*) AS order_count
            FROM orders
            GROUP BY customer_id
        )
        SELECT *
        FROM customer_orders
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.PROCEDURE,
        )
    )

    finding = next(
        finding
        for finding in result.findings
        if finding.name == "MULTI_STEP_EXECUTION"
    )

    assert finding.detected is True


def test_procedure_detects_mutation():
    sql = """
        UPDATE orders
        SET status = 'completed'
        WHERE order_id = $1
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.PROCEDURE,
        )
    )

    data_mutation = next(
        finding
        for finding in result.findings
        if finding.name == "DATA_MUTATION_BEHAVIOR"
    )

    side_effect = next(
        finding
        for finding in result.findings
        if finding.name == "SIDE_EFFECT_BEHAVIOR"
    )

    assert data_mutation.detected is True
    assert side_effect.detected is True


def test_procedure_detects_transaction_construct():
    sql = """
        BEGIN;
        UPDATE orders
        SET status = 'completed'
        WHERE order_id = $1;
        COMMIT;
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.PROCEDURE,
        )
    )

    transaction = next(
        finding
        for finding in result.findings
        if finding.name == "TRANSACTION_BEHAVIOR"
    )

    rollback = next(
        finding
        for finding in result.findings
        if finding.name == "ERROR_AND_ROLLBACK_BEHAVIOR"
    )

    assert transaction.detected is True
    assert rollback.detected is True


def test_procedure_detects_parameter_signature():
    sql = """
        UPDATE orders
        SET status = 'completed'
        WHERE order_id = $1
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.PROCEDURE,
        )
    )

    finding = next(
        finding
        for finding in result.findings
        if finding.name == "PARAMETER_SIGNATURE"
    )

    assert finding.detected is True


def test_invalid_sql_is_not_assessed():
    sql = """
        SELECT FROM
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.FUNCTION,
        )
    )

    assert (
        result.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )

    assert result.findings == ()


def test_function_and_procedure_have_different_precondition_sets():
    sql = """
        SELECT customer_id
        FROM orders
        WHERE customer_id = $1
    """

    analyzer = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
    )

    function_result = analyzer.analyze(
        sql,
        DatabaseRoutineRecommendationType.FUNCTION,
    )

    procedure_result = analyzer.analyze(
        sql,
        DatabaseRoutineRecommendationType.PROCEDURE,
    )

    function_names = {
        finding.name
        for finding in function_result.findings
    }

    procedure_names = {
        finding.name
        for finding in procedure_result.findings
    }

    assert "DETERMINISM_VOLATILITY" in function_names
    assert "MULTI_STEP_EXECUTION" in procedure_names

    assert "TRANSACTION_BEHAVIOR" not in function_names
    assert "DETERMINISM_VOLATILITY" not in procedure_names


def test_precondition_analysis_is_deterministic():
    sql = """
        SELECT customer_id
        FROM orders
        WHERE customer_id = $1
    """

    analyzer = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
    )

    first = analyzer.analyze(
        sql,
        DatabaseRoutineRecommendationType.FUNCTION,
    )

    second = analyzer.analyze(
        sql,
        DatabaseRoutineRecommendationType.FUNCTION,
    )

    assert first == second


def test_precondition_analysis_does_not_claim_safety():
    sql = """
        SELECT customer_id
        FROM orders
        WHERE customer_id = $1
    """

    result = (
        StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        .analyze(
            sql,
            DatabaseRoutineRecommendationType.FUNCTION,
        )
    )

    assert (
        result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )

    assert result.semantic_safety != (
        SemanticSafetyStatus.UNSAFE
    )
