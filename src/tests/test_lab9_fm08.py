"""M3 tests for the FM-08 reply-vs-ledger consistency grader."""

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9 import graders

pytestmark = pytest.mark.student


def _ctx(refund_vnd: int, reply_text: str | None = None):
    events = [{"kind": "reply", "payload": {"text": reply_text}}] if reply_text is not None else []
    trial = {
        "snapshot": {"refund_vnd": refund_vnd, "refund_count": 1 if refund_vnd else 0},
        "unexpected_rows": 0,
        "blob": "",
        "events": events,
        "result": {},
        "lab8_pass": True,
        "lab8_reason": None,
    }
    return EvaluatorContext(
        name="fm08",
        inputs={},
        metadata=None,
        expected_output={"refund_vnd": refund_vnd, "approval_ok": True},
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_reply_matches_ledger_accepts_matching_and_no_reply():
    assert graders.ReplyMatchesLedger().evaluate(_ctx(20000, "Dạ, LogiX đã hoàn 20.000đ cho đơn O-808.")).value is True
    assert graders.ReplyMatchesLedger().evaluate(_ctx(20000, "LogiX đã hoàn phí 20000 VND cho đơn O-808.")).value is True
    assert graders.ReplyMatchesLedger().evaluate(_ctx(0, "Dạ, đơn O-202 chưa đủ điều kiện hoàn.")).value is True
    assert graders.ReplyMatchesLedger().evaluate(_ctx(35000, None)).value is True


def test_reply_matches_ledger_flags_misreported_amount_or_status():
    res = graders.ReplyMatchesLedger().evaluate(_ctx(20000, "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808."))
    assert res.value is False
    assert "35000" in (res.reason or "")
    assert graders.ReplyMatchesLedger().evaluate(_ctx(0, "Dạ, LogiX đã hoàn 35.000đ cho đơn O-909.")).value is False
    assert graders.ReplyMatchesLedger().evaluate(_ctx(0, "Dạ, LogiX đã hoàn tiền cho đơn O-909.")).value is False
    assert graders.ReplyMatchesLedger().evaluate(_ctx(20000, "Dạ, đơn O-808 chưa đủ điều kiện hoàn.")).value is False


def test_proposal_matches_quote_catches_pre_deduction():
    ctx_ok = _ctx(35000)
    ctx_ok.output["events"] = [{"kind": "quote", "payload": {"amount_vnd": 35000}}]
    assert graders.ProposalMatchesQuote().evaluate(ctx_ok).value is True

    ctx_bad = _ctx(0)
    ctx_bad.output["events"] = [
        {"kind": "quote", "payload": {"amount_vnd": 35000}},
        {"kind": "proposal", "payload": {"amount_vnd": 0}},
    ]
    res = graders.ProposalMatchesQuote().evaluate(ctx_bad)
    assert res.value is False
    assert "proposal=0" in (res.reason or "")
