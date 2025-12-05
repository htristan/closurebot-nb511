#!/bin/bash
# Test script for NB511 closure bot

# Activate virtual environment
source venv/bin/activate

# Check if DISCORD_WEBHOOK is set
if [ -z "$DISCORD_WEBHOOK" ]; then
    echo "ERROR: DISCORD_WEBHOOK environment variable is not set"
    echo "Please set it with: export DISCORD_WEBHOOK='your_webhook_url'"
    exit 1
fi

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "ERROR: config.json not found"
    echo "Creating symlink from config_develop.json..."
    cp config_develop.json config.json
fi

echo "Running scrape.py..."
python scrape.py
