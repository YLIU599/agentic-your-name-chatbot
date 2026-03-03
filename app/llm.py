from __future__ import annotations

import os
from dotenv import load_dotenv
from litellm import acompletion

from .prompts import SYSTEM_PROMPT, FEW_SHOT

load_dotenv()

# Vertex AI uses Application Default Credentials (ADC):
#   gcloud init
#   gcloud auth application-default login
#
# LiteLLM expects:
#   VERTEX_PROJECT, VERTEX_LOCATION
# We accept VERTEX_PROJECT_ID in .env and map it.
if os.getenv("VERTEX_PROJECT_ID") and not os.getenv("VERTEX_PROJECT"):
    os.environ["VERTEX_PROJECT"] = os.environ["VERTEX_PROJECT_ID"]

MODEL = os.environ.get("MODEL", "vertex_ai/gemini-2.0-flash-lite")


def _render_system_prompt() -> str:
    # Minimal templating; replace placeholders once you choose a domain.
    replacements = {
        "{{DOMAIN_ONE_LINER}}": "REPLACE_WITH_YOUR_DOMAIN_ONE_LINER",
        "{{IN_SCOPE_1}}": "REPLACE_WITH_IN_SCOPE_1",
        "{{IN_SCOPE_2}}": "REPLACE_WITH_IN_SCOPE_2",
        "{{IN_SCOPE_3}}": "REPLACE_WITH_IN_SCOPE_3",
        "{{OOS_CAT_1}}": "REPLACE_WITH_OOS_CATEGORY_1",
        "{{OOS_CAT_2}}": "REPLACE_WITH_OOS_CATEGORY_2",
        "{{OOS_CAT_3}}": "REPLACE_WITH_OOS_CATEGORY_3",
    }
    s = SYSTEM_PROMPT
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s


async def generate_answer(user_message: str) -> str:
    messages = [{"role": "system", "content": _render_system_prompt()}]

    # few-shot examples (>=3 required by spec)
    for ex in FEW_SHOT:
        messages.append({"role": "user", "content": ex["user"]})
        messages.append({"role": "assistant", "content": ex["assistant"]})

    messages.append({"role": "user", "content": user_message})

    resp = await acompletion(model=MODEL, messages=messages, temperature=0.2)
    return resp["choices"][0]["message"]["content"].strip()
