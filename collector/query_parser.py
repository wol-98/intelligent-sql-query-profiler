"""
SQL Query Metadata Extractor
----------------------------
Extracts tables, aliases, WHERE columns, JOIN columns,
ORDER BY columns, and GROUP BY columns from SQL queries.

It also includes query fingerprinting to group structurally
similar queries.

This module does not execute SQL.
"""

import re
import hashlib


# =========================================================
# QUERY FINGERPRINTING
# =========================================================

class QueryFingerprinter:
    """
    Generates normalized SQL templates and fingerprints
    for structurally similar SQL queries.
    """

    @staticmethod
    def normalize_query(sql_query: str) -> str:
        """
        Normalize SQL text into a generic query template.

        Normalization includes:

        1. Removing SQL comments.
        2. Replacing string literals with '?'.
        3. Replacing numeric literals with '?'.
        4. Normalizing whitespace and case.
        5. Normalizing whitespace around common SQL operators.
        6. Removing repeated whitespace created by normalization.
        """

        # -------------------------------------------------
        # 1. Remove inline and multiline SQL comments
        # -------------------------------------------------

        sql = re.sub(
            r'--.*?\n|/\*.*?\*/',
            '',
            sql_query,
            flags=re.DOTALL,
        )

        # -------------------------------------------------
        # 2. Replace string literals
        # -------------------------------------------------

        sql = re.sub(
            r"'.*?'",
            "'?'",
            sql,
        )

        # -------------------------------------------------
        # 3. Replace numeric literals
        # -------------------------------------------------

        sql = re.sub(
            r'\b\d+\.?\d*\b',
            '?',
            sql,
        )

        # -------------------------------------------------
        # 4. Normalize whitespace and case
        # -------------------------------------------------

        sql = ' '.join(
            sql.split()
        ).upper()

        # -------------------------------------------------
        # 5. Normalize whitespace around operators
        # -------------------------------------------------

        sql = re.sub(
            r'\s*(=|<>|!=|<=|>=|<|>)\s*',
            r' \1 ',
            sql,
        )

        # -------------------------------------------------
        # 6. Normalize repeated whitespace
        # -------------------------------------------------

        sql = ' '.join(
            sql.split()
        )

        return sql

    @staticmethod
    def generate_fingerprint(
        sql_query: str,
    ) -> tuple[str, str]:
        """
        Generate a SHA-256 fingerprint for a normalized
        SQL query.

        Returns
        -------
        tuple[str, str]
            Fingerprint hash and normalized SQL template.
        """

        normalized_sql = (
            QueryFingerprinter.normalize_query(
                sql_query
            )
        )

        fingerprint_hash = hashlib.sha256(
            normalized_sql.encode(
                'utf-8'
            )
        ).hexdigest()

        return (
            fingerprint_hash,
            normalized_sql,
        )


# =========================================================
# QUERY PARSER
# =========================================================

