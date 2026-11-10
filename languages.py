"""Offline prototype. See README.md for scope and limitations."""

SCRIPTS = {
    "hinglish": {
        "disclosure": ("Namaste, main {desk} se {agent} bol raha hoon, {lender} ki taraf se. "
                       "Yeh offline simulation hai, koi live call nahi. "
                       "Kya main {name} se baat kar raha hoon?"),
        "not_available": "Koi baat nahi. Hum baad mein call karenge. Dhanyavaad.",
        "purpose": ("Aapka {amount} rupaye ka EMI {due} ko due tha aur abhi pending hai. "
                    "Kya aap bata sakte hain kab tak payment ho payega?"),
        "close": ("Dhanyavaad {name} ji. Humne note kar liya hai. Yeh sirf demo note hai, koi SMS nahi bheja gaya. "
                  "Shubh din."),
        "escalate": "Main aapko humare human officer se connect kar raha hoon. Demo mein sirf handoff flag set hua hai.",
        "window_block": "Yeh call sirf subah 8 baje se shaam 7 baje ke beech allowed hai. Hum kal call karenge.",
    },
    "hi": {
        "disclosure": ("नमस्ते, मैं {desk} से {agent} बोल रहा हूँ, {lender} की ओर से. "
                       "यह ऑफलाइन डेमो है, लाइव कॉल नहीं. क्या मैं {name} से बात कर रहा हूँ?"),
        "not_available": "कोई बात नहीं. हम बाद में कॉल करेंगे. धन्यवाद.",
        "purpose": "आपका {amount} रुपये का EMI {due} को देय था और अभी लंबित है. कब तक भुगतान संभव है?",
        "close": "धन्यवाद {name} जी. हमने नोट कर लिया है. कोई SMS नहीं भेजा गया है.",
        "escalate": "मैं आपको हमारे अधिकारी से जोड़ रहा हूँ. यह केवल डेमो फ्लैग है.",
        "window_block": "यह कॉल केवल सुबह 8 से शाम 7 बजे के बीच अनुमत है. हम कल कॉल करेंगे.",
    },
    "en": {
        "disclosure": ("Hello, this is {agent} calling from {desk} on behalf of {lender}. "
                       "This is an offline simulation, not a live call. "
                       "Am I speaking with {name}?"),
        "not_available": "No problem. We will call back later. Thank you.",
        "purpose": "Your EMI of {amount} rupees was due on {due} and is still pending. When can you pay it?",
        "close": "Thank you, {name}. We have noted this. This is a demo note; no SMS has been sent. Have a good day.",
        "escalate": "I am connecting you to a human officer. Only a handoff flag is set in this demo.",
        "window_block": "We are only permitted to call between 8 AM and 7 PM. We will call tomorrow.",
    },
}


def script(lang: str, key: str, **kw) -> str:
    return SCRIPTS[lang][key].format(**kw)
