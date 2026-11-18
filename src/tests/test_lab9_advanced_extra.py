"""Extra M5-M7 checks for hidden traps (duplicate rows, evaluator_failures, relabeled slices, metric tampering)."""

import copy

import pytest

from lab9 import gate, stats

pytestmark = pytest.mark.student

ROWS = [
    {"item_id": f"E-{i:03d}", "seed": s, "pass_rate": True, "slices": ["money_movement"] if i < 2 else ["denial"]}
    for i in range(4)
    for s in (1, 2)
]
SPEC = {
    "eval_set_version": "v2",
    "eval_set": "data/eval/eval_set_v2.jsonl",
    "metrics": [{"id": "pass_rate", "kind": "capability", "blocking": True, "threshold": {"min": 0.85, "no_significant_drop": True}}],
    "slices": [{"name": "money_movement", "metric": "pass_rate", "min": 0.9, "no_significant_drop": True, "blocking": True}],
}


def _rep(rows, pass_rate=1.0, failures=()):
    return {
        "manifest": {"eval_set_sha": "aaa", "items": 4, "seeds": [1, 2]},
        "rows": rows,
        "metrics": {"pass_rate": pass_rate},
        "evaluator_failures": list(failures),
    }


def test_advanced_integrity_catches_duplicate_rows_and_green_evaluator_failures():
    base = _rep(copy.deepcopy(ROWS))
    assert gate.integrity_check(base, base, SPEC) == []

    dup_rows = copy.deepcopy(ROWS[:-1]) + [copy.deepcopy(ROWS[0])]
    assert gate.integrity_check(_rep(dup_rows), base, SPEC)

    green_but_crashed = _rep(copy.deepcopy(ROWS), failures=["E-001@1:Grader:RuntimeError"])
    assert gate.integrity_check(green_but_crashed, base, SPEC)


def test_advanced_integrity_catches_relabeled_slices_and_tampered_metrics():
    base = _rep(copy.deepcopy(ROWS))
    relabeled = copy.deepcopy(ROWS)
    relabeled[0]["slices"] = ["denial"]
    assert gate.integrity_check(_rep(relabeled), base, SPEC)

    tampered_rows = copy.deepcopy(ROWS)
    tampered_rows[0]["pass_rate"] = False
    assert gate.integrity_check(_rep(tampered_rows, pass_rate=1.0), base, SPEC)


def test_advanced_ratchet_catches_slice_and_blocking_weakening():
    base = _rep(copy.deepcopy(ROWS))
    loose_slice = copy.deepcopy(SPEC)
    loose_slice["slices"][0].pop("no_significant_drop")
    assert gate.integrity_check(base, base, loose_slice, SPEC)

    non_blocking = copy.deepcopy(SPEC)
    non_blocking["metrics"][0]["blocking"] = False
    assert gate.integrity_check(base, base, non_blocking, SPEC)


def test_advanced_pass_k_rejects_negative_and_bool_args():
    for args in [(0, 0, 1), (5, -1, 1), (5, 1, -1), (True, 1, 1)]:
        with pytest.raises(ValueError):
            stats.pass_at_k(*args)
        with pytest.raises(ValueError):
            stats.pass_hat_k(*args)
