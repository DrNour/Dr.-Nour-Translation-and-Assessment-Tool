# main.py  — EduApp (single file)
# - Evidence-based adaptive feedback (with concrete examples)
# - Safer instructor login (env var or SHA256; fallback for dev)
# - JSON storage maintained (no DB migration needed)
# - Reflection capture, progress charts, class snapshot
# - Graceful fallbacks for optional libs; no crashes on missing deps

import os
import re
import json
import time
import hashlib
import random
import threading
from io import BytesIO
from pathlib import Path
from typing import List, Tuple
from difflib import SequenceMatcher, ndiff
import datetime

import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import RGBColor

# Optional metrics deps (graceful fallback if missing)
try:
    import sacrebleu
except Exception:
    sacrebleu = None

try:
    from bert_score import score as bertscore_score
except Exception:
    bertscore_score = None

# Optional plotting
try:
    import matplotlib.pyplot as plt  # noqa: F401
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False

# ---------------- Proof-of-life banner (so you know this file is loaded) ----------------
THIS_FILE = os.path.abspath(__file__)
LAST_EDIT = datetime.datetime.fromtimestamp(os.path.getmtime(THIS_FILE))

# ---------------- Storage (JSON with basic locking & atomic writes) ----------------
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

EXERCISES_FILE = DATA_DIR / "exercises.json"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"

_lock = threading.Lock()

