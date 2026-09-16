"""
Validation Analysis & Evaluation Metrics
----------------------------------------
Analyzes completed benchmark validation results.

This module does NOT:
- execute benchmark queries
- create indexes
- modify database indexes

It only reads validation results already stored in
benchmark_results and calculates project-level metrics.

M11 includes:
1. Overall validation metrics
2. Performance metrics by validation status
3. Recommendation quality metrics
4. Detailed recommendation evaluation
5. Query-level validation analysis
"""

from config.database import get_connection


def get_validation_records():
    """
    Retrieve all completed validation records.

    Returns:
        list: Benchmark and recommendation records.
    """

    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                br.benchmark_id,
                br.recommendation_id,
                ir.query_profile_id,
                ir.table_name,
                ir.column_name,
                ir.recommendation_score,
                ir.priority,
                br.improvement_percentage,
                br.rows_before,
                br.rows_after,
                br.rows_preserved,
                br.index_used,
                br.index_node_type,
                br.plan_changed,
                br.validation_status
            FROM benchmark_results br
            JOIN index_recommendations ir
                ON br.recommendation_id = ir.recommendation_id
            ORDER BY br.benchmark_id;
        """)

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()


def calculate_overall_metrics(records):
    """
    Calculate overall validation metrics.
    """

    total = len(records)

    if total == 0:
        return {
            "total_experiments": 0,
            "successful": 0,
            "neutral": 0,
            "unsuccessful": 0,
            "unsafe": 0,
            "success_rate": 0.0,
            "index_usage_rate": 0.0,
            "rows_preserved_rate": 0.0,
            "plan_change_rate": 0.0,
            "average_improvement": 0.0,
        }

    successful = sum(
        1
        for r in records
        if r[14] == "SUCCESSFUL"
    )

    neutral = sum(
        1
        for r in records
        if r[14] == "NEUTRAL"
    )

    unsuccessful = sum(
        1
        for r in records
        if r[14] == "UNSUCCESSFUL"
    )

    unsafe = sum(
        1
        for r in records
        if r[14] == "UNSAFE"
    )

    index_used = sum(
        1
        for r in records
        if r[11] is True
    )

    rows_preserved = sum(
        1
        for r in records
        if r[10] is True
    )

    plan_changed = sum(
        1
        for r in records
        if r[13] is True
    )

    improvements = [
        r[7]
        for r in records
        if r[7] is not None
    ]

    average_improvement = (
        sum(improvements) / len(improvements)
        if improvements
        else 0.0
    )

    return {
        "total_experiments": total,
        "successful": successful,
        "neutral": neutral,
        "unsuccessful": unsuccessful,
        "unsafe": unsafe,
        "success_rate": successful / total * 100,
        "index_usage_rate": index_used / total * 100,
        "rows_preserved_rate": rows_preserved / total * 100,
        "plan_change_rate": plan_changed / total * 100,
        "average_improvement": average_improvement,
    }


def print_overall_metrics(metrics):
    """
    Display overall validation metrics.
    """

    print("\n" + "=" * 90)
    print("M11 — VALIDATION ANALYSIS & EVALUATION METRICS")
    print("=" * 90)

    print(
        f"Total experiments       : "
        f"{metrics['total_experiments']}"
    )

    print(
        f"Successful              : "
        f"{metrics['successful']}"
    )

    print(
        f"Neutral                 : "
        f"{metrics['neutral']}"
    )

    print(
        f"Unsuccessful            : "
        f"{metrics['unsuccessful']}"
    )

    print(
        f"Unsafe                  : "
        f"{metrics['unsafe']}"
    )

    print("-" * 90)

    print(
        f"Success rate            : "
        f"{metrics['success_rate']:.2f}%"
    )

    print(
        f"Index usage rate        : "
        f"{metrics['index_usage_rate']:.2f}%"
    )

    print(
        f"Rows preserved rate     : "
        f"{metrics['rows_preserved_rate']:.2f}%"
    )

    print(
        f"Plan change rate        : "
        f"{metrics['plan_change_rate']:.2f}%"
    )

    print(
        f"Average improvement     : "
        f"{metrics['average_improvement']:.2f}%"
    )

    print("=" * 90)


def calculate_status_metrics(records):
    """
    Calculate performance metrics separately for each
    validation status.
    """

    statuses = [
        "SUCCESSFUL",
        "NEUTRAL",
        "UNSUCCESSFUL",
        "UNSAFE",
    ]

    results = {}

    for status in statuses:

        status_records = [
            r
            for r in records
            if r[14] == status
        ]

        improvements = [
            r[7]
            for r in status_records
            if r[7] is not None
        ]

        if improvements:

            average_improvement = (
                sum(improvements) / len(improvements)
            )

            maximum_improvement = max(
                improvements
            )

            minimum_improvement = min(
                improvements
            )

        else:

            average_improvement = 0.0
            maximum_improvement = 0.0
            minimum_improvement = 0.0

        results[status] = {
            "count": len(status_records),
            "average_improvement":
                average_improvement,
            "maximum_improvement":
                maximum_improvement,
            "minimum_improvement":
                minimum_improvement,
        }

    return results


def print_status_metrics(status_metrics):
    """
    Display performance metrics by validation status.
    """

    print("\n" + "=" * 90)
    print("PERFORMANCE METRICS BY VALIDATION STATUS")
    print("=" * 90)

    print(
        f"{'Status':<18}"
        f"{'Count':>8}"
        f"{'Avg Improvement':>20}"
        f"{'Max Improvement':>20}"
        f"{'Min Improvement':>20}"
    )

    print("-" * 90)

    for status, metrics in status_metrics.items():

        print(
            f"{status:<18}"
            f"{metrics['count']:>8}"
            f"{metrics['average_improvement']:>19.2f}%"
            f"{metrics['maximum_improvement']:>19.2f}%"
            f"{metrics['minimum_improvement']:>19.2f}%"
        )

    print("=" * 90)


def calculate_recommendation_quality(records):
    """
    Analyze the relationship between recommendation scores
    and experimentally validated outcomes.
    """

    if not records:
        return {
            "average_score": 0.0,
            "successful_average_score": 0.0,
            "neutral_average_score": 0.0,
            "unsuccessful_average_score": 0.0,
            "high_priority_count": 0,
            "high_priority_successful": 0,
            "high_priority_success_rate": 0.0,
        }

    scores = [
        r[5]
        for r in records
        if r[5] is not None
    ]

    successful_scores = [
        r[5]
        for r in records
        if r[14] == "SUCCESSFUL"
        and r[5] is not None
    ]

    neutral_scores = [
        r[5]
        for r in records
        if r[14] == "NEUTRAL"
        and r[5] is not None
    ]

    unsuccessful_scores = [
        r[5]
        for r in records
        if r[14] == "UNSUCCESSFUL"
        and r[5] is not None
    ]

    high_priority_records = [
        r
        for r in records
        if r[6] == "High"
    ]

    high_priority_successful = [
        r
        for r in high_priority_records
        if r[14] == "SUCCESSFUL"
    ]

    average_score = (
        sum(scores) / len(scores)
        if scores
        else 0.0
    )

    successful_average_score = (
        sum(successful_scores)
        / len(successful_scores)
        if successful_scores
        else 0.0
    )

    neutral_average_score = (
        sum(neutral_scores)
        / len(neutral_scores)
        if neutral_scores
        else 0.0
    )

    unsuccessful_average_score = (
        sum(unsuccessful_scores)
        / len(unsuccessful_scores)
        if unsuccessful_scores
        else 0.0
    )

    high_priority_count = len(
        high_priority_records
    )

    high_priority_successful_count = len(
        high_priority_successful
    )

    high_priority_success_rate = (
        high_priority_successful_count
        / high_priority_count
        * 100
        if high_priority_count
        else 0.0
    )

    return {
        "average_score": average_score,
        "successful_average_score":
            successful_average_score,
        "neutral_average_score":
            neutral_average_score,
        "unsuccessful_average_score":
            unsuccessful_average_score,
        "high_priority_count":
            high_priority_count,
        "high_priority_successful":
            high_priority_successful_count,
        "high_priority_success_rate":
            high_priority_success_rate,
    }


def print_recommendation_quality(metrics):
    """
    Display recommendation quality metrics.
    """

    print("\n" + "=" * 90)
    print("RECOMMENDATION QUALITY METRICS")
    print("=" * 90)

    print(
        f"Average recommendation score       : "
        f"{metrics['average_score']:.2f}"
    )

    print(
        f"Successful average score           : "
        f"{metrics['successful_average_score']:.2f}"
    )

    print(
        f"Neutral average score              : "
        f"{metrics['neutral_average_score']:.2f}"
    )

    print(
        f"Unsuccessful average score         : "
        f"{metrics['unsuccessful_average_score']:.2f}"
    )

    print("-" * 90)

    print(
        f"High-priority recommendations      : "
        f"{metrics['high_priority_count']}"
    )

    print(
        f"High-priority successful           : "
        f"{metrics['high_priority_successful']}"
    )

    print(
        f"High-priority success rate         : "
        f"{metrics['high_priority_success_rate']:.2f}%"
    )

    print("=" * 90)


def print_recommendation_evaluation(records):
    """
    Display detailed evaluation results for every
    validated recommendation.
    """

    print("\n" + "=" * 150)
    print("DETAILED RECOMMENDATION EVALUATION")
    print("=" * 150)

    print(
        f"{'Bench':<7}"
        f"{'Profile':<9}"
        f"{'Table':<18}"
        f"{'Column':<20}"
        f"{'Score':>8}"
        f"{'Priority':<12}"
        f"{'Improvement':>15}"
        f"{'Index Used':>12}"
        f"{'Plan Changed':>14}"
        f"{'Status':<15}"
    )

    print("-" * 150)

    for r in records:

        benchmark_id = r[0]
        query_profile_id = r[2]
        table_name = r[3]
        column_name = r[4]
        score = r[5]
        priority = r[6]
        improvement = r[7]
        index_used = r[11]
        plan_changed = r[13]
        status = r[14]

        score_text = (
            f"{score:.2f}"
            if score is not None
            else "N/A"
        )

        improvement_text = (
            f"{improvement:.2f}%"
            if improvement is not None
            else "N/A"
        )

        print(
            f"{benchmark_id:<7}"
            f"{query_profile_id:<9}"
            f"{table_name:<18}"
            f"{column_name:<20}"
            f"{score_text:>8}"
            f"{str(priority):<12}"
            f"{improvement_text:>15}"
            f"{str(index_used):>12}"
            f"{str(plan_changed):>14}"
            f"{str(status):<15}"
        )

    print("=" * 150)


def calculate_query_metrics(records):
    """
    Calculate validation metrics grouped by query profile.
    """

    query_groups = {}

    for r in records:

        query_profile_id = r[2]
        improvement = r[7]
        status = r[14]

        if query_profile_id not in query_groups:
            query_groups[query_profile_id] = {
                "recommendations": 0,
                "successful": 0,
                "neutral": 0,
                "unsuccessful": 0,
                "unsafe": 0,
                "improvements": [],
            }

        group = query_groups[query_profile_id]

        group["recommendations"] += 1

        if status == "SUCCESSFUL":

            group["successful"] += 1

        elif status == "NEUTRAL":

            group["neutral"] += 1

        elif status == "UNSUCCESSFUL":

            group["unsuccessful"] += 1

        elif status == "UNSAFE":

            group["unsafe"] += 1

        if improvement is not None:

            group["improvements"].append(
                improvement
            )

    results = []

    for query_profile_id, group in sorted(
        query_groups.items()
    ):

        improvements = group["improvements"]

        if improvements:

            average_improvement = (
                sum(improvements)
                / len(improvements)
            )

            best_improvement = max(
                improvements
            )

        else:

            average_improvement = 0.0
            best_improvement = 0.0

        results.append({
            "query_profile_id":
                query_profile_id,
            "recommendations":
                group["recommendations"],
            "successful":
                group["successful"],
            "neutral":
                group["neutral"],
            "unsuccessful":
                group["unsuccessful"],
            "unsafe":
                group["unsafe"],
            "average_improvement":
                average_improvement,
            "best_improvement":
                best_improvement,
        })

    return results


def print_query_metrics(query_metrics):
    """
    Display validation metrics grouped by query.
    """

    print("\n" + "=" * 120)
    print("QUERY-LEVEL VALIDATION ANALYSIS")
    print("=" * 120)

    print(
        f"{'Profile':<10}"
        f"{'Recommendations':>17}"
        f"{'Successful':>13}"
        f"{'Neutral':>10}"
        f"{'Unsuccessful':>15}"
        f"{'Unsafe':>9}"
        f"{'Avg Improvement':>18}"
        f"{'Best Improvement':>18}"
    )

    print("-" * 120)

    for result in query_metrics:

        print(
            f"{result['query_profile_id']:<10}"
            f"{result['recommendations']:>17}"
            f"{result['successful']:>13}"
            f"{result['neutral']:>10}"
            f"{result['unsuccessful']:>15}"
            f"{result['unsafe']:>9}"
            f"{result['average_improvement']:>17.2f}%"
            f"{result['best_improvement']:>17.2f}%"
        )

    print("=" * 120)
def calculate_coverage_metrics(records):
    """
    Calculate recommendation coverage and low-benefit metrics.

    Coverage is calculated against the distinct recommendations
    represented in the validation records.
    """

    validated_recommendations = {
        r[1]
        for r in records
        if r[1] is not None
    }

    positive_benefit = [
        r
        for r in records
        if r[7] is not None
        and r[7] > 0
    ]

    low_benefit = [
        r
        for r in records
        if r[7] is not None
        and r[7] < 5
    ]

    index_used_low_benefit = [
        r
        for r in low_benefit
        if r[11] is True
    ]

    index_not_used = [
        r
        for r in records
        if r[11] is False
    ]

    total = len(records)

    return {
        "validated_recommendations":
            len(validated_recommendations),

        "positive_benefit_count":
            len(positive_benefit),

        "low_benefit_count":
            len(low_benefit),

        "index_used_low_benefit_count":
            len(index_used_low_benefit),

        "index_not_used_count":
            len(index_not_used),

        "positive_benefit_rate":
            (
                len(positive_benefit)
                / total
                * 100
                if total
                else 0.0
            ),

        "low_benefit_rate":
            (
                len(low_benefit)
                / total
                * 100
                if total
                else 0.0
            ),

        "index_not_used_rate":
            (
                len(index_not_used)
                / total
                * 100
                if total
                else 0.0
            ),
    }


def print_coverage_metrics(metrics):
    """
    Display recommendation coverage and low-benefit metrics.
    """

    print("\n" + "=" * 90)
    print("RECOMMENDATION COVERAGE & LOW-BENEFIT ANALYSIS")
    print("=" * 90)

    print(
        f"Validated recommendations       : "
        f"{metrics['validated_recommendations']}"
    )

    print(
        f"Positive-benefit recommendations: "
        f"{metrics['positive_benefit_count']}"
    )

    print(
        f"Low-benefit recommendations     : "
        f"{metrics['low_benefit_count']}"
    )

    print(
        f"Index-used low-benefit cases     : "
        f"{metrics['index_used_low_benefit_count']}"
    )

    print(
        f"Index-not-used cases             : "
        f"{metrics['index_not_used_count']}"
    )

    print("-" * 90)

    print(
        f"Positive-benefit rate            : "
        f"{metrics['positive_benefit_rate']:.2f}%"
    )

    print(
        f"Low-benefit rate                 : "
        f"{metrics['low_benefit_rate']:.2f}%"
    )

    print(
        f"Index-not-used rate              : "
        f"{metrics['index_not_used_rate']:.2f}%"
    )

    print("=" * 90)

def main():
    """
    Run complete M11 validation analysis.
    """

    records = get_validation_records()

    print(
        f"\nValidation records found: "
        f"{len(records)}"
    )

    # --------------------------------------------------
    # 1. Overall validation metrics
    # --------------------------------------------------

    overall_metrics = calculate_overall_metrics(
        records
    )

    print_overall_metrics(
        overall_metrics
    )

    # --------------------------------------------------
    # 2. Performance metrics by validation status
    # --------------------------------------------------

    status_metrics = calculate_status_metrics(
        records
    )

    print_status_metrics(
        status_metrics
    )

    # --------------------------------------------------
    # 3. Recommendation quality metrics
    # --------------------------------------------------

    recommendation_metrics = (
        calculate_recommendation_quality(
            records
        )
    )

    print_recommendation_quality(
        recommendation_metrics
    )

    # --------------------------------------------------
    # 4. Detailed recommendation evaluation
    # --------------------------------------------------

    print_recommendation_evaluation(
        records
    )

    # --------------------------------------------------
    # 5. Query-level validation analysis
    # --------------------------------------------------

    query_metrics = calculate_query_metrics(
        records
    )

    print_query_metrics(
        query_metrics
    )

    # --------------------------------------------------
    # 6. Recommendation coverage & low-benefit analysis
    # --------------------------------------------------

    coverage_metrics = calculate_coverage_metrics(
        records
    )

    print_coverage_metrics(
        coverage_metrics
    )


if __name__ == "__main__":
    main()
