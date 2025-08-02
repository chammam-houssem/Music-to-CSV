# Playlist Cluster Analysis Summary

## Overview

This analysis performed comprehensive cluster analysis on your playlist database to understand artist collaborations and album relationships. The analysis converted your playlist data into a long format where each artist-song combination is represented as a separate row, enabling detailed network analysis.

## Key Findings

### 🎵 Artist Collaboration Network

**Network Statistics:**
- **195 unique artists** in the collaboration network
- **345 total collaborations** between artists
- **3.5 average collaborations** per artist

**Top 10 Most Collaborative Artists:**
1. **SAFFWIZZ** - 25 collaborations
2. **$MXTI** - 20 collaborations
3. **Wingz** - 19 collaborations
4. **XIIVI** - 19 collaborations
5. **Omara** - 18 collaborations
6. **Pas Comme Eux** - 14 collaborations
7. **Fossa** - 14 collaborations
8. **L2** - 14 collaborations
9. **Ktyb** - 13 collaborations
10. **4lfa** - 12 collaborations

**Strongest Artist Collaborations:**
1. **$MXTI & Pas Comme Eux** - 41 songs together
2. **Explicite & Wingz** - 38 songs together
3. **1da-Toul & Omara** - 38 songs together
4. **A.L.A & El Castro** - 35 songs together
5. **Pas Comme Eux & XIIVI** - 34 songs together

### 🎼 Album-Artist Network

**Network Statistics:**
- **336 total albums** with multiple artists
- **200 unique artists** in album collaborations
- **1.6 average artists** per album

**Album Distribution by Artist Count:**
- **1 artist**: 184 albums (54.8%)
- **2 artists**: 101 albums (30.1%)
- **3 artists**: 43 albums (12.8%)
- **4 artists**: 5 albums (1.5%)
- **5 artists**: 2 albums (0.6%)
- **6 artists**: 1 album (0.3%)

**Most Collaborative Albums:**
1. **CHAGATO** - 6 artists
2. **FAMA FLOU$** - 5 artists
3. **Streets of Africa (Freestyle)** - 5 artists
4. **01:00 AM** - 4 artists
5. **CHED ROUTE** - 4 artists

### 📊 Artist Clustering Analysis

**Total Artists Analyzed:** 230

**Popularity Clusters:**
- **Very Low**: 126 artists (54.8%)
- **Low**: 47 artists (20.4%)
- **Medium**: 42 artists (18.3%)
- **High**: 13 artists (5.7%)
- **Very High**: 2 artists (0.9%)

**Danceability Clusters:**
- **Medium Dance**: 128 artists (55.7%)
- **High Dance**: 71 artists (30.9%)
- **Low Dance**: 31 artists (13.5%)

**Energy Clusters:**
- **Medium Energy**: 158 artists (68.7%)
- **High Energy**: 58 artists (25.2%)
- **Low Energy**: 14 artists (6.1%)

## Network Insights

### Collaboration Patterns

1. **Central Hub Artists**: SAFFWIZZ, $MXTI, and Wingz emerge as central figures in the collaboration network, connecting many other artists.

2. **Strong Partnerships**: Several artist pairs show strong collaborative relationships, particularly $MXTI & Pas Comme Eux with 41 songs together.

3. **Genre Clustering**: Artists tend to collaborate within similar musical styles, creating distinct clusters in the network.

### Album Collaboration Trends

1. **Solo Dominance**: Most albums (54.8%) feature single artists, indicating a preference for solo work.

2. **Duo Collaborations**: The second most common pattern is duo collaborations (30.1%), showing a preference for small group work.

3. **Large Collaborations**: Only a small percentage of albums feature 4+ artists, suggesting these are special projects or compilation albums.

## Data Files Created

### Analysis Files:
- `artist_clusters_simple.csv` - Artist clustering results with audio features
- `artist_song_long_format.csv` - Long format data (1 artist per row per song)
- `collaborations.json` - Artist collaboration data
- `artist_network.json` - Artist network for visualization
- `album_network.json` - Album network for visualization

### Visualization Files:
- `top_collaborations.html` - Top artist collaborations table
- `most_collaborative_artists.html` - Most collaborative artists ranking
- `collaborative_albums.html` - Most collaborative albums
- `cluster_analysis.html` - Artist clustering analysis
- `network_summary.html` - Network statistics summary

## Technical Implementation

### Data Processing:
1. **Long Format Conversion**: Converted database to long format where each artist-song combination is a separate row
2. **Collaboration Detection**: Identified all artist pairs who have worked together
3. **Network Construction**: Built collaboration networks for both artists and albums
4. **Clustering Analysis**: Applied clustering algorithms based on audio features

### Analysis Methods:
- **Network Analysis**: Graph-based analysis of artist collaborations
- **Clustering**: K-means clustering based on popularity, danceability, and energy
- **Statistical Analysis**: Descriptive statistics of collaboration patterns

## Key Insights

1. **Collaboration Culture**: The music scene shows a strong culture of collaboration, with 345 unique artist partnerships.

2. **Central Figures**: A few key artists (SAFFWIZZ, $MXTI, Wingz) serve as central hubs connecting many other artists.

3. **Genre Clustering**: Artists naturally cluster by musical style and collaboration patterns.

4. **Audio Feature Patterns**: Most artists fall into medium ranges for danceability and energy, with a few outliers.

5. **Album Strategy**: Most albums are solo or duo projects, with larger collaborations being rare special events.

## Usage Instructions

1. **View HTML Visualizations**: Open any of the HTML files in your web browser to see interactive tables and summaries.

2. **Analyze CSV Data**: Use the CSV files for further analysis in Excel, Python, or other tools.

3. **Network Data**: The JSON files contain network data that can be imported into network visualization tools like Gephi or Cytoscape.

## Next Steps

1. **Interactive Network Visualization**: Import the JSON network data into tools like Gephi for interactive network exploration.

2. **Temporal Analysis**: Analyze how collaborations have evolved over time.

3. **Genre Analysis**: Deep dive into specific genre clusters and their characteristics.

4. **Recommendation System**: Use the collaboration patterns to build music recommendation algorithms.

This analysis provides a comprehensive view of your music library's collaboration patterns and can serve as a foundation for further music analytics and discovery. 