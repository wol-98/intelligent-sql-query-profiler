from collector.cross_workload_experiment import (
    build_m18_4_experiment_set,
)


def test_m18_4_experiment_set_has_three_experiments():
    experiments = build_m18_4_experiment_set()

    assert len(experiments) == 3


def test_m18_4_experiment_ids_are_unique():
    experiments = build_m18_4_experiment_set()

    ids = [experiment["experiment_id"] for experiment in experiments]

    assert len(ids) == len(set(ids))


def test_m18_4_experiment_index_names_are_unique():
    experiments = build_m18_4_experiment_set()

    names = [experiment["index_name"] for experiment in experiments]

    assert len(names) == len(set(names))


def test_m18_4_experiments_have_read_table_placeholder():
    experiments = build_m18_4_experiment_set()

    for experiment in experiments:
        assert "{table}" in experiment["read_query"]


def test_m18_4_experiments_have_valid_measurement_settings():
    experiments = build_m18_4_experiment_set()

    for experiment in experiments:
        assert experiment["read_iterations"] >= 1
        assert experiment["write_iterations"] >= 1
        assert experiment["read_warmup_runs"] >= 0
        assert experiment["write_warmup_runs"] >= 0


def test_m18_4_experiments_have_notes():
    experiments = build_m18_4_experiment_set()

    for experiment in experiments:
        assert experiment["notes"]
