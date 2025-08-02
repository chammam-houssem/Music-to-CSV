import pandas as pd
import re

def extract_artists_from_playlist():
    """
    Extract individual artists from the combined playlist CSV and create new columns.
    """
    try:
        # Read the combined playlist
        print("Loading combined playlist...")
        df = pd.read_csv('combined_playlists.csv')
        
        print(f"Processing {len(df)} tracks...")
        
        # Find the maximum number of artists in any single track
        max_artists = 0
        for artists_str in df['Artist Name(s)'].dropna():
            if artists_str:
                # Split by comma and clean up
                artists = [artist.strip() for artist in artists_str.split(',')]
                max_artists = max(max_artists, len(artists))
        
        print(f"Maximum number of artists found in a single track: {max_artists}")
        
        # Create new columns for each artist
        for i in range(1, max_artists + 1):
            df[f'Artist{i}'] = ''
        
        # Extract artists for each track
        for idx, row in df.iterrows():
            artists_str = row['Artist Name(s)']
            if pd.notna(artists_str) and artists_str:
                # Split by comma and clean up
                artists = [artist.strip() for artist in artists_str.split(',')]
                
                # Fill in the artist columns
                for i, artist in enumerate(artists, 1):
                    if i <= max_artists:
                        df.at[idx, f'Artist{i}'] = artist
        
        # Show some statistics
        print("\nArtist extraction statistics:")
        print(f"  - Total tracks processed: {len(df)}")
        print(f"  - Maximum artists per track: {max_artists}")
        
        # Count tracks with different numbers of artists
        artist_counts = []
        for idx, row in df.iterrows():
            artists_str = row['Artist Name(s)']
            if pd.notna(artists_str) and artists_str:
                artists = [artist.strip() for artist in artists_str.split(',')]
                artist_counts.append(len(artists))
            else:
                artist_counts.append(0)
        
        artist_count_series = pd.Series(artist_counts)
        print(f"  - Tracks with 1 artist: {(artist_count_series == 1).sum()}")
        print(f"  - Tracks with 2 artists: {(artist_count_series == 2).sum()}")
        print(f"  - Tracks with 3+ artists: {(artist_count_series >= 3).sum()}")
        
        # Save the new CSV
        output_file = 'combined_playlists_with_artists.csv'
        df.to_csv(output_file, index=False)
        print(f"\n✓ Enhanced playlist saved as: {output_file}")
        
        # Show some examples
        print("\n=== EXAMPLES ===")
        print("Sample tracks with multiple artists:")
        multi_artist_tracks = df[artist_count_series >= 2].head(5)
        for idx, row in multi_artist_tracks.iterrows():
            print(f"  Track: {row['Track Name']}")
            print(f"    Original: {row['Artist Name(s)']}")
            artists = []
            for i in range(1, max_artists + 1):
                if row[f'Artist{i}']:
                    artists.append(row[f'Artist{i}'])
            print(f"    Extracted: {', '.join(artists)}")
            print()
        
        return df
        
    except FileNotFoundError:
        print("Error: combined_playlists.csv not found. Please run combine_playlists.py first.")
        return None
    except Exception as e:
        print(f"Error processing playlist: {e}")
        return None

if __name__ == "__main__":
    extract_artists_from_playlist() 