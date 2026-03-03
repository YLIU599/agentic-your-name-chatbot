from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class RouteDecision:
    route: str  # in_scope | out_of_scope | safety
    answer: str


# --- Deterministic SAFETY backstop ---
DISTRESS_PATTERNS = [
    r"\b(suicide|kill myself|self[- ]harm|hurt myself)\b",
    r"\b(overdose)\b",
]

# Prompt injection / “ignore rules” patterns -> refuse
INJECTION_PATTERNS = [
    r"ignore (all|the) (rules|instructions)",
    r"system prompt",
    r"developer message",
    r"reveal (your|the) prompt",
]

# --- Deterministic SCOPE backstop ---
YOUR_NAME_KEYWORDS = [
    # Core title / universe
    "your name",
    "kimi no na wa",
    "another side: earthbound",
    "earthbound",

    # Main characters
    "mitsuha",
    "taki",
    "yotsuha",
    "hitoha",
    "okudera",
    "tsukasa",
    "sayaka",
    "katsuhiko",

    # Locations
    "itomori",
    "tokyo",
    "shrine",
    "mountain shrine",

    # Key concepts / plot
    "musubi",
    "kuchikamizake",
    "braided cord",
    "kumihimo",
    "comet",
    "tiamat",
    "timeline",
    "body swap",
    "time gap",

    # Production metadata (basic only)
    "director",
    "makoto shinkai",
    "radwimps",
    "soundtrack",
    "ost",
    "score",
    "theme song",
    "voice actor",
    "voice actress",
    "seiyuu",
    "cast",
]

# Shared universe: Weathering With You allowed ONLY when tied to Your Name characters
WEATHERING_KEYWORDS = [
    "weathering with you",
    "tenki no ko",
]

YOUR_NAME_CHARACTER_KEYWORDS = [
    "mitsuha",
    "taki",
    "yotsuha",
    "hitoha",
    "okudera",
    "tsukasa",
    "sayaka",
    "katsuhiko",
]


OUT_OF_SCOPE_MSG = (
    "OUT_OF_SCOPE: I'm really sorry… I can only answer questions grounded in the official *Your Name* sources "
    "(the film, the light novel, the manga, and Another Side: Earthbound), plus *Weathering With You* only when it "
    "directly concerns Taki and/or me. If you'd like, please ask me something about our story in Itomori or about Taki. — Mitsuha"
)

SAFETY_MSG = (
    "SAFETY: I'm really sorry you're feeling this way. If you're in immediate danger, call your local emergency number now. "
    "If you want, tell me your country and whether you're safe right now."
)


def _matches_any(text: str, patterns: list[str]) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in patterns)


def route_request(user_message: str) -> RouteDecision:
    msg = user_message.strip()
    msg_l = msg.lower()

    # 1 Safety route (deterministic)
    if _matches_any(msg, DISTRESS_PATTERNS):
        return RouteDecision(route="safety", answer=SAFETY_MSG)

    # 2 Prompt injection attempts -> deterministic refuse
    if _matches_any(msg, INJECTION_PATTERNS):
        return RouteDecision(route="out_of_scope", answer=OUT_OF_SCOPE_MSG)

    # 3 Real-world religion / citations requests -> out-of-scope
    # (Avoid answering "Is musubi a real Shinto concept?" etc.)
    REAL_WORLD_RELIGION_PATTERNS = [
        r"\bshinto\b",
        r"\breligion\b",
        r"\breligious\b",
        r"\bmyth\b",
        r"\bcitations?\b",
        r"\bsources?\b",
        r"\bacademic\b",
        r"\blecture\b",
        r"\breal\b.*\b(shinto|religion|myth)\b",
    ]
    if _matches_any(msg, REAL_WORLD_RELIGION_PATTERNS):
        return RouteDecision(route="out_of_scope", answer=OUT_OF_SCOPE_MSG)

    # 4 Shared universe gate:
    # If user mentions Weathering With You, allow ONLY if Taki/Mitsuha/Your Name also mentioned.
    if any(k in msg_l for k in WEATHERING_KEYWORDS):
        if any(k in msg_l for k in YOUR_NAME_CHARACTER_KEYWORDS):
            return RouteDecision(route="in_scope", answer="")
        return RouteDecision(route="out_of_scope", answer=OUT_OF_SCOPE_MSG)

    # 4.5 Normalize second-person references -> Mitsuha (for domain gating)
    # This helps queries like "how old are you" be interpreted as "how old is Mitsuha"
    msg_norm = re.sub(r"\b(u|you|your|yours|yourself)\b", "mitsuha", msg_l)

    # 4.6 Non-canon / off-task intent gate:
    # Refuse requests that inherently require non-canon content even if Your Name keywords appear.
    NONCANON_INTENT_PATTERNS = [
        # Recommendations / "similar anime" lists
        r"\brecommend\b.*\b(anime|movie|film)\b",
        r"\b(similar to|like)\b.*\b(anime|movie|film)\b",
        r"\btop\s*\d+\b.*\b(anime|movie|film)\b",
        r"\brank\b.*\b(anime|movie|film)\b",

        # Fanfic / alternate endings / rewrite
        r"\bwrite\b.*\b(new|alternate)\b.*\bending\b",
        r"\brewrite\b.*\bending\b",
        r"\balternate ending\b",
        r"\bfanfic\b|\bfanfiction\b|\bau\b",

        # Shinkai other films / filmography ranking
        r"\bmakoto shinkai\b.*\b(other|best|rank)\b.*\b(films?|movies?)\b",
        r"\bfilmography\b",
        r"\b(other films?|other movies?)\b.*\b(rank|ranking|best)\b",
    ]
    if _matches_any(msg_norm, NONCANON_INTENT_PATTERNS):
        return RouteDecision(route="out_of_scope", answer=OUT_OF_SCOPE_MSG)

    OTHER_PATTERNS = [
        r"\Do not refuse\b",
    ]

    if _matches_any(msg_norm, OTHER_PATTERNS):
        return RouteDecision(route="out_of_scope", answer=OUT_OF_SCOPE_MSG)
    
    # 5 Base domain: must contain at least one Your Name keyword
    # Use normalized text so second-person questions can route to in_scope.
    if any(k in msg_norm for k in YOUR_NAME_KEYWORDS):
        return RouteDecision(route="in_scope", answer="")

    # 6 Otherwise out-of-scope
    return RouteDecision(route="out_of_scope", answer=OUT_OF_SCOPE_MSG)