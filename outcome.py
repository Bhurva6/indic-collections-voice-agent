"""Offline prototype. See README.md for scope and limitations."""
import json
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Optional


class Disposition(Enum):
    PROMISE_TO_PAY = "promise_to_pay"
    PARTIAL_PROMISE = "partial_promise"
    CALLBACK_REQUESTED = "callback_requested"
    HARDSHIP_RESTRUCTURE = "hardship_restructure"
    DISPUTED = "disputed"
    DO_NOT_CALL = "do_not_call"
    WRONG_PARTY = "wrong_party"
    ESCALATED_HUMAN = "escalated_human"
    NO_COMMITMENT = "no_commitment"


@dataclass
class CallOutcome:
    disposition: str
    promised_amount: Optional[int] = None
    promised_date: Optional[str] = None
    language: str = "hinglish"
    escalated: bool = False
    escalation_reason: Optional[str] = None
    notes: list = field(default_factory=list)
    turns: int = 0

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)
