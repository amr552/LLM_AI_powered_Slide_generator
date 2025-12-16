import os
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError, AuthenticationError, APIConnectionError, BadRequestError

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SYSTEM_PROMPT = """
You are an expert presentation designer and instructor.

Rules:
- Output must be SHORT and structured.
- No JSON. No markdown tables.
- Each slide: Title + 3–5 bullets (max).
- Optional speaker notes: 1–2 short lines per slide.
- Total output should fit typical short deck constraints.
- Respect audience, goal, tone, duration, slide count, and must-include/must-avoid items.
- If user content is provided, refine it (do NOT invent new unrelated sections).
Output format EXACTLY:

Deck Title:
Audience:
Goal:
Tone:
Duration:
Slides:

Slide 1 — <Title>
- bullet
- bullet
- bullet
Notes: ...

Slide 2 — ...
"""

@dataclass
class SlideInputs:
    topic: str
    audience: str
    goal: str
    tone: str
    duration_min: int
    slide_count: int
    level: str
    language: str
    must_include: str
    must_avoid: str
    speaker_notes: bool
    user_content: str  # optional (used in guided mode)
    extra_notes: str

def build_prompt(inputs: SlideInputs, mode: str) -> str:
    """
    mode:
      - "guided": user writes/has content; we build a strong prompt template
      - "ai": generate slide content from topic/constraints
    """
    base = f"""
Topic: {inputs.topic}
Audience: {inputs.audience}
Goal: {inputs.goal}
Tone: {inputs.tone}
Duration: {inputs.duration_min} minutes
Slide count: {inputs.slide_count}
Level: {inputs.level}
Language: {inputs.language}
Must include: {inputs.must_include or "None"}
Must avoid: {inputs.must_avoid or "None"}
Speaker notes: {"Yes" if inputs.speaker_notes else "No"}
Extra notes: {inputs.extra_notes or "None"}
""".strip()

    if mode == "guided":
        return f"""
You are helping a user write a PERFECT prompt for generating slide content.

1) Convert the following structured requirements into a single high-quality prompt.
2) Keep it concise and specific.
3) Include an explicit output format.

REQUIREMENTS:
{base}

USER'S DRAFT CONTENT (if any):
{inputs.user_content or "None"}

Return only the final prompt text that the user can copy/paste into an LLM.
""".strip()

    # mode == "ai"
    content_hint = ""
    if inputs.user_content and inputs.user_content.strip():
        content_hint = f"\nUser-provided content (use and refine, do not expand wildly):\n{inputs.user_content.strip()}\n"

    return f"""
Create slide-by-slide content for a presentation using the rules.
{base}
{content_hint}
Return output in the required format only. Keep it short.
""".strip()

def prompt_quality_check(inputs: SlideInputs) -> str:
    """
    Lightweight UX helper: tells the user what's missing (no model call).
    """
    missing = []
    if not inputs.topic.strip():
        missing.append("- Topic is missing.")
    if not inputs.audience.strip():
        missing.append("- Audience is missing (e.g., students, HR, engineers).")
    if not inputs.goal.strip():
        missing.append("- Goal is missing (what should the audience do/learn?).")
    if inputs.slide_count < 3:
        missing.append("- Slide count is very low; consider 5–12 for most talks.")
    if inputs.duration_min < 5:
        missing.append("- Duration is very short; reduce scope or slides.")
    if missing:
        return "Prompt quality check:\n" + "\n".join(missing)
    return "Prompt quality check:\n- Looks good. You can generate now."

def generate_slides_ai(inputs: SlideInputs) -> str:
    """
    Calls OpenAI to generate slide content (token-efficient).
    """
    if client is None:
        return "Missing OPENAI_API_KEY in .env"

    if not inputs.topic.strip():
        return "Please enter a topic."

    user_prompt = build_prompt(inputs, mode="ai")

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.4,
            max_tokens=500,  # control cost
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return (resp.choices[0].message.content or "").strip()

    except RateLimitError:
        return "API quota exceeded (429). Check billing/quota."
    except AuthenticationError:
        return "Invalid API key. Check OPENAI_API_KEY."
    except APIConnectionError:
        return "Network error. Try again."
    except BadRequestError as e:
        return f"Request error: {e}"
