# modules/evaluation.py
from nltk.translate.bleu_score import sentence_bleu
from sacrebleu import corpus_chrf
try:
    from bert_score import score as bert_score
except ModuleNotFoundError:
    bert_score = None

def bleu_metric(reference, candidate):
    return sentence_bleu([reference.split()], candidate.split())

def chrf_metric(reference, candidate):
    return corpus_chrf([candidate], [[reference]]).score

def bert_metric(reference, candidate):
    if not bert_score:
        return None
    P, R, F1 = bert_score([candidate], [reference], lang="en")
    return float(F1[0])
