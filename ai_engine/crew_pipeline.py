# ai_engine/crew_pipeline.py
"""
CrewAI 4-Agent Social Media Analysis Pipeline
Agents:
  1. DataCollectorAgent   — gathers raw post data from platform
  2. SentimentAnalystAgent — runs sentiment + emotion + toxicity
  3. TrendStrategistAgent  — forecasts trends + viral potential
  4. ReportWriterAgent     — produces final human-readable insight report

Fallback: if crewai not installed, runs a lightweight sequential pipeline
using the existing ai_engine functions directly.
"""

from datetime import datetime
from typing import Optional, List
from collections import Counter
import re

# ── Internal AI Engine Imports ────────────────────────────────────────────────
from ai_engine.sentiment         import analyze_sentiment
from ai_engine.emotion           import detect_emotion
from ai_engine.toxicity          import detect_toxicity
from ai_engine.hinglish_nlp      import analyze_hinglish
from ai_engine.trend_forecasting import (
    forecast_viral_potential,
    forecast_trend,
    score_content,
)


# ── Lightweight Agent base (no crewai dependency needed) ─────────────────────

class _Agent:
    def __init__(self, name: str, role: str, goal: str):
        self.name = name
        self.role = role
        self.goal = goal

    def run(self, context: dict) -> dict:
        raise NotImplementedError


# ── Agent 1: Data Collector ───────────────────────────────────────────────────

class DataCollectorAgent(_Agent):
    def __init__(self):
        super().__init__(
            name="DataCollector",
            role="Social Media Data Harvester",
            goal="Collect and normalize raw content for analysis",
        )

    def run(self, context: dict) -> dict:
        """
        Accepts raw posts list OR a single text.
        Normalizes to a list of {text, platform, post_id} dicts.
        """
        posts = context.get("posts", [])
        text  = context.get("text", "")
        platform = context.get("platform", "unknown")

        if not posts and text:
            posts = [{"text": text, "platform": platform, "post_id": "single_0"}]

        normalized = []
        for i, p in enumerate(posts):
            if isinstance(p, str):
                p = {"text": p, "platform": platform, "post_id": f"post_{i}"}
            normalized.append({
                "text":      str(p.get("text", ""))[:512],
                "platform":  p.get("platform", platform),
                "post_id":   p.get("post_id", f"post_{i}"),
            })

        return {
            **context,
            "normalized_posts": normalized,
            "total_posts":      len(normalized),
            "agent_log":        context.get("agent_log", []) + [
                f"✅ DataCollector: {len(normalized)} posts collected & normalized"
            ],
        }


# ── Agent 2: Sentiment Analyst ────────────────────────────────────────────────

