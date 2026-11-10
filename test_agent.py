import unittest
from datetime import time
from policy import CallContext, State
from providers import MockLLM
from session import CallSession
import compliance


def ctx():
    return CallContext(borrower_name="Ramesh Kumar", lender_name="DemoFin NBFC",
                       agent_desk_name="Collections Desk", emi_amount=4500,
                       due_date="2026-11-05")


class TestCompliance(unittest.TestCase):
    def test_call_window(self):
        self.assertTrue(compliance.within_call_window(time(10, 0)))
        self.assertFalse(compliance.within_call_window(time(21, 30)))
        self.assertFalse(compliance.within_call_window(time(6, 59)))

    def test_abuse_veto(self):
        r = compliance.check_agent_reply("Pay or police bulaa dunga")
        self.assertFalse(r.allowed)

    def test_dnc_ends_call(self):
        r = compliance.check_borrower_turn("please do not call me again")
        self.assertEqual(r.action, "end_call")


class TestSession(unittest.TestCase):
    def test_ptp_flow(self):
        s = CallSession(ctx(), MockLLM(), time(10, 0))
        o = s.run_simulation(["Haan ji boliye", "Kal 4500 kar dunga", "ji theek hai"])
        self.assertEqual(o.disposition, "no_commitment")
        self.assertIsNone(o.promised_amount)
        self.assertFalse(o.escalated)

    def test_partial_promise(self):
        s = CallSession(ctx(), MockLLM(), time(10, 0))
        o = s.run_simulation(["haan", "naukri chali gayi, 1500 kal kar dunga", "theek hai"])
        self.assertEqual(o.disposition, "no_commitment")
        self.assertIsNone(o.promised_amount)
        self.assertTrue(any("hardship" in n for n in o.notes))

    def test_dispute_escalates(self):
        s = CallSession(ctx(), MockLLM(), time(10, 0))
        o = s.run_simulation(["haan ji", "yeh mera loan nahi hai, fraud hai"])
        self.assertEqual(o.disposition, "disputed")
        self.assertTrue(o.escalated)
        self.assertEqual(s.ctx.state, State.ENDED)

    def test_outside_window_never_opens(self):
        s = CallSession(ctx(), MockLLM(), time(22, 15))
        o = s.run_simulation(["haan"])
        self.assertEqual(o.disposition, "callback_requested")
        self.assertNotIn("EMI", str(s.transcript))

    def test_wrong_party(self):
        s = CallSession(ctx(), MockLLM(), time(9, 0))
        o = s.run_simulation(["nahi, yeh wrong number hai"])
        self.assertEqual(o.disposition, "wrong_party")

    def test_no_banned_language_in_any_state(self):
        s = CallSession(ctx(), MockLLM(), time(10, 0))
        s.run_simulation(["haan", "paise nahi hain, kya kar loge?", "kal dunga", "ok"])
        for t in s.transcript:
            if t["speaker"] == "agent":
                self.assertTrue(compliance.check_agent_reply(t["text"]).allowed)


if __name__ == "__main__":
    unittest.main()

class TestNoInferredCommitments(unittest.TestCase):
    def test_negated_payment(self):
        s = CallSession(ctx(), MockLLM(), time(10, 0))
        o = s.run_simulation(["haan", "I cannot pay tomorrow"])
        self.assertIsNone(o.promised_amount)
    def test_negative_identity(self):
        s = CallSession(ctx(), MockLLM(), time(10, 0))
        s.run_simulation(["nahi ji"])
        self.assertNotIn("4500", str(s.transcript))
    def test_exclusive_window_end(self):
        self.assertFalse(compliance.within_call_window(time(19, 0)))
