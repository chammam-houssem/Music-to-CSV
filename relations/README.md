# Playlists Database

This directory contains a SQLite database that serves as the primary data storage for the combined playlists CSV file.

## Files

- `playlists_library.db` - SQLite database (created automatically)
- `create_playlist_database.py` - Script to initialize and populate the database
- `playlist_db_utils.py` - Utility functions for interacting with the database
- `combined_playlists_with_artists.csv` - Source CSV file

## Database Schema

### Tables

1. **`tracks`** - Main tracks table with all track information
   - `id` (Primary Key)
   - `track_uri` - Spotify track URI (unique)
   - `track_name` - Track title
   - `album_name` - Album name
   - `artist_names` - Combined artist names
   - `release_date` - Release date
   - `duration_ms` - Duration in milliseconds
   - `popularity` - Spotify popularity score
   - `explicit` - Whether track is explicit
   - `added_by` - User who added the track
   - `added_at` - When track was added
   - `genres` - Track genres
   - `record_label` - Record label
   - Audio features: `danceability`, `energy`, `key`, `loudness`, `mode`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo`, `time_signature`
   - `source_playlist` - Which playlist the track came from
   - `artist1` through `artist6` - Individual artist names
   - `date_imported` - When track was imported to database

2. **`playlists`** - Playlist information
   - `id` (Primary Key)
   - `playlist_name` - Playlist name (unique)
   - `track_count` - Number of tracks in playlist
   - `date_created` - When playlist was created

3. **`artists`** - Artist information
   - `id` (Primary Key)
   - `artist_name` - Artist name (unique)
   - `track_count` - Number of tracks by this artist
   - `first_appearance` - When artist first appeared

4. **`track_artists`** - Junction table for track-artist relationships
   - `id` (Primary Key)
   - `track_id` - Foreign key to tracks
   - `artist_id` - Foreign key to artists
   - `artist_position` - Position of artist in track (1-6)

## Usage

### Initialize Database

```python
from create_playlist_database import init_playlist_database, migrate_csv_to_sqlite

# Initialize database
db_path = init_playlist_database()

# Migrate CSV data
migrate_csv_to_sqlite('relations/combined_playlists_with_artists.csv', db_path)
```

### Query Database

```python
from playlist_db_utils import PlaylistDatabase

db = PlaylistDatabase()

# Search tracks
results = db.search_tracks("XIIVI")

# Get tracks by playlist
playlist_tracks = db.get_tracks_by_playlist("2k23")

# Get tracks by artist
artist_tracks = db.get_tracks_by_artist("Cheb terro")

# Get audio features statistics
stats = db.get_audio_features_stats()

# Export to CSV
db.export_to_csv("export.csv")
```

## Features

- **Comprehensive Track Data**: All Spotify track information including audio features
- **Artist Management**: Separate artist table with track counts
- **Playlist Tracking**: Track which playlist each song came from
- **Search Capabilities**: Search by track name, artist, or album
- **Audio Analysis**: Statistical analysis of audio features
- **Export Functionality**: Export data back to CSV format
- **Performance Optimized**: Indexes on frequently queried columns

## Benefits Over CSV

- **Better Performance**: Fast queries with SQL indexes
- **Data Integrity**: Proper relationships and constraints
- **Advanced Queries**: Complex filtering and aggregation
- **Scalability**: Can handle large datasets efficiently
- **Data Analysis**: Built-in statistical functions
- **Concurrent Access**: Multiple applications can access simultaneously

## Database Statistics

The database contains:
- **598 tracks** from the combined playlists
- **Multiple playlists** including "2k23", "tuna_hip_hop", "tunisian_doomer", "zzh5"
- **Rich audio features** for music analysis
- **Artist collaboration data** with up to 6 artists per track
- **Comprehensive metadata** including genres, labels, and timestamps

## Quick Start

1. **Run the database creation script:**
   ```bash
   python relations/create_playlist_database.py
   ```

2. **Test the database utilities:**
   ```bash
   python relations/playlist_db_utils.py
   ```

3. **Use in your own code:**
   ```python
   from relations.playlist_db_utils import PlaylistDatabase
   
   db = PlaylistDatabase()
   tracks = db.search_tracks("hip hop")
   ```

## Audio Features Analysis

The database includes comprehensive audio features from Spotify:
- **Danceability**: How suitable a track is for dancing
- **Energy**: Perceptual measure of intensity and activity
- **Tempo**: Overall estimated tempo in BPM
- **Loudness**: Overall loudness in decibels
- **Valence**: Musical positiveness conveyed by a track
- **Key**: Estimated overall key of the track
- **Mode**: Modality (major or minor)
- **Speechiness**: Presence of spoken words
- **Acousticness**: Confidence measure of acousticness
- **Instrumentalness**: Predicts whether a track contains no vocals
- **Liveness**: Detects presence of audience in recording
- **Time Signature**: Estimated overall time signature

## Playlist Sources

The database tracks tracks from multiple playlists:
- **2k23**: Main playlist with various artists
- **tuna_hip_hop**: Hip hop focused tracks
- **tunisian_doomer**: Tunisian music collection
- **zzh5**: Another music collection

## Data Migration

The database automatically migrates data from the CSV file with:
- **Data validation**: Ensures data integrity
- **Error handling**: Graceful handling of malformed data
- **Progress tracking**: Shows migration progress
- **Statistics**: Provides summary of imported data 