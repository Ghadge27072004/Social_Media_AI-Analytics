# ai_engine/chatbot.py
"""
AI Chatbot — Social Media Analytics Assistant
- Understands platform analytics context (Instagram, YouTube, Pinterest, etc.)
- Remembers conversation history per session
- Uses rule-based + keyword intent detection (no extra LLM dependency)
- Integrates with existing ai_engine functions for live answers
- Supports Hinglish queries
"""

import random
import re
from datetime import datetime
from typing import Optional

# ── Internal AI Engine Imports ────────────────────────────────────────────────
from ai_engine.sentiment         import analyze_sentiment
from ai_engine.emotion           import detect_emotion
from ai_engine.toxicity          import detect_toxicity
from ai_engine.trend_forecasting import forecast_trend, forecast_viral_potential
from ai_engine.clustering        import best_time_to_post, cluster_audience


# ── Intent Detection ──────────────────────────────────────────────────────────

INTENT_PATTERNS = {
    "sentiment": [
        r"sentiment", r"feel(ing)?", r"positive|negative|neutral",
        r"tone", r"vibe", r"mood", r"how people feel", r"log kya soch",
    ],
    "emotion": [
        r"emotion", r"angry|happy|sad|fear|joy|disgust|surprise|trust",
        r"feeling", r"gussa|khushi|dukh", r"what emotion",
    ],
    "toxicity": [
        r"tox(ic|icity)", r"hate|hateful|harmful", r"bad comment",
        r"bura|galat|abusive", r"shield", r"filter",
    ],
    "viral": [
        r"viral", r"trend(ing)?", r"popular", r"reach", r"go viral",
        r"viral hoga", r"kitna viral", r"viral score",
    ],
    "forecast": [
        r"forecast", r"predict", r"future", r"next week", r"growth",
        r"badhega", r"agle", r"trend forecast",
    ],
    "audience": [
        r"audience", r"follower", r"segment", r"cluster", r"who follow",
        r"fake follower", r"real follower", r"kaun follow",
    ],
    "best_time": [
        r"best time", r"when (to )?post", r"kab post", r"timing",
        r"schedule", r"optimal time",
    ],
    "content_tips": [
        r"tip", r"advice", r"suggest", r"improve", r"better content",
        r"kya post karu", r"content idea", r"what (should i|to) post",
    ],
    "platform_info": [
        r"instagram|insta", r"youtube|yt", r"pinterest", r"twitter|x\.com",
        r"reddit", r"platform",
    ],
    "greeting": [
        r"^(hi|hello|hey|hii|helo|namaste|namaskar|yo|sup)\b",
        r"good (morning|afternoon|evening|night)",
        r"kya haal", r"kaise ho", r"what'?s up",
    ],
    "help": [
        r"\bhelp\b", r"what can you do", r"features", r"kya kar sakte",
        r"capabilities", r"commands",
    ],
    "thanks": [
        r"thank(s| you)?", r"shukriya", r"dhanyawad", r"tysm", r"ty\b",
    ],
    "analyze": [
        r"analyze|analyse", r"check this", r"analyze (this|my|the)",
        r"is this toxic", r"what sentiment", r"iska sentiment",
    ],
}


def detect_intent(text: str) -> str:
    text_lower = text.lower().strip()
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return intent
    return "general"


# ── Response Templates ────────────────────────────────────────────────────────

GREETINGS = [
    "Hey! 👋 Main hun Social Analytics AI — tumhara social media expert! Kya jaanna chahte ho?",
    "Hi there! 😊 Aaj kaunse platform ka analysis karna hai?",
    "Hello! 🚀 Social media insights chahiye? Sahi jagah aaye ho!",
    "Heyyy! Main tumhare posts analyze karne ke liye ready hun! Kya chahiye?",
]

HELP_RESPONSE = """Main ye sab kar sakta hun 🤖:

📊 **Sentiment Analysis** — batao koi text, main positive/negative/neutral bolunga
😮 **Emotion Detection** — anger, joy, fear, sadness... 8 emotions detect karta hun
🛡️ **Toxicity Check** — harmful ya abusive content identify karta hun
🔥 **Viral Score** — tumhara post viral hoga ya nahi estimate karta hun
📈 **Trend Forecast** — agle 7 din ka trend predict karta hun
👥 **Audience Insights** — followers ka segment, fake follower detection
⏰ **Best Time to Post** — platform ke hisaab se optimal posting time
💡 **Content Tips** — better engagement ke liye suggestions

Bas likho koi bhi query — main samjhunga! 😎"""

