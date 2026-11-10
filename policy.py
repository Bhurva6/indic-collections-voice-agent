"""Offline prototype. See README.md for scope and limitations."""
from dataclasses import dataclass, field
from enum import Enum


class State(Enum):
    OPEN_DISCLOSURE = "open_disclosure"      # who we are, lender, recording notice
    VERIFY_IDENTITY = "verify_identity"      # confirm we're speaking to the borrower
    STATE_PURPOSE = "state_purpose"          # pending EMI, amount, due date
    NEGOTIATE = "negotiate"                  # hear the borrower, offer options
    CAPTURE_PROMISE = "capture_promise"      # amount + date of promise-to-pay
    RECAP_CLOSE = "recap_close"              # repeat commitment, SMS link, close
    ESCALATE_HUMAN = "escalate_human"        # hand off to a human officer
    ENDED = "ended"


ALLOWED_TRANSITIONS = {
    State.OPEN_DISCLOSURE: {State.VERIFY_IDENTITY, State.ENDED},
    State.VERIFY_IDENTITY: {State.STATE_PURPOSE, State.ENDED},
    State.STATE_PURPOSE: {State.NEGOTIATE, State.ESCALATE_HUMAN, State.ENDED},
    State.NEGOTIATE: {State.CAPTURE_PROMISE, State.ESCALATE_HUMAN,
                      State.RECAP_CLOSE, State.ENDED},
    State.CAPTURE_PROMISE: {State.RECAP_CLOSE, State.NEGOTIATE},
    State.RECAP_CLOSE: {State.ENDED},
    State.ESCALATE_HUMAN: {State.ENDED},
    State.ENDED: set(),
}


@dataclass
class CallContext:
    borrower_name: str
    lender_name: str
    agent_desk_name: str
    emi_amount: int
    currency: str = "INR"
    due_date: str = ""
    language: str = "hinglish"  # hi | en | hinglish
    state: State = State.OPEN_DISCLOSURE
    transitions: list = field(default_factory=list)

    def move(self, to: State, why: str) -> bool:
        if to not in ALLOWED_TRANSITIONS[self.state]:
            return False
        self.transitions.append({"from": self.state.value, "to": to.value, "why": why})
        self.state = to
        return True
