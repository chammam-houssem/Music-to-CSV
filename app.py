from flask import Flask, render_template, request, jsonify, send_file
import csv
import os
import re
from datetime import datetime
import yt_dlp
from urllib.parse import urlparse, parse_qs
import sqlite3
import json

app = Flask(__name__)

# Database configuration
DATABASE = 'music_library.db'

def init_db():
    """Initialize the SQLite database with the required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create songs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            producer TEXT,
            year TEXT,
            album TEXT,
            cover_image TEXT,
            youtube_url TEXT UNIQUE NOT NULL,
            date_added TEXT NOT NULL
        )
    ''')
    
    # Create lyrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lyrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER NOT NULL,
            lyrics_text TEXT NOT NULL,
            date_added TEXT NOT NULL,
            FOREIGN KEY (song_id) REFERENCES songs (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def migrate_csv_to_sqlite():
    """Migrate existing CSV data to SQLite if CSV exists"""
    if os.path.exists('music_data.csv'):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if songs table is empty
        cursor.execute('SELECT COUNT(*) FROM songs')
        if cursor.fetchone()[0] == 0:
            # Migrate CSV data
            with open('music_data.csv', 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cursor.execute('''
                        INSERT INTO songs (title, artist, producer, year, album, cover_image, youtube_url, date_added)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['Title'],
                        row['Artist'],
                        row['Producer'],
                        row['Year'],
                        row['Album'],
                        row['Cover Image'],
                        row['YouTube URL'],
                        row['Date Added']
                    ))
            
            conn.commit()
            print("Migrated CSV data to SQLite database")
        
        conn.close()

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
    """Check if a song already exists in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM songs WHERE youtube_url = ?', (youtube_url,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def add_to_database(metadata):
    """Add metadata to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO songs (title, artist, producer, year, album, cover_image, youtube_url, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metadata['title'],
        metadata['artist'],
        metadata['producer'],
        metadata['year'],
        metadata['album'],
        metadata['cover_image'],
        metadata['youtube_url'],
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    conn.commit()
    conn.close()

def read_database_data():
    """Read all data from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, 
               CASE WHEN l.id IS NOT NULL THEN 1 ELSE 0 END as has_lyrics
        FROM songs s
        LEFT JOIN lyrics l ON s.id = l.song_id
        ORDER BY s.date_added DESC
    ''')
    
    rows = cursor.fetchall()
    data = []
    for row in rows:
        data.append({
            'id': row['id'],
            'Title': row['title'],
            'Artist': row['artist'],
            'Producer': row['producer'],
            'Year': row['year'],
            'Album': row['album'],
            'Cover Image': row['cover_image'],
            'YouTube URL': row['youtube_url'],
            'Date Added': row['date_added'],
            'has_lyrics': row['has_lyrics']
        })
    
    conn.close()
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
        add_to_database(song_data)
        return jsonify(song_data)
    
    # This is an extraction request
    metadata_list = extract_metadata_with_yt_dlp(url)
    
    if not metadata_list:
        return jsonify({'error': 'Could not extract metadata from this URL. Please check if it\'s a valid YouTube video or playlist.'}), 400
    
    if is_playlist_url(url):
        # Process playlist: add all songs to database
        processed_songs = []
        skipped_songs = []
        
        for metadata in metadata_list:
            if not is_duplicate_song(metadata['youtube_url']):
                add_to_database(metadata)
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
    data = read_database_data()
    
    # Calculate statistics
    unique_artists = len(set(song['Artist'] for song in data))
    songs_with_year = len([song for song in data if song['Year']])
    
    return render_template('library.html', songs=data, unique_artists=unique_artists, songs_with_year=songs_with_year)

@app.route('/music_data.csv')
def download_csv():
    # Generate CSV from database
    data = read_database_data()
    
    # Create temporary CSV file
    temp_csv = 'temp_music_data.csv'
    with open(temp_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Artist', 'Producer', 'Year', 'Album', 'Cover Image', 'YouTube URL', 'Date Added'])
        for song in data:
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
    
    return send_file(temp_csv, as_attachment=True, download_name='music_library.csv')

@app.route('/update_song', methods=['POST'])
def update_song():
    """Update a song in the database"""
    try:
        data = request.json
        youtube_url = data.get('youtube_url', '')
        updated_data = data.get('song_data', {})
        
        if not youtube_url:
            return jsonify({'error': 'YouTube URL is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update the song
        cursor.execute('''
            UPDATE songs 
            SET title = ?, artist = ?, producer = ?, year = ?, album = ?
            WHERE youtube_url = ?
        ''', (
            updated_data.get('title', ''),
            updated_data.get('artist', ''),
            updated_data.get('producer', ''),
            updated_data.get('year', ''),
            updated_data.get('album', ''),
            youtube_url
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Song updated successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Error updating song: {str(e)}'}), 500

@app.route('/get_lyrics/<int:song_id>', methods=['GET'])
def get_lyrics(song_id):
    """Get lyrics for a specific song"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT lyrics_text FROM lyrics WHERE song_id = ?', (song_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return jsonify({'lyrics': result['lyrics_text']})
        else:
            return jsonify({'lyrics': ''})
            
    except Exception as e:
        return jsonify({'error': f'Error getting lyrics: {str(e)}'}), 500

@app.route('/save_lyrics', methods=['POST'])
def save_lyrics():
    """Save or update lyrics for a song"""
    try:
        data = request.json
        song_id = data.get('song_id')
        lyrics_text = data.get('lyrics', '').strip()
        
        if not song_id:
            return jsonify({'error': 'Song ID is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if lyrics already exist
        cursor.execute('SELECT id FROM lyrics WHERE song_id = ?', (song_id,))
        existing_lyrics = cursor.fetchone()
        
        if existing_lyrics:
            # Update existing lyrics
            cursor.execute('''
                UPDATE lyrics 
                SET lyrics_text = ?, date_added = ?
                WHERE song_id = ?
            ''', (lyrics_text, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), song_id))
        else:
            # Insert new lyrics
            cursor.execute('''
                INSERT INTO lyrics (song_id, lyrics_text, date_added)
                VALUES (?, ?, ?)
            ''', (song_id, lyrics_text, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Lyrics saved successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Error saving lyrics: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    migrate_csv_to_sqlite()
    app.run(debug=True, host='0.0.0.0', port=5000) 