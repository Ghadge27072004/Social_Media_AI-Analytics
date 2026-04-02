# ai_engine/crisis_alert.py
"""
Crisis Alert System — Social Media Brand Protection
Detects and alerts on:
  - Sudden spike in negative sentiment
  - Viral toxic/hate content
  - Coordinated attack patterns
  - Reputation threats
  - Mental health crisis signals in comments

Alert levels:
  LEVEL 1 🟡 WATCH   — minor uptick, keep monitoring
  LEVEL 2 🟠 WARNING — moderate threat, action recommended
  LEVEL 3 🔴 CRISIS  — severe threat, immediate action needed
  LEVEL 4 🆘 EMERGENCY — extreme — potential brand/safety emergency
"""

import random
import re
from datetime import datetime
from typing import Optional

# ── Internal AI Engine Imports ────────────────────────────────────────────────
from ai_engine.sentiment import analyze_sentiment
from ai_engine.toxicity  import detect_toxicity


# ── Crisis Keywords & Patterns ────────────────────────────────────────────────

CRISIS_KEYWORDS = {
    "boycott":       {"weight": 8,  "category": "brand_attack",   "emoji": "🚫"},
    "cancel":        {"weight": 7,  "category": "brand_attack",   "emoji": "❌"},
    "scam":          {"weight": 9,  "category": "fraud_claim",    "emoji": "🚨"},
    "fraud":         {"weight": 9,  "category": "fraud_claim",    "emoji": "🚨"},
    "fake":          {"weight": 5,  "category": "misinformation", "emoji": "⚠️"},
    "lie":           {"weight": 6,  "category": "misinformation", "emoji": "⚠️"},
    "cheat":         {"weight": 7,  "category": "fraud_claim",    "emoji": "🚨"},
    "lawsuit":       {"weight": 9,  "category": "legal_threat",   "emoji": "⚖️"},
    "sue":           {"weight": 8,  "category": "legal_threat",   "emoji": "⚖️"},
    "hack":          {"weight": 8,  "category": "security",       "emoji": "💻"},
    "breach":        {"weight": 9,  "category": "security",       "emoji": "💻"},
    "exposed":       {"weight": 7,  "category": "reputation",     "emoji": "📢"},
    "viral hate":    {"weight": 10, "category": "hate_campaign",  "emoji": "🔥"},
    "hate campaign": {"weight": 10, "category": "hate_campaign",  "emoji": "🔥"},
    "racist":        {"weight": 9,  "category": "hate_speech",    "emoji": "🚨"},
    "harassment":    {"weight": 8,  "category": "harassment",     "emoji": "🚨"},
    "death threat":  {"weight": 10, "category": "safety",         "emoji": "🆘"},
    "kill":          {"weight": 6,  "category": "safety",         "emoji": "🆘"},
    "suicide":       {"weight": 10, "category": "mental_health",  "emoji": "🆘"},
    "self harm":     {"weight": 10, "category": "mental_health",  "emoji": "🆘"},
    "going to hurt": {"weight": 10, "category": "safety",         "emoji": "🆘"},
}

MENTAL_HEALTH_PATTERNS = [
    r"want(ing)? to (die|end it|kill myself)",
    r"no reason to live",
    r"can'?t (take|do) (this|it) anymore",
    r"ending (my|this) life",
    r"suicid(e|al)",
    r"self.?harm",
    r"cut(ting)? (myself|me)",
    r"i'?m (so|too) tired of (living|life|everything)",
]

ATTACK_PATTERNS = [
    r"everyone (report|block|cancel) (this|them|their)",
    r"(spread|share) (the word|this everywhere)",
    r"let('?s| us) (take (them|this) down|expose)",
    r"coordinated (attack|report|spam)",
    r"(mass )?report (this|them|their account)",
]


# ── Alert Level Thresholds ────────────────────────────────────────────────────