class SentimentAnalystAgent(_Agent):
    def __init__(self):
        super().__init__(
            name="SentimentAnalyst",
            role="NLP Sentiment & Emotion Expert",
            goal="Run sentiment, emotion, toxicity and Hinglish analysis on all posts",
        )

    def run(self, context: dict) -> dict:

        posts   = context.get("normalized_posts", [])
        results = []

        for post in posts:
            text = post["text"]
            try:
                sentiment = analyze_sentiment(text)
                emotion   = detect_emotion(text)
                toxicity  = detect_toxicity(text)
                hinglish  = analyze_hinglish(text)
            except Exception as e:
                sentiment = {"label": "neutral", "confidence": 0.5, "error": str(e)}
                emotion   = {"dominant_emotion": "neutral", "error": str(e)}
                toxicity  = {"is_toxic": False, "error": str(e)}
                hinglish  = {"is_hinglish": False, "error": str(e)}

            results.append({
                "post_id":   post["post_id"],
                "text":      text[:100],
                "platform":  post["platform"],
                "sentiment": sentiment,
                "emotion":   emotion,
                "toxicity":  toxicity,
                "hinglish":  hinglish,
            })

        # Aggregate summary
        sentiments   = [r["sentiment"].get("label", "neutral") for r in results]
        emotions     = [r["emotion"].get("dominant_emotion", "neutral") for r in results]
        toxic_count  = sum(1 for r in results if r["toxicity"].get("is_toxic", False))
        pos_count    = sentiments.count("positive")
        neg_count    = sentiments.count("negative")
        neu_count    = sentiments.count("neutral")

        top_emotion = Counter(emotions).most_common(1)[0][0] if emotions else "neutral"

        summary = {
            "total_posts":    len(results),
            "positive":       pos_count,
            "negative":       neg_count,
            "neutral":        neu_count,
            "toxic_posts":    toxic_count,
            "top_emotion":    top_emotion,
            "sentiment_ratio": {
                "positive_pct": round(pos_count / max(len(results), 1) * 100, 1),
                "negative_pct": round(neg_count / max(len(results), 1) * 100, 1),
                "neutral_pct":  round(neu_count / max(len(results), 1) * 100, 1),
            },
        }

        return {
            **context,
            "analysis_results":   results,
            "sentiment_summary":  summary,
            "agent_log":          context.get("agent_log", []) + [
                f"✅ SentimentAnalyst: {len(results)} posts analyzed — "
                f"{pos_count} positive, {neg_count} negative, {toxic_count} toxic"
            ],
        }


# ── Agent 3: Trend Strategist ─────────────────────────────────────────────────

class TrendStrategistAgent(_Agent):
    def __init__(self):
        super().__init__(
            name="TrendStrategist",
            role="Viral Content & Trend Forecasting Specialist",
            goal="Identify viral potential, forecast trends, and recommend content strategy",
        )

    def run(self, context: dict) -> dict:

        keyword  = context.get("keyword", context.get("text", "social media")[:50])
        platform = context.get("platform", "instagram")
        posts    = context.get("normalized_posts", [])

        # Viral score on first post or provided text
        sample_text = posts[0]["text"] if posts else context.get("text", keyword)
        try:
            viral    = forecast_viral_potential(sample_text, "")
            trend    = forecast_trend(keyword, forecast_days=7)
            content  = score_content(sample_text, "", platform, [])
        except Exception as e:
            viral   = {"viral_score": 50, "error": str(e)}
            trend   = {"forecast": [], "error": str(e)}
            content = {"overall_score": 50, "error": str(e)}

        # Extract top keywords from all posts (simple frequency)
        all_words = []
        for p in posts:
            words = re.findall(r"\b[a-zA-Z]{4,}\b", p["text"].lower())
            all_words.extend(words)

        stopwords = {"this", "that", "with", "from", "have", "will", "your",
                     "just", "been", "they", "were", "when", "what", "also"}
        top_keywords = [w for w, _ in Counter(all_words).most_common(20)
                        if w not in stopwords][:8]

        return {
            **context,
            "viral_analysis":  viral,
            "trend_forecast":  trend,
            "content_score":   content,
            "top_keywords":    top_keywords,
            "agent_log":       context.get("agent_log", []) + [
                f"✅ TrendStrategist: Viral score {viral.get('viral_score', '?')} | "
                f"Top keywords: {', '.join(top_keywords[:3])}"
            ],
        }


# ── Agent 4: Report Writer ────────────────────────────────────────────────────

