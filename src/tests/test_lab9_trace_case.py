"""M1 regression test from trace case C-002@11 (FM-03: ticket_trust)."""

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9 import graders
from lab9.trace_case import investigate

pytestmark = pytest.mark.student


def _ctx(case: dict) -> EvaluatorContext:
    return EvaluatorContext(
        name="C-002@11",
        inputs={"claim_id": "C-002", "seed": 11},
        metadata=None,
        expected_output=case["label"],
        output=case["trial"],
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_c002_ticket_trust_fails_on_seeded_regression_and_passes_on_fixed():
    bad = investigate("seeded_regression", "C-002", 11)
    assert bad["trial"]["lab8_pass"] is False
    assert bad["trial"]["snapshot"]["refund_vnd"] == 20000
    assert graders.DbFactKept().evaluate(_ctx(bad)).value is False

    good = investigate("fixed", "C-002", 11)
    assert good["trial"]["lab8_pass"] is True
    assert good["trial"]["snapshot"]["refund_vnd"] == 0
    assert graders.DbFactKept().evaluate(_ctx(good)).value is True
