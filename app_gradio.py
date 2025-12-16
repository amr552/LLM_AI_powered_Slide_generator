import gradio as gr
from slide_ai import SlideInputs, build_prompt, generate_slides_ai, prompt_quality_check

TONES = ["Professional", "Academic", "Sales/Marketing", "Simple", "Technical"]
LEVELS = ["Beginner", "Intermediate", "Advanced"]
LANGS = ["English", "Arabic"]

def guided_prompt_fn(topic, audience, goal, tone, duration, slide_count, level, language, speaker_notes, must_include, must_avoid, extra_notes, user_content):
    inputs = SlideInputs(
        topic=topic or "",
        audience=audience or "",
        goal=goal or "",
        tone=tone,
        duration_min=int(duration),
        slide_count=int(slide_count),
        level=level,
        language=language,
        must_include=must_include or "",
        must_avoid=must_avoid or "",
        speaker_notes=bool(speaker_notes),
        user_content=user_content or "",
        extra_notes=extra_notes or "",
    )
    qc = prompt_quality_check(inputs)
    prompt_text = build_prompt(inputs, mode="guided")
    return qc, prompt_text

def ai_mode_fn(topic, audience, goal, tone, duration, slide_count, level, language, speaker_notes, must_include, must_avoid, extra_notes, user_content):
    inputs = SlideInputs(
        topic=topic or "",
        audience=audience or "",
        goal=goal or "",
        tone=tone,
        duration_min=int(duration),
        slide_count=int(slide_count),
        level=level,
        language=language,
        must_include=must_include or "",
        must_avoid=must_avoid or "",
        speaker_notes=bool(speaker_notes),
        user_content=user_content or "",
        extra_notes=extra_notes or "",
    )
    qc = prompt_quality_check(inputs)
    slides = generate_slides_ai(inputs)
    return qc, slides

with gr.Blocks(title="Slide Content Builder") as demo:
    gr.Markdown("# Slide Content Builder\nTwo modes: guided prompt writing or AI slide generation (short output).")

    with gr.Row():
        topic = gr.Textbox(label="Topic", placeholder="e.g., AI in Business (overview)")
        audience = gr.Textbox(label="Audience", placeholder="e.g., HR / students / engineers")
    goal = gr.Textbox(label="Goal", placeholder="e.g., explain key concepts + practical takeaways")

    with gr.Row():
        tone = gr.Dropdown(TONES, value="Professional", label="Tone")
        level = gr.Dropdown(LEVELS, value="Beginner", label="Level")
        language = gr.Dropdown(LANGS, value="English", label="Language")

    with gr.Row():
        duration = gr.Slider(5, 60, value=10, step=1, label="Duration (minutes)")
        slide_count = gr.Slider(3, 25, value=8, step=1, label="Slide count")

    speaker_notes = gr.Checkbox(value=True, label="Include speaker notes")
    must_include = gr.Textbox(label="Must include (optional)", placeholder="e.g., examples, risks, roadmap")
    must_avoid = gr.Textbox(label="Must avoid (optional)", placeholder="e.g., jargon, long text")
    extra_notes = gr.Textbox(label="Extra notes (optional)", placeholder="e.g., end with CTA, include Q&A slide")
    user_content = gr.Textbox(label="User content / draft (optional)", lines=6, placeholder="Paste rough outline here...")

    with gr.Tab("Guided Prompt Mode"):
        btn1 = gr.Button("Build My Prompt")
        qc1 = gr.Markdown()
        prompt_out = gr.Textbox(label="Copy/Paste Prompt", lines=10)
        btn1.click(
            guided_prompt_fn,
            inputs=[topic, audience, goal, tone, duration, slide_count, level, language, speaker_notes, must_include, must_avoid, extra_notes, user_content],
            outputs=[qc1, prompt_out],
        )

    with gr.Tab("AI Mode"):
        btn2 = gr.Button("Generate Slide Content")
        qc2 = gr.Markdown()
        slides_out = gr.Markdown()
        btn2.click(
            ai_mode_fn,
            inputs=[topic, audience, goal, tone, duration, slide_count, level, language, speaker_notes, must_include, must_avoid, extra_notes, user_content],
            outputs=[qc2, slides_out],
        )

if __name__ == "__main__":
    demo.launch(server_port=7860)
