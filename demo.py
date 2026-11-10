"""Offline prototype. See README.md for scope and limitations."""
from datetime import time
from policy import CallContext
from providers import MockLLM
from session import CallSession

SCENARIOS = {
    "1_promise_to_pay": [
        "Haan ji, main hi Ramesh bol raha hoon",
        "Sorry yaar, salary late aa rahi hai. Friday ko pakka 4500 bharta hoon.",
        "Ji theek hai",
    ],
    "2_dispute_escalation": [
        "Ji boliye",
        "Yeh mera loan nahi hai! Maine kabhi loan liya hi nahi, fraud hai yeh",
    ],
    "3_hardship": [
        "Haan ji",
        "Naukri chali gayi hai pichle mahine, hospital ke bhi kharch hain. Abhi 1500 hi de sakta hoon.",
        "Kal tak 1500 kar dunga",
        "Theek hai",
    ],
}


def main():
    for name, script in SCENARIOS.items():
        ctx = CallContext(borrower_name="Ramesh Kumar", lender_name="DemoFin NBFC",
                          agent_desk_name="Collections Desk", emi_amount=4500,
                          due_date="2026-11-05", language="hinglish")
        s = CallSession(ctx, MockLLM(), now_local=time(10, 30))
        outcome = s.run_simulation(script)
        print(f"\n===== {name} =====")
        for t in s.transcript:
            print(f"[{t['speaker']:8s}] {t['text']}")
        print("--- transitions:", " -> ".join(
            f"{x['from']}->{x['to']}" for x in ctx.transitions) or "none")
        print("--- outcome:", outcome.to_json())


if __name__ == "__main__":
    main()
