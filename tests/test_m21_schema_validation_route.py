from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from api.main import app
from api.services.schema_introspector import SchemaIntrospector
from api.services.schema_validator import (
    ColumnReference,
    ColumnValidationResult,
    SchemaValidationResult,
    TableReference,
    TableValidationResult,
)

client = TestClient(app)


def make_valid_schema_result():
    return SchemaValidationResult(
        valid=True,
        tables=(
            TableValidationResult(
                reference=TableReference(
                    schema="public",
                    table="products",
                ),
                exists=True,
            ),
        ),
        columns=(
            ColumnValidationResult(
                reference=ColumnReference(
                    name="price",
                    table="products",
                ),
                resolved_table="products",
                exists=True,
            ),
        ),
    )


def make_invalid_schema_result(
    *,
    missing_tables=(),
    missing_columns=(),
    ambiguous_columns=(),
):
    return SchemaValidationResult(
        valid=False,
        missing_tables=tuple(missing_tables),
        missing_columns=tuple(missing_columns),
        ambiguous_columns=tuple(ambiguous_columns),
    )


def make_introspector():
    introspector = MagicMock(spec=SchemaIntrospector)
    introspector.schema_exists.return_value = True
    return introspector


@patch("api.routes.dynamic_optimization.validate_tables")
@patch("api.routes.dynamic_optimization.SchemaIntrospector")
def test_valid_schema_reaches_optimization_pipeline(
    mock_introspector_class,
    mock_validate_tables,
):
    introspector = make_introspector()
    mock_introspector_class.return_value = introspector
    mock_validate_tables.return_value = make_valid_schema_result()

    response = client.post(
        "/api/v2/optimization/studio/blueprint",
        json={
            "raw_sql": "SELECT * FROM products WHERE price > 100;",
            "target_schema": "public",
            "enforce_safety_guardrails": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["sections"][0]["section"] == (
        "1. Structural Performance Evaluation"
    )

    mock_introspector_class.assert_called_once_with(schema="public")
    introspector.schema_exists.assert_called_once()
    mock_validate_tables.assert_called_once()


@patch("api.routes.dynamic_optimization.validate_tables")
@patch("api.routes.dynamic_optimization.SchemaIntrospector")
def test_missing_schema_returns_422(
    mock_introspector_class,
    mock_validate_tables,
):
    introspector = make_introspector()
    introspector.schema_exists.return_value = False
    mock_introspector_class.return_value = introspector

    response = client.post(
        "/api/v2/optimization/studio/blueprint",
        json={
            "raw_sql": "SELECT * FROM products;",
            "target_schema": "missing_schema",
            "enforce_safety_guardrails": True,
        },
    )

    assert response.status_code == 422

    detail = response.json()["detail"]

    assert detail["status"] == "INVALID_SCHEMA"
    assert detail["error_type"] == "SCHEMA_NOT_FOUND"
    assert detail["schema"] == "missing_schema"

    mock_validate_tables.assert_not_called()


@patch("api.routes.dynamic_optimization.validate_tables")
@patch("api.routes.dynamic_optimization.SchemaIntrospector")
def test_missing_table_returns_422(
    mock_introspector_class,
    mock_validate_tables,
):
    mock_introspector_class.return_value = make_introspector()
    mock_validate_tables.return_value = make_invalid_schema_result(
        missing_tables=("public/missing_products",),
    )

    response = client.post(
        "/api/v2/optimization/studio/blueprint",
        json={
            "raw_sql": "SELECT * FROM missing_products;",
            "target_schema": "public",
            "enforce_safety_guardrails": True,
        },
    )

    assert response.status_code == 422

    detail = response.json()["detail"]

    assert detail["status"] == "INVALID_SCHEMA"
    assert detail["error_type"] == "SCHEMA_COMPATIBILITY_FAILED"
    assert detail["missing_tables"] == ["public/missing_products"]


@patch("api.routes.dynamic_optimization.validate_tables")
@patch("api.routes.dynamic_optimization.SchemaIntrospector")
def test_missing_column_returns_422(
    mock_introspector_class,
    mock_validate_tables,
):
    mock_introspector_class.return_value = make_introspector()
    mock_validate_tables.return_value = make_invalid_schema_result(
        missing_columns=("products.prize",),
    )

    response = client.post(
        "/api/v2/optimization/studio/blueprint",
        json={
            "raw_sql": "SELECT prize FROM products;",
            "target_schema": "public",
            "enforce_safety_guardrails": True,
        },
    )

    assert response.status_code == 422

    detail = response.json()["detail"]

    assert detail["status"] == "INVALID_SCHEMA"
    assert detail["missing_columns"] == ["products.prize"]


@patch("api.routes.dynamic_optimization.validate_tables")
@patch("api.routes.dynamic_optimization.SchemaIntrospector")
def test_ambiguous_column_returns_422(
    mock_introspector_class,
    mock_validate_tables,
):
    mock_introspector_class.return_value = make_introspector()
    mock_validate_tables.return_value = make_invalid_schema_result(
        ambiguous_columns=("customer_id",),
    )

    response = client.post(
        "/api/v2/optimization/studio/blueprint",
        json={
            "raw_sql": """
                SELECT customer_id
                FROM orders o
                JOIN customers c
                  ON o.customer_id = c.customer_id;
            """,
            "target_schema": "public",
            "enforce_safety_guardrails": True,
        },
    )

    assert response.status_code == 422

    detail = response.json()["detail"]

    assert detail["status"] == "INVALID_SCHEMA"
    assert detail["ambiguous_columns"] == ["customer_id"]
