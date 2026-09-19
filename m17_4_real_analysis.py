from collector.cost_aware_recommendation_analyzer import (
    analyze_historical_recommendations,
    build_cost_aware_summary,
    print_cost_aware_analysis,
)

from m17_3_real_analysis import (
    build_real_m17_3_analysis,
)


def build_real_m17_4_analysis():
    """
    Build the M17.4 cost-aware recommendation analysis.

    Historical recommendation evidence is analyzed
    independently from the M17.1/M17.2 cost evidence
    unless an explicitly linked experimental index exists.
    """

    m17_3_analysis = (
        build_real_m17_3_analysis()
    )

    dataset = (
        m17_3_analysis[
            "recommendation_quality_analysis"
        ]
    )

    # The recommendation-quality analysis stores the
    # evaluated dataset under the existing pipeline.
    #
    # Recover the original dataset through the established
    # M17.3 loading path rather than reconstructing it.
    from m17_3_real_analysis import (
        load_real_read_benefit_dataset,
    )

    recommendation_dataset = (
        load_real_read_benefit_dataset()
    )

    records = analyze_historical_recommendations(
        recommendation_dataset
    )

    summary = build_cost_aware_summary(
        records
    )

    return {
        "m17_3_analysis": m17_3_analysis,
        "records": records,
        "summary": summary,
    }


def main():
    analysis = build_real_m17_4_analysis()

    print_cost_aware_analysis(
        analysis["records"],
        analysis["summary"],
    )


if __name__ == "__main__":
    main()
