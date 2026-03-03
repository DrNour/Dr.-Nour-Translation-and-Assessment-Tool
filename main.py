def build_ai_feedback_prompt(source_text: str, mt_text: str, student_text: str, task_type: str) -> str:
    mt_block = mt_text if mt_text else "(no MT output – direct translation task)"
    return f"""
You are an expert English–Arabic translation trainer specialising in translation and MT post-editing.

TASK TYPE: {task_type}

SOURCE TEXT:
{source_text}

MT OUTPUT (if any):
{mt_block}

STUDENT VERSION:
{student_text}

Give concise feedback suitable for a university translation classroom. Please:
1) Comment on accuracy (meaning transfer).
2) Comment on register and appropriateness for the context.
3) Comment on idiomatic and culturally appropriate choices.
4) Highlight one or two concrete examples where the student could improve.
5) If useful, propose a short improved version of one or two sentences, not the entire text.

You may answer partly in Arabic where it helps the student, but keep the structure clear and concise.
"""


def generate_ai_feedback(prompt: str):
    """
    Try to generate feedback using (in order of preference):
    1. OpenAI ChatGPT API (requires OPENAI_API_KEY)
    2. Hugging Face Inference API (requires HF_API_TOKEN)
    Returns None on any failure so the app never crashes.
    """

    # --- Option 1: OpenAI ChatGPT (paid, recommended for quality) ---
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # or gpt-3.5-turbo, etc.

    if openai and openai_api_key:
        try:
            openai.api_key = openai_api_key
            resp = openai.ChatCompletion.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful, expert translation instructor."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=600,
                temperature=0.4,
            )
            text = resp.choices[0].message["content"].strip()
            return text
        except Exception:
            pass  # fall through to HF

    # --- Option 2: Hugging Face free/hosted model (if token configured) ---
    HF_TOKEN = os.getenv("HF_API_TOKEN", "")
    if not HF_TOKEN:
        try:
            if hasattr(st, "secrets"):
                HF_TOKEN = st.secrets.get("HF_API_TOKEN", "")
        except Exception:
            HF_TOKEN = ""

    if HF_TOKEN:
        try:
            import requests
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = {"inputs": prompt}
            response = requests.post(
                "https://api-inference.huggingface.co/models/gpt2",
                headers=headers,
                json=payload,
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data and "generated_text" in data[0]:
                    return data[0]["generated_text"].strip()
        except Exception:
            pass

    # No configured backend
    return None
