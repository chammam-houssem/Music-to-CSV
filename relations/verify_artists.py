import pandas as pd

def verify_artist_extraction():
    """
    Verify the artist extraction results and show detailed statistics.
    """
    try:
        # Read the enhanced playlist
        df = pd.read_csv('combined_playlists_with_artists.csv')
        
        print("=== ARTIST EXTRACTION VERIFICATION ===\n")
        
        # Check the new columns
        artist_columns = [col for col in df.columns if col.startswith('Artist') and col != 'Artist Name(s)']
        print(f"New artist columns created: {artist_columns}")
        
        # Statistics
        print("\n=== STATISTICS ===")
        print(f"Total tracks: {len(df)}")
        
        # Count tracks by number of artists
        artist_counts = []
        for idx, row in df.iterrows():
            count = 0
            for col in artist_columns:
                if pd.notna(row[col]) and row[col].strip():
                    count += 1
            artist_counts.append(count)
        
        artist_count_series = pd.Series(artist_counts)
        print(f"Tracks with 1 artist: {(artist_count_series == 1).sum()}")
        print(f"Tracks with 2 artists: {(artist_count_series == 2).sum()}")
        print(f"Tracks with 3 artists: {(artist_count_series == 3).sum()}")
        print(f"Tracks with 4+ artists: {(artist_count_series >= 4).sum()}")
        
        # Show examples of different artist counts
        print("\n=== EXAMPLES BY ARTIST COUNT ===")
        
        # Single artist examples
        single_artist = df[artist_count_series == 1].head(3)
        print("Single artist tracks:")
        for idx, row in single_artist.iterrows():
            print(f"  {row['Track Name']} - {row['Artist1']}")
        
        # Multiple artist examples
        multi_artist = df[artist_count_series >= 2].head(3)
        print("\nMultiple artist tracks:")
        for idx, row in multi_artist.iterrows():
            artists = []
            for col in artist_columns:
                if pd.notna(row[col]) and row[col].strip():
                    artists.append(row[col])
            print(f"  {row['Track Name']} - {', '.join(artists)}")
        
        # Most collaborative tracks (most artists)
        max_artists = artist_count_series.max()
        most_collaborative = df[artist_count_series == max_artists].head(3)
        print(f"\nMost collaborative tracks ({max_artists} artists):")
        for idx, row in most_collaborative.iterrows():
            artists = []
            for col in artist_columns:
                if pd.notna(row[col]) and row[col].strip():
                    artists.append(row[col])
            print(f"  {row['Track Name']} - {', '.join(artists)}")
        
        # Check for any extraction issues
        print(f"\n=== VALIDATION ===")
        issues = 0
        for idx, row in df.iterrows():
            original = str(row['Artist Name(s)']) if pd.notna(row['Artist Name(s)']) else ''
            extracted = []
            for col in artist_columns:
                if pd.notna(row[col]) and row[col].strip():
                    extracted.append(row[col].strip())
            
            # Compare original vs extracted
            original_clean = [a.strip() for a in original.split(',') if a.strip()]
            if original_clean != extracted:
                issues += 1
                if issues <= 3:  # Show first 3 issues
                    print(f"  Issue in track '{row['Track Name']}':")
                    print(f"    Original: {original}")
                    print(f"    Extracted: {', '.join(extracted)}")
        
        if issues == 0:
            print("  ✓ No extraction issues found!")
        else:
            print(f"  ⚠ Found {issues} potential extraction issues")
        
        print(f"\n=== SUMMARY ===")
        print(f"✓ Successfully extracted artists from {len(df)} tracks")
        print(f"✓ Created {len(artist_columns)} artist columns")
        print(f"✓ Maximum artists per track: {max_artists}")
        print(f"✓ File saved as: combined_playlists_with_artists.csv")
        
    except FileNotFoundError:
        print("Error: combined_playlists_with_artists.csv not found.")
    except Exception as e:
        print(f"Error verifying artist extraction: {e}")

if __name__ == "__main__":
    verify_artist_extraction() 