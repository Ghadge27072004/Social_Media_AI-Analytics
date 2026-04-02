# 🚀 Social Analytics Backend

AI-powered Social Media Analytics — FastAPI + MongoDB + Realtime Updater

---

## 📁 Project Structure

```
s/
├── main.py                  ← FastAPI app entry point
├── db.py                    ← MongoDB connection + collections
├── config.py                ← All settings via .env
├── run.py                   ← Start server
├── requirements.txt
├── .env.example             ← Copy → .env and fill keys
│
├── routes/
│   ├── youtube.py           ← /api/youtube/*
│   ├── reddit.py            ← /api/reddit/*
│   ├── dashboard.py         ← /api/dashboard/*
│   ├── instagram.py         ← /api/instagram/*
│   ├── twitter.py           ← /api/twitter/*
│   ├── pinterest.py         ← /api/pinterest/*
│   ├── ai_routes.py         ← /api/ai/*
│   └── realtime.py          ← /api/realtime/stream (SSE)
│
├── services/
│   ├── youtube_service.py   ← Real YouTube API calls
│   ├── reddit_service.py    ← Real Reddit API (praw)
│   ├── instagram_scraper.py ← Scraping + AI estimation
│   ├── twitter_scraper.py   ← snscrape + synthetic
│   ├── pinterest_scraper.py ← Scraping + trend analysis
│   └── seeder.py            ← Seeds initial DB data
│
├── ai_engine/
│   ├── sentiment.py         ← Positive / Negative / Neutral
│   ├── emotion.py           ← 8-class emotion detection
│   ├── toxicity.py          ← 6-category toxicity shield
│   ├── hinglish_nlp.py      ← Hindi + English NLP
│   ├── trend_forecasting.py ← Linear forecast + viral score
│   └── clustering.py        ← K-Means audience segments
│
├── realtime/
│   └── updater.py           ← APScheduler background jobs
│
└── models/
    └── user_model.py        ← Pydantic models
```

---

## ⚡ Quick Start

### Mac / Linux

```bash
cd s
bash setup.sh        # one-time setup
source venv/bin/activate
# Fill .env with your API keys
python run.py
```

### Windows

```cmd
cd s
setup.bat            # one-time setup
venv\Scripts\activate
# Fill .env with your API keys
python run.py
```

Open **http://localhost:8000/docs** — interactive API explorer.

---

## 🔑 API Keys You Need

| Key | Where to get | Required? |
|-----|-------------|-----------|
| `YOUTUBE_API_KEY` | [console.cloud.google.com](https://console.cloud.google.com) → Enable YouTube Data API v3 → Credentials | ✅ Yes |
| `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) → Create App → Script type | ✅ Yes |
| `MONGO_URI` | Local: `mongodb://localhost:27017` or [MongoDB Atlas](https://mongodb.com/atlas) free tier | ✅ Yes |

---

## 🌐 API Endpoints

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/summary` | All platforms combined stats |
| GET | `/api/dashboard/trending` | Top posts by engagement |
| GET | `/api/dashboard/platform/{name}` | Single platform live stats |
| GET | `/api/dashboard/recent-posts` | Recent posts (filterable) |

### YouTube (Real Data ✅)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/youtube/search?query=...` | Search videos |
| GET | `/api/youtube/trending?region=IN` | Trending in India |
| GET | `/api/youtube/stats/{video_id}` | Video statistics |

### Reddit (Real Data ✅)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reddit/posts?subreddit=india` | Subreddit posts |
| GET | `/api/reddit/search?query=...` | Search all of Reddit |
| GET | `/api/reddit/comments/{post_id}` | Post comments |

### Instagram (AI Insights ⚠️)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/instagram/profile?username=...` | Public profile data |
| GET | `/api/instagram/insights?username=...` | AI-based insights |

### Twitter (Public Analysis ⚠️)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/twitter/search?query=...` | Tweet search |
| GET | `/api/twitter/trends?region=India` | Trending topics |

### Pinterest (Trend Insights 🔥)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/pinterest/trends?keyword=...` | Keyword trends |
| GET | `/api/pinterest/boards?keyword=...` | Board analysis |

### AI Engine
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/sentiment` | Sentiment analysis |
| POST | `/api/ai/emotion` | 8-class emotion |
| POST | `/api/ai/toxicity` | Toxicity shield |
| POST | `/api/ai/hinglish` | Hinglish NLP |
| POST | `/api/ai/forecast` | Trend forecasting |
| POST | `/api/ai/viral-score` | Pre-publish viral score |
| POST | `/api/ai/cluster` | Audience clustering |
| POST | `/api/ai/analyze-full` | All models in one call |

### Realtime
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/realtime/stream` | SSE live stream (every 5s) |
| GET | `/api/realtime/snapshot` | One-shot stats snapshot |

---

## ⚡ Realtime System

Three background jobs run automatically:

| Job | Interval | What it does |
|-----|----------|-------------|
| Micro update | Every 5 sec | Increments followers, views, likes etc. |
| Engagement recalc | Every 30 sec | Tweaks engagement scores on recent posts |
| Macro update | Every 5 min | Refreshes real YouTube trending + Reddit posts |

Flutter connects to `/api/realtime/stream` using Server-Sent Events and updates the UI automatically.

---

## 🗄️ MongoDB Atlas (Cloud — Recommended)

1. Go to [mongodb.com/atlas](https://mongodb.com/atlas) → Create free account
2. Create cluster → M0 free tier
3. Database Access → Add user with read/write
4. Network Access → Add IP: `0.0.0.0/0`
5. Connect → Drivers → Copy connection string
6. Paste into `.env` as `MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/`

---

## 📱 Flutter Integration (Coming Next)

Flutter app connects to this backend via HTTP + SSE:

```dart
// Base URL
const String baseUrl = 'http://localhost:8000';

// Dashboard summary
final response = await http.get(Uri.parse('$baseUrl/api/dashboard/summary'));

// Realtime stream
final eventSource = EventSource('$baseUrl/api/realtime/stream');
```
