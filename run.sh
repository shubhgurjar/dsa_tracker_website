#!/usr/bin/env bash
# Quick Start Script for Minimal DSA Tracker
cd "$(dirname "$0")"

# Activate virtualenv if present
if [ -d "venv" ]; then
    source venv/bin/activate
fi

export PYTHONPATH=.
echo "🚀 Starting Minimal DSA Tracker on http://127.0.0.1:8000"
echo "🔑 Default Unlock PIN: 1234 (changeable in Profile & Settings)"
exec python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
