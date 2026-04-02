#!/bin/bash
# setup.sh — Run this ONCE to set up the full backend
set -e

echo "================================================"
echo "  Social Analytics Backend — Setup Script"
echo "================================================"

# 1. Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Upgrade pip
pip install --upgrade pip --quiet

# 3. Install dependencies
echo "📥 Installing dependencies (this takes ~2 min)..."
pip install -r requirements.txt --quiet

# 4. Copy .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  .env created from template — FILL IN YOUR API KEYS before running!"
else
    echo "✅  .env already exists"
fi

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "  Next steps:"
echo "  1. Open .env and add your API keys"
echo "  2. Make sure MongoDB is running"
echo "  3. Run: source venv/bin/activate"
echo "  4. Run: python run.py"
echo "  5. Open: http://localhost:8000/docs"
echo ""