def load_json(file: Path):
    file = Path(file)
    if file.exists():
        with file.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_json(file: Path, data):
    with _lock:
        tmp = Path(str(file) + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        tmp.replace(file)

# ---------------- Auth (safer than hard-coded) ----------------
def _env(name, default=""):
    return os.getenv(name, default)

# Set one of these before running (recommended):
#   export INSTRUCTOR_PASSWORD_PLAIN='StrongPass'
#   export INSTRUCTOR_PASSWORD_SHA256='<sha256 hex of StrongPass>'
_INSTRUCTOR_PLAIN = _env("INSTRUCTOR_PASSWORD_PLAIN", "")
_INSTRUCTOR_SHA256 = _env("INSTRUCTOR_PASSWORD_SHA256", "")
_FALLBACK_PLAIN = "admin123"  # used only if env vars aren't set

def check_password(typed: str) -> bool:
    try:
        if _INSTRUCTOR_SHA256:
            h = hashlib.sha256(typed.encode("utf-8")).hexdigest()
            return h == _INSTRUCTOR_SHA256
        if _INSTRUCTOR_PLAIN:
            return typed == _INSTRUCTOR_PLAIN
        return typed == _FALLBACK_PLAIN
    except Exception:
        return False  # never crash on login

# ---------------- Tokenization & Edit Helpers ----------------
_token_re = re.compile(r"\w+|[^\w\s]", re.UNICODE)

def _tokenize(s: str) -> List[str]:
    return _token_re.findall(s or "")

def compute_edit_details(mt_text: str, student_text: str) -> Tuple[int, int, int]:
    mt_tokens = _tokenize(mt_text)
    st_tokens = _tokenize(student_text)
    matcher = SequenceMatcher(None, mt_tokens, st_tokens)

    additions = deletions = replacements = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            additions += (j2 - j1)
        elif tag == "delete":
            deletions += (i2 - i1)
        elif tag == "replace":
            replacements += max(i2 - i1, j2 - j1)
    total_edits = additions + deletions + replacements
    return additions, deletions, total_edits

# ---------------- Metrics ----------------
def evaluate_translation(student_text, mt_text=None, reference=None, task_type="Translate", source_text=""):
    """
    Returns a metrics dict using:
      - length_ratio (target tokens / source tokens)
      - BLEU (sacrebleu, if reference provided)
      - chrF++ (sacrebleu, if reference provided)
      - BERTScore_F1 (if available & reference provided)
      - edit counts for post-edit tasks
    All metrics gracefully fallback to None if libs or references are missing.
    """
    src_len = max(1, len(_tokenize(source_text)))
    tgt_len = len(_tokenize(student_text))
    length_ratio = round(tgt_len / src_len, 3)

    if task_type == "Post-edit MT" and mt_text:
        additions, deletions, edits = compute_edit_details(mt_text, student_text)
    else:
        additions = deletions = edits = 0

    bleu = chrf = bert_f1 = None
    if reference:
        refs = [reference]
        try:
            if sacrebleu:
                bleu = float(sacrebleu.corpus_bleu([student_text], [refs]).score)  # 0-100
                chrf = float(sacrebleu.corpus_chrf([student_text], [refs]).score)  # 0-100
        except Exception:
            bleu = None
            chrf = None
        try:
            if bertscore_score:
                P, R, F1 = bertscore_score([student_text], [reference], lang="en")
                bert_f1 = float(F1.mean().item())  # 0-1
        except Exception:
            bert_f1 = None

    return {
        "length_ratio": length_ratio,
        "BLEU": None if bleu is None else round(bleu, 2),
        "chrF++": None if chrf is None else round(chrf, 2),
        "BERTScore_F1": None if bert_f1 is None else round(bert_f1, 3),
        "additions": additions,
        "deletions": deletions,
        "edits": edits
    }

# ---------------- Track Changes (HTML + DOCX) ----------------
def _join_tokens_for_display(tokens: List[str]) -> str:
    out = " ".join(tokens)
    out = re.sub(r"\s+([.,!?;:])", r"\1", out)
    return out

def diff_text(baseline: str, student_text: str) -> str:
    differ = ndiff(_tokenize(baseline), _tokenize(student_text))
    parts = []
    for w in differ:
        token = w[2:]
        if w.startswith("- "):
            parts.append(f"<span style='color:#c00;text-decoration:line-through'>{token}</span>")
        elif w.startswith("+ "):
            parts.append(f"<span style='color:#080'>{token}</span>")
        else:
            parts.append(token)
    return _join_tokens_for_display(parts)

def add_diff_to_doc(doc: Document, baseline: str, student_text: str):
    differ = ndiff(_tokenize(baseline), _tokenize(student_text))
    p = doc.add_paragraph()
    for w in differ:
        token = w[2:]
        if w.startswith("- "):
            run = p.add_run(token + " ")
            run.font.strike = True
            run.font.color.rgb = RGBColor(255, 0, 0)
        elif w.startswith("+ "):
            run = p.add_run(token + " ")
            run.font.color.rgb = RGBColor(0, 128, 0)
        else:
            p.add_run(token + " ")

# ---------------- Exports ----------------
def export_student_word(submissions, student_name):
    doc = Document()
    doc.add_heading(f"Student: {student_name}", 0)
    subs = submissions.get(student_name, {})
    for ex_id, sub in subs.items():
        doc.add_heading(f"Exercise {ex_id}", level=1)
        doc.add_paragraph("Source Text:")
        doc.add_paragraph(sub.get("source_text", ""))
        if sub.get("mt_text"):
            doc.add_paragraph("MT Output:")
            doc.add_paragraph(sub.get("mt_text", ""))

        if sub.get("task_type") == "Post-edit MT":
            doc.add_paragraph("Student Submission (Track Changes):")
            base = sub.get("mt_text", "") or ""
            add_diff_to_doc(doc, base, sub.get("student_text", ""))
        else:
            doc.add_paragraph("Student Submission:")
            doc.add_paragraph(sub.get("student_text", ""))

        metrics = sub.get("metrics", {})
        doc.add_paragraph(f"Metrics: {metrics}")
        doc.add_paragraph(f"Task Type: {sub.get('task_type','')}")
        doc.add_paragraph(f"Time Spent: {sub.get('time_spent_sec', 0):.2f} sec")
        doc.add_paragraph(f"Characters (not keystrokes): {sub.get('keystrokes', 0)}")
        if sub.get("reflection"):
            doc.add_paragraph("Reflection:")
            doc.add_paragraph(sub.get("reflection"))
        doc.add_paragraph("---")

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def export_summary_excel(submissions):
    rows = []
    for student, subs in submissions.items():
        for ex_id, sub in subs.items():
            m = sub.get("metrics", {})
            rows.append({
                "Student": student,
                "Exercise": ex_id,
                "Task Type": sub.get("task_type", ""),
                "Length Ratio": m.get("length_ratio"),
                "BLEU": m.get("BLEU"),
                "chrF++": m.get("chrF++"),
                "BERTScore_F1": m.get("BERTScore_F1"),
                "Additions": m.get("additions"),
                "Deletions": m.get("deletions"),
                "Edits": m.get("edits"),
                "Time Spent (s)": sub.get("time_spent_sec", 0),
                "Characters Typed": sub.get("keystrokes", 0)
            })
    df = pd.DataFrame(rows)
    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return buf

# ---------------- Gamification ----------------
def load_leaderboard():
    return load_json(LEADERBOARD_FILE)

def update_leaderboard(student_name, points):
    leaderboard = load_leaderboard()
    leaderboard[student_name] = leaderboard.get(student_name, 0) + points
    save_json(LEADERBOARD_FILE, leaderboard)

def show_leaderboard():
    leaderboard = load_leaderboard()
    st.subheader("Leaderboard")
    if leaderboard:
        items = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        df = pd.DataFrame(items, columns=["Student", "Points"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No leaderboard data yet.")

# ---------------- Optional AI generator (safe off) ----------------
def ai_generate_text(prompt):
    HF_TOKEN = ""  # Leave empty for safety
    if not HF_TOKEN:
        return None
    try:
        import requests
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": prompt}
        response = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers=headers,
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return data[0]["generated_text"]
    except Exception:
        pass
    return None

# ---------------- Evidence-based Linguistic Hints ----------------
_AR_LETTERS = r"\u0600-\u06FF"  # Arabic Unicode block

def _tokenize_words(text: str):
    # words incl. hyphen/apostrophes; keep numbers as tokens
    return re.findall(r"[A-Za-z" + _AR_LETTERS + r"]+[’'\-]?[A-Za-z" + _AR_LETTERS + r"]+|\d+(?:[.,]\d+)?", text)

def _likely_terms(source_text: str):
    """
    Heuristics for 'terms/proper names':
    - Titlecase/ALLCAPS (Latin)
    - Contains hyphen or digits
    - Quoted spans
    - Arabic words length>=4
    """
    terms = set()
    # quoted chunks
    for q in re.findall(r"[\"“”‘’'`«»](.+?)[\"“”‘’'`«»]", source_text):
        for w in _tokenize_words(q):
            if len(w) >= 3:
                terms.add(w)

    for w in _tokenize_words(source_text):
        if re.match(r"[A-Z][A-Za-z\-]+$", w):          # Titlecase
            terms.add(w)
        elif re.match(r"[A-Z0-9\-]{3,}$", w):          # ALLCAPS or alnum with -
            terms.add(w)
        elif "-" in w or re.search(r"\d", w):          # hyphenated or digits
            terms.add(w)
        elif re.match(r"[" + _AR_LETTERS + r"]{4,}$", w):  # Arabic word len>=4
            terms.add(w)
    return terms

def _short_list(items, n=4):
    items = list(items)
    if not items:
        return ""
    if len(items) <= n:
        return " | ".join(items)
    return " | ".join(items[:n]) + f" … (+{len(items)-n} more)"

def quick_linguistic_hints(source_text: str, student_text: str):
    hints = []
    try:
        # Numbers: exact evidence
        src_nums = set(re.findall(r"\d+(?:[.,]\d+)?", source_text))
        tgt_nums = set(re.findall(r"\d+(?:[.,]\d+)?", student_text))
        missing_nums = sorted(src_nums - tgt_nums, key=lambda x: (len(x), x))
        if missing_nums:
            hints.append({
                "rule": "numbers_missing",
                "message": "Some figures from the source didn’t appear in your text.",
                "evidence": f"Missing: {_short_list(missing_nums)}"
            })

        # Brackets & quotes balance
        for sym_open, sym_close, label in [("(", ")", "parentheses"), ("[", "]", "brackets"), ("{", "}", "braces")]:
            if source_text.count(sym_open) != student_text.count(sym_close):
                hints.append({
                    "rule": f"{label}_unbalanced",
                    "message": f"{label.capitalize()} look unbalanced.",
                    "evidence": (f"Source {sym_open}/{sym_close}: {source_text.count(sym_open)}/{source_text.count(sym_close)}; "
                                 f"Your text: {student_text.count(sym_open)}/{student_text.count(sym_close)}")
                })
        if source_text.count('"') != student_text.count('"'):
            hints.append({
                "rule": "quotes_unbalanced",
                "message": "Quotation marks may be unbalanced.",
                "evidence": f'Source quotes: {source_text.count(chr(34))}; Yours: {student_text.count(chr(34))}'
            })

        # Terms/proper names: concrete examples
        src_terms = _likely_terms(source_text)
        tgt_tokens = set(_tokenize_words(student_text))
        missing_terms = sorted([t for t in src_terms if t not in tgt_tokens], key=lambda x: (-len(x), x))
        if missing_terms:
            hints.append({
                "rule": "terms_missing",
                "message": "Some key terms/names from the source weren’t reflected.",
                "evidence": f"Examples: {_short_list(missing_terms)}"
            })
    except Exception:
        pass
    return hints

# ---------------- Adaptive Feedback (varied phrasing + evidence) ----------------
def generate_feedback(metrics: dict, task_type: str, source_text: str, student_text: str, extra_hints=None):
    msgs = []
    lr = metrics.get("length_ratio")
    edits = int(metrics.get("edits", 0) or 0)
    adds = int(metrics.get("additions", 0) or 0)
    dels = int(metrics.get("deletions", 0) or 0)
    bleu = metrics.get("BLEU")
    chrf = metrics.get("chrF++")

    # 1) Edit profile (Post-edit MT)
    if task_type == "Post-edit MT":
        if edits == 0:
            msgs.append(("edits_none",
                         "No edits were applied to the MT output.",
                         "Review the MT carefully—critical errors may remain."))
        elif edits > 20:
            msgs.append(("edits_many",
                         f"High edit volume detected: {edits} edits (additions {adds}, deletions {dels}).",
                         "Prioritize adequacy/accuracy first; avoid cosmetic rephrasing that doesn’t fix meaning."))

    # 2) Length ratio diagnostics
    if lr is not None:
        if lr < 0.80:
            msgs.append(("len_low",
                         f"Length ratio is {lr:.2f} (target ~0.90–1.20).",
                         "Your translation may be over-compressed—recheck for omitted content."))
        elif lr > 1.30:
            msgs.append(("len_high",
                         f"Length ratio is {lr:.2f} (target ~0.90–1.20).",
                         "Consider concision—trim redundancy and literal padding."))

    # 3) Metric interplay (accuracy vs fluency)
    if bleu is not None and chrf is not None:
        if bleu < 30 <= chrf:
            msgs.append(("acc_low_flu_ok",
                         f"chrF++ is {ch
