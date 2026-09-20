"""
M21 Dynamic SQL Validation
--------------------------

Validates user-supplied SQL without executing it.

This module is intentionally limited to validation and
statement classification. Structural analysis,
optimization candidate generation, benchmarking, and
database execution belong to later M21 milestones.
"""

from sqlglot import parse
from sqlglot.errors import ParseError

from api.schemas.structural_optimization import (
    QueryValidationResult,
    QueryValidationStatus,
)


# =========================================================
# SUPPORTED STATEMENT TYPES
# =========================================================

SUPPORTED_QUERY_TYPES = {
    "SELECT",
}


# =========================================================
# VALIDATOR
# =========================================================

def validate_sql(
    sql_query: str,
) -> QueryValidationResult:
    """
    Validate user-supplied SQL without executing it.

    Returns
    -------
    QueryValidationResult
        VALID:
            The SQL is syntactically valid and belongs to
            the currently supported read-oriented scope.

        INVALID:
            The SQL cannot be parsed as valid SQL.

        UNSUPPORTED:
            The SQL is syntactically valid but is outside
            the currently supported M21 scope.
    """

    # -----------------------------------------------------
    # Empty input
    # -----------------------------------------------------

    if not sql_query or not sql_query.strip():
        return QueryValidationResult(
            status=QueryValidationStatus.INVALID,
            message="SQL query is empty.",
        )

    sql = sql_query.strip()

    # -----------------------------------------------------
    # Parse SQL using PostgreSQL dialect
    # -----------------------------------------------------

    try:
        statements = parse(
            sql,
            dialect="postgres",
        )
    except ParseError as exc:
        return QueryValidationResult(
            status=QueryValidationStatus.INVALID,
            message=f"SQL parsing failed: {exc}",
        )
    except Exception as exc:
        return QueryValidationResult(
            status=QueryValidationStatus.INVALID,
            message=f"SQL validation failed: {exc}",
        )

    # -----------------------------------------------------
    # Empty parse result
    # -----------------------------------------------------

    if not statements:
        return QueryValidationResult(
            status=QueryValidationStatus.INVALID,
            message="No SQL statement was detected.",
        )

    # -----------------------------------------------------
    # Multiple statements
    # -----------------------------------------------------

    if len(statements) > 1:
        return QueryValidationResult(
            status=QueryValidationStatus.UNSUPPORTED,
            message="Multiple SQL statements are not supported.",
        )

    statement = statements[0]

    # -----------------------------------------------------
    # Determine statement type
    # -----------------------------------------------------

    query_type = statement.key.upper()

    # -----------------------------------------------------
    # Supported read-oriented statement
    # -----------------------------------------------------

    if query_type in SUPPORTED_QUERY_TYPES:
        normalized_query = statement.sql(
            dialect="postgres",
        )

        return QueryValidationResult(
            status=QueryValidationStatus.VALID,
            message="SQL query is valid and supported.",
            query_type=query_type,
            normalized_query=normalized_query,
        )

    # -----------------------------------------------------
    # Valid SQL but unsupported statement type
    # -----------------------------------------------------

    return QueryValidationResult(
        status=QueryValidationStatus.UNSUPPORTED,
        message=(
            f"SQL statement type '{query_type}' "
            "is valid but outside the current M21 "
            "read-oriented scope."
        ),
        query_type=query_type,
    )
