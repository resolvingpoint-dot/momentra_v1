#!/bin/bash
set -e

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3.14 -m venv .venv
fi

# Install requirements
echo "Installing dependencies..."
.venv/bin/pip install -r requirements.txt

echo "Done! Start the server with:"
echo "  .venv/bin/python3.14 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"