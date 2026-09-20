"""
M21 Schema Introspection
------------------------

Read-only PostgreSQL schema discovery for the dynamic SQL
optimization pipeline.

This module reads metadata from information_schema only.
It does not execute user-supplied SQL and does not modify
the database.
"""

from dataclasses import dataclass, field

from config.database import get_connection


@dataclass(frozen=True)
class ColumnMetadata:
    """Metadata describing one database column."""

    name: str
    data_type: str
    ordinal_position: int


@dataclass(frozen=True)
class TableMetadata:
    """Metadata describing one database table."""

    schema: str
    name: str
    columns: tuple[ColumnMetadata, ...] = field(
        default_factory=tuple
    )


class SchemaIntrospector:
    """
    Read-only PostgreSQL schema introspector.

    By default, the application schema is public.
    """

    def __init__(self, schema: str = "public"):
        self.schema = schema

    def get_tables(self) -> tuple[TableMetadata, ...]:
        """
        Return all tables and their columns for the configured
        PostgreSQL schema.

        Only information_schema metadata is queried.
        """

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        table_schema,
                        table_name,
                        column_name,
                        data_type,
                        ordinal_position
                    FROM information_schema.columns
                    WHERE table_schema = %s
                    ORDER BY
                        table_name,
                        ordinal_position;
                    """,
                    (self.schema,),
                )

                rows = cursor.fetchall()

        finally:
            connection.close()

        tables: dict[str, list[ColumnMetadata]] = {}

        for (
            table_schema,
            table_name,
            column_name,
            data_type,
            ordinal_position,
        ) in rows:
            tables.setdefault(table_name, []).append(
                ColumnMetadata(
                    name=column_name,
                    data_type=data_type,
                    ordinal_position=ordinal_position,
                )
            )

        return tuple(
            TableMetadata(
                schema=self.schema,
                name=table_name,
                columns=tuple(columns),
            )
            for table_name, columns in sorted(tables.items())
        )

    def get_table(
        self,
        table_name: str,
    ) -> TableMetadata | None:
        """
        Return metadata for one table, or None if it does not
        exist in the configured schema.
        """

        normalized_name = table_name.strip().lower()

        for table in self.get_tables():
            if table.name.lower() == normalized_name:
                return table

        return None

    def table_exists(
        self,
        table_name: str,
    ) -> bool:
        """Return whether a table exists in the configured schema."""

        return self.get_table(table_name) is not None

    def column_exists(
        self,
        table_name: str,
        column_name: str,
    ) -> bool:
        """
        Return whether a column exists on a table in the
        configured schema.
        """

        table = self.get_table(table_name)

        if table is None:
            return False

        normalized_column = column_name.strip().lower()

        return any(
            column.name.lower() == normalized_column
            for column in table.columns
        )
