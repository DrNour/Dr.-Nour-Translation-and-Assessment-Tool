# ai_feedback.py

import os
import requests
import streamlit as st


def get_hf_token() -> str:
    """
    Get HuggingFace token from:
    - environment variable HF_API_TOKEN, or
    - Streamlit secrets: HF_API_TOKEN

    Works both locally (.streamlit/secrets.toml) and on Streamlit Cloud.
    """
    return os.getenv("HF_API_TOKEN", "") or st.secrets.get("HF_API_TOKEN", "")


def generate_ai_feedback(prompt: str) -> str | None:
    """
    Call an instruction-tuned model on HuggingFace Inference API.

    Returns:
        - generated text (str) on success
        - None if no token or hard failure
    """

    token = get_hf_token()
    if not token:
        return None

    # You can switch this to another HF model if you like
    model_name = "google/flan-t5-large"
    url = f"https://api-inference.huggingface.co/models/{model_name}"

    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.3,
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=25)

        if resp.status_code == 200:
            data = resp.json()
            # Standard HF text-generation format
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return data[0]["generated_text"]

        # If we reach here, something went wrong with HF
        # You can log resp.text to a file if you want, but we stay quiet in the UI.
        return None

    except Exception:
        # Network / timeout / etc.
        return None