THANKS_RESPONSES = [
    "Anytime! 😊 Koi aur help chahiye?",
    "No problem yaar! 🙌 Aur kuch analyze karna ho toh batao!",
    "Always here for you! 🚀 Koi bhi social media question poocho!",
]

CONTENT_TIPS = {
    "instagram": [
        "📸 Reels ko 7–15 second mein hook daalna zaroori hai",
        "🕐 Instagram pe best time: Tuesday–Friday, 11am–1pm ya 7pm–9pm IST",
        "📝 Caption mein 3–5 relevant hashtags use karo (30 se kam)",
        "🎨 Consistent color palette se brand recall badhta hai",
        "💬 First comment mein hashtags dalo — cleaner look!",
    ],
    "youtube": [
        "🎬 First 30 seconds mein viewer ka attention pakdo — hook strong rakho",
        "📌 Thumbnail pe face + emotion + text — CTR badh jaata hai",
        "🕐 YouTube ke liye best: Friday–Sunday, 2pm–5pm IST",
        "📖 Description mein timestamps daalo — watch time badhta hai",
        "🔔 Subscribers ko notification bell ke baare mein remind karo",
    ],
    "pinterest": [
        "📌 Vertical images (2:3 ratio) Pinterest pe best perform karte hain",
        "🕐 Pinterest pe Saturday–Sunday evening sabse active time hai",
        "📝 Board descriptions mein keywords daalo — SEO ke liye important hai",
        "🎨 Bright, high-contrast images zyada saves laate hain",
        "🔗 Har pin ko apni website se link karo for traffic",
    ],
    "general": [
        "📊 Consistency > Viral posts — regular posting se growth steady rehta hai",
        "💬 Comments ka reply karo — engagement rate badhta hai",
        "🤝 Collaborations se new audience reach milti hai",
        "📈 Analytics weekly check karo aur low-performing content adjust karo",
        "🎯 Ek clear niche — zyada targeted audience, better engagement",
    ],
}


# ── Live Analysis Integration ─────────────────────────────────────────────────

def _quick_analyze(text: str) -> dict:
    """Run quick sentiment + emotion + toxicity on given text."""
    results = {}
    try:
        s = analyze_sentiment(text)
        results["sentiment"] = f"{s['label'].capitalize()} ({round(s['confidence']*100)}% confidence)"
    except Exception:
        results["sentiment"] = "Could not analyze"

    try:
        e = detect_emotion(text)
        emo  = e.get("dominant_emotion", "neutral")
        emoji = e.get("dominant_emoji", "😐")
        results["emotion"] = f"{emoji} {emo.capitalize()}"
    except Exception:
        results["emotion"] = "Could not analyze"

    try:
        t = detect_toxicity(text)
        if t.get("is_toxic"):
            results["toxicity"] = f"⚠️ Toxic detected (score: {t.get('overall_score', '?')})"
        else:
            results["toxicity"] = "✅ Clean content"
    except Exception:
        results["toxicity"] = "Could not analyze"

    return results


# ── Session Memory ────────────────────────────────────────────────────────────

