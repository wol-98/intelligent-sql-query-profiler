"""
Feature Extractor
-----------------
Extracts useful query-plan features from the flattened
execution-plan nodes produced by plan_analyzer.py.
"""


def extract_plan_features(plan_nodes):
    """
    Extract structured features from flattened plan nodes.

    Parameters
    ----------
    plan_nodes : list of dict
        Output returned by analyze_plan()

    Returns
    -------
    dict
        Structured plan features
    """

    features = {
        "node_count": len(plan_nodes),

        "node_types": [],
        "scan_nodes": [],
        "join_nodes": [],
        "aggregate_nodes": [],
        "sort_nodes": [],

        "tables": [],

        "filters": [],
        "index_conditions": [],
        "join_conditions": [],

        "index_names": [],

        "total_actual_rows": 0,
        "total_plan_rows": 0,

        "total_rows_removed_by_filter": 0,

        "total_shared_hit_blocks": 0,
        "total_shared_read_blocks": 0,

        "seq_scan_count": 0,
        "index_scan_count": 0,
        "bitmap_scan_count": 0,

        "hash_join_count": 0,
        "nested_loop_count": 0,
        "merge_join_count": 0,

        "has_filter": False,
        "has_index_condition": False,
        "has_join": False,
        "has_sequential_scan": False,
        "has_index_scan": False,
    }

    for node in plan_nodes:

        node_type = node.get("node_type")
        relation_name = node.get("relation_name")
        index_name = node.get("index_name")
        join_type = node.get("join_type")

        actual_rows = node.get("actual_rows") or 0
        plan_rows = node.get("plan_rows") or 0
        rows_removed = node.get("rows_removed_by_filter") or 0

        shared_hits = node.get("shared_hit_blocks") or 0
        shared_reads = node.get("shared_read_blocks") or 0

        filter_condition = node.get("filter")
        index_condition = node.get("index_condition")
        join_filter = node.get("join_filter")
        hash_condition = node.get("hash_condition")

        # --------------------------------------------------
        # Node types
        # --------------------------------------------------

        if node_type:
            features["node_types"].append(node_type)

        # --------------------------------------------------
        # Tables
        # --------------------------------------------------

        if relation_name:
            if relation_name not in features["tables"]:
                features["tables"].append(relation_name)

        # --------------------------------------------------
        # Scan nodes
        # --------------------------------------------------

        if node_type in (
            "Seq Scan",
            "Index Scan",
            "Index Only Scan",
            "Bitmap Heap Scan",
            "Bitmap Index Scan",
        ):
            features["scan_nodes"].append({
                "node_type": node_type,
                "table": relation_name,
                "actual_rows": actual_rows,
                "plan_rows": plan_rows,
                "rows_removed_by_filter": rows_removed,
                "filter": filter_condition,
                "index_condition": index_condition,
                "index_name": index_name,
            })

        # --------------------------------------------------
        # Sequential scans
        # --------------------------------------------------

        if node_type == "Seq Scan":
            features["seq_scan_count"] += 1
            features["has_sequential_scan"] = True

        # --------------------------------------------------
        # Index scans
        # --------------------------------------------------

        if node_type in ("Index Scan", "Index Only Scan"):
            features["index_scan_count"] += 1
            features["has_index_scan"] = True

        # --------------------------------------------------
        # Bitmap scans
        # --------------------------------------------------

        if node_type in ("Bitmap Heap Scan", "Bitmap Index Scan"):
            features["bitmap_scan_count"] += 1

        # --------------------------------------------------
        # Join nodes
        # --------------------------------------------------

        if join_type or node_type in (
            "Hash Join",
            "Nested Loop",
            "Merge Join",
        ):
            features["has_join"] = True

            features["join_nodes"].append({
                "node_type": node_type,
                "join_type": join_type,
                "join_filter": join_filter,
                "hash_condition": hash_condition,
            })

        if node_type == "Hash Join":
            features["hash_join_count"] += 1

        if node_type == "Nested Loop":
            features["nested_loop_count"] += 1

        if node_type == "Merge Join":
            features["merge_join_count"] += 1

        # --------------------------------------------------
        # Aggregate nodes
        # --------------------------------------------------

        if node_type in (
            "Aggregate",
            "HashAggregate",
            "GroupAggregate",
        ):
            features["aggregate_nodes"].append({
                "node_type": node_type,
                "actual_rows": actual_rows,
                "plan_rows": plan_rows,
            })

        # --------------------------------------------------
        # Sort nodes
        # --------------------------------------------------

        if node_type == "Sort":
            features["sort_nodes"].append({
                "actual_rows": actual_rows,
                "plan_rows": plan_rows,
            })

        # --------------------------------------------------
        # Filters
        # --------------------------------------------------

        if filter_condition:
            features["has_filter"] = True

            features["filters"].append({
                "table": relation_name,
                "condition": filter_condition,
                "rows_removed": rows_removed,
            })

        # --------------------------------------------------
        # Index conditions
        # --------------------------------------------------

        if index_condition:
            features["has_index_condition"] = True

            features["index_conditions"].append({
                "table": relation_name,
                "condition": index_condition,
                "index_name": index_name,
            })

        # --------------------------------------------------
        # Existing indexes
        # --------------------------------------------------

        if index_name:
            if index_name not in features["index_names"]:
                features["index_names"].append(index_name)

        # --------------------------------------------------
        # Row statistics
        # --------------------------------------------------

        features["total_actual_rows"] += actual_rows
        features["total_plan_rows"] += plan_rows

        features["total_rows_removed_by_filter"] += rows_removed

        # --------------------------------------------------
        # Buffer statistics
        # --------------------------------------------------

        features["total_shared_hit_blocks"] += shared_hits
        features["total_shared_read_blocks"] += shared_reads

    return features


