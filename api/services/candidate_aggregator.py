"""
Candidate Aggregator  (M21.13)
--------------------------------
Merges recommendations from three separate recommenders into a single, 
deduplicated, priority-sorted candidate list.
"""

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

def _index_is_covered_by_view(index_rec: dict, view_recs: list) -> bool:
    index_table = index_rec.get("table_name", "").lower()
    for view_rec in view_recs:
        if view_rec.get("type") != "materialized_view":
            continue
        if index_table and index_table in view_rec.get("sql", "").lower():
            return True
    return False

def aggregate_candidates(index_recommendations: list, view_recommendations: list, function_recommendations: list) -> list:
    combined = []

    for rec in index_recommendations:
        entry = dict(rec)
        entry["source"] = "index_recommender"
        entry.setdefault("flags", [])
        if _index_is_covered_by_view(rec, view_recommendations):
            entry["flags"].append(
                "possibly redundant — a materialized view recommendation "
                "already covers this table; review before applying both"
            )
        combined.append(entry)

    for rec in view_recommendations:
        entry = dict(rec)
        entry["source"] = "view_recommender"
        entry.setdefault("flags", [])
        combined.append(entry)

    for rec in function_recommendations:
        entry = dict(rec)
        entry["source"] = "function_recommender"
        entry.setdefault("flags", [])
        combined.append(entry)

    combined.sort(key=lambda r: _PRIORITY_ORDER.get(r.get("priority", "low"), 3))
    return combined

def summarize_candidates(combined_candidates: list) -> dict:
    summary = {"total": len(combined_candidates), "by_type": {}, "flagged": 0}
    for rec in combined_candidates:
        rec_type = rec.get("type", "unknown")
        summary["by_type"][rec_type] = summary["by_type"].get(rec_type, 0) + 1
        if rec.get("flags"):
            summary["flagged"] += 1
    return summary
