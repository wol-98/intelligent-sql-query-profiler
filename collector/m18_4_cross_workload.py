import json

from collector.cross_workload_experiment import (
    build_m18_4_experiment_set,
)
from collector.cross_workload_cost_benefit_analyzer import (
    build_cross_workload_summary,
)
from collector.linked_cost_benefit_benchmark import (
    run_linked_cost_benefit_experiment,
)
from collector.linked_cost_benefit_analyzer import (
    build_linked_cost_benefit_analysis,
)


def build_m18_4_experiments():
    """Build fresh M18.4 experiment definitions.

    The completed M18.2 experiment M18_001 is intentionally
    not reused. M18.4 receives its own experiment identifiers.
    """

    experiments = build_m18_4_experiment_set()

    id_mapping = {
        "M18_001": "M18_004",
        "M18_002": "M18_005",
        "M18_003": "M18_006",
    }

    for experiment in experiments:
        old_id = experiment["experiment_id"]
        new_id = id_mapping[old_id]

        experiment["experiment_id"] = new_id

        experiment["index_name"] = (
            experiment["index_name"].replace(
                old_id.lower(),
                new_id.lower(),
            )
        )

    return experiments


def run_m18_4_experiment(experiment):
    """Run and analyze one M18.4 linked experiment."""

    result = run_linked_cost_benefit_experiment(
        experiment,
        source_table=experiment["table_name"],
        write_batch_size=1000,
    )

    analysis = build_linked_cost_benefit_analysis(result)

    return {
        "experiment": experiment,
        "result": result,
        "analysis": analysis,
    }


def main():
    experiments = build_m18_4_experiments()

    print("\n" + "=" * 70)
    print("M18.4 CROSS-WORKLOAD COST-BENEFIT EVALUATION")
    print("=" * 70)

    print(f"\nExperiments scheduled: {len(experiments)}")

    analyzed_results = []

    for experiment in experiments:
        print("\n" + "-" * 70)
        print(
            f"Running {experiment['experiment_id']}: "
            f"{experiment['notes']}"
        )
        print("-" * 70)

        combined = run_m18_4_experiment(experiment)

        analyzed_results.append(combined["analysis"])

        print(
            f"Completed {experiment['experiment_id']} "
            f"({experiment['index_name']})"
        )

    summary = build_cross_workload_summary(
        analyzed_results
    )

    output = {
        "experiment_count": len(experiments),
        "experiments": analyzed_results,
        "cross_workload_summary": summary,
    }

    print("\n" + "=" * 70)
    print("M18.4 CROSS-WORKLOAD RESULTS")
    print("=" * 70)

    print(
        json.dumps(
            output,
            indent=2,
            default=str,
        )
    )

    print("\n" + "=" * 70)
    print("M18.4 evaluation completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()
