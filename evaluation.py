import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import Levenshtein as lev

# Make sure NLTK tokenizer data is ready
nltk.download('punkt', quiet=True)

def evaluate_translation(hypothesis, reference):
    scores = {}
    ref_tokens = reference.split()
    hyp_tokens = hypothesis.split()

    # BLEU
    smoothie = SmoothingFunction().method4
    bleu = sentence_bleu([ref_tokens], hyp_tokens, smoothing_function=smoothie)
    scores["BLEU"] = round(bleu, 4)

    # Edit Distance
    edit_dist = lev.distance(reference, hypothesis)
    scores["Edit Distance"] = edit_dist
    scores["WER"] = round(edit_dist / max(1, len(reference.split())), 4)

    return scores
