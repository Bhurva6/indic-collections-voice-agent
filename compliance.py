"""Offline prototype. See README.md for scope and limitations."""
from dataclasses import dataclass
from datetime import time
from typing import Optional

CALL_WINDOW_START = time(8, 0)   # RBI: contact borrowers only 08:00-19:00
CALL_WINDOW_END = time(19, 0)

BANNED_PATTERNS = [
    "threaten", "dhamki", "jail", "arrest karwa", "police bulaa",
    "sharam", "insult", "gaali",
]

ESCALATION_TRIGGERS = [
    "lawyer", "vakil", "complaint", "ombudsman", "fraud", "galti hai",
    "not my loan", "mera loan nahi", "harass", "tang mat karo",
]

HARDSHIP_SIGNALS = [
    "job chali gayi", "naukri chali gayi", "lost my job", "naukri nahi", "hospital",
    "bemari", "medical", "death", "accident",
]


@dataclass
class GuardrailResult:
    allowed: bool
    reason: Optional[str] = None
    action: str = "proceed"  # proceed | block | escalate | end_call


def within_call_window(now_local: time) -> bool:
    return CALL_WINDOW_START <= now_local < CALL_WINDOW_END


def check_agent_reply(text: str) -> GuardrailResult:
    low = text.lower()
    for pat in BANNED_PATTERNS:
        if pat in low:
            return GuardrailResult(False, f"banned pattern: {pat}", "block")
    return GuardrailResult(True)


def check_borrower_turn(text: str) -> GuardrailResult:
    low = text.lower()
    if any(t in low for t in ("do not call", "mat call karo", "dnc")):
        return GuardrailResult(True, "contact preference needs human review", "end_call")
    for trig in ESCALATION_TRIGGERS:
        if trig in low:
            return GuardrailResult(True, f"escalation trigger: {trig}", "escalate")
    for sig in HARDSHIP_SIGNALS:
        if sig in low:
            return GuardrailResult(True, f"hardship signal: {sig}", "proceed")
    if "do not call" in low or "mat call karo" in low or "dnc" in low:
        return GuardrailResult(True, "borrower asked not to be called", "end_call")
    return GuardrailResult(True)