class ChatSession:
    """Manages conversation history for a single user session."""

    def __init__(self, session_id: str):
        self.session_id   = session_id
        self.history      = []          # list of {role, content, timestamp}
        self.context      = {}          # platform, last_intent, etc.
        self.created_at   = datetime.utcnow().isoformat()
        self.message_count = 0

    def add_message(self, role: str, content: str):
        self.history.append({
            "role":      role,
            "content":   content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        if role == "user":
            self.message_count += 1

    def get_history(self, last_n: int = 10) -> list:
        return self.history[-last_n:]

    def to_dict(self) -> dict:
        return {
            "session_id":    self.session_id,
            "message_count": self.message_count,
            "history":       self.get_history(),
            "context":       self.context,
            "created_at":    self.created_at,
        }


# In-memory session store (resets on server restart — good for demo)
_sessions: dict[str, ChatSession] = {}


def get_or_create_session(session_id: str) -> ChatSession:
    if session_id not in _sessions:
        _sessions[session_id] = ChatSession(session_id)
    return _sessions[session_id]


def clear_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]


# ── Core Chat Function ────────────────────────────────────────────────────────

def chat(message: str, session_id: str = "default", platform: str = "general") -> dict:
    """
    Main chat function.
    Returns: {reply, intent, session_id, message_count, timestamp}
    """
    session = get_or_create_session(session_id)
    session.context["platform"] = platform
    session.add_message("user", message)

    intent  = detect_intent(message)
    session.context["last_intent"] = intent
    reply   = _generate_reply(message, intent, session, platform)

    session.add_message("assistant", reply)

    return {
        "reply":         reply,
        "intent":        intent,
        "session_id":    session_id,
        "message_count": session.message_count,
        "platform":      platform,
        "timestamp":     datetime.utcnow().isoformat(),
    }


def _generate_reply(message: str, intent: str, session: ChatSession, platform: str) -> str:
    msg_lower = message.lower()

    if intent == "greeting":
        return random.choice(GREETINGS)

    elif intent == "help":
        return HELP_RESPONSE

    elif intent == "thanks":
        return random.choice(THANKS_RESPONSES)

    elif intent == "analyze":
        # User wants to analyze some text — extract it
        text_to_analyze = message
        # Remove command words
        for kw in ["analyze this", "analyse this", "check this", "iska sentiment",
                   "is this toxic", "what sentiment", "analyze:", "analyse:"]:
            text_to_analyze = re.sub(kw, "", text_to_analyze, flags=re.IGNORECASE).strip()

        if len(text_to_analyze.strip()) < 3:
            return "Koi text do analyze karne ke liye! 😊 Example: 'analyze this: I love this product!'"

        results = _quick_analyze(text_to_analyze)
        return (
            f"📊 **Analysis Results:**\n\n"
            f"💬 Sentiment: {results['sentiment']}\n"
            f"😮 Emotion: {results['emotion']}\n"
            f"🛡️ Toxicity: {results['toxicity']}\n\n"
            f"_Text analyzed: \"{text_to_analyze[:80]}{'...' if len(text_to_analyze) > 80 else ''}\"_"
        )

    elif intent == "sentiment":
        # Check if they gave text to analyze
        if len(message) > 30:
            results = _quick_analyze(message)
            return f"Sentiment check: {results['sentiment']} | Emotion: {results['emotion']}"
        return (
            "Sentiment analysis ke liye text do! 📝\n"
            "Example: _'analyze this: This product is amazing!'_\n\n"
            "Main 3 categories detect karta hun: Positive 😊, Negative 😞, Neutral 😐"
        )

    elif intent == "emotion":
        if len(message) > 30:
            try:
                e      = detect_emotion(message)
                emo    = e.get("dominant_emotion", "neutral")
                emoji  = e.get("dominant_emoji", "😐")
                conf   = round(e.get("confidence", 0) * 100)
                return f"{emoji} Dominant emotion: **{emo}** ({conf}% confidence)\n\nMain 8 emotions detect karta hun: joy, sadness, anger, fear, surprise, disgust, trust, neutral"
            except Exception:
                pass
        return "8-class emotion detection available hai! Joy 😄, Anger 😡, Sadness 😢, Fear 😨, Surprise 😮, Disgust 🤢, Trust 🤝, Neutral 😐 — koi text do!"

    elif intent == "toxicity":
        if len(message) > 20:
            try:
                t = detect_toxicity(message)
                if t.get("is_toxic"):
                    score = t.get("overall_score", 0)
                    return f"⚠️ Toxic content detected! Score: {score}\n\nCategories: {', '.join([k for k, v in t.get('categories', {}).items() if v > 0.5])}"
                return "✅ Content clean hai — koi toxicity nahi mili!"
            except Exception:
                pass
        return "Toxicity Shield active hai! 🛡️ Koi comment ya post do — main check karunga ki harmful hai ya nahi."

    elif intent == "viral":
        try:
            v     = forecast_viral_potential(message, "")
            score = v.get("viral_score", 50)
            label = v.get("viral_label", "")
            tips  = v.get("tips", [])
            tip   = tips[0] if tips else "Strong hook use karo!"
            return (
                f"🔥 **Viral Score: {score}/100** {label}\n\n"
                f"💡 Tip: {tip}\n\n"
                f"_Score 70+ = high viral potential!_"
            )
        except Exception:
            pass
        return "Viral score check karne ke liye apna post title ya caption do! 🔥"

    elif intent == "forecast":
        try:
            keyword = re.sub(r"(forecast|predict|future|trend|badhega|agle)", "", msg_lower).strip()
            keyword = keyword if len(keyword) > 3 else "social media"
            t       = forecast_trend(keyword, forecast_days=7)
            direction = t.get("trend_direction", "stable")
            peak_day  = t.get("peak_day", "Day 4")
            return (
                f"📈 **7-Day Trend Forecast for '{keyword}':**\n\n"
                f"Direction: {'📈 Growing' if direction == 'up' else '📉 Declining' if direction == 'down' else '➡️ Stable'}\n"
                f"Peak expected: {peak_day}\n\n"
                f"_Forecast updates daily based on platform data!_"
            )
        except Exception:
            pass
        return "Trend forecast ke liye keyword do! Example: 'forecast AI content' 📈"

    elif intent == "best_time":
        plat = platform if platform != "general" else "instagram"
        for p in ["instagram", "youtube", "pinterest", "twitter", "reddit"]:
            if p in msg_lower:
                plat = p
                break
        try:
            t = best_time_to_post(plat)
            times = ", ".join(t.get("best_times", [])[:3])
            days  = ", ".join(t.get("best_days", [])[:3])
            return (
                f"⏰ **Best Time to Post on {plat.capitalize()}:**\n\n"
                f"🕐 Times: {times} IST\n"
                f"📅 Days: {days}\n"
                f"🏆 Peak day: {t.get('peak_day', 'Wednesday')}\n\n"
                f"💡 {t.get('insight', '')}"
            )
        except Exception:
            pass
        return "Best posting times jaanne ke liye platform bolo! (instagram/youtube/pinterest) ⏰"

    elif intent == "audience":
        try:
            c = cluster_audience(10000, 4)
            dominant = c.get("dominant_segment", "Power Engagers")
            return (
                f"👥 **Audience Intelligence:**\n\n"
                f"Dominant segment: **{dominant}** {c.get('dominant_emoji', '🔥')}\n"
                f"Best post time: {c.get('best_post_time', '18:00–23:00')}\n"
                f"Best days: {', '.join(c.get('best_post_days', []))}\n\n"
                f"📊 {c.get('recommendation', '')}"
            )
        except Exception:
            pass
        return "Audience segmentation available hai! 5 types: Power Engagers 🔥, Silent Watchers 👀, Trend Surfers 🌊, Brand Advocates 💎, Casual Scrollers 📱"

    elif intent == "content_tips":
        plat = platform if platform != "general" else "general"
        for p in ["instagram", "youtube", "pinterest"]:
            if p in msg_lower:
                plat = p
                break
        tips_list = CONTENT_TIPS.get(plat, CONTENT_TIPS["general"])
        tips      = random.sample(tips_list, min(3, len(tips_list)))
        return f"💡 **Content Tips for {plat.capitalize()}:**\n\n" + "\n".join(tips)

    elif intent == "platform_info":
        for p in ["instagram", "youtube", "pinterest", "twitter", "reddit"]:
            if p in msg_lower:
                session.context["platform"] = p
                tips = CONTENT_TIPS.get(p, CONTENT_TIPS["general"])
                return f"📱 **{p.capitalize()} ke liye tips:**\n\n" + "\n".join(tips[:3])

    # General fallback
    fallbacks = [
        "Hmm, samja nahi 😅 Try: 'analyze this: [your text]' ya 'best time instagram'",
        "Main social media analytics mein expert hun! Kuch specific poocho 😊",
        "Interesting! Kya tum apna koi post analyze karwana chahte ho? Bas text paste karo!",
        "Mujhe thoda aur context do! Platform kaunsa hai — Instagram, YouTube ya Pinterest? 🤔",
    ]
    return random.choice(fallbacks)