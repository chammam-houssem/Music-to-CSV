from flask import Flask, render_template, request, jsonify, send_file
import csv
import os
import re
from datetime import datetime
import requests
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# Ensure the CSV file exists
CSV_FILE = 'music_data.csv'

# YouTube API Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')  # Set your API key as environment variable
YOUTUBE_API_BASE_URL = 'https://www.googleapis.com/youtube/v3'

def ensure_csv_exists():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Artist', 'Producer', 'Year', 'Album', 'Cover Image', 'YouTube URL', 'Date Added'])

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'm.youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    
    return None

def extract_playlist_id(url):
    """Extract playlist ID from various YouTube playlist URL formats"""
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'm.youtube.com']:
        if parsed_url.path == '/playlist':
            return parse_qs(parsed_url.query).get('list', [None])[0]
        elif parsed_url.path.startswith('/playlist/'):
            return parsed_url.path.split('/')[2]
    
    return None

def is_playlist_url(url):
    """Check if the URL is a playlist URL"""
    return 'playlist' in url or 'list=' in url

def extract_metadata_from_url(url):
    """Extract metadata from YouTube URL using YouTube Data API v3"""
    video_id = extract_video_id(url)
    if not video_id:
        return None
    
    # If no API key is provided, fall back to oEmbed API
    if not YOUTUBE_API_KEY:
        return extract_metadata_oembed(video_id, url)
    
    try:
        # Use YouTube Data API v3
        api_url = f"{YOUTUBE_API_BASE_URL}/videos"
        params = {
            'part': 'snippet,contentDetails',
            'id': video_id,
            'key': YOUTUBE_API_KEY
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('items'):
            return None
        
        video_data = data['items'][0]
        snippet = video_data['snippet']
        
        # Extract basic info
        title = snippet.get('title', 'Unknown Title')
        artist = snippet.get('channelTitle', 'Unknown Artist')
        published_at = snippet.get('publishedAt', '')
        
        # Get the highest quality thumbnail
        thumbnails = snippet.get('thumbnails', {})
        cover_image = ''
        if 'maxres' in thumbnails:
            cover_image = thumbnails['maxres']['url']
        elif 'high' in thumbnails:
            cover_image = thumbnails['high']['url']
        elif 'medium' in thumbnails:
            cover_image = thumbnails['medium']['url']
        elif 'default' in thumbnails:
            cover_image = thumbnails['default']['url']
        
        # Extract year from published date
        year = ''
        if published_at:
            try:
                year = datetime.fromisoformat(published_at.replace('Z', '+00:00')).year
            except:
                pass
        
        # Try to extract year from title (common pattern: "Song Name (Year)")
        if not year:
            year_match = re.search(r'\((\d{4})\)', title)
            year = year_match.group(1) if year_match else ''
        
        # Try to extract album info from title (common pattern: "Song Name - Album Name")
        album_match = re.search(r' - (.+?)(?:\s*\(|$)', title)
        album = album_match.group(1) if album_match else ''
        
        # Clean up title by removing year and album info
        clean_title = re.sub(r'\s*\([^)]*\)', '', title)
        clean_title = re.sub(r'\s*-\s*[^-]*$', '', clean_title)
        
        return {
            'title': clean_title.strip(),
            'artist': artist,
            'producer': '',  # YouTube API doesn't provide producer info
            'year': str(year) if year else '',
            'album': album,
            'cover_image': cover_image,
            'youtube_url': url
        }
        
    except Exception as e:
        print(f"Error with YouTube Data API: {e}")
        # Fall back to oEmbed API
        return extract_metadata_oembed(video_id, url)

def extract_metadata_oembed(video_id, url):
    """Fallback method using oEmbed API"""
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    
    try:
        response = requests.get(oembed_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract basic info
        title = data.get('title', 'Unknown Title')
        author = data.get('author_name', 'Unknown Artist')
        thumbnail = data.get('thumbnail_url', '')
        
        # Try to extract year from title (common pattern: "Song Name (Year)")
        year_match = re.search(r'\((\d{4})\)', title)
        year = year_match.group(1) if year_match else ''
        
        # Try to extract album info from title (common pattern: "Song Name - Album Name")
        album_match = re.search(r' - (.+?)(?:\s*\(|$)', title)
        album = album_match.group(1) if album_match else ''
        
        # Clean up title by removing year and album info
        clean_title = re.sub(r'\s*\([^)]*\)', '', title)
        clean_title = re.sub(r'\s*-\s*[^-]*$', '', clean_title)
        
        return {
            'title': clean_title.strip(),
            'artist': author,
            'producer': '',  # YouTube API doesn't provide producer info
            'year': year,
            'album': album,
            'cover_image': thumbnail,
            'youtube_url': url
        }
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None

def get_playlist_video_ids(playlist_id):
    """Get all video IDs from a playlist using YouTube Data API"""
    if not YOUTUBE_API_KEY:
        return None
    
    video_ids = []
    next_page_token = None
    
    try:
        while True:
            api_url = f"{YOUTUBE_API_BASE_URL}/playlistItems"
            params = {
                'part': 'contentDetails',
                'playlistId': playlist_id,
                'maxResults': 50,
                'key': YOUTUBE_API_KEY
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract video IDs
            for item in data.get('items', []):
                video_id = item['contentDetails'].get('videoId')
                if video_id:
                    video_ids.append(video_id)
            
            # Check for next page
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
                
    except Exception as e:
        print(f"Error getting playlist video IDs: {e}")
        return None
    
    return video_ids

def is_duplicate_song(youtube_url):
    """Check if a song already exists in the CSV"""
    try:
        data = read_csv_data()
        return any(song['YouTube URL'] == youtube_url for song in data)
    except:
        return False

def add_to_csv(metadata):
    """Add metadata to CSV file"""
    ensure_csv_exists()
    
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            metadata['title'],
            metadata['artist'],
            metadata['producer'],
            metadata['year'],
            metadata['album'],
            metadata['cover_image'],
            metadata['youtube_url'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ])

def read_csv_data():
    """Read all data from CSV file"""
    ensure_csv_exists()
    
    data = []
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_metadata():
    url = request.json.get('url', '').strip()
    song_data = request.json.get('song_data', None)
    
    if not url:
        return jsonify({'error': 'Please provide a YouTube URL'}), 400
    
    if song_data:
        # Use provided song data (from edit form)
        metadata = song_data
        add_to_csv(metadata)
        return jsonify(metadata)
    
    # Check if it's a playlist URL
    if is_playlist_url(url):
        return process_playlist(url)
    else:
        # Extract metadata from single video URL
        metadata = extract_metadata_from_url(url)
        
        if not metadata:
            return jsonify({'error': 'Could not extract metadata from this URL. Please check if it\'s a valid YouTube video.'}), 400
        
        # Add to CSV
        add_to_csv(metadata)
        
        return jsonify(metadata)

def process_playlist(url):
    """Process a YouTube playlist URL"""
    playlist_id = extract_playlist_id(url)
    
    if not playlist_id:
        return jsonify({'error': 'Could not extract playlist ID from this URL. Please check if it\'s a valid YouTube playlist.'}), 400
    
    if not YOUTUBE_API_KEY:
        return jsonify({'error': 'YouTube API key is required to process playlists. Please set the YOUTUBE_API_KEY environment variable.'}), 400
    
    # Get all video IDs from playlist
    video_ids = get_playlist_video_ids(playlist_id)
    
    if not video_ids:
        return jsonify({'error': 'Could not retrieve videos from this playlist. Please check if the playlist is public and accessible.'}), 400
    
    # Process each video
    processed_songs = []
    skipped_songs = []
    
    for video_id in video_ids:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Check for duplicates
        if is_duplicate_song(video_url):
            skipped_songs.append(video_id)
            continue
        
        # Extract metadata for this video
        metadata = extract_metadata_from_url(video_url)
        
        if metadata:
            add_to_csv(metadata)
            processed_songs.append(metadata)
        else:
            skipped_songs.append(video_id)
    
    return jsonify({
        'type': 'playlist',
        'processed_count': len(processed_songs),
        'skipped_count': len(skipped_songs),
        'total_count': len(video_ids),
        'songs': processed_songs,
        'skipped_ids': skipped_songs
    })

@app.route('/library')
def library():
    data = read_csv_data()
    
    # Calculate statistics
    unique_artists = len(set(song['Artist'] for song in data))
    songs_with_year = len([song for song in data if song['Year']])
    
    return render_template('library.html', songs=data, unique_artists=unique_artists, songs_with_year=songs_with_year)

@app.route('/music_data.csv')
def download_csv():
    return send_file(CSV_FILE, as_attachment=True, download_name='music_library.csv')

@app.route('/update_song', methods=['POST'])
def update_song():
    """Update a song in the CSV file"""
    try:
        data = request.json
        youtube_url = data.get('youtube_url', '')
        updated_data = data.get('song_data', {})
        
        if not youtube_url:
            return jsonify({'error': 'YouTube URL is required'}), 400
        
        # Read all data from CSV
        songs = read_csv_data()
        
        # Find and update the song
        for song in songs:
            if song['YouTube URL'] == youtube_url:
                song.update(updated_data)
                break
        
        # Write back to CSV
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Artist', 'Producer', 'Year', 'Album', 'Cover Image', 'YouTube URL', 'Date Added'])
            for song in songs:
                writer.writerow([
                    song['Title'],
                    song['Artist'],
                    song['Producer'],
                    song['Year'],
                    song['Album'],
                    song['Cover Image'],
                    song['YouTube URL'],
                    song['Date Added']
                ])
        
        return jsonify({'success': True, 'message': 'Song updated successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Error updating song: {str(e)}'}), 500

if __name__ == '__main__':
    ensure_csv_exists()
    app.run(debug=True, host='0.0.0.0', port=5000) 