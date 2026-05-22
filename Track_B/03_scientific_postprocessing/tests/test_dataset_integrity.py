"""Basic structural-integrity checks for the shipped datasets.

These confirm both the reference and challenge datasets are well-formed enough to start
analysing. They check structure only; deeper data-quality checks are something you build
in Task 4.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATASETS = ["reference", "challenge"]

RAW_RUNS_COLUMNS = {
    "run_id",
    "solver",
    "dt",
    "n_steps",
    "mass",
    "spring_constant",
    "x0",
    "v0",
    "n_periods",
    "final_position_error",
    "max_energy_error",
    "period_error",
    "runtime_proxy",
    "status",
}

TRAJECTORY_COLUMNS = {
    "run_id",
    "time",
    "x_numeric",
    "v_numeric",
    "x_reference",
    "energy",
}

RAW_NUMERIC_COLUMNS = [
    "dt",
    "n_steps",
    "mass",
    "spring_constant",
    "x0",
    "v0",
    "n_periods",
    "final_position_error",
    "max_energy_error",
    "period_error",
    "runtime_proxy",
]


@pytest.fixture(params=DATASETS)
def dataset_dir(request):
    return DATA_DIR / request.param


@pytest.fixture
def raw_runs(dataset_dir):
    return pd.read_csv(dataset_dir / "raw_runs.csv")


@pytest.fixture
def trajectories(dataset_dir):
    return pd.read_csv(dataset_dir / "trajectories_sample.csv")


@pytest.fixture
def metadata(dataset_dir):
    with open(dataset_dir / "metadata.json", encoding="utf-8") as fh:
        return json.load(fh)


def test_required_files_exist(dataset_dir):
    for name in ("raw_runs.csv", "trajectories_sample.csv", "metadata.json"):
        assert (dataset_dir / name).is_file(), f"missing data file: {dataset_dir.name}/{name}"


def test_raw_runs_has_required_columns(raw_runs):
    assert RAW_RUNS_COLUMNS.issubset(raw_runs.columns)


def test_trajectories_have_required_columns(trajectories):
    assert TRAJECTORY_COLUMNS.issubset(trajectories.columns)


def test_run_id_present_and_non_null(raw_runs):
    assert raw_runs["run_id"].notna().all()
    assert (raw_runs["run_id"].astype(str).str.len() > 0).all()


def test_raw_numeric_columns_are_finite(raw_runs):
    for col in RAW_NUMERIC_COLUMNS:
        values = pd.to_numeric(raw_runs[col], errors="coerce")
        assert np.isfinite(values).all(), f"non-finite values in column: {col}"


def test_trajectory_numeric_columns_are_finite(trajectories):
    for col in ("time", "x_numeric", "v_numeric", "x_reference", "energy"):
        values = pd.to_numeric(trajectories[col], errors="coerce")
        assert np.isfinite(values).all(), f"non-finite values in column: {col}"


def test_trajectory_run_ids_exist_in_raw_runs(raw_runs, trajectories):
    known = set(raw_runs["run_id"])
    assert set(trajectories["run_id"]).issubset(known)


def test_metadata_describes_columns(metadata):
    files = metadata.get("files", {})
    raw_columns = files.get("raw_runs.csv", {}).get("columns", {})
    traj_columns = files.get("trajectories_sample.csv", {}).get("columns", {})
    assert RAW_RUNS_COLUMNS.issubset(raw_columns)
    assert TRAJECTORY_COLUMNS.issubset(traj_columns)


def test_analysis_dependencies_importable():
    import matplotlib  # noqa: F401
    import numpy  # noqa: F401
    import pandas  # noqa: F401
