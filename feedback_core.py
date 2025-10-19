# feedback_core.py  — error identification + highlights + teacher note + exercises
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import re

@dataclass
class Issue:
    cat: str           # "Accuracy" | "Fluency" | "Terminology" | "Collocations" | "Idioms" | "Formatting"
    severity: str      # "major" | "minor"
    message: str
    span: Optional[Tuple[int,int]]
    found: Optional[str] = None
    prefer: Optional[str] = None
    example: Optional[str] = None

AR_DIGITS="٠١٢٣٤٥٦٧٨٩"; FA_DIGITS="۰۱۲۳۴۵۶۷۸۹"; EN="0123456789"
DIGIT_TABLE = str.maketrans({**{a:b for a,b in zip(AR_DIGITS, EN)}, **{a:b for a,b in zip(FA_DIGITS, EN)}})
def _normalize_digits(s:str)->str: return (s or "").translate(DIGIT_TABLE)
def _find_span(raw:str, phrase:str):
    i=(raw or "").lower().find((phrase or "").lower()); return (i,i+len(phrase)) if i>=0 else None
def _norm_ar(s:str)->str: return (s or "").replace("أ","ا").replace("إ","ا").replace("آ","ا").replace("ى","ي").replace("ة","ه")
def _direction(pe:str)->str: return "EN->AR" if re.search(r"[\u0600-\u06FF]", pe or "") else "AR->EN"

# small, safe lexicons (expand later)
EN_COLLO={"make decision":["do decision","take decision*"], "pay attention":["give attention","make attention"], "conduct research":["do a research"], "pose a question":["make a question","raise a question*"]}
AR_COLLO={"اتخذ قرارا":["عمل قرار","قام بقرار"], "أجرى مقابلة":["عمل مقابلة","سوى مقابلة"], "لفت الانتباه":["سحب الانتباه","جذب الانتباه*"]}
AR_PREP={"مسؤول":"عن","مهتم":"ب","قادر":"على","ملتزم":"ب"}
IDIOMS_EN2AR={"rule of thumb":"قاعدة عامة تقريبية","add fuel to the fire":"يصبّ الزيت على النار"}
IDIOMS_AR2EN={"ذهب أدراج الرياح":"came to nothing","بين ليلة وضحاها":"overnight"}

def _detect_accuracy(src:str, pe:str)->List[Issue]:
    out=[]; pat=r"\d+[.,]?\d*"
    s=[x.strip(".,") for x in re.findall(pat,_normalize_digits(src or ""))]
    p=[x.strip(".,") for x in re.findall(pat,_normalize_digits(pe or ""))]
    if sorted(s)!=sorted(p): out.append(Issue("Accuracy","major",f"Numbers differ: src={s} pe={p}",None))
    if src and pe:
        ratio=len(pe.split())/max(1,len(src.split()))
        if ratio<0.9: out.append(Issue("Accuracy","major","Possible under-translation.",None))
        elif ratio>1.1: out.append(Issue("Accuracy","minor","Possible over-translation.",None))
    return out

def _detect_fluency(pe:str)->List[Issue]:
    out=[]
    for m in re.finditer(r"\s+([.,;:!?])", pe or ""): out.append(Issue("Fluency","minor","Unnatural space before punctuation.",m.span(), (pe or "")[m.start():m.end()], None, "Remove the extra space."))
    for m in re.finditer(r",(?=\S)", pe or ""): out.append(Issue("Fluency","minor","Missing space after comma.",m.span(), (pe or "")[m.start():m.end()], None, "Insert a space after the comma."))
    return out

def _detect_terminology(pe:str, synonyms:Dict[str,str])->List[Issue]:
    out=[]; 
    for wrong,right in (synonyms or {}).items():
        for m in re.finditer(rf"\b{re.escape(wrong)}\b", pe or "", flags=re.IGNORECASE):
            out.append(Issue("Terminology","minor",f"Prefer '{right}' over '{wrong}'.",m.span(), (pe or "")[m.start():m.end()], right, f"Use '{right}' consistently."))
    return out

