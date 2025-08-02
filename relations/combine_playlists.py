import pandas as pd
import os
import glob

def combine_playlists():
    """
    Combine all CSV files in the Playlists folder into one CSV file.
    """
    # Get all CSV files in the Playlists folder
    playlist_files = glob.glob('Playlists/*.csv')
    
    if not playlist_files:
        print("No CSV files found in the Playlists folder.")
        return
    
    print(f"Found {len(playlist_files)} playlist files:")
    for file in playlist_files:
        print(f"  - {os.path.basename(file)}")
    
    # List to store all dataframes
    all_dataframes = []
    
    # Read each CSV file and add a source column
    for file in playlist_files:
        try:
            df = pd.read_csv(file)
            # Add a column to identify the source playlist
            playlist_name = os.path.splitext(os.path.basename(file))[0]
            df['Source_Playlist'] = playlist_name
            all_dataframes.append(df)
            print(f"  ✓ Loaded {len(df)} tracks from {os.path.basename(file)}")
        except Exception as e:
            print(f"  ✗ Error loading {file}: {e}")
    
    if not all_dataframes:
        print("No valid CSV files could be loaded.")
        return
    
    # Combine all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Remove duplicates based on Track URI (same track might be in multiple playlists)
    original_count = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['Track URI'], keep='first')
    final_count = len(combined_df)
    
    print(f"\nCombined {original_count} total tracks")
    print(f"After removing duplicates: {final_count} unique tracks")
    
    # Save the combined playlist
    output_file = 'combined_playlists.csv'
    combined_df.to_csv(output_file, index=False)
    print(f"\n✓ Combined playlist saved as: {output_file}")
    
    # Show some statistics
    print("\nStatistics:")
    print(f"  - Total unique tracks: {final_count}")
    print(f"  - Number of source playlists: {len(playlist_files)}")
    
    # Show playlist breakdown
    print("\nTracks per playlist:")
    playlist_counts = combined_df['Source_Playlist'].value_counts()
    for playlist, count in playlist_counts.items():
        print(f"  - {playlist}: {count} tracks")

if __name__ == "__main__":
    combine_playlists() 