class ReportWriterAgent(_Agent):
    def __init__(self):
        super().__init__(
            name="ReportWriter",
            role="Insight Report Generator",
            goal="Synthesize all agent outputs into a clear, actionable report",
        )

    def run(self, context: dict) -> dict:
        summary    = context.get("sentiment_summary", {})
        viral      = context.get("viral_analysis", {})
        trend      = context.get("trend_forecast", {})
        content_sc = context.get("content_score", {})
        keywords   = context.get("top_keywords", [])
        platform   = context.get("platform", "unknown")
        total      = summary.get("total_posts", 0)

        pos_pct    = summary.get("sentiment_ratio", {}).get("positive_pct", 0)
        neg_pct    = summary.get("sentiment_ratio", {}).get("negative_pct", 0)
        top_emo    = summary.get("top_emotion", "neutral")
        toxic      = summary.get("toxic_posts", 0)
        viral_sc   = viral.get("viral_score", 0)
        cont_sc    = content_sc.get("overall_score", 0)

        # Overall health score
        health_score = round(
            (pos_pct * 0.4) +
            (min(viral_sc, 100) * 0.3) +
            (min(cont_sc, 100) * 0.2) +
            (max(0, 100 - (toxic / max(total, 1)) * 100) * 0.1),
            1
        )

        # Generate recommendation
        if health_score >= 75:
            health_label = "Excellent 🚀"
            recommendation = (
                f"Your {platform} content is performing strongly. "
                f"Keep creating {', '.join(keywords[:3])} content. "
                f"Audience emotion is predominantly {top_emo} — maintain this tone."
            )
        elif health_score >= 50:
            health_label = "Good 👍"
            recommendation = (
                f"Decent performance on {platform}. "
                f"Reduce negative tone posts (currently {neg_pct}%). "
                f"Focus on viral triggers — try hooks related to: {', '.join(keywords[:3])}."
            )
        else:
            health_label = "Needs Attention ⚠️"
            recommendation = (
                f"Content health is low on {platform}. "
                f"{toxic} toxic posts detected — review & remove. "
                f"Shift tone towards positivity and use trending keywords: {', '.join(keywords[:3])}."
            )

        trend_direction = "📈 Upward" if trend.get("trend_direction") == "up" else \
                          "📉 Downward" if trend.get("trend_direction") == "down" else "➡️ Stable"

        report = {
            "platform":          platform,
            "total_posts_analyzed": total,
            "health_score":      health_score,
            "health_label":      health_label,
            "sentiment_summary": summary,
            "viral_score":       viral_sc,
            "content_score":     cont_sc,
            "trend_direction":   trend_direction,
            "trend_7_day":       trend.get("forecast_values", []),
            "top_keywords":      keywords,
            "top_emotion":       top_emo,
            "toxic_posts_found": toxic,
            "recommendation":    recommendation,
            "agent_pipeline":    context.get("agent_log", []),
            "generated_at":      datetime.utcnow().isoformat(),
        }

        return {
            **context,
            "final_report": report,
            "agent_log":    context.get("agent_log", []) + [
                f"✅ ReportWriter: Report generated — Health: {health_score} ({health_label})"
            ],
        }


# ── Main Pipeline Runner ──────────────────────────────────────────────────────

class CrewPipeline:
    """
    Runs all 4 agents in sequence.
    Usage:
        pipeline = CrewPipeline()
        result   = pipeline.run(text="...", platform="instagram")
        result   = pipeline.run(posts=[...], platform="youtube", keyword="AI")
    """

    def __init__(self):
        self.agents = [
            DataCollectorAgent(),
            SentimentAnalystAgent(),
            TrendStrategistAgent(),
            ReportWriterAgent(),
        ]

    def run(
        self,
        text:     Optional[str] = None,
        posts:    Optional[list] = None,
        platform: str = "instagram",
        keyword:  Optional[str] = None,
    ) -> dict:
        context = {
            "text":      text or "",
            "posts":     posts or [],
            "platform":  platform,
            "keyword":   keyword or text or "social media",
            "agent_log": [],
        }

        for agent in self.agents:
            try:
                context = agent.run(context)
            except Exception as e:
                context["agent_log"].append(f"❌ {agent.name} failed: {str(e)}")

        return context.get("final_report", {
            "error":      "Pipeline did not complete",
            "agent_log":  context.get("agent_log", []),
        })


# ── Singleton ─────────────────────────────────────────────────────────────────

_pipeline_instance = None

def get_pipeline() -> CrewPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = CrewPipeline()
    return _pipeline_instance