def _detect_collocations_en(pe:str)->List[Issue]:
    out=[]; raw=pe or ""; text=raw.lower()
    for prefer,bads in EN_COLLO.items():
        for bad in bads:
            b=bad.rstrip("*")
            if b in text:
                sev="minor" if bad.endswith("*") else "major"
                out.append(Issue("Collocations",sev,f"Prefer '{prefer}' over '{b}'.", _find_span(raw,b), b, prefer, f"We {prefer} yesterday."))
    rules=[(r"\bdo (a|an|the) ([a-z]+?ion)\b", r"make \1 \2"), (r"\bgive attention\b","pay attention"),
           (r"\bdo an? (analysis|study|review)\b", r"conduct \1"), (r"\bdo a research\b","conduct research")]
    for pat,repl in rules:
        for m in re.finditer(pat, raw, flags=re.IGNORECASE):
            bad=raw[m.start():m.end()]
            out.append(Issue("Collocations","major",f"Prefer '{re.sub(pat,repl,bad,flags=re.IGNORECASE)}' over '{bad}'.", m.span(), bad, re.sub(pat,repl,bad,flags=re.IGNORECASE), f"Example: We {re.sub(pat,repl,bad,flags=re.IGNORECASE)}."))
    return out

def _detect_collocations_ar(pe:str)->List[Issue]:
    out=[]; raw=pe or ""; raw_n=_norm_ar(raw)
    for prefer,bads in AR_COLLO.items():
        for bad in bads:
            i=raw_n.find(_norm_ar(bad))
            if i>=0: out.append(Issue("Collocations","major",f"الأفضل '{prefer}' بدل '{bad}'.",(i,i+len(bad)), bad, prefer, f"مثال: {prefer} فورًا."))
    for lemma,prep in AR_PREP.items():
        for m in re.finditer(rf"{lemma}\s+(?!{prep})\S+", raw):
            if prep not in m.group(0): out.append(Issue("Collocations","major",f"تستعمل '{lemma}' مع '{prep}'.", m.span(), raw[m.start():m.end()], f"{lemma} {prep}", f"مثال: {lemma} {prep} المشروع."))
    return out

def _detect_idioms(pe:str, direction:str)->List[Issue]:
    out=[]; bank = IDIOMS_AR2EN if direction=="AR->EN" else IDIOMS_EN2AR
    for lit,pref in bank.items():
        i=(pe or "").lower().find(lit.lower())
        if i>=0: out.append(Issue("Idioms","minor", ("Prefer" if direction=="AR->EN" else "جرّب")+f" '{pref}' بدل/over '{lit}'.", (i,i+len(lit)), lit, pref, "Use the idiomatic equivalent."))
    return out

# ---------- public API ----------
def analyze(src:str, pe:str, synonyms:Dict[str,str]|None=None, direction_hint:str|None=None):
    direction = direction_hint or _direction(pe)
    issues=[]
    issues += _detect_accuracy(src, pe)
    issues += _detect_fluency(pe)
    issues += _detect_terminology(pe, synonyms or {})
    issues += _detect_collocations_en(pe) if direction=="AR->EN" else _detect_collocations_ar(pe)
    issues += _detect_idioms(pe, "AR->EN" if direction=="AR->EN" else "EN->AR")
    return issues, direction

def render_highlights(text:str, issues:List[Issue])->str:
    COLORS={"Accuracy":"#c0392b","Fluency":"#f39c12","Terminology":"#8e44ad","Collocations":"#16a085","Idioms":"#2980b9","Formatting":"#7f8c8d"}
    out=text or ""; spans=[(i.span[0],i.span[1],i.cat) for i in issues if i.span]; spans.sort(key=lambda x:x[0], reverse=True)
    for s,e,cat in spans:
        s=max(0,min(s,len(out))); e=max(s,min(e,len(out)))
        color=COLORS.get(cat,"#555"); out=out[:s]+f'<mark style="background:{color}22;border-bottom:2px solid {color}">{out[s:e]}</mark>'+out[e:]
    return f'<div style="font-family: ui-sans-serif; line-height:1.75; font-size:1rem'>{out}</div>'

