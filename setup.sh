#!/bin/bash

# Instant Scout App - Setup Script
# This script sets up the environment and runs the AI-powered MLB scouting report generator

# Set Google API Key for Gemini AI
# Get your key from: https://aistudio.google.com/app/apikey
# NOTE: Keep this key secure and never commit it to version control
export GOOGLE_API_KEY='AIzaSyAs74_rqyxWOnIKTu5jt6D92uNqigEVjC8'

# Run the main Python script
# The script will:
# 1. Fetch the last 100 plate appearances for a player (using pybaseball)
# 2. Generate an AI-powered scouting report using Gemini AI
# 3. Save and display the report
python3 AI-Scout.py

# chmod +x setup.sh
# ./setup.sh
