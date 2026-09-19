from collector.m18_4_cross_workload import (
    build_m18_4_experiments,
)


def test_m18_4_uses_three_fresh_experiments():
    experiments = build_m18_4_experiments()

    assert len(experiments) == 3

    ids = [
        experiment["experiment_id"]
        for experiment in experiments
    ]

    assert ids == [
        "M18_004",
        "M18_005",
        "M18_006",
    ]


def test_m18_4_does_not_reuse_m18_001():
    experiments = build_m18_4_experiments()

    ids = {
        experiment["experiment_id"]
        for experiment in experiments
    }

    assert "M18_001" not in ids


def test_m18_4_index_names_are_fresh():
    experiments = build_m18_4_experiments()

    names = [
        experiment["index_name"]
        for experiment in experiments
    ]

    assert len(names) == len(set(names))

    for name in names:
        assert name.startswith("m18_00")


def test_m18_4_experiments_have_required_fields():
    experiments = build_m18_4_experiments()

    for experiment in experiments:
        assert experiment["experiment_id"]
        assert experiment["index_name"]
        assert experiment["table_name"]
        assert experiment["columns"]
        assert experiment["read_query"]


def test_m18_4_read_queries_use_table_placeholder():
    experiments = build_m18_4_experiments()

    for experiment in experiments:
        assert "{table}" in experiment["read_query"]
