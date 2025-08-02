import sqlite3
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class PlaylistClusterAnalysis:
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
    
    def create_artist_collaboration_network(self):
        """Create network graph for artist collaborations"""
        df = self.get_artist_song_data()
        
        # Create collaboration matrix
        collaborations = defaultdict(int)
        artist_tracks = defaultdict(set)
        
        for _, row in df.iterrows():
            track_name = row['track_name']
            artist = row['artist']
            artist_tracks[artist].add(track_name)
            
            # Find all artists on this track
            track_artists = [a.strip() for a in row['all_artists'].split(',')]
            
            # Create collaborations between all artists on this track
            for i, artist1 in enumerate(track_artists):
                for j, artist2 in enumerate(track_artists):
                    if i < j:  # Avoid self-collaborations and duplicates
                        pair = tuple(sorted([artist1, artist2]))
                        collaborations[pair] += 1
        
        # Create network graph
        G = nx.Graph()
        
        # Add edges with weights
        for (artist1, artist2), weight in collaborations.items():
            G.add_edge(artist1, artist2, weight=weight)
        
        # Add nodes for artists with no collaborations
        all_artists = set(df['artist'].unique())
        for artist in all_artists:
            if artist not in G.nodes():
                G.add_node(artist)
        
        return G, df
    
    def create_album_network(self):
        """Create network graph for album relationships"""
        query = """
        SELECT 
            album_name,
            artist_names,
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
        
        # Create bipartite graph
        G = nx.Graph()
        
        for album, artists in album_artists.items():
            for artist in artists:
                G.add_edge(album, artist, weight=1)
        
        return G, df
    
    def perform_artist_clustering(self, G, df):
        """Perform clustering analysis on artist network"""
        # Get artist features for clustering
        artist_features = df.groupby('artist').agg({
            'popularity': ['mean', 'std', 'count'],
            'danceability': ['mean', 'std'],
            'energy': ['mean', 'std'],
            'tempo': ['mean', 'std']
        }).fillna(0)
        
        # Flatten column names
        artist_features.columns = ['_'.join(col).strip() for col in artist_features.columns]
        
        # Prepare features for clustering
        features_for_clustering = artist_features.copy()
        
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features_for_clustering)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=min(5, len(features_scaled)), random_state=42)
        artist_features['cluster'] = kmeans.fit_predict(features_scaled)
        
        # Perform DBSCAN clustering
        dbscan = DBSCAN(eps=0.5, min_samples=2)
        artist_features['dbscan_cluster'] = dbscan.fit_predict(features_scaled)
        
        return artist_features, features_scaled
    
    def visualize_artist_network(self, G, artist_features, output_path='relations/artist_network.html'):
        """Create interactive visualization of artist collaboration network"""
        
        # Calculate network metrics
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Get node sizes based on degree
        node_sizes = [G.degree(node) * 10 + 5 for node in G.nodes()]
        
        # Get node colors based on clustering
        node_colors = []
        for node in G.nodes():
            if node in artist_features.index:
                cluster = artist_features.loc[node, 'cluster']
                node_colors.append(cluster)
            else:
                node_colors.append(-1)
        
        # Create edge traces
        edge_x = []
        edge_y = []
        edge_weights = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(edge[2]['weight'])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
        
        # Create node traces
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"{node}<br>Degree: {G.degree(node)}")
            node_size.append(G.degree(node) * 10 + 5)
            
            if node in artist_features.index:
                cluster = artist_features.loc[node, 'cluster']
                node_color.append(cluster)
            else:
                node_color.append(-1)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[node.split()[0] for node in G.nodes()],  # Show first word of artist name
            textposition="middle center",
            marker=dict(
                size=node_size,
                color=node_color,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Cluster")
            ))
        
        # Create layout
        layout = go.Layout(
            title='Artist Collaboration Network',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
        fig.write_html(output_path)
        print(f"Artist network visualization saved to {output_path}")
        
        return fig
    
    def visualize_album_network(self, G, output_path='relations/album_network.html'):
        """Create interactive visualization of album-artist network"""
        
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Separate albums and artists
        albums = [node for node in G.nodes() if G.degree(node) > 1]  # Albums have multiple artists
        artists = [node for node in G.nodes() if G.degree(node) <= 1]  # Artists
        
        # Create edge traces
        edge_x = []
        edge_y = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
        
        # Create album node traces
        album_x = []
        album_y = []
        album_text = []
        
        for album in albums:
            x, y = pos[album]
            album_x.append(x)
            album_y.append(y)
            album_text.append(f"Album: {album}<br>Artists: {G.degree(album)}")
        
        album_trace = go.Scatter(
            x=album_x, y=album_y,
            mode='markers+text',
            hoverinfo='text',
            text=[album.split()[0] for album in albums],
            textposition="middle center",
            marker=dict(
                size=20,
                color='red',
                symbol='diamond'
            ),
            name='Albums')
        
        # Create artist node traces
        artist_x = []
        artist_y = []
        artist_text = []
        
        for artist in artists:
            x, y = pos[artist]
            artist_x.append(x)
            artist_y.append(y)
            artist_text.append(f"Artist: {artist}")
        
        artist_trace = go.Scatter(
            x=artist_x, y=artist_y,
            mode='markers+text',
            hoverinfo='text',
            text=[artist.split()[0] for artist in artists],
            textposition="middle center",
            marker=dict(
                size=15,
                color='blue',
                symbol='circle'
            ),
            name='Artists')
        
        # Create layout
        layout = go.Layout(
            title='Album-Artist Network',
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        fig = go.Figure(data=[edge_trace, album_trace, artist_trace], layout=layout)
        fig.write_html(output_path)
        print(f"Album network visualization saved to {output_path}")
        
        return fig
    
    def create_cluster_summary(self, artist_features):
        """Create summary of artist clusters"""
        print("\n=== Artist Cluster Analysis ===")
        
        # Summary by cluster
        cluster_summary = artist_features.groupby('cluster').agg({
            'popularity_mean': ['mean', 'count'],
            'danceability_mean': 'mean',
            'energy_mean': 'mean',
            'tempo_mean': 'mean'
        }).round(3)
        
        print("\nCluster Summary:")
        print(cluster_summary)
        
        # Top artists in each cluster
        print("\nTop Artists by Cluster:")
        for cluster in sorted(artist_features['cluster'].unique()):
            cluster_artists = artist_features[artist_features['cluster'] == cluster]
            top_artists = cluster_artists.nlargest(5, 'popularity_mean')
            print(f"\nCluster {cluster} ({len(cluster_artists)} artists):")
            for artist in top_artists.index:
                print(f"  - {artist} (Popularity: {top_artists.loc[artist, 'popularity_mean']:.1f})")
        
        return cluster_summary
    
    def create_collaboration_matrix(self, G):
        """Create and visualize collaboration matrix"""
        # Get top artists by degree
        top_artists = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:20]
        top_artist_names = [artist for artist, degree in top_artists]
        
        # Create collaboration matrix
        matrix = np.zeros((len(top_artist_names), len(top_artist_names)))
        
        for i, artist1 in enumerate(top_artist_names):
            for j, artist2 in enumerate(top_artist_names):
                if G.has_edge(artist1, artist2):
                    matrix[i][j] = G[artist1][artist2]['weight']
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(matrix, 
                   xticklabels=[name.split()[0] for name in top_artist_names],
                   yticklabels=[name.split()[0] for name in top_artist_names],
                   cmap='YlOrRd',
                   annot=True,
                   fmt='.0f',
                   cbar_kws={'label': 'Number of Collaborations'})
        
        plt.title('Artist Collaboration Matrix (Top 20 Artists)')
        plt.xlabel('Artists')
        plt.ylabel('Artists')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig('relations/collaboration_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return matrix
    
    def run_analysis(self):
        """Run complete analysis"""
        print("Starting Playlist Cluster Analysis...")
        
        # Artist collaboration analysis
        print("\n1. Creating artist collaboration network...")
        G_artist, df_artist = self.create_artist_collaboration_network()
        
        print(f"   - Network has {G_artist.number_of_nodes()} artists")
        print(f"   - Network has {G_artist.number_of_edges()} collaborations")
        
        # Album network analysis
        print("\n2. Creating album-artist network...")
        G_album, df_album = self.create_album_network()
        
        print(f"   - Album network has {G_album.number_of_nodes()} nodes")
        print(f"   - Album network has {G_album.number_of_edges()} relationships")
        
        # Perform clustering
        print("\n3. Performing artist clustering...")
        artist_features, features_scaled = self.perform_artist_clustering(G_artist, df_artist)
        
        # Create visualizations
        print("\n4. Creating visualizations...")
        self.visualize_artist_network(G_artist, artist_features)
        self.visualize_album_network(G_album)
        
        # Create collaboration matrix
        print("\n5. Creating collaboration matrix...")
        self.create_collaboration_matrix(G_artist)
        
        # Create cluster summary
        print("\n6. Creating cluster summary...")
        cluster_summary = self.create_cluster_summary(artist_features)
        
        # Save analysis results
        print("\n7. Saving analysis results...")
        artist_features.to_csv('relations/artist_clusters.csv')
        df_artist.to_csv('relations/artist_song_long_format.csv', index=False)
        
        print("\n=== Analysis Complete ===")
        print("Files created:")
        print("- relations/artist_network.html (Interactive artist network)")
        print("- relations/album_network.html (Interactive album network)")
        print("- relations/collaboration_matrix.png (Collaboration heatmap)")
        print("- relations/artist_clusters.csv (Artist clustering results)")
        print("- relations/artist_song_long_format.csv (Long format data)")
        
        return {
            'artist_network': G_artist,
            'album_network': G_album,
            'artist_features': artist_features,
            'long_format_data': df_artist
        }

def main():
    """Run the cluster analysis"""
    analyzer = PlaylistClusterAnalysis()
    results = analyzer.run_analysis()
    
    # Print some key insights
    print("\n=== Key Insights ===")
    
    # Most collaborative artists
    top_collaborators = sorted(results['artist_network'].degree(), 
                              key=lambda x: x[1], reverse=True)[:10]
    print("\nTop 10 Most Collaborative Artists:")
    for artist, degree in top_collaborators:
        print(f"  - {artist}: {degree} collaborations")
    
    # Network statistics
    G = results['artist_network']
    print(f"\nNetwork Statistics:")
    print(f"  - Total artists: {G.number_of_nodes()}")
    print(f"  - Total collaborations: {G.number_of_edges()}")
    print(f"  - Average collaborations per artist: {G.number_of_edges() * 2 / G.number_of_nodes():.1f}")
    
    # Clustering insights
    clusters = results['artist_features']['cluster'].value_counts()
    print(f"\nClustering Results:")
    print(f"  - Number of clusters: {len(clusters)}")
    for cluster, count in clusters.items():
        print(f"  - Cluster {cluster}: {count} artists")

if __name__ == "__main__":
    main() 