def parse_query(
    sql_query: str,
) -> dict:
    """
    Extract structural metadata from an SQL query.

    The parser extracts:

    - Query type
    - Fingerprint
    - Normalized template
    - Tables
    - Aliases
    - WHERE columns
    - JOIN columns
    - ORDER BY columns
    - GROUP BY columns

    This function does not execute SQL.
    """

    # -----------------------------------------------------
    # Normalize original query whitespace
    # -----------------------------------------------------

    normalized_query = ' '.join(
        sql_query.strip().split()
    )

    # -----------------------------------------------------
    # Query type
    # -----------------------------------------------------

    query_type_match = re.match(
        r'^\s*(SELECT|INSERT|UPDATE|DELETE)',
        normalized_query,
        re.IGNORECASE,
    )

    query_type = (
        query_type_match.group(1).upper()
        if query_type_match
        else "UNKNOWN"
    )

    # -----------------------------------------------------
    # Generate query fingerprint
    # -----------------------------------------------------

    fingerprint, normalized_template = (
        QueryFingerprinter.generate_fingerprint(
            normalized_query
        )
    )

    # -----------------------------------------------------
    # Table extraction
    # -----------------------------------------------------

    tables = []

    table_patterns = [
        r'\bFROM\s+([A-Za-z_][A-Za-z0-9_]*)',
        r'\bJOIN\s+([A-Za-z_][A-Za-z0-9_]*)',
    ]

    for pattern in table_patterns:

        matches = re.findall(
            pattern,
            normalized_query,
            re.IGNORECASE,
        )

        for table in matches:

            if table.lower() not in [
                existing.lower()
                for existing in tables
            ]:
                tables.append(table)

    # -----------------------------------------------------
    # Alias extraction
    # -----------------------------------------------------

    aliases = {}

    alias_patterns = [
        r'\bFROM\s+([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)',
        r'\bJOIN\s+([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)',
    ]

    for pattern in alias_patterns:

        matches = re.findall(
            pattern,
            normalized_query,
            re.IGNORECASE,
        )

        for table, alias in matches:

            if alias.upper() in {
                "ON",
                "WHERE",
                "JOIN",
                "INNER",
                "LEFT",
                "RIGHT",
                "FULL",
                "GROUP",
                "ORDER",
                "LIMIT",
            }:
                continue

            aliases[
                alias.lower()
            ] = table.lower()

    # -----------------------------------------------------
    # WHERE columns
    # -----------------------------------------------------

    where_columns = []

    where_match = re.search(
        r'\bWHERE\b(.*?)(?:\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|$)',
        normalized_query,
        re.IGNORECASE,
    )

    if where_match:

        where_clause = (
            where_match.group(1)
        )

        # Match qualified or unqualified columns
        # appearing before common comparison operators.
        #
        # Examples:
        #
        # p.category_id = 1
        # status = 'Completed'
        # price BETWEEN 1000 AND 3000

        comparison_matches = re.findall(
            r'\b([A-Za-z_][A-Za-z0-9_]*'
            r'(?:\.[A-Za-z_][A-Za-z0-9_]*)?)'
            r'\s*(?:=|<>|!=|<=|>=|<|>|LIKE|IN)\s*',
            where_clause,
            re.IGNORECASE,
        )

        where_columns.extend(
            comparison_matches
        )

        # -------------------------------------------------
        # BETWEEN expressions
        # -------------------------------------------------

        between_matches = re.findall(
            r'\b([A-Za-z_][A-Za-z0-9_]*'
            r'(?:\.[A-Za-z_][A-Za-z0-9_]*)?)'
            r'\s+BETWEEN\b',
            where_clause,
            re.IGNORECASE,
        )

        where_columns.extend(
            between_matches
        )

    # -----------------------------------------------------
    # Remove duplicate WHERE columns
    # -----------------------------------------------------

    where_columns = list(
        dict.fromkeys(
            where_columns
        )
    )

    # -----------------------------------------------------
    # JOIN columns
    # -----------------------------------------------------

    join_columns = []

    join_matches = re.findall(
        r'\bON\s+'
        r'([A-Za-z_][A-Za-z0-9_]*'
        r'\.[A-Za-z_][A-Za-z0-9_]*)'
        r'\s*=\s*'
        r'([A-Za-z_][A-Za-z0-9_]*'
        r'\.[A-Za-z_][A-Za-z0-9_]*)',
        normalized_query,
        re.IGNORECASE,
    )

    for left_column, right_column in (
        join_matches
    ):
        join_columns.append(
            left_column
        )
        join_columns.append(
            right_column
        )

    # -----------------------------------------------------
    # Remove duplicate JOIN columns
    # -----------------------------------------------------

    join_columns = list(
        dict.fromkeys(
            join_columns
        )
    )

    # -----------------------------------------------------
    # ORDER BY columns
    # -----------------------------------------------------

    order_by_columns = []

    order_match = re.search(
        r'\bORDER\s+BY\b(.*?)(?:\bLIMIT\b|$)',
        normalized_query,
        re.IGNORECASE,
    )

    if order_match:

        order_clause = (
            order_match.group(1)
        )

        matches = re.findall(
            r'\b([A-Za-z_][A-Za-z0-9_]*'
            r'(?:\.[A-Za-z_][A-Za-z0-9_]*)?)\b',
            order_clause,
        )

        for column in matches:

            if column.upper() not in {
                "ASC",
                "DESC",
            }:
                order_by_columns.append(
                    column
                )

    # -----------------------------------------------------
    # Remove duplicate ORDER BY columns
    # -----------------------------------------------------

    order_by_columns = list(
        dict.fromkeys(
            order_by_columns
        )
    )

    # -----------------------------------------------------
    # GROUP BY columns
    # -----------------------------------------------------

    group_by_columns = []

    group_match = re.search(
        r'\bGROUP\s+BY\b(.*?)(?:\bORDER\s+BY\b|\bLIMIT\b|$)',
        normalized_query,
        re.IGNORECASE,
    )

    if group_match:

        group_clause = (
            group_match.group(1)
        )

        matches = re.findall(
            r'\b([A-Za-z_][A-Za-z0-9_]*'
            r'(?:\.[A-Za-z_][A-Za-z0-9_]*)?)\b',
            group_clause,
        )

        for column in matches:

            if column.upper() not in {
                "ASC",
                "DESC",
            }:
                group_by_columns.append(
                    column
                )

    # -----------------------------------------------------
    # Remove duplicate GROUP BY columns
    # -----------------------------------------------------

    group_by_columns = list(
        dict.fromkeys(
            group_by_columns
        )
    )

    # -----------------------------------------------------
    # Return metadata
    # -----------------------------------------------------

    return {
        "query_type": query_type,
        "fingerprint": fingerprint,
        "normalized_template":
            normalized_template,
        "tables": tables,
        "aliases": aliases,
        "where_columns":
            where_columns,
        "join_columns":
            join_columns,
        "order_by_columns":
            order_by_columns,
        "group_by_columns":
            group_by_columns,
    }


# =========================================================
# TEST / DEMONSTRATION
# =========================================================

def print_query_metadata(
    metadata: dict,
) -> None:
    """
    Print parsed SQL metadata in a readable format.
    """

    print("\n" + "=" * 65)
    print("SQL QUERY METADATA")
    print("=" * 65)

    print(
        f"Query type          : "
        f"{metadata['query_type']}"
    )

    print(
        f"Fingerprint Hash    : "
        f"{metadata['fingerprint']}"
    )

    print(
        f"Normalized Template : "
        f"{metadata['normalized_template']}"
    )

    print(
        f"Tables              : "
        f"{metadata['tables']}"
    )

    print(
        f"Aliases             : "
        f"{metadata['aliases']}"
    )

    print(
        f"WHERE columns       : "
        f"{metadata['where_columns']}"
    )

    print(
        f"JOIN columns        : "
        f"{metadata['join_columns']}"
    )

    print(
        f"ORDER BY columns    : "
        f"{metadata['order_by_columns']}"
    )

    print(
        f"GROUP BY columns    : "
        f"{metadata['group_by_columns']}"
    )

    print("=" * 65)


def main() -> None:
    """
    Run a simple parser demonstration.
    """

    query = """
        SELECT
            oi.order_id,
            p.product_name,
            oi.quantity,
            oi.unit_price
        FROM order_items oi
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE p.category_id = 1
        ORDER BY oi.order_id DESC
        LIMIT 20;
    """

    metadata = parse_query(
        query
    )

    print_query_metadata(
        metadata
    )


# =========================================================
# SCRIPT ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
