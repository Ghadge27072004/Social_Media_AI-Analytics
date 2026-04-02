# ai_engine/hinglish_nlp.py
"""
Hinglish / Hindi NLP module.
Handles code-switched text (Hindi + English mixed).
"""
import re
import random
from datetime import datetime

# Common Hinglish positive/negative markers
HINGLISH_POSITIVE = [
    "bahut accha", "zabardast", "mast", "ekdum sahi", "bindaas", "jhakaas",
    "superb", "shandar", "waah", "kamaal", "achi", "pyaara", "lajawaab",
    "solid", "dhamaal", "top class", "best hai", "sahi hai", "ekdum mast",
]
HINGLISH_NEGATIVE = [
    "bakwaas", "bekar", "ghatiya", "faltu", "bura", "ganda", "kharab",
    "worst hai", "achha nahi", "nahi pasand", "boring", "time waste",
    "dumb", "stupid", "bura laga",
]
HINGLISH_NEUTRAL = [
    "theek hai", "chalega", "dekhte hain", "pata nahi", "soch raha hoon",
    "maybe", "ho sakta hai", "lagta hai", "shayad",
]

HINDI_STOPWORDS = {
    "hai", "hain", "ka", "ki", "ke", "ko", "se", "mein", "par", "aur",
    "ya", "jo", "yeh", "woh", "kya", "kaise", "kab", "kyun", "nahi",
    "tha", "thi", "the", "ho", "hoga", "kar", "karo", "kiya",
}


def analyze_hinglish(text: str) -> dict:
    """
    Analyzes Hinglish text for sentiment, language mix ratio,
    and key phrase extraction.
    """
    text_lower = text.lower()
    words      = re.findall(r'\b\w+\b', text_lower)

    # Detect language mix
    hindi_words   = [w for w in words if w in HINDI_STOPWORDS or _is_devanagari(w)]
    english_words = [w for w in words if w.isascii() and w not in HINDI_STOPWORDS]
    total_words   = max(len(words), 1)

    hindi_ratio   = round(len(hindi_words)   / total_words, 3)
    english_ratio = round(len(english_words) / total_words, 3)
    is_hinglish   = 0.1 < hindi_ratio < 0.9

    # Sentiment from Hinglish keywords
    pos_hits = sum(1 for phrase in HINGLISH_POSITIVE if phrase in text_lower)
    neg_hits = sum(1 for phrase in HINGLISH_NEGATIVE if phrase in text_lower)
    neu_hits = sum(1 for phrase in HINGLISH_NEUTRAL  if phrase in text_lower)

    if pos_hits > neg_hits:
        sentiment = "positive"
        score     = round(min(pos_hits * 0.3 + 0.2 + random.uniform(0, 0.2), 1.0), 4)
    elif neg_hits > pos_hits:
        sentiment = "negative"
        score     = round(-min(neg_hits * 0.3 + 0.2 + random.uniform(0, 0.2), 1.0), 4)
    else:
        sentiment = "neutral"
        score     = round(random.uniform(-0.1, 0.1), 4)

    return {
        "text_sample":    text[:100],
        "is_hinglish":    is_hinglish,
        "language_mix": {
            "hindi_ratio":   hindi_ratio,
            "english_ratio": english_ratio,
            "script":        "devanagari" if _has_devanagari(text) else "roman_hinglish",
        },
        "sentiment":      sentiment,
        "sentiment_score": score,
        "detected_phrases": {
            "positive": [p for p in HINGLISH_POSITIVE if p in text_lower][:3],
            "negative": [p for p in HINGLISH_NEGATIVE if p in text_lower][:3],
        },
        "word_count":     len(words),
        "analyzed_at":    datetime.utcnow().isoformat(),
    }


def _has_devanagari(text: str) -> bool:
    return bool(re.search(r'[\u0900-\u097F]', text))


def _is_devanagari(word: str) -> bool:
    return bool(re.search(r'[\u0900-\u097F]', word))


def batch_analyze(texts: list) -> list:
    return [analyze_hinglish(t) for t in texts]
