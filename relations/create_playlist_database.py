import sqlite3
import csv
import os
from datetime import datetime

def init_playlist_database():
    """Initialize the SQLite database for combined playlists data"""
    
    # Database file path
    DATABASE = 'relations/playlists_library.db'
    
    # Create the relations directory if it doesn't exist
    os.makedirs('relations', exist_ok=True)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create tracks table with all the columns from the CSV
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_uri TEXT UNIQUE NOT NULL,
            track_name TEXT NOT NULL,
            album_name TEXT,
            artist_names TEXT,
            release_date TEXT,
            duration_ms INTEGER,
            popularity INTEGER,
            explicit BOOLEAN,
            added_by TEXT,
            added_at TEXT,
            genres TEXT,
            record_label TEXT,
            danceability REAL,
            energy REAL,
            key INTEGER,
            loudness REAL,
            mode INTEGER,
            speechiness REAL,
            acousticness REAL,
            instrumentalness REAL,
            liveness REAL,
            valence REAL,
            tempo REAL,
            time_signature INTEGER,
            source_playlist TEXT,
            artist1 TEXT,
            artist2 TEXT,
            artist3 TEXT,
            artist4 TEXT,
            artist5 TEXT,
            artist6 TEXT,
            date_imported TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create playlists table to track different playlist sources
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_name TEXT UNIQUE NOT NULL,
            track_count INTEGER DEFAULT 0,
            date_created TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create artists table for better artist management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_name TEXT UNIQUE NOT NULL,
            track_count INTEGER DEFAULT 0,
            first_appearance TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create track_artists junction table for many-to-many relationship
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS track_artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER NOT NULL,
            artist_id INTEGER NOT NULL,
            artist_position INTEGER NOT NULL,
            FOREIGN KEY (track_id) REFERENCES tracks (id),
            FOREIGN KEY (artist_id) REFERENCES artists (id),
            UNIQUE(track_id, artist_id, artist_position)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracks_uri ON tracks(track_uri)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracks_playlist ON tracks(source_playlist)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks(artist_names)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_artists_name ON artists(artist_name)')
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized: {DATABASE}")
    return DATABASE

def migrate_csv_to_sqlite(csv_file_path, database_path):
    """Migrate CSV data to SQLite database"""
    
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Check if tracks table is empty
    cursor.execute('SELECT COUNT(*) FROM tracks')
    if cursor.fetchone()[0] > 0:
        print("Database already contains data. Skipping migration.")
        conn.close()
        return
    
    # Read CSV file
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        tracks_inserted = 0
        artists_inserted = set()
        playlists_inserted = set()
        
        for row in reader:
            try:
                # Insert track
                cursor.execute('''
                    INSERT INTO tracks (
                        track_uri, track_name, album_name, artist_names, release_date,
                        duration_ms, popularity, explicit, added_by, added_at,
                        genres, record_label, danceability, energy, key, loudness,
                        mode, speechiness, acousticness, instrumentalness, liveness,
                        valence, tempo, time_signature, source_playlist,
                        artist1, artist2, artist3, artist4, artist5, artist6
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['Track URI'],
                    row['Track Name'],
                    row['Album Name'],
                    row['Artist Name(s)'],
                    row['Release Date'],
                    int(row['Duration (ms)']) if row['Duration (ms)'] else None,
                    int(row['Popularity']) if row['Popularity'] else None,
                    row['Explicit'].lower() == 'true' if row['Explicit'] else False,
                    row['Added By'],
                    row['Added At'],
                    row['Genres'],
                    row['Record Label'],
                    float(row['Danceability']) if row['Danceability'] else None,
                    float(row['Energy']) if row['Energy'] else None,
                    int(row['Key']) if row['Key'] else None,
                    float(row['Loudness']) if row['Loudness'] else None,
                    int(row['Mode']) if row['Mode'] else None,
                    float(row['Speechiness']) if row['Speechiness'] else None,
                    float(row['Acousticness']) if row['Acousticness'] else None,
                    float(row['Instrumentalness']) if row['Instrumentalness'] else None,
                    float(row['Liveness']) if row['Liveness'] else None,
                    float(row['Valence']) if row['Valence'] else None,
                    float(row['Tempo']) if row['Tempo'] else None,
                    int(row['Time Signature']) if row['Time Signature'] else None,
                    row['Source_Playlist'],
                    row['Artist1'],
                    row['Artist2'],
                    row['Artist3'],
                    row['Artist4'],
                    row['Artist5'],
                    row['Artist6']
                ))
                
                tracks_inserted += 1
                
                # Track unique artists and playlists
                if row['Source_Playlist']:
                    playlists_inserted.add(row['Source_Playlist'])
                
                # Add individual artists
                for i in range(1, 7):
                    artist_key = f'Artist{i}'
                    if row[artist_key] and row[artist_key].strip():
                        artists_inserted.add(row[artist_key].strip())
                
            except Exception as e:
                print(f"Error inserting track {row.get('Track Name', 'Unknown')}: {e}")
                continue
        
        # Insert playlists
        for playlist in playlists_inserted:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO playlists (playlist_name)
                    VALUES (?)
                ''', (playlist,))
            except Exception as e:
                print(f"Error inserting playlist {playlist}: {e}")
        
        # Insert artists
        for artist in artists_inserted:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO artists (artist_name)
                    VALUES (?)
                ''', (artist,))
            except Exception as e:
                print(f"Error inserting artist {artist}: {e}")
        
        conn.commit()
        print(f"Migration completed:")
        print(f"- {tracks_inserted} tracks inserted")
        print(f"- {len(artists_inserted)} unique artists")
        print(f"- {len(playlists_inserted)} unique playlists")
    
    conn.close()

def get_database_stats(database_path):
    """Get statistics about the database"""
    
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Get track count
    cursor.execute('SELECT COUNT(*) FROM tracks')
    track_count = cursor.fetchone()[0]
    
    # Get artist count
    cursor.execute('SELECT COUNT(*) FROM artists')
    artist_count = cursor.fetchone()[0]
    
    # Get playlist count
    cursor.execute('SELECT COUNT(*) FROM playlists')
    playlist_count = cursor.fetchone()[0]
    
    # Get top artists
    cursor.execute('''
        SELECT artist_name, COUNT(*) as track_count 
        FROM artists 
        ORDER BY track_count DESC 
        LIMIT 10
    ''')
    top_artists = cursor.fetchall()
    
    # Get top playlists
    cursor.execute('''
        SELECT source_playlist, COUNT(*) as track_count 
        FROM tracks 
        WHERE source_playlist IS NOT NULL
        GROUP BY source_playlist 
        ORDER BY track_count DESC 
        LIMIT 10
    ''')
    top_playlists = cursor.fetchall()
    
    conn.close()
    
    print(f"\nDatabase Statistics:")
    print(f"- Total tracks: {track_count}")
    print(f"- Unique artists: {artist_count}")
    print(f"- Unique playlists: {playlist_count}")
    
    print(f"\nTop 10 Artists:")
    for artist, count in top_artists:
        print(f"  {artist}: {count} tracks")
    
    print(f"\nTop 10 Playlists:")
    for playlist, count in top_playlists:
        print(f"  {playlist}: {count} tracks")

if __name__ == "__main__":
    # Initialize database
    db_path = init_playlist_database()
    
    # Migrate CSV data
    csv_path = 'relations/combined_playlists_with_artists.csv'
    if os.path.exists(csv_path):
        migrate_csv_to_sqlite(csv_path, db_path)
        get_database_stats(db_path)
    else:
        print(f"CSV file not found: {csv_path}") 