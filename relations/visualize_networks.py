import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def load_network_data():
    """Load the network data from JSON files"""
    with open('relations/artist_network.json', 'r') as f:
        artist_network = json.load(f)
    
    with open('relations/album_network.json', 'r') as f:
        album_network = json.load(f)
    
    with open('relations/collaborations.json', 'r') as f:
        collaborations = json.load(f)
    
    return artist_network, album_network, collaborations

def create_collaboration_chart(collaborations):
    """Create a bar chart of top collaborations"""
    # Sort collaborations by count
    sorted_collaborations = sorted(collaborations.items(), key=lambda x: x[1], reverse=True)[:15]
    
    artists = [collab.split(' & ')[0] for collab, count in sorted_collaborations]
    counts = [count for collab, count in sorted_collaborations]
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(range(len(artists)), counts, color='skyblue', edgecolor='navy')
    
    plt.title('Top 15 Artist Collaborations', fontsize=16, fontweight='bold')
    plt.xlabel('Artist Pairs', fontsize=12)
    plt.ylabel('Number of Songs Together', fontsize=12)
    
    # Rotate x-axis labels for better readability
    plt.xticks(range(len(artists)), artists, rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('relations/top_collaborations.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_artist_popularity_chart(artist_network):
    """Create a chart showing artist collaboration counts"""
    # Get collaboration counts for each artist
    artist_counts = {}
    for node in artist_network['nodes']:
        artist_counts[node['label']] = node['collaborations']
    
    # Get top 20 most collaborative artists
    top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    artists = [artist for artist, count in top_artists]
    counts = [count for artist, count in top_artists]
    
    plt.figure(figsize=(14, 8))
    bars = plt.bar(range(len(artists)), counts, color='lightcoral', edgecolor='darkred')
    
    plt.title('Top 20 Most Collaborative Artists', fontsize=16, fontweight='bold')
    plt.xlabel('Artists', fontsize=12)
    plt.ylabel('Number of Collaborations', fontsize=12)
    
    # Rotate x-axis labels
    plt.xticks(range(len(artists)), artists, rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('relations/most_collaborative_artists.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_album_artist_distribution(album_network):
    """Create a chart showing album-artist distribution"""
    # Count albums by number of artists
    album_artist_counts = {}
    for node in album_network['nodes']:
        if node.get('type') == 'album':
            artist_count = node.get('artists_count', 1)
            album_artist_counts[artist_count] = album_artist_counts.get(artist_count, 0) + 1
    
    # Sort by artist count
    sorted_counts = sorted(album_artist_counts.items())
    
    artist_counts = [count for count, album_count in sorted_counts]
    album_counts = [album_count for count, album_count in sorted_counts]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(artist_counts, album_counts, color='lightgreen', edgecolor='darkgreen')
    
    plt.title('Albums by Number of Artists', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Artists per Album', fontsize=12)
    plt.ylabel('Number of Albums', fontsize=12)
    
    # Add value labels on bars
    for bar, count in zip(bars, album_counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('relations/album_artist_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_cluster_analysis():
    """Create visualizations for clustering analysis"""
    # Load clustering data
    clusters_df = pd.read_csv('relations/artist_clusters_simple.csv')
    
    # Create popularity distribution
    plt.figure(figsize=(12, 8))
    
    # Subplot 1: Popularity clusters
    plt.subplot(2, 2, 1)
    popularity_counts = clusters_df['popularity_cluster'].value_counts()
    plt.pie(popularity_counts.values, labels=popularity_counts.index, autopct='%1.1f%%')
    plt.title('Artists by Popularity Cluster')
    
    # Subplot 2: Danceability clusters
    plt.subplot(2, 2, 2)
    dance_counts = clusters_df['danceability_cluster'].value_counts()
    plt.pie(dance_counts.values, labels=dance_counts.index, autopct='%1.1f%%')
    plt.title('Artists by Danceability Cluster')
    
    # Subplot 3: Energy clusters
    plt.subplot(2, 2, 3)
    energy_counts = clusters_df['energy_cluster'].value_counts()
    plt.pie(energy_counts.values, labels=energy_counts.index, autopct='%1.1f%%')
    plt.title('Artists by Energy Cluster')
    
    # Subplot 4: Popularity vs Danceability scatter
    plt.subplot(2, 2, 4)
    plt.scatter(clusters_df['popularity_mean'], clusters_df['danceability_mean'], alpha=0.6)
    plt.xlabel('Average Popularity')
    plt.ylabel('Average Danceability')
    plt.title('Popularity vs Danceability')
    
    plt.tight_layout()
    plt.savefig('relations/cluster_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_network_summary():
    """Generate a summary of network statistics"""
    artist_network, album_network, collaborations = load_network_data()
    
    print("=== Network Analysis Summary ===\n")
    
    # Artist network statistics
    print("Artist Collaboration Network:")
    print(f"- Total artists: {len(artist_network['nodes'])}")
    print(f"- Total collaborations: {len(artist_network['edges'])}")
    
    # Calculate average collaborations per artist
    total_collaborations = sum(node['collaborations'] for node in artist_network['nodes'])
    avg_collaborations = total_collaborations / len(artist_network['nodes'])
    print(f"- Average collaborations per artist: {avg_collaborations:.1f}")
    
    # Album network statistics
    album_nodes = [node for node in album_network['nodes'] if node.get('type') == 'album']
    artist_nodes = [node for node in album_network['nodes'] if node.get('type') == 'artist']
    
    print(f"\nAlbum-Artist Network:")
    print(f"- Total albums: {len(album_nodes)}")
    print(f"- Total artists: {len(artist_nodes)}")
    print(f"- Total relationships: {len(album_network['edges'])}")
    
    # Calculate average artists per album
    total_artists_in_albums = sum(node.get('artists_count', 1) for node in album_nodes)
    avg_artists_per_album = total_artists_in_albums / len(album_nodes)
    print(f"- Average artists per album: {avg_artists_per_album:.1f}")
    
    # Collaboration statistics
    print(f"\nCollaboration Statistics:")
    print(f"- Total unique collaborations: {len(collaborations)}")
    
    # Find most frequent collaboration
    most_frequent = max(collaborations.items(), key=lambda x: x[1])
    print(f"- Most frequent collaboration: {most_frequent[0]} ({most_frequent[1]} songs)")
    
    # Find artists with most collaborations
    artist_collaboration_counts = {}
    for node in artist_network['nodes']:
        artist_collaboration_counts[node['label']] = node['collaborations']
    
    top_collaborator = max(artist_collaboration_counts.items(), key=lambda x: x[1])
    print(f"- Most collaborative artist: {top_collaborator[0]} ({top_collaborator[1]} collaborations)")

def main():
    """Run all visualizations"""
    print("Creating network visualizations...")
    
    # Load data
    artist_network, album_network, collaborations = load_network_data()
    
    # Create visualizations
    print("1. Creating collaboration chart...")
    create_collaboration_chart(collaborations)
    
    print("2. Creating artist popularity chart...")
    create_artist_popularity_chart(artist_network)
    
    print("3. Creating album-artist distribution...")
    create_album_artist_distribution(album_network)
    
    print("4. Creating cluster analysis...")
    create_cluster_analysis()
    
    print("5. Generating network summary...")
    generate_network_summary()
    
    print("\n=== Visualization Complete ===")
    print("Files created:")
    print("- relations/top_collaborations.png")
    print("- relations/most_collaborative_artists.png")
    print("- relations/album_artist_distribution.png")
    print("- relations/cluster_analysis.png")

if __name__ == "__main__":
    main() 