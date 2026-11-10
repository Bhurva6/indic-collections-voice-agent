# Indic collections dialogue prototype

An offline Python prototype of a collections-call state machine. It accepts
written Hindi/Hinglish/English fixture utterances and emits fixed responses,
a transition log and an unconfirmed outcome record. No live voice, speech
recognition, speech synthesis, LLM API, dialler, SMS or CRM is connected.

## Run

Python 3.10+, standard library only:

```sh
python3 demo.py
python3 -m unittest discover -s . -v
```

The tests cover a configurable 08:00-19:00 local contact window, a small
keyword veto list, negative identity replies, disputes, contact preferences,
hardship and negated payment intent. The clock is injected by the caller,
not timezone-verified. Keyword matching is deliberately limited and is not
a reliable multilingual safety classifier.

The contact window is an illustrative conservative demo setting, not a
legal-compliance certification. Applicable law, lender policy, consent,
identity checks and language coverage need independent review before use.
The prototype does not authenticate identity, actually record a call, send
a message or connect a human. It only marks an escalation in its log.
Informal payment intent does not become a confirmed amount or date.

## Status and next work

12 unit tests pass on synthetic scripted examples. These are software tests,
not a safety benchmark. Next: real audio input/output, an evaluated model
adapter, robust identity and consent flows, exact commitment confirmation,
and tests with diverse native-speaker utterances. No models trained or
fine-tuned. All examples were written for this demo; no customer data used.
