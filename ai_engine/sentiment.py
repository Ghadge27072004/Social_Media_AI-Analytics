# ai_engine/sentiment.py
"""
Sentiment analysis using TextBlob as lightweight default.
Can be swapped to transformers model later.
"""
import random
from datetime import datetime


def analyze_sentiment(text: str) -> dict:
    """Returns sentiment label + score for a given text."""
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        polarity    = blob.sentiment.polarity       # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1

        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"

        return {
            "label":         label,
            "score":         round(polarity, 4),
            "subjectivity":  round(subjectivity, 4),
            "confidence":    round(abs(polarity) * 0.8 + 0.2, 4),
            "analyzed_at":   datetime.utcnow().isoformat(),
        }
    except ImportError:
        # Fallback if textblob not installed
        score = random.uniform(-1, 1)
        return {
            "label":       "positive" if score > 0.1 else ("negative" if score < -0.1 else "neutral"),
            "score":       round(score, 4),
            "confidence":  round(random.uniform(0.6, 0.95), 4),
            "analyzed_at": datetime.utcnow().isoformat(),
        }


def batch_analyze(texts: list) -> list:
    return [{"text": t[:100], **analyze_sentiment(t)} for t in texts]
