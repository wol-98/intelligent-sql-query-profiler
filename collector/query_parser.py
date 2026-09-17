"""
SQL Query Metadata Extractor
----------------------------
Extracts tables, aliases, WHERE columns, JOIN columns,
ORDER BY columns, and GROUP BY columns from SQL queries.
It also includes query fingerprinting to group similar queries.

This module does not execute SQL.
"""

import re
import hashlib


# =========================================================
# QUERY FINGERPRINTING
# =========================================================

class QueryFingerprinter:
    @staticmethod
    def normalize_query(sql_query: str) -> str:
        """
        Strips literals (strings, numbers) and normalizes whitespace/case
        to create a generic query template.
        """
        # 1. Remove inline and multiline SQL comments
        sql = re.sub(r'--.*?\n|/\*.*?\*/', '', sql_query, flags=re.DOTALL)

        # 2. Replace string literals (e.g., 'Completed') with a placeholder '?'
        sql = re.sub(r"'.*?'", "'?'", sql)

        # 3. Replace numeric literals (e.g., 500, 10) with a placeholder ?
        sql = re.sub(r'\b\d+\.?\d*\b', '?', sql)

        # 4. Normalize whitespace and convert to uppercase for strict consistency
        sql = ' '.join(sql.split()).upper()

        return sql

    @staticmethod
    def generate_fingerprint(sql_query: str) -> tuple[str, str]:
        """
        Returns the SHA-256 hash fingerprint and the normalized SQL template.
        """
        normalized_sql = QueryFingerprinter.normalize_query(sql_query)
        fingerprint_hash = hashlib.sha256(normalized_sql.encode('utf-8')).hexdigest()

        return fingerprint_hash, normalized_sql


# =========================================================
# MAIN PARSER
# =========================================================

def parse_query(query: str) -> dict:
    """
    Extract metadata from a SQL query.

    Returns
    -------
    dict
        Structured SQL metadata, now including fingerprint hash.
    """

    normalized_query = " ".join(
        query.strip().split()
    )

    # Generate fingerprint and template
    fingerprint, normalized_template = QueryFingerprinter.generate_fingerprint(normalized_query)

    metadata = {
        "query": normalized_query,
        "query_type": get_query_type(
            normalized_query
        ),
        "fingerprint": fingerprint,
        "normalized_template": normalized_template,
        "tables": [],
        "aliases": {},
        "where_columns": [],
        "join_columns": [],
        "order_by_columns": [],
        "group_by_columns": [],
    }

    metadata["tables"] = extract_tables(
        normalized_query
    )

    metadata["aliases"] = extract_aliases(
        normalized_query
    )

    metadata["where_columns"] = extract_where_columns(
        normalized_query
    )

    metadata["join_columns"] = extract_join_columns(
        normalized_query
    )

    metadata["order_by_columns"] = extract_order_by_columns(
        normalized_query
    )

    metadata["group_by_columns"] = extract_group_by_columns(
        normalized_query
    )

    return metadata


# =========================================================
# QUERY TYPE
# =========================================================

def get_query_type(query: str) -> str:
    """
    Return the SQL query type.
    """

    if not query:
        return "UNKNOWN"

    return query.split()[0].upper()


# =========================================================
# TABLE EXTRACTION
# =========================================================

def extract_tables(query: str) -> list:
    """
    Extract table names appearing after FROM and JOIN.
    """

    tables = []

    pattern = re.compile(
        r"\b(?:FROM|JOIN)\s+"
        r"([A-Za-z_][A-Za-z0-9_]*)",
        re.IGNORECASE
    )

    matches = pattern.findall(
        query
    )

    for table in matches:

        if table not in tables:
            tables.append(table)

    return tables


# =========================================================
# ALIAS EXTRACTION
# =========================================================

def extract_aliases(query: str) -> dict:
    """
    Extract table aliases.

    Examples
    --------
    FROM order_items oi
        -> {"oi": "order_items"}

    JOIN products p
        -> {"p": "products"}
    """

    aliases = {}

    pattern = re.compile(
        r"\b(?:FROM|JOIN)\s+"
        r"([A-Za-z_][A-Za-z0-9_]*)"
        r"(?:\s+AS)?\s+"
        r"([A-Za-z_][A-Za-z0-9_]*)",
        re.IGNORECASE
    )

    matches = pattern.findall(
        query
    )

    sql_keywords = {
        "ON",
        "WHERE",
        "JOIN",
        "LEFT",
        "RIGHT",
        "INNER",
        "OUTER",
        "FULL",
        "CROSS",
        "GROUP",
        "ORDER",
        "LIMIT",
        "HAVING",
    }

    for table, alias in matches:

        if alias.upper() in sql_keywords:
            continue

        aliases[alias] = table

    return aliases


# =========================================================
# WHERE COLUMN EXTRACTION
# =========================================================

