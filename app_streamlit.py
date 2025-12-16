import streamlit as st
from slide_ai import SlideInputs, build_prompt, generate_slides_ai, prompt_quality_check

st.set_page_config(page_title="Slide Content Builder", layout="wide")

st.title("Slide Content Builder")
st.write("Two modes: guided prompt writing or AI-generated slide content (short, token-efficient).")

with st.sidebar:
    st.header("Presentation Settings")
    topic = st.text_input("Topic", placeholder="e.g., Introduction to Computer Vision")
    audience = st.text_input("Audience", placeholder="e.g., non-technical HR, beginners, engineers")
    goal = st.text_input("Goal", placeholder="e.g., explain basics + key applications + next steps")
    tone = st.selectbox("Tone", ["Professional", "Academic", "Sales/Marketing", "Simple", "Technical"], index=0)
    duration_min = st.slider("Duration (minutes)", 5, 60, 10, 1)
    slide_count = st.slider("Slide count", 3, 25, 8, 1)
    level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"], index=0)
    language = st.selectbox("Language", ["English", "Arabic"], index=0)
    speaker_notes = st.checkbox("Include speaker notes", value=True)

    must_include = st.text_area("Must include (optional)", placeholder="e.g., timeline, use-cases, risks, examples")
    must_avoid = st.text_area("Must avoid (optional)", placeholder="e.g., avoid jargon, avoid political content, no long text")
    extra_notes = st.text_area("Extra notes (optional)", placeholder="e.g., 10-slide pitch deck, end with CTA, add Q&A slide")

tabs = st.tabs(["1) Guided Prompt Mode (User writes)", "2) AI Mode (Generate slides)"])

# ---------- Guided Prompt Mode ----------
with tabs[0]:
    st.subheader("Guided Prompt Mode")
    st.write("Write your slide ideas; the app will generate a high-quality prompt you can copy/paste into any LLM.")

    user_content = st.text_area(
        "Your draft slide content (optional)",
        placeholder="e.g., Slide 1: What is CV...\nSlide 2: Applications...\n"
    )

    inputs = SlideInputs(
        topic=topic or "",
        audience=audience or "",
        goal=goal or "",
        tone=tone,
        duration_min=int(duration_min),
        slide_count=int(slide_count),
        level=level,
        language=language,
        must_include=must_include or "",
        must_avoid=must_avoid or "",
        speaker_notes=bool(speaker_notes),
        user_content=user_content or "",
        extra_notes=extra_notes or "",
    )

    st.info(prompt_quality_check(inputs))

    if st.button("Build My Prompt", type="primary"):
        prompt_text = build_prompt(inputs, mode="guided")
        st.subheader("Copy/Paste Prompt")
        st.code(prompt_text, language="text")

# ---------- AI Mode ----------
with tabs[1]:
    st.subheader("AI Mode")
    st.write("The app generates short slide-by-slide content using your constraints. (Token-efficient output.)")

    user_content_ai = st.text_area(
        "Optional content to refine (optional)",
        placeholder="Paste notes or a rough outline; AI will refine without expanding too much."
    )

    inputs_ai = SlideInputs(
        topic=topic or "",
        audience=audience or "",
        goal=goal or "",
        tone=tone,
        duration_min=int(duration_min),
        slide_count=int(slide_count),
        level=level,
        language=language,
        must_include=must_include or "",
        must_avoid=must_avoid or "",
        speaker_notes=bool(speaker_notes),
        user_content=user_content_ai or "",
        extra_notes=extra_notes or "",
    )

    st.info(prompt_quality_check(inputs_ai))

    if st.button("Generate Slide Content", type="primary"):
        with st.spinner("Generating..."):
            result = generate_slides_ai(inputs_ai)
        st.markdown(result)
