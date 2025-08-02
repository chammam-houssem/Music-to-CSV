import sqlite3
import pandas as pd
from datetime import datetime

class PlaylistDatabase:
    def __init__(self, db_path='relations/playlists_library.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def search_tracks(self, query, limit=50):
        """Search tracks by name, artist, or album"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tracks 
            WHERE track_name LIKE ? OR artist_names LIKE ? OR album_name LIKE ?
            ORDER BY popularity DESC, track_name
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_tracks_by_playlist(self, playlist_name, limit=100):
        """Get all tracks from a specific playlist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tracks 
            WHERE source_playlist = ?
            ORDER BY added_at DESC
            LIMIT ?
        ''', (playlist_name, limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_tracks_by_artist(self, artist_name, limit=100):
        """Get all tracks by a specific artist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tracks 
            WHERE artist_names LIKE ? OR artist1 = ? OR artist2 = ? OR artist3 = ?
            ORDER BY popularity DESC, track_name
            LIMIT ?
        ''', (f'%{artist_name}%', artist_name, artist_name, artist_name, limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_audio_features_stats(self):
        """Get statistics about audio features"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                AVG(danceability) as avg_danceability,
                AVG(energy) as avg_energy,
                AVG(tempo) as avg_tempo,
                AVG(loudness) as avg_loudness,
                AVG(valence) as avg_valence,
                COUNT(*) as total_tracks
            FROM tracks 
            WHERE danceability IS NOT NULL
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        return stats
    
    def export_to_csv(self, output_path='relations/playlists_export.csv'):
        """Export all tracks to CSV"""
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT * FROM tracks', conn)
        df.to_csv(output_path, index=False)
        conn.close()
        print(f"Exported {len(df)} tracks to {output_path}")
    
    def get_playlist_summary(self):
        """Get summary of all playlists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                source_playlist,
                COUNT(*) as track_count,
                AVG(popularity) as avg_popularity,
                AVG(danceability) as avg_danceability,
                AVG(energy) as avg_energy
            FROM tracks 
            WHERE source_playlist IS NOT NULL
            GROUP BY source_playlist
            ORDER BY track_count DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_artist_summary(self):
        """Get summary of all artists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                artist_name,
                COUNT(*) as track_count,
                AVG(popularity) as avg_popularity
            FROM artists 
            ORDER BY track_count DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_recent_tracks(self, days=30, limit=50):
        """Get recently added tracks"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tracks 
            WHERE date_imported >= datetime('now', '-{} days')
            ORDER BY date_imported DESC
            LIMIT ?
        '''.format(days), (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_popular_tracks(self, limit=50):
        """Get most popular tracks"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tracks 
            WHERE popularity IS NOT NULL
            ORDER BY popularity DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_tracks_by_genre(self, genre, limit=100):
        """Get tracks by genre"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tracks 
            WHERE genres LIKE ?
            ORDER BY popularity DESC
            LIMIT ?
        ''', (f'%{genre}%', limit))
        
        results = cursor.fetchall()
        conn.close()
        return results

def main():
    """Example usage of the PlaylistDatabase class"""
    db = PlaylistDatabase()
    
    print("=== Playlist Database Utilities ===\n")
    
    # Get database stats
    stats = db.get_audio_features_stats()
    if stats:
        print(f"Audio Features Statistics:")
        print(f"- Average Danceability: {stats['avg_danceability']:.3f}")
        print(f"- Average Energy: {stats['avg_energy']:.3f}")
        print(f"- Average Tempo: {stats['avg_tempo']:.1f} BPM")
        print(f"- Average Loudness: {stats['avg_loudness']:.1f} dB")
        print(f"- Average Valence: {stats['avg_valence']:.3f}")
        print(f"- Total Tracks: {stats['total_tracks']}")
    
    print("\n=== Playlist Summary ===")
    playlists = db.get_playlist_summary()
    for playlist in playlists[:5]:  # Show top 5
        print(f"{playlist['source_playlist']}: {playlist['track_count']} tracks")
    
    # Example search
    print("\n=== Search Example ===")
    results = db.search_tracks("XIIVI", limit=5)
    print(f"Found {len(results)} tracks by XIIVI:")
    for track in results:
        print(f"- {track['track_name']} ({track['album_name']})")
    
    # Popular tracks
    print("\n=== Popular Tracks ===")
    popular = db.get_popular_tracks(limit=5)
    print("Top 5 most popular tracks:")
    for track in popular:
        print(f"- {track['track_name']} by {track['artist_names']} (Popularity: {track['popularity']})")

if __name__ == "__main__":
    main() 