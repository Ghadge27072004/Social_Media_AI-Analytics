# ai_engine/emotion.py
"""
8-class emotion detection.
Uses keyword heuristics + randomized confidence for demo.
Swap inner logic with a HuggingFace model for production.
"""
import re
import random
from datetime import datetime

EMOTIONS = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation"]

KEYWORD_MAP = {
    "joy":          ["happy", "love", "great", "awesome", "amazing", "excellent", "wonderful", "fantastic", "🔥", "❤️", "😍"],
    "sadness":      ["sad", "miss", "cry", "depressed", "lonely", "heartbroken", "loss", "grief", "😢", "💔"],
    "anger":        ["angry", "hate", "furious", "worst", "terrible", "awful", "stupid", "idiot", "😡", "🤬"],
    "fear":         ["scared", "afraid", "worried", "anxious", "nervous", "terrified", "panic", "😨", "😱"],
    "surprise":     ["wow", "omg", "unexpected", "shocked", "unbelievable", "whoa", "wait", "😮", "😲"],
    "disgust":      ["disgusting", "gross", "eww", "horrible", "nauseating", "vile", "🤮", "😖"],
    "trust":        ["trust", "reliable", "honest", "safe", "secure", "believe", "confident", "👍", "✅"],
    "anticipation": ["excited", "can't wait", "looking forward", "soon", "upcoming", "future", "🚀", "⏳"],
}


def detect_emotion(text: str) -> dict:
    text_lower = text.lower()
    scores = {emotion: 0.0 for emotion in EMOTIONS}

    for emotion, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                scores[emotion] += 1.0

    # Normalize
    total = sum(scores.values())
    if total == 0:
        # No keywords found — assign random distribution
        for e in EMOTIONS:
            scores[e] = random.uniform(0.02, 0.25)
        total = sum(scores.values())

    normalized = {e: round(v / total, 4) for e, v in scores.items()}
    dominant   = max(normalized, key=normalized.get)

    return {
        "dominant_emotion": dominant,
        "confidence":       normalized[dominant],
        "all_scores":       normalized,
        "analyzed_at":      datetime.utcnow().isoformat(),
    }


def batch_detect(texts: list) -> list:
    return [{"text": t[:100], **detect_emotion(t)} for t in texts]
