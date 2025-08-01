from flask import Flask, render_template, request, jsonify, send_file
import csv
import os
import re
from datetime import datetime
import yt_dlp
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# Ensure the CSV file exists
CSV_FILE = 'music_data.csv'

def ensure_csv_exists():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Artist', 'Producer', 'Year', 'Album', 'Cover Image', 'YouTube URL', 'Date Added'])

def is_playlist_url(url):
    """Check if the URL is a playlist URL"""
    return 'playlist' in url or 'list=' in url

def parse_yt_dlp_info(info):
    """Parse the info dictionary from yt-dlp to our format."""
    title = info.get('title', 'Unknown Title')
    artist = info.get('artist') or info.get('uploader', 'Unknown Artist')
    upload_date = info.get('upload_date')  # YYYYMMDD
    
    year = ''
    if upload_date:
        year = upload_date[:4]

    album = info.get('album', '')
    track = info.get('track', '')

    # Clean up title
    clean_title = re.sub(r'\s*\([^)]*\)', '', title).strip()

    video_id = info.get('id')
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    thumbnails = info.get('thumbnails', [])
    cover_image = ''
    if thumbnails:
        # Get the best quality thumbnail
        cover_image = thumbnails[-1]['url']

    return {
        'title': track or clean_title,
        'artist': artist,
        'producer': '',  # Not available from yt-dlp
        'year': year,
        'album': album,
        'cover_image': cover_image,
        'youtube_url': youtube_url,
    }

def extract_metadata_with_yt_dlp(url):
    """Extract metadata from a YouTube URL (video or playlist) using yt-dlp."""
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'force_generic_extractor': False,
        'skip_download': True,
        'format': 'best',
        'youtube_api_key': 'YOUR_API_KEY'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        if 'entries' in info and info['entries']:
            # It's a playlist
            return [parse_yt_dlp_info(entry) for entry in info['entries'] if entry]
        else:
            # It's a single video
            return [parse_yt_dlp_info(info)]

    except Exception as e:
        print(f"Error extracting metadata with yt-dlp: {e}")
        return None

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
        # This is a save request from the frontend form
        add_to_csv(song_data)
        return jsonify(song_data)
    
    # This is an extraction request
    metadata_list = extract_metadata_with_yt_dlp(url)
    
    if not metadata_list:
        return jsonify({'error': 'Could not extract metadata from this URL. Please check if it\'s a valid YouTube video or playlist.'}), 400
    
    if is_playlist_url(url):
        # Process playlist: add all songs to CSV
        processed_songs = []
        skipped_songs = []
        
        for metadata in metadata_list:
            if not is_duplicate_song(metadata['youtube_url']):
                add_to_csv(metadata)
                processed_songs.append(metadata)
            else:
                skipped_songs.append(metadata['youtube_url'])
        
        return jsonify({
            'type': 'playlist',
            'processed_count': len(processed_songs),
            'skipped_count': len(skipped_songs),
            'total_count': len(metadata_list),
            'songs': processed_songs,
            'skipped_ids': skipped_songs
        })
    else:
        # Process single video: return metadata for frontend form
        metadata = metadata_list[0]
        return jsonify(metadata)

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