def print_features(features):
    """
    Print extracted features in a readable format.
    """

    print("\n" + "=" * 65)
    print("EXTRACTED PLAN FEATURES")
    print("=" * 65)

    print(f"Node count              : {features['node_count']}")

    print(f"Tables                  : {features['tables']}")

    print(f"Node types              : {features['node_types']}")

    print(f"Sequential scans        : {features['seq_scan_count']}")
    print(f"Index scans             : {features['index_scan_count']}")
    print(f"Bitmap scans            : {features['bitmap_scan_count']}")

    print(f"Hash joins              : {features['hash_join_count']}")
    print(f"Nested loops            : {features['nested_loop_count']}")
    print(f"Merge joins             : {features['merge_join_count']}")

    print(f"Has filter              : {features['has_filter']}")
    print(f"Has index condition     : {features['has_index_condition']}")
    print(f"Has join                : {features['has_join']}")

    print(f"Actual rows             : {features['total_actual_rows']}")
    print(f"Estimated rows          : {features['total_plan_rows']}")

    print(
        f"Rows removed by filter : "
        f"{features['total_rows_removed_by_filter']}"
    )

    print(
        f"Shared buffer hits     : "
        f"{features['total_shared_hit_blocks']}"
    )

    print(
        f"Shared buffer reads    : "
        f"{features['total_shared_read_blocks']}"
    )

    print("\nScan details:")

    for scan in features["scan_nodes"]:
        print(
            f"  {scan['node_type']} | "
            f"table={scan['table']} | "
            f"actual_rows={scan['actual_rows']} | "
            f"plan_rows={scan['plan_rows']}"
        )

        if scan["filter"]:
            print(f"      Filter: {scan['filter']}")

        if scan["index_condition"]:
            print(
                f"      Index condition: "
                f"{scan['index_condition']}"
            )

    print("\nFilters:")

    for item in features["filters"]:
        print(
            f"  {item['table']} | "
            f"{item['condition']} | "
            f"rows_removed={item['rows_removed']}"
        )

    print("\nIndex conditions:")

    for item in features["index_conditions"]:
        print(
            f"  {item['table']} | "
            f"{item['condition']} | "
            f"index={item['index_name']}"
        )

    print("=" * 65)
