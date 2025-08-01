# YouTube Music Metadata Extractor

A minimalist web application that extracts metadata from YouTube and YouTube Music videos and stores them in a local CSV file.

## Features

- 🎵 Extract metadata from YouTube/YouTube Music URLs
- 📊 Display song information including title, artist, year, album, and cover image
- 💾 Automatically save metadata to a local CSV file
- 📚 View your complete music library in a clean table format
- 📱 Responsive design that works on desktop and mobile
- 🎨 Clean, minimalist interface with modern styling

## Extracted Metadata

- **Song Title** - Cleaned title without year/album info
- **Artist** - Channel/artist name from YouTube
- **Producer** - (Currently empty, YouTube API doesn't provide this)
- **Year** - Extracted from title if available (e.g., "Song Name (2023)")
- **Album** - Extracted from title if available (e.g., "Song Name - Album Name")
- **Cover Image** - YouTube video thumbnail
- **YouTube URL** - Original video link
- **Date Added** - Timestamp when added to library

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

## Usage

1. **Add a Song:**
   - Paste a YouTube or YouTube Music URL in the input field
   - Click "Extract Metadata" or press Enter
   - The song information will be displayed and automatically saved to your library

2. **View Library:**
   - Click "View Library" to see all your saved songs
   - Browse through your collection with cover images and metadata
   - Export your library as a CSV file

3. **Navigation:**
   - Use "Add Another Song" to return to the input screen
   - Use "View Library" to see your complete collection

## Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## Files

- `app.py` - Main Flask application
- `templates/index.html` - Main input page
- `templates/library.html` - Library display page
- `music_data.csv` - Local storage file (created automatically)
- `requirements.txt` - Python dependencies

## Technical Details

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Data Storage:** Local CSV file
- **YouTube API:** Uses YouTube Data API v3 (with oEmbed fallback)
- **Styling:** Custom CSS with gradient backgrounds and modern design

## YouTube API Setup (Optional but Recommended)

For better metadata extraction, you can set up a YouTube Data API v3 key:

1. **Get a YouTube API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create credentials (API key)

2. **Set the API Key:**
   ```bash
   # Windows
   set YOUTUBE_API_KEY=your_api_key_here
   
   # macOS/Linux
   export YOUTUBE_API_KEY=your_api_key_here
   ```

3. **Benefits with API Key:**
   - More accurate artist/channel information
   - Better quality thumbnails (maxres, high quality)
   - Published date for more accurate year extraction
   - Higher rate limits
   - More reliable metadata extraction

**Note:** The app works without an API key using the oEmbed API as fallback, but you'll get better results with the official API.

## Notes

- The app uses YouTube Data API v3 with oEmbed API as fallback
- With an API key: Better metadata, higher quality thumbnails, published dates
- Without API key: Still works using oEmbed API (no authentication required)
- Producer information is not available through the YouTube API
- Year and album information is extracted from video titles and published dates
- All data is stored locally in `music_data.csv`
- The app is designed to be lightweight and easy to use

## Troubleshooting

- **"Could not extract metadata"** - Make sure the URL is a valid YouTube video
- **"Network error"** - Check your internet connection
- **Port already in use** - Change the port in `app.py` or stop other services using port 5000 