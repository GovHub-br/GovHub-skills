"""Testes de dbt_lineage.py. Rode: python3 scripts/test_dbt_lineage.py (ou pytest)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dbt_lineage import load  # noqa: E402

FIX = os.path.join(HERE, "fixtures", "manifest.min.json")


def _names(out):
    return {g["name"]: [n["name"] for n in g["nodes"]] for g in out["groups"]}


def test_group_by_schema():
    assert _names(load(FIX, "schema")) == {
        "bacen": ["deflator"],
        "bronze": ["salic.projetos"],
        "cotas": ["cotas"],
        "silver": ["stg_projetos"],
    }


def test_group_by_layer():
    names = _names(load(FIX, "layer"))
    assert names["fonte"] == ["salic.projetos"]
    assert names["silver"] == ["stg_projetos"]
    assert names["gold"] == ["cotas"]
    assert names["bacen"] == ["deflator"]  # seed sem camada no path cai no schema


def test_edges_sorted_and_tests_ignored():
    out = load(FIX)
    assert out["edges"] == [
        ["model.minc.stg_projetos", "model.minc.cotas"],
        ["seed.minc.deflator", "model.minc.cotas"],
        ["source.minc.salic.projetos", "model.minc.stg_projetos"],
    ]
    kinds = {n["id"]: n["kind"] for g in out["groups"] for n in g["nodes"]}
    assert "test.minc.not_null_cotas" not in kinds
    assert kinds["seed.minc.deflator"] == "seed"
    assert kinds["source.minc.salic.projetos"] == "source"


def test_materialization_and_description():
    nodes = {n["id"]: n for g in load(FIX)["groups"] for n in g["nodes"]}
    assert nodes["model.minc.cotas"]["materialization"] == "table"
    assert nodes["model.minc.stg_projetos"]["materialization"] == "view"
    assert nodes["source.minc.salic.projetos"]["description"].startswith("Réplica")


def test_cli_missing_file_exit_2():
    r = subprocess.run([sys.executable, os.path.join(HERE, "dbt_lineage.py"), "/nao/existe.json"],
                       capture_output=True, text=True)
    assert r.returncode == 2
    assert "dbt parse" in r.stderr


def test_cli_bad_group_exit_1():
    r = subprocess.run([sys.executable, os.path.join(HERE, "dbt_lineage.py"), FIX, "--group", "x"],
                       capture_output=True, text=True)
    assert r.returncode == 1


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
