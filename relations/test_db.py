from playlist_db_utils import PlaylistDatabase

def test_database():
    db = PlaylistDatabase()
    
    print("=== Testing Playlist Database ===\n")
    
    # Test getting tracks by playlist
    print("Tracks from 2k23 playlist (first 3):")
    tracks = db.get_tracks_by_playlist('2k23', limit=3)
    for track in tracks:
        print(f"- {track['track_name']} by {track['artist_names']}")
    
    print("\n" + "="*50 + "\n")
    
    # Test getting tracks by artist
    print("Tracks by Cheb terro (first 3):")
    tracks = db.get_tracks_by_artist('Cheb terro', limit=3)
    for track in tracks:
        print(f"- {track['track_name']} ({track['album_name']})")
    
    print("\n" + "="*50 + "\n")
    
    # Test getting popular tracks
    print("Top 3 most popular tracks:")
    tracks = db.get_popular_tracks(limit=3)
    for track in tracks:
        print(f"- {track['track_name']} by {track['artist_names']} (Popularity: {track['popularity']})")
    
    print("\n" + "="*50 + "\n")
    
    # Test getting tracks by genre
    print("Tracks with 'arabic hip hop' genre (first 3):")
    tracks = db.get_tracks_by_genre('arabic hip hop', limit=3)
    for track in tracks:
        print(f"- {track['track_name']} by {track['artist_names']}")

if __name__ == "__main__":
    test_database() 