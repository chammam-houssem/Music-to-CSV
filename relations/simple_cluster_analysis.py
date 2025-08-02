import sqlite3
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import json
import csv

class SimplePlaylistAnalysis:
    def __init__(self, db_path='relations/playlists_library.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
    def get_artist_song_data(self):
        """Convert database to long format: 1 artist per row per song"""
        query = """
        SELECT 
            track_name,
            album_name,
            artist_names,
            artist1, artist2, artist3, artist4, artist5, artist6,
            source_playlist,
            popularity,
            danceability,
            energy,
            tempo
        FROM tracks
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Create long format data
        long_data = []
        
        for _, row in df.iterrows():
            # Get all artists for this track
            artists = []
            for i in range(1, 7):
                artist_col = f'artist{i}'
                if pd.notna(row[artist_col]) and row[artist_col].strip():
                    artists.append(row[artist_col].strip())
            
            # Remove duplicates while preserving order
            unique_artists = list(dict.fromkeys(artists))
            
            # Create one row per artist
            for artist in unique_artists:
                long_data.append({
                    'track_name': row['track_name'],
                    'album_name': row['album_name'],
                    'artist': artist,
                    'all_artists': ', '.join(unique_artists),
                    'source_playlist': row['source_playlist'],
                    'popularity': row['popularity'],
                    'danceability': row['danceability'],
                    'energy': row['energy'],
                    'tempo': row['tempo']
                })
        
        return pd.DataFrame(long_data)
    
    def create_artist_collaboration_matrix(self):
        """Create collaboration matrix for artists"""
        df = self.get_artist_song_data()
        
        # Create collaboration dictionary
        collaborations = defaultdict(int)
        
        for _, row in df.iterrows():
            # Find all artists on this track
            track_artists = [a.strip() for a in row['all_artists'].split(',')]
            
            # Create collaborations between all artists on this track
            for i, artist1 in enumerate(track_artists):
                for j, artist2 in enumerate(track_artists):
                    if i < j:  # Avoid self-collaborations and duplicates
                        pair = tuple(sorted([artist1, artist2]))
                        collaborations[pair] += 1
        
        return collaborations, df
    
    def create_album_artist_relationships(self):
        """Create album-artist relationships"""
        query = """
        SELECT 
            album_name,
            artist1, artist2, artist3, artist4, artist5, artist6,
            COUNT(*) as track_count,
            AVG(popularity) as avg_popularity,
            AVG(danceability) as avg_danceability,
            AVG(energy) as avg_energy,
            AVG(tempo) as avg_tempo
        FROM tracks
        WHERE album_name IS NOT NULL AND album_name != ''
        GROUP BY album_name
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Create album-artist relationships
        album_artists = defaultdict(set)
        
        for _, row in df.iterrows():
            album = row['album_name']
            artists = []
            
            for i in range(1, 7):
                artist_col = f'artist{i}'
                if pd.notna(row[artist_col]) and row[artist_col].strip():
                    artists.append(row[artist_col].strip())
            
            for artist in artists:
                album_artists[album].add(artist)
        
        return album_artists, df
    
    def perform_simple_clustering(self, df):
        """Perform simple clustering based on audio features"""
        # Get artist features
        artist_features = df.groupby('artist').agg({
            'popularity': ['mean', 'count'],
            'danceability': 'mean',
            'energy': 'mean',
            'tempo': 'mean'
        }).fillna(0)
        
        # Flatten column names
        artist_features.columns = ['_'.join(col).strip() for col in artist_features.columns]
        
        # Simple clustering based on popularity and audio features
        # Create clusters based on popularity ranges
        artist_features['popularity_cluster'] = pd.cut(
            artist_features['popularity_mean'], 
            bins=5, 
            labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
        )
        
        # Create clusters based on danceability
        artist_features['danceability_cluster'] = pd.cut(
            artist_features['danceability_mean'], 
            bins=3, 
            labels=['Low Dance', 'Medium Dance', 'High Dance']
        )
        
        # Create clusters based on energy
        artist_features['energy_cluster'] = pd.cut(
            artist_features['energy_mean'], 
            bins=3, 
            labels=['Low Energy', 'Medium Energy', 'High Energy']
        )
        
        return artist_features
    
    def create_network_data(self, collaborations):
        """Create network data for visualization"""
        # Get all unique artists
        all_artists = set()
        for (artist1, artist2) in collaborations.keys():
            all_artists.add(artist1)
            all_artists.add(artist2)
        
        # Create nodes data
        nodes = []
        for artist in all_artists:
            # Count collaborations for this artist
            collaboration_count = sum(1 for (a1, a2) in collaborations.keys() 
                                   if a1 == artist or a2 == artist)
            nodes.append({
                'id': artist,
                'collaborations': collaboration_count,
                'label': artist
            })
        
        # Create edges data
        edges = []
        for (artist1, artist2), weight in collaborations.items():
            edges.append({
                'source': artist1,
                'target': artist2,
                'weight': weight
            })
        
        return nodes, edges
    
    def create_album_network_data(self, album_artists):
        """Create album network data"""
        nodes = []
        edges = []
        
        # Add album nodes
        for album in album_artists.keys():
            nodes.append({
                'id': album,
                'type': 'album',
                'artists_count': len(album_artists[album]),
                'label': album
            })
        
        # Add artist nodes and edges
        all_artists = set()
        for artists in album_artists.values():
            all_artists.update(artists)
        
        for artist in all_artists:
            nodes.append({
                'id': artist,
                'type': 'artist',
                'label': artist
            })
        
        # Add edges
        for album, artists in album_artists.items():
            for artist in artists:
                edges.append({
                    'source': album,
                    'target': artist,
                    'weight': 1
                })
        
        return nodes, edges
    
    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        print("=== Playlist Cluster Analysis Report ===\n")
        
        # Get data
        print("1. Loading data...")
        collaborations, df_artist = self.create_artist_collaboration_matrix()
        album_artists, df_album = self.create_album_artist_relationships()
        
        print(f"   - Found {len(collaborations)} artist collaborations")
        print(f"   - Found {len(album_artists)} albums with multiple artists")
        
        # Artist analysis
        print("\n2. Artist Collaboration Analysis...")
        
        # Most collaborative artists
        artist_collaborations = defaultdict(int)
        for (artist1, artist2) in collaborations.keys():
            artist_collaborations[artist1] += 1
            artist_collaborations[artist2] += 1
        
        top_collaborators = sorted(artist_collaborations.items(), 
                                 key=lambda x: x[1], reverse=True)[:10]
        
        print("\nTop 10 Most Collaborative Artists:")
        for artist, count in top_collaborators:
            print(f"   - {artist}: {count} collaborations")
        
        # Strongest collaborations
        top_collaborations = sorted(collaborations.items(), 
                                  key=lambda x: x[1], reverse=True)[:10]
        
        print("\nTop 10 Strongest Collaborations:")
        for (artist1, artist2), count in top_collaborations:
            print(f"   - {artist1} & {artist2}: {count} songs together")
        
        # Album analysis
        print("\n3. Album-Artist Analysis...")
        
        albums_by_artist_count = defaultdict(int)
        for album, artists in album_artists.items():
            albums_by_artist_count[len(artists)] += 1
        
        print("\nAlbums by Number of Artists:")
        for artist_count, album_count in sorted(albums_by_artist_count.items()):
            print(f"   - {artist_count} artist(s): {album_count} albums")
        
        # Most collaborative albums
        top_collaborative_albums = sorted(album_artists.items(), 
                                        key=lambda x: len(x[1]), reverse=True)[:10]
        
        print("\nTop 10 Most Collaborative Albums:")
        for album, artists in top_collaborative_albums:
            print(f"   - {album}: {len(artists)} artists")
        
        # Clustering analysis
        print("\n4. Artist Clustering Analysis...")
        artist_features = self.perform_simple_clustering(df_artist)
        
        print("\nClustering Results:")
        print(f"   - Total artists analyzed: {len(artist_features)}")
        
        # Popularity clusters
        popularity_clusters = artist_features['popularity_cluster'].value_counts()
        print("\nArtists by Popularity Cluster:")
        for cluster, count in popularity_clusters.items():
            print(f"   - {cluster}: {count} artists")
        
        # Danceability clusters
        dance_clusters = artist_features['danceability_cluster'].value_counts()
        print("\nArtists by Danceability Cluster:")
        for cluster, count in dance_clusters.items():
            print(f"   - {cluster}: {count} artists")
        
        # Energy clusters
        energy_clusters = artist_features['energy_cluster'].value_counts()
        print("\nArtists by Energy Cluster:")
        for cluster, count in energy_clusters.items():
            print(f"   - {cluster}: {count} artists")
        
        # Save data files
        print("\n5. Saving analysis data...")
        
        # Save collaboration data
        collaborations_dict = {f"{artist1} & {artist2}": count for (artist1, artist2), count in collaborations.items()}
        with open('relations/collaborations.json', 'w') as f:
            json.dump(collaborations_dict, f, indent=2)
        
        # Save network data
        nodes, edges = self.create_network_data(collaborations)
        with open('relations/artist_network.json', 'w') as f:
            json.dump({'nodes': nodes, 'edges': edges}, f, indent=2)
        
        # Save album network data
        album_nodes, album_edges = self.create_album_network_data(album_artists)
        with open('relations/album_network.json', 'w') as f:
            json.dump({'nodes': album_nodes, 'edges': album_edges}, f, indent=2)
        
        # Save clustering results
        artist_features.to_csv('relations/artist_clusters_simple.csv')
        
        # Save long format data
        df_artist.to_csv('relations/artist_song_long_format.csv', index=False)
        
        print("\n=== Analysis Complete ===")
        print("Files created:")
        print("- relations/collaborations.json (Artist collaboration data)")
        print("- relations/artist_network.json (Artist network for visualization)")
        print("- relations/album_network.json (Album network for visualization)")
        print("- relations/artist_clusters_simple.csv (Artist clustering results)")
        print("- relations/artist_song_long_format.csv (Long format data)")
        
        return {
            'collaborations': collaborations,
            'album_artists': album_artists,
            'artist_features': artist_features,
            'long_format_data': df_artist
        }

def main():
    """Run the analysis"""
    analyzer = SimplePlaylistAnalysis()
    results = analyzer.generate_analysis_report()
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    
    # Network statistics
    collaborations = results['collaborations']
    total_artists = len(set([a for (a1, a2) in collaborations.keys() for a in [a1, a2]]))
    total_collaborations = len(collaborations)
    
    print(f"Artist Network:")
    print(f"  - Total unique artists: {total_artists}")
    print(f"  - Total collaborations: {total_collaborations}")
    print(f"  - Average collaborations per artist: {total_collaborations * 2 / total_artists:.1f}")
    
    # Album statistics
    album_artists = results['album_artists']
    total_albums = len(album_artists)
    total_album_artists = len(set([a for artists in album_artists.values() for a in artists]))
    
    print(f"\nAlbum Network:")
    print(f"  - Total albums: {total_albums}")
    print(f"  - Total unique artists: {total_album_artists}")
    print(f"  - Average artists per album: {sum(len(artists) for artists in album_artists.values()) / total_albums:.1f}")

if __name__ == "__main__":
    main() 