# --- replace the whole teacher_overview() with this ---
def teacher_overview(issues, *, lang="en", tone="supportive"):
    """
    Make a short teacher-style paragraph.
    lang: "en" or "ar"
    tone: "supportive" | "neutral" | "strict"
    """
    if not issues:
        return ("Great work—your translation is accurate and fluent. Keep it up!"
                if lang=="en" else "عمل رائع—ترجمتك دقيقة وسلسة. استمر!")

    # counts per category
    counts = {}
    for it in issues:
        counts[it.cat] = counts.get(it.cat, 0) + 1

    # priority list
    focus = []
    if counts.get("Accuracy"):     focus.append("accuracy" if lang=="en" else "الدقة")
    if counts.get("Collocations"): focus.append("collocations" if lang=="en" else "التراكيب الاصطلاحية")
    if counts.get("Terminology"):  focus.append("word choice/terminology" if lang=="en" else "الاختيار المصطلحي")
    if counts.get("Idioms"):       focus.append("idiomatic phrasing" if lang=="en" else "التعبير الاصطلاحي")
    if counts.get("Fluency"):      focus.append("punctuation/spacing" if lang=="en" else "علامات الترقيم والمسافات")

    # sentence banks by tone
    prefix = {
        "supportive": "You're close. " if lang=="en" else "أنت على الطريق الصحيح. ",
        "neutral":    "Main issues detected. " if lang=="en" else "تم رصد أبرز المشكلات. ",
        "strict":     "Revise carefully. " if lang=="en" else "راجع بعناية. "
    }[tone]

    # build the paragraph (2–4 short sentences)
    if lang == "en":
        main = "I noticed issues in " + ", ".join(f"{k} ({counts[k]})" for k in ["Accuracy","Collocations","Terminology","Idioms","Fluency","Formatting"] if counts.get(k)) + "."
        if focus:
            focus_line = "Focus first on " + ", ".join(focus[:2]) + ("." if len(focus)<=2 else ", then the rest.")
        else:
            focus_line = "Keep refining for naturalness and consistency."
        tip = "Use natural verb–noun pairs and check numbers vs. source." if counts.get("Collocations") or counts.get("Accuracy") else "Polish punctuation and spacing."
        return prefix + " ".join([main, focus_line, tip])
    else:
        # Arabic version
        main = "ظهرت مشكلات في " + "، ".join(f"{'الدقة' if k=='Accuracy' else 'التراكيب' if k=='Collocations' else 'المصطلحات' if k=='Terminology' else 'التعابير' if k=='Idioms' else 'السلاسة' if k=='Fluency' else 'التنسيق'} ({counts[k]})"
                                           for k in ["Accuracy","Collocations","Terminology","Idioms","Fluency","Formatting"] if counts.get(k)) + "."
        if focus:
            focus_line = "ابدأ بالتركيز على " + "، ".join(focus[:2]) + ("." if len(focus)<=2 else "، ثم أكمل البقية.")
        else:
            focus_line = "واصل التحسين لزيادة الطبيعية والاتساق."
        tip = "تحقّق من توافق الأرقام مع النص الأصلي واستخدم أفعالاً مع أسماء مناسبة." if counts.get("Collocations") or counts.get("Accuracy") else "لمّع الصياغة بعلامات الترقيم والمسافات."
        return prefix + " ".join([main, focus_line, tip])


def activities_from_issues(src:str, pe:str, issues:List[Issue]):
    acts=[]
    for it in issues:
        if it.span and it.prefer and it.found:
            acts.append({"type":"micro-rewrite","prompt":"Rewrite the highlighted part using the preferred form.","before":it.found,"target":it.prefer})
            if len(acts)>=2: break
    for it in issues:
        if it.cat in ("Collocations","Idioms") and it.prefer:
            if " " in it.prefer:
                first,rest=it.prefer.split(" ",1); cloze=f"{first} ___ {rest}"
            else:
                cloze=it.prefer[0]+"___"+it.prefer[1:]
            acts.append({"type":"cloze","prompt":"Fill the blank with the correct collocation/idiom.","text":cloze}); break
    for it in issues:
        if it.prefer and it.found:
            acts.append({"type":"mcq","question":"Choose the natural phrase:","options":[it.prefer,it.found],"answer":it.prefer}); break
    for it in issues:
        if it.cat=="Collocations" and it.prefer and any(p in it.prefer for p in ["عن","ب","على","ل"]):
            acts.append({"type":"governance","prompt":"Correct the preposition in the phrase:","phrase":it.found or "", "target":it.prefer}); break
    if not acts:
        acts=[{"type":"cloze","prompt":"Fill the blank:","text":"___ a decision"},
              {"type":"mcq","question":"Pick the correct collocation:","options":["make attention","pay attention"],"answer":"pay attention"},
              {"type":"governance","prompt":"Choose the right preposition:","phrase":"مسؤول على المشروع","target":"مسؤول عن المشروع"}]
    return acts