def _compute_alert_level(score: float, categories: set) -> tuple:
    """Returns (level_int, level_label, color, emoji)"""
    has_emergency = any(c in categories for c in ["safety", "mental_health"])
    has_critical  = any(c in categories for c in ["hate_campaign", "fraud_claim", "legal_threat"])

    if has_emergency or score >= 85:
        return 4, "EMERGENCY", "#dc2626", "🆘"
    elif has_critical or score >= 65:
        return 3, "CRISIS",    "#ea580c", "🔴"
    elif score >= 40:
        return 2, "WARNING",   "#d97706", "🟠"
    elif score >= 15:
        return 1, "WATCH",     "#ca8a04", "🟡"
    else:
        return 0, "SAFE",      "#16a34a", "✅"


def _recommended_actions(level: int, categories: set) -> list:
    base_actions = {
        0: ["Continue regular monitoring", "No immediate action needed"],
        1: [
            "Monitor mentions more frequently (every 15 min)",
            "Review flagged posts manually",
            "Prepare response templates",
        ],
        2: [
            "🔔 Alert your social media team immediately",
            "Pause scheduled content temporarily",
            "Draft a public response / statement",
            "Increase monitoring frequency to real-time",
            "Document all flagged content for records",
        ],
        3: [
            "🚨 Activate crisis communication protocol NOW",
            "Stop ALL scheduled posts immediately",
            "Escalate to management / PR team",
            "Issue public statement within 2 hours",
            "Engage with top comments proactively",
            "Consider temporarily limiting comments",
            "Contact legal team if fraud/legal threat detected",
        ],
        4: [
            "🆘 IMMEDIATE ESCALATION REQUIRED",
            "Contact platform support immediately (safety issue)",
            "Activate emergency PR response",
            "If mental health crisis: report content to platform",
            "Loop in legal + executive team",
            "Prepare holding statement for media",
            "Document everything — screenshots + timestamps",
        ],
    }
    actions = base_actions.get(level, [])

    # Category-specific additions
    if "mental_health" in categories:
        actions.insert(0, "🆘 Report mental health content to platform safety team FIRST")
    if "legal_threat" in categories:
        actions.append("⚖️ Forward to legal team for review")
    if "security" in categories:
        actions.append("🔒 Check account security + enable 2FA immediately")
    if "hate_campaign" in categories:
        actions.append("📢 Document coordinated attack evidence")

    return actions


# ── Main Analysis Functions ───────────────────────────────────────────────────

def analyze_crisis(
    text: str,
    context: Optional[dict] = None,
) -> dict:
    """
    Analyze a single text for crisis signals.
    Returns full crisis assessment with level, categories, actions.
    """
    text_lower = text.lower()
    context    = context or {}

    crisis_score    = 0.0
    flagged_keywords = []
    flagged_categories = set()

    # ── 1. Keyword scan ───────────────────────────────────────────────────────
    for keyword, meta in CRISIS_KEYWORDS.items():
        if keyword in text_lower:
            crisis_score += meta["weight"]
            flagged_keywords.append({
                "keyword":  keyword,
                "category": meta["category"],
                "emoji":    meta["emoji"],
                "weight":   meta["weight"],
            })
            flagged_categories.add(meta["category"])

    # ── 2. Mental health pattern check ───────────────────────────────────────
    mental_health_detected = False
    for pattern in MENTAL_HEALTH_PATTERNS:
        if re.search(pattern, text_lower):
            crisis_score += 20
            flagged_categories.add("mental_health")
            mental_health_detected = True
            break

    # ── 3. Coordinated attack pattern ─────────────────────────────────────────
    attack_detected = False
    for pattern in ATTACK_PATTERNS:
        if re.search(pattern, text_lower):
            crisis_score += 15
            flagged_categories.add("coordinated_attack")
            attack_detected = True
            break

    # ── 4. Sentiment integration ──────────────────────────────────────────────
    sentiment_label     = "neutral"
    sentiment_score_neg = 0.0
    try:
        s = analyze_sentiment(text)
        sentiment_label     = s.get("label", "neutral")
        # Extract negative score if present or use polarity
        if sentiment_label == "negative":
            sentiment_score_neg = abs(s.get("score", 0))
            crisis_score += sentiment_score_neg * 10
    except Exception:
        pass

    # ── 5. Toxicity integration ───────────────────────────────────────────────
    toxicity_score = 0.0
    is_toxic       = False
    try:
        t              = detect_toxicity(text)
        is_toxic       = t.get("is_toxic", False)
        toxicity_score = t.get("overall_score", 0)
        if is_toxic:
            crisis_score  += toxicity_score * 15
            flagged_categories.add("toxic_content")
    except Exception:
        pass

    # ── 6. Normalize score to 0–100 ───────────────────────────────────────────
    crisis_score = min(100, round(crisis_score, 1))

    # ── 7. Compute alert level ─────────────────────────────────────────────────
    level, label, color, level_emoji = _compute_alert_level(crisis_score, flagged_categories)

    # ── 8. Actions ────────────────────────────────────────────────────────────
    actions = _recommended_actions(level, flagged_categories)

    return {
        "text_preview":          text[:150] + ("..." if len(text) > 150 else ""),
        "crisis_score":          crisis_score,
        "alert_level":           level,
        "alert_label":           label,
        "alert_emoji":           level_emoji,
        "alert_color":           color,
        "categories_detected":   list(flagged_categories),
        "flagged_keywords":      flagged_keywords,
        "mental_health_signal":  mental_health_detected,
        "coordinated_attack":    attack_detected,
        "sentiment":             sentiment_label,
        "negative_sentiment":    round(sentiment_score_neg, 3),
        "toxicity_detected":     is_toxic,
        "toxicity_score":        round(toxicity_score, 3),
        "recommended_actions":   actions,
        "requires_immediate_action": level >= 3,
        "analyzed_at":           datetime.utcnow().isoformat(),
    }


