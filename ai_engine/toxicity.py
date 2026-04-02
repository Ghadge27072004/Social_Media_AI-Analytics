# ai_engine/toxicity.py
"""
6-category toxicity detection.
Categories: toxic, severe_toxic, obscene, threat, insult, identity_hate
Uses keyword matching. Upgrade to Detoxify/transformers for production.
"""
import re
import random
from datetime import datetime

TOXIC_KEYWORDS = {
    "toxic":         ["hate", "kill", "destroy", "terrible", "worst", "stupid"],
    "severe_toxic":  ["die", "murder", "violent", "extreme harm"],
    "obscene":       ["explicit words"],  # sanitized in code
    "threat":        ["i will", "you'll regret", "watch out", "threat", "harm you"],
    "insult":        ["idiot", "fool", "moron", "loser", "dumb", "ugly"],
    "identity_hate": ["racist", "sexist", "discriminate", "bigot"],
}


def detect_toxicity(text: str) -> dict:
    text_lower = text.lower()
    scores = {}

    for category, keywords in TOXIC_KEYWORDS.items():
        hit_count = sum(1 for kw in keywords if kw in text_lower)
        base_score = min(hit_count * 0.3 + random.uniform(0.0, 0.1), 1.0)
        scores[category] = round(base_score, 4)

    overall_toxic   = max(scores.values())
    is_toxic        = overall_toxic > 0.5
    toxicity_level  = (
        "🔴 High"   if overall_toxic > 0.7 else
        "🟡 Medium" if overall_toxic > 0.4 else
        "🟢 Low"
    )

    return {
        "is_toxic":      is_toxic,
        "toxicity_level": toxicity_level,
        "overall_score": round(overall_toxic, 4),
        "categories":    scores,
        "recommendation": "Block content" if overall_toxic > 0.7 else (
                          "Review content" if overall_toxic > 0.4 else "Safe to publish"
        ),
        "analyzed_at":   datetime.utcnow().isoformat(),
    }


def batch_detect(texts: list) -> list:
    return [{"text": t[:100], **detect_toxicity(t)} for t in texts]
