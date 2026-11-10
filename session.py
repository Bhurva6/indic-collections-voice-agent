"""Offline prototype. See README.md for scope and limitations."""
import re
from datetime import time as dtime
import compliance, languages
from outcome import CallOutcome, Disposition
from policy import CallContext, State
from providers import LLMProvider

SYSTEM_PROMPT = (
    "You are a polite loan-collections voice agent for an Indian NBFC. "
    "Speak short Hinglish/Hindi sentences. Never threaten, never shame, "
    "never mention police or jail. Goal: agree a realistic payment date "
    "and amount, or a clean reason why not. Follow the state you are in."
)


class CallSession:
    def __init__(self, ctx: CallContext, llm: LLMProvider, now_local: dtime = dtime(10, 0)):
        self.ctx = ctx
        self.llm = llm
        self.now = now_local
        self.outcome = CallOutcome(disposition=Disposition.NO_COMMITMENT.value,
                                   language=ctx.language)
        self.history = []
        self.transcript = []

    def _say(self, text: str):
        check = compliance.check_agent_reply(text)
        if not check.allowed:
            text = ("Maaf kijiye, main aisi baat nahi kar sakta. "
                    "Let me connect you to a human officer.")
            self._escalate(f"agent reply vetoed: {check.reason}")
        self.transcript.append({"speaker": "agent", "text": text})
        self.history.append({"role": "assistant", "content": text})

    def _escalate(self, reason: str):
        self.outcome.escalated = True
        self.outcome.escalation_reason = reason
        if self.outcome.disposition not in (Disposition.DISPUTED.value,
                                            Disposition.DO_NOT_CALL.value):
            self.outcome.disposition = Disposition.ESCALATED_HUMAN.value
        self.ctx.move(State.ESCALATE_HUMAN, reason)
        self._say(languages.script(self.ctx.language, "escalate"))
        self.ctx.move(State.ENDED, "handoff complete")

    def open(self):
        if not compliance.within_call_window(self.now):
            self._say(languages.script(self.ctx.language, "window_block"))
            self.outcome.disposition = Disposition.CALLBACK_REQUESTED.value
            self.outcome.notes.append("outside RBI 08:00-19:00 contact window")
            self.ctx.move(State.ENDED, "outside call window")
            return
        c = self.ctx
        self._say(languages.script(c.language, "disclosure", desk=c.agent_desk_name,
                                   agent="Kavya", lender=c.lender_name, name=c.borrower_name))
        c.move(State.VERIFY_IDENTITY, "disclosure delivered")

    def hear(self, borrower_text: str):
        if self.ctx.state == State.ENDED:
            return
        self.transcript.append({"speaker": "borrower", "text": borrower_text})
        self.history.append({"role": "user", "content": borrower_text})
        self.outcome.turns += 1
        g = compliance.check_borrower_turn(borrower_text)
        c = self.ctx

        if g.action == "end_call":
            self.outcome.disposition = Disposition.DO_NOT_CALL.value
            self._say("Contact preference flagged for human review. Demo only; no live suppression list updated.")
            c.move(State.ENDED, g.reason)
            return
        if g.action == "escalate":
            if "not my loan" in g.reason or "mera loan nahi" in g.reason or "fraud" in g.reason:
                self.outcome.disposition = Disposition.DISPUTED.value
            self._escalate(g.reason)
            return

        low = borrower_text.lower()
        if c.state == State.VERIFY_IDENTITY:
            if low.strip() in ("haan", "haan ji", "yes", "yes speaking", "haan ji boliye", "haan ji, main hi ramesh bol raha hoon"):
                c.move(State.STATE_PURPOSE, "identity confirmed")
                self._say(languages.script(c.language, "purpose", amount=c.emi_amount,
                                           due=c.due_date))
                c.move(State.NEGOTIATE, "purpose stated")
            else:
                self._say(languages.script(c.language, "not_available"))
                self.outcome.disposition = Disposition.WRONG_PARTY.value
                c.move(State.ENDED, "borrower not on call")
            return

        if c.state == State.NEGOTIATE:
            if re.search(r"\b(no|not|cannot|cant|nahi|nahin)\b", low):
                self._say("No commitment recorded. Human review needed.")
                return
            if g.reason and "hardship" in g.reason:
                self.outcome.disposition = Disposition.HARDSHIP_RESTRUCTURE.value
                self.outcome.notes.append(g.reason)
            m = re.search(r"(\d{1,3}(?:,\d{3})+|\d+)\s*(?:rupaye|rupees|rs|₹)?", low)
            if any(w in low for w in ["kal", "tomorrow", "pay", "bharta", "kar dunga",
                                      "kar dungi", "friday", "monday", "salary"]):
                c.move(State.CAPTURE_PROMISE, "payment intent detected")
                # An informal utterance is not a confirmed promise or exact date.
                self.outcome.promised_amount = None
                self.outcome.promised_date = None
                self.outcome.disposition = Disposition.NO_COMMITMENT.value
                self.outcome.notes.append("Unconfirmed payment intent in transcript; human confirmation needed")
                self._say(self.llm.reply(SYSTEM_PROMPT, self.history))
                c.move(State.RECAP_CLOSE, "promise captured")
            else:
                self._say(self.llm.reply(SYSTEM_PROMPT, self.history))
            return

        if c.state == State.RECAP_CLOSE:
            self._say(languages.script(c.language, "close", name=c.borrower_name))
            c.move(State.ENDED, "recap delivered")
            return

    def run_simulation(self, borrower_script: list[str]):
        """Drive a full simulated call from a scripted borrower (offline demo)."""
        self.open()
        for line in borrower_script:
            if self.ctx.state == State.ENDED:
                break
            self.hear(line)
        if self.ctx.state not in (State.ENDED,):
            self.hear("ji")
        return self.outcome