def batch_crisis_scan(
    posts: list,
    threshold_level: int = 1,
) -> dict:
    """
    Scan multiple posts for crisis signals.
    Returns aggregate summary + list of flagged posts above threshold.

    posts: list of str or dict with 'text' key
    threshold_level: only include posts with alert_level >= this
    """
    results     = []
    flagged     = []
    max_level   = 0
    total_score = 0.0
    all_categories = set()

    for i, post in enumerate(posts):
        text = post if isinstance(post, str) else post.get("text", "")
        if not text:
            continue

        analysis = analyze_crisis(text)
        analysis["post_index"] = i
        results.append(analysis)

        total_score   += analysis["crisis_score"]
        all_categories |= set(analysis["categories_detected"])

        if analysis["alert_level"] > max_level:
            max_level = analysis["alert_level"]

        if analysis["alert_level"] >= threshold_level:
            flagged.append(analysis)

    avg_score = round(total_score / max(len(results), 1), 1)

    # Sort flagged by score descending
    flagged.sort(key=lambda x: x["crisis_score"], reverse=True)

    overall_level, overall_label, overall_color, overall_emoji = \
        _compute_alert_level(avg_score * 1.2 if max_level >= 3 else avg_score, all_categories)

    return {
        "total_posts_scanned":   len(results),
        "flagged_posts_count":   len(flagged),
        "average_crisis_score":  avg_score,
        "max_crisis_score":      max(r["crisis_score"] for r in results) if results else 0,
        "overall_alert_level":   overall_level,
        "overall_alert_label":   overall_label,
        "overall_alert_color":   overall_color,
        "overall_alert_emoji":   overall_emoji,
        "categories_detected":   list(all_categories),
        "mental_health_signals": sum(1 for r in results if r["mental_health_signal"]),
        "toxic_posts":           sum(1 for r in results if r["toxicity_detected"]),
        "flagged_posts":         flagged[:10],    # top 10 worst
        "recommended_actions":   _recommended_actions(overall_level, all_categories),
        "requires_immediate_action": overall_level >= 3,
        "scanned_at":            datetime.utcnow().isoformat(),
    }


def get_crisis_history(db_alerts_collection=None, limit: int = 20) -> list:
    """
    Returns recent crisis alerts from MongoDB alerts collection.
    Pass db.alerts_collection if you want DB history.
    Falls back to empty list.
    """
    if db_alerts_collection is None:
        return []
    try:
        return []  # Handled async in route
    except Exception:
        return []


async def save_crisis_alert(alert: dict, db_alerts_collection) -> str:
    """Save a crisis alert to MongoDB."""
    try:
        result = await db_alerts_collection.insert_one({
            **alert,
            "saved_at": datetime.utcnow().isoformat(),
        })
        return str(result.inserted_id)
    except Exception as e:
        return f"error: {str(e)}"