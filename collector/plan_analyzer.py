def analyze_plan(node, depth=0):
    """
    Recursively analyze a PostgreSQL execution-plan node.

    Parameters
    ----------
    node : dict
        PostgreSQL execution-plan node.

    depth : int
        Depth of the node in the execution-plan tree.

    Returns
    -------
    list
        Flattened list of execution-plan nodes.
    """

    results = []

    # ---------------------------------------------------------
    # Extract information from the current node
    # ---------------------------------------------------------

    node_info = {
        "depth": depth,

        "node_type": node.get(
            "Node Type"
        ),

        "relation_name": node.get(
            "Relation Name"
        ),

        "alias": node.get(
            "Alias"
        ),

        "index_name": node.get(
            "Index Name"
        ),

        "join_type": node.get(
            "Join Type"
        ),

        "actual_rows": node.get(
            "Actual Rows",
            0
        ),

        "actual_loops": node.get(
            "Actual Loops",
            0
        ),

        "startup_cost": node.get(
            "Startup Cost"
        ),

        "total_cost": node.get(
            "Total Cost"
        ),

        "plan_rows": node.get(
            "Plan Rows"
        ),

        "plan_width": node.get(
            "Plan Width"
        ),

        "rows_removed_by_filter": node.get(
            "Rows Removed by Filter",
            0
        ),

        "shared_hit_blocks": node.get(
            "Shared Hit Blocks",
            0
        ),

        "shared_read_blocks": node.get(
            "Shared Read Blocks",
            0
        ),

        "filter": node.get(
            "Filter"
        ),

        "index_condition": node.get(
            "Index Cond"
        ),

        "join_filter": node.get(
            "Join Filter"
        ),

        "hash_condition": node.get(
            "Hash Cond"
        )
    }

    # Add the current node
    results.append(node_info)

    # ---------------------------------------------------------
    # Recursively process child nodes
    # ---------------------------------------------------------

    child_nodes = node.get(
        "Plans",
        []
    )

    for child in child_nodes:

        results.extend(
            analyze_plan(
                child,
                depth + 1
            )
        )

    return results
