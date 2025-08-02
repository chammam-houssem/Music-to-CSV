import json
import pandas as pd
import html

def load_network_data():
    """Load the network data from JSON files"""
    with open('relations/artist_network.json', 'r') as f:
        artist_network = json.load(f)
    
    with open('relations/album_network.json', 'r') as f:
        album_network = json.load(f)
    
    with open('relations/collaborations.json', 'r') as f:
        collaborations = json.load(f)
    
    return artist_network, album_network, collaborations

def create_collaboration_html(collaborations):
    """Create HTML table of top collaborations"""
    # Sort collaborations by count
    sorted_collaborations = sorted(collaborations.items(), key=lambda x: x[1], reverse=True)[:20]
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Top Artist Collaborations</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .rank { font-weight: bold; color: #333; }
            .count { font-weight: bold; color: #0066cc; }
        </style>
    </head>
    <body>
        <h1>Top 20 Artist Collaborations</h1>
        <table>
            <tr>
                <th>Rank</th>
                <th>Artist Pair</th>
                <th>Songs Together</th>
            </tr>
    """
    
    for i, (collab, count) in enumerate(sorted_collaborations, 1):
        html_content += f"""
            <tr>
                <td class="rank">{i}</td>
                <td>{html.escape(collab)}</td>
                <td class="count">{count}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open('relations/top_collaborations.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Created: relations/top_collaborations.html")

def create_artist_network_html(artist_network):
    """Create HTML table of most collaborative artists"""
    # Get collaboration counts for each artist
    artist_counts = {}
    for node in artist_network['nodes']:
        artist_counts[node['label']] = node['collaborations']
    
    # Get top 30 most collaborative artists
    top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:30]
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Most Collaborative Artists</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .rank { font-weight: bold; color: #333; }
            .count { font-weight: bold; color: #cc0066; }
        </style>
    </head>
    <body>
        <h1>Top 30 Most Collaborative Artists</h1>
        <table>
            <tr>
                <th>Rank</th>
                <th>Artist</th>
                <th>Number of Collaborations</th>
            </tr>
    """
    
    for i, (artist, count) in enumerate(top_artists, 1):
        html_content += f"""
            <tr>
                <td class="rank">{i}</td>
                <td>{html.escape(artist)}</td>
                <td class="count">{count}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open('relations/most_collaborative_artists.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Created: relations/most_collaborative_artists.html")

def create_album_network_html(album_network):
    """Create HTML table of album-artist relationships"""
    # Get albums with multiple artists
    collaborative_albums = []
    for node in album_network['nodes']:
        if node.get('type') == 'album' and node.get('artists_count', 1) > 1:
            collaborative_albums.append({
                'album': node['label'],
                'artists_count': node.get('artists_count', 1)
            })
    
    # Sort by number of artists
    collaborative_albums.sort(key=lambda x: x['artists_count'], reverse=True)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Most Collaborative Albums</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .rank { font-weight: bold; color: #333; }
            .count { font-weight: bold; color: #006600; }
        </style>
    </head>
    <body>
        <h1>Most Collaborative Albums</h1>
        <table>
            <tr>
                <th>Rank</th>
                <th>Album</th>
                <th>Number of Artists</th>
            </tr>
    """
    
    for i, album_data in enumerate(collaborative_albums[:30], 1):
        html_content += f"""
            <tr>
                <td class="rank">{i}</td>
                <td>{html.escape(album_data['album'])}</td>
                <td class="count">{album_data['artists_count']}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open('relations/collaborative_albums.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Created: relations/collaborative_albums.html")

def create_cluster_analysis_html():
    """Create HTML visualization of clustering analysis"""
    # Load clustering data
    clusters_df = pd.read_csv('relations/artist_clusters_simple.csv')
    
    # Create popularity cluster summary
    popularity_summary = clusters_df['popularity_cluster'].value_counts()
    dance_summary = clusters_df['danceability_cluster'].value_counts()
    energy_summary = clusters_df['energy_cluster'].value_counts()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Artist Clustering Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .cluster-section { margin: 20px 0; }
            table { border-collapse: collapse; width: 100%; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .cluster-name { font-weight: bold; color: #333; }
            .count { font-weight: bold; color: #0066cc; }
            .percentage { color: #666; }
        </style>
    </head>
    <body>
        <h1>Artist Clustering Analysis</h1>
        
        <div class="cluster-section">
            <h2>Popularity Clusters</h2>
            <table>
                <tr>
                    <th>Cluster</th>
                    <th>Number of Artists</th>
                    <th>Percentage</th>
                </tr>
    """
    
    total_artists = len(clusters_df)
    for cluster, count in popularity_summary.items():
        percentage = (count / total_artists) * 100
        html_content += f"""
                <tr>
                    <td class="cluster-name">{cluster}</td>
                    <td class="count">{count}</td>
                    <td class="percentage">{percentage:.1f}%</td>
                </tr>
        """
    
    html_content += """
            </table>
        </div>
        
        <div class="cluster-section">
            <h2>Danceability Clusters</h2>
            <table>
                <tr>
                    <th>Cluster</th>
                    <th>Number of Artists</th>
                    <th>Percentage</th>
                </tr>
    """
    
    for cluster, count in dance_summary.items():
        percentage = (count / total_artists) * 100
        html_content += f"""
                <tr>
                    <td class="cluster-name">{cluster}</td>
                    <td class="count">{count}</td>
                    <td class="percentage">{percentage:.1f}%</td>
                </tr>
        """
    
    html_content += """
            </table>
        </div>
        
        <div class="cluster-section">
            <h2>Energy Clusters</h2>
            <table>
                <tr>
                    <th>Cluster</th>
                    <th>Number of Artists</th>
                    <th>Percentage</th>
                </tr>
    """
    
    for cluster, count in energy_summary.items():
        percentage = (count / total_artists) * 100
        html_content += f"""
                <tr>
                    <td class="cluster-name">{cluster}</td>
                    <td class="count">{count}</td>
                    <td class="percentage">{percentage:.1f}%</td>
                </tr>
        """
    
    html_content += """
            </table>
        </div>
        
        <div class="cluster-section">
            <h2>Top Artists by Popularity</h2>
            <table>
                <tr>
                    <th>Rank</th>
                    <th>Artist</th>
                    <th>Average Popularity</th>
                    <th>Cluster</th>
                </tr>
    """
    
    # Get top 20 artists by popularity
    top_artists = clusters_df.nlargest(20, 'popularity_mean')[['artist', 'popularity_mean', 'popularity_cluster']]
    
    for i, (_, row) in enumerate(top_artists.iterrows(), 1):
        html_content += f"""
                <tr>
                    <td class="rank">{i}</td>
                    <td>{html.escape(row['artist'])}</td>
                    <td class="count">{row['popularity_mean']:.1f}</td>
                    <td class="cluster-name">{row['popularity_cluster']}</td>
                </tr>
        """
    
    html_content += """
            </table>
        </div>
    </body>
    </html>
    """
    
    with open('relations/cluster_analysis.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Created: relations/cluster_analysis.html")

def create_network_summary_html():
    """Create HTML summary of network statistics"""
    artist_network, album_network, collaborations = load_network_data()
    
    # Calculate statistics
    total_artists = len(artist_network['nodes'])
    total_collaborations = len(artist_network['edges'])
    total_collaboration_count = sum(node['collaborations'] for node in artist_network['nodes'])
    avg_collaborations = total_collaboration_count / total_artists
    
    album_nodes = [node for node in album_network['nodes'] if node.get('type') == 'album']
    artist_nodes = [node for node in album_network['nodes'] if node.get('type') == 'artist']
    total_albums = len(album_nodes)
    total_album_artists = len(artist_nodes)
    total_relationships = len(album_network['edges'])
    
    total_artists_in_albums = sum(node.get('artists_count', 1) for node in album_nodes)
    avg_artists_per_album = total_artists_in_albums / total_albums
    
    most_frequent = max(collaborations.items(), key=lambda x: x[1])
    
    artist_collaboration_counts = {}
    for node in artist_network['nodes']:
        artist_collaboration_counts[node['label']] = node['collaborations']
    
    top_collaborator = max(artist_collaboration_counts.items(), key=lambda x: x[1])
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Analysis Summary</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .stat {{ margin: 10px 0; }}
            .stat-name {{ font-weight: bold; color: #333; }}
            .stat-value {{ color: #0066cc; font-weight: bold; }}
            .highlight {{ background-color: #f0f8ff; padding: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Network Analysis Summary</h1>
        
        <div class="section">
            <h2>Artist Collaboration Network</h2>
            <div class="stat">
                <span class="stat-name">Total Artists:</span>
                <span class="stat-value">{total_artists}</span>
            </div>
            <div class="stat">
                <span class="stat-name">Total Collaborations:</span>
                <span class="stat-value">{total_collaborations}</span>
            </div>
            <div class="stat">
                <span class="stat-name">Average Collaborations per Artist:</span>
                <span class="stat-value">{avg_collaborations:.1f}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>Album-Artist Network</h2>
            <div class="stat">
                <span class="stat-name">Total Albums:</span>
                <span class="stat-value">{total_albums}</span>
            </div>
            <div class="stat">
                <span class="stat-name">Total Artists:</span>
                <span class="stat-value">{total_album_artists}</span>
            </div>
            <div class="stat">
                <span class="stat-name">Total Relationships:</span>
                <span class="stat-value">{total_relationships}</span>
            </div>
            <div class="stat">
                <span class="stat-name">Average Artists per Album:</span>
                <span class="stat-value">{avg_artists_per_album:.1f}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>Key Insights</h2>
            <div class="highlight">
                <div class="stat">
                    <span class="stat-name">Most Frequent Collaboration:</span>
                    <span class="stat-value">{html.escape(most_frequent[0])} ({most_frequent[1]} songs)</span>
                </div>
                <div class="stat">
                    <span class="stat-name">Most Collaborative Artist:</span>
                    <span class="stat-value">{html.escape(top_collaborator[0])} ({top_collaborator[1]} collaborations)</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('relations/network_summary.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Created: relations/network_summary.html")

def main():
    """Create all HTML visualizations"""
    print("Creating HTML-based network visualizations...")
    
    # Load data
    artist_network, album_network, collaborations = load_network_data()
    
    # Create visualizations
    print("1. Creating collaboration analysis...")
    create_collaboration_html(collaborations)
    
    print("2. Creating artist network analysis...")
    create_artist_network_html(artist_network)
    
    print("3. Creating album network analysis...")
    create_album_network_html(album_network)
    
    print("4. Creating cluster analysis...")
    create_cluster_analysis_html()
    
    print("5. Creating network summary...")
    create_network_summary_html()
    
    print("\n=== HTML Visualization Complete ===")
    print("Files created:")
    print("- relations/top_collaborations.html")
    print("- relations/most_collaborative_artists.html")
    print("- relations/collaborative_albums.html")
    print("- relations/cluster_analysis.html")
    print("- relations/network_summary.html")
    print("\nOpen these HTML files in your browser to view the visualizations!")

if __name__ == "__main__":
    main() 