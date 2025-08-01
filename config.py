# YouTube API Configuration
# To get better metadata extraction, you can set up a YouTube Data API v3 key

# How to get a YouTube API key:
# 1. Go to https://console.cloud.google.com/
# 2. Create a new project or select an existing one
# 3. Enable the YouTube Data API v3
# 4. Create credentials (API key)
# 5. Set the API key as an environment variable: YOUTUBE_API_KEY=your_api_key_here

# The app will work without an API key (using oEmbed API as fallback),
# but with an API key you'll get:
# - More accurate artist/channel information
# - Better quality thumbnails
# - Published date for more accurate year extraction
# - Higher rate limits

import os

# YouTube API Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
YOUTUBE_API_BASE_URL = 'https://www.googleapis.com/youtube/v3'

# App Configuration
CSV_FILE = 'music_data.csv'
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000 