def extract_where_columns(query: str) -> list:
    """
    Extract probable columns used in WHERE conditions.

    Examples
    --------
    WHERE p.category_id = 1
        -> ['p.category_id']

    WHERE status = 'Completed'
        -> ['status']

    WHERE price > 1000
        -> ['price']
    """

    where_match = re.search(
        r"\bWHERE\b(.*?)(?:"
        r"\bGROUP\s+BY\b|"
        r"\bORDER\s+BY\b|"
        r"\bLIMIT\b|$"
        r")",
        query,
        re.IGNORECASE
    )

    if not where_match:
        return []

    where_clause = where_match.group(1)

    columns = []

    # -----------------------------------------------------
    # Qualified columns
    # Example:
    #     p.category_id = 1
    # -----------------------------------------------------

    qualified_pattern = re.compile(
        r"\b"
        r"([A-Za-z_][A-Za-z0-9_]*\."
        r"[A-Za-z_][A-Za-z0-9_]*)"
        r"\s*"
        r"(?:=|<>|!=|>=|<=|>|<|LIKE|ILIKE|BETWEEN|IN)",
        re.IGNORECASE
    )

    qualified_matches = qualified_pattern.findall(
        where_clause
    )

    for column in qualified_matches:

        if column not in columns:
            columns.append(column)

    # -----------------------------------------------------
    # Unqualified columns
    #
    # (?<!\.) prevents matching the column portion
    # of a qualified reference such as:
    #
    #     p.category_id
    # -----------------------------------------------------

    unqualified_pattern = re.compile(
        r"(?<!\.)"
        r"\b([A-Za-z_][A-Za-z0-9_]*)\b"
        r"\s*"
        r"(?:=|<>|!=|>=|<=|>|<|LIKE|ILIKE|BETWEEN|IN)",
        re.IGNORECASE
    )

    unqualified_matches = unqualified_pattern.findall(
        where_clause
    )

    sql_keywords = {
        "AND",
        "OR",
        "NOT",
        "IS",
        "NULL",
        "TRUE",
        "FALSE",
        "BETWEEN",
        "IN",
        "LIKE",
        "ILIKE",
    }

    for column in unqualified_matches:

        if column.upper() in sql_keywords:
            continue

        if column not in columns:
            columns.append(column)

    return columns


# =========================================================
# JOIN COLUMN EXTRACTION
# =========================================================

def extract_join_columns(query: str) -> list:
    """
    Extract columns used in JOIN conditions.

    Example:

        ON oi.product_id = p.product_id

    Returns:

        [
            "oi.product_id",
            "p.product_id"
        ]
    """

    columns = []

    pattern = re.compile(
        r"\bON\b(.*?)(?:"
        r"\bWHERE\b|"
        r"\bJOIN\b|"
        r"\bGROUP\s+BY\b|"
        r"\bORDER\s+BY\b|"
        r"\bLIMIT\b|$"
        r")",
        re.IGNORECASE
    )

    matches = pattern.findall(
        query
    )

    for join_condition in matches:

        qualified_columns = re.findall(
            r"\b"
            r"[A-Za-z_][A-Za-z0-9_]*\."
            r"[A-Za-z_][A-Za-z0-9_]*"
            r"\b",
            join_condition
        )

        for column in qualified_columns:

            if column not in columns:
                columns.append(column)

    return columns


# =========================================================
# ORDER BY EXTRACTION
# =========================================================

def extract_order_by_columns(query: str) -> list:
    """
    Extract columns used in ORDER BY.
    """

    match = re.search(
        r"\bORDER\s+BY\b(.*?)(?:"
        r"\bLIMIT\b|$"
        r")",
        query,
        re.IGNORECASE
    )

    if not match:
        return []

    order_clause = match.group(1)

    columns = []

    parts = order_clause.split(",")

    for part in parts:

        part = part.strip()

        # -------------------------------------------------
        # Remove ASC / DESC
        # -------------------------------------------------

        part = re.sub(
            r"\s+(ASC|DESC)\s*$",
            "",
            part,
            flags=re.IGNORECASE
        )

        # -------------------------------------------------
        # Remove trailing semicolon
        # -------------------------------------------------

        part = part.rstrip(";").strip()

        if part and part not in columns:
            columns.append(part)

    return columns


# =========================================================
# GROUP BY EXTRACTION
# =========================================================

def extract_group_by_columns(query: str) -> list:
    """
    Extract columns used in GROUP BY.

    Examples
    --------
    GROUP BY customer_id;
        -> ['customer_id']

    GROUP BY c.customer_id, c.name
        -> ['c.customer_id', 'c.name']
    """

    match = re.search(
        r"\bGROUP\s+BY\b(.*?)(?:"
        r"\bORDER\s+BY\b|"
        r"\bHAVING\b|"
        r"\bLIMIT\b|$"
        r")",
        query,
        re.IGNORECASE
    )

    if not match:
        return []

    group_clause = match.group(1)

    columns = []

    parts = group_clause.split(",")

    for part in parts:

        # -------------------------------------------------
        # Clean whitespace and trailing semicolon
        # -------------------------------------------------

        column = (
            part
            .strip()
            .rstrip(";")
            .strip()
        )

        if column and column not in columns:
            columns.append(column)

    return columns


# =========================================================
# DISPLAY
# =========================================================

def print_query_metadata(metadata: dict):
    """
    Print extracted SQL metadata.
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
