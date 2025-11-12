"""
Artist Data Explorer
Interactive utility for querying and analyzing artist data
"""

import json
import pandas as pd
from typing import List, Dict

class ArtistExplorer:
    def __init__(self, json_path='artist_analysis.json'):
        """Load artist analysis results"""
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        self.artists = self.data['artists']
        self.summary = self.data['summary']
        
    def find_artist(self, name: str) -> Dict:
        """Search for an artist by name (case-insensitive, partial match)"""
        name_lower = name.lower()
        matches = {k: v for k, v in self.artists.items() 
                  if name_lower in k.lower()}
        
        if len(matches) == 0:
            print(f"No artists found matching '{name}'")
            return None
        elif len(matches) == 1:
            artist_name = list(matches.keys())[0]
            return {artist_name: matches[artist_name]}
        else:
            print(f"Found {len(matches)} matches:")
            for i, artist in enumerate(matches.keys(), 1):
                print(f"{i}. {artist}")
            return matches
    
    def top_artists_by(self, metric: str, n: int = 10, min_songs: int = 1) -> List:
        """
        Get top N artists by any metric
        
        Args:
            metric: 'revenue', 'hit_rate', 'songs', 'hits', etc.
            n: number of results
            min_songs: minimum song count requirement
        """
        # Map common terms to actual keys
        metric_map = {
            'revenue': 'estimated_total_revenue',
            'money': 'estimated_total_revenue',
            'hit_rate': 'hit_rate',
            'hits': 'hit_songs',
            'songs': 'total_songs',
            'career': 'career_span_years',
            'energy': 'avg_energy',
            'danceability': 'avg_danceability'
        }
        
        key = metric_map.get(metric.lower(), metric)
        
        # Filter by minimum songs
        eligible = {k: v for k, v in self.artists.items() 
                   if v['total_songs'] >= min_songs}
        
        # Sort and get top N
        sorted_artists = sorted(eligible.items(), 
                               key=lambda x: x[1].get(key, 0), 
                               reverse=True)[:n]
        
        return sorted_artists
    
    def compare_artists(self, *artist_names: str) -> pd.DataFrame:
        """Compare multiple artists side-by-side"""
        comparison_data = {}
        
        for name in artist_names:
            if name in self.artists:
                comparison_data[name] = self.artists[name]
            else:
                # Try to find partial match
                matches = self.find_artist(name)
                if matches and len(matches) == 1:
                    artist_name = list(matches.keys())[0]
                    comparison_data[artist_name] = matches[artist_name]
        
        if not comparison_data:
            print("No valid artists found for comparison")
            return None
        
        # Select key metrics for comparison
        metrics = [
            'total_songs', 'hit_songs', 'good_songs', 'mid_songs', 'bust_songs',
            'hit_rate', 'good_rate', 'estimated_total_revenue', 
            'avg_revenue_per_song', 'career_span_years',
            'avg_energy', 'avg_danceability', 'primary_genre'
        ]
        
        comparison = {}
        for artist, data in comparison_data.items():
            comparison[artist] = {m: data.get(m, 'N/A') for m in metrics}
        
        df = pd.DataFrame(comparison).T
        return df
    
    def genre_analysis(self) -> Dict:
        """Analyze performance by genre"""
        genre_stats = {}
        
        for artist, data in self.artists.items():
            genre = data.get('primary_genre')
            if not genre:
                continue
                
            if genre not in genre_stats:
                genre_stats[genre] = {
                    'artists': 0,
                    'total_songs': 0,
                    'total_hits': 0,
                    'total_revenue': 0,
                    'hit_rates': []
                }
            
            genre_stats[genre]['artists'] += 1
            genre_stats[genre]['total_songs'] += data['total_songs']
            genre_stats[genre]['total_hits'] += data['hit_songs']
            genre_stats[genre]['total_revenue'] += data['estimated_total_revenue']
            genre_stats[genre]['hit_rates'].append(data['hit_rate'])
        
        # Calculate averages
        for genre, stats in genre_stats.items():
            stats['avg_hit_rate'] = sum(stats['hit_rates']) / len(stats['hit_rates'])
            stats['avg_revenue_per_artist'] = stats['total_revenue'] / stats['artists']
            del stats['hit_rates']  # Remove raw list
        
        return genre_stats
    
    def career_stage_analysis(self) -> Dict:
        """Analyze artists by career stage (years active)"""
        stages = {
            'New (0-2 years)': [],
            'Emerging (2-5 years)': [],
            'Established (5-10 years)': [],
            'Veteran (10+ years)': []
        }
        
        for artist, data in self.artists.items():
            years = data.get('career_span_years', 0)
            
            if years <= 2:
                stages['New (0-2 years)'].append((artist, data))
            elif years <= 5:
                stages['Emerging (2-5 years)'].append((artist, data))
            elif years <= 10:
                stages['Established (5-10 years)'].append((artist, data))
            else:
                stages['Veteran (10+ years)'].append((artist, data))
        
        # Calculate stage statistics
        stage_stats = {}
        for stage, artists in stages.items():
            if not artists:
                continue
                
            stage_stats[stage] = {
                'count': len(artists),
                'avg_hit_rate': sum(d['hit_rate'] for _, d in artists) / len(artists),
                'avg_songs': sum(d['total_songs'] for _, d in artists) / len(artists),
                'avg_revenue': sum(d['estimated_total_revenue'] for _, d in artists) / len(artists)
            }
        
        return stage_stats
    
    def print_artist_profile(self, artist_name: str):
        """Print detailed profile for an artist"""
        if artist_name not in self.artists:
            matches = self.find_artist(artist_name)
            if not matches or len(matches) != 1:
                return
            artist_name = list(matches.keys())[0]
        
        data = self.artists[artist_name]
        
        print("\n" + "="*80)
        print(f"ARTIST PROFILE: {artist_name}")
        print("="*80)
        
        print("\n📊 OVERVIEW")
        print(f"Total Songs: {data['total_songs']}")
        print(f"Career Span: {data['career_span_years']} years ({data['first_release']} to {data['last_release']})")
        print(f"Primary Genre: {data['primary_genre']}")
        
        print("\n🎵 SONG BREAKDOWN")
        print(f"  Hits (80-100):  {data['hit_songs']:3d} ({data['hit_rate']:5.1f}%)")
        print(f"  Good (65-79):   {data['good_songs']:3d} ({data['good_rate']:5.1f}%)")
        print(f"  Mid (35-64):    {data['mid_songs']:3d} ({data['mid_rate']:5.1f}%)")
        print(f"  Bust (0-34):    {data['bust_songs']:3d} ({data['bust_rate']:5.1f}%)")
        
        print("\n💰 REVENUE")
        print(f"Total Estimated Revenue: ${data['estimated_total_revenue']:,.2f}")
        print(f"Average per Song: ${data['avg_revenue_per_song']:,.2f}")
        
        print("\n🎼 AUDIO PROFILE")
        print(f"Energy: {data['avg_energy']:.1f} | Danceability: {data['avg_danceability']:.1f}")
        print(f"Positiveness: {data['avg_positiveness']:.1f} | Speechiness: {data['avg_speechiness']:.1f}")
        print(f"Liveness: {data['avg_liveness']:.1f} | Acousticness: {data['avg_acousticness']:.1f}")
        
        print("\n📝 CONTENT")
        print(f"Explicit Content: {data['explicit_ratio']:.1f}%")
        
        if len(data.get('genre_distribution', {})) > 1:
            print("\nGenre Distribution:")
            for genre, count in sorted(data['genre_distribution'].items(), 
                                       key=lambda x: x[1], reverse=True):
                print(f"  {genre}: {count}")
        
        print("\n🎵 TOP SONGS (by estimated revenue)")
        top_songs = sorted(data['songs'], key=lambda x: x['revenue'], reverse=True)[:5]
        for i, song in enumerate(top_songs, 1):
            print(f"{i}. {song['title']}")
            print(f"   Pop: {song['popularity']} | Tier: {song['tier'].upper()} | "
                  f"Revenue: ${song['revenue']:,.0f} | Released: {song['release_date']}")
        
        print("="*80 + "\n")


# Example usage
if __name__ == "__main__":
    explorer = ArtistExplorer('/mnt/user-data/outputs/artist_analysis.json')
    
    print("="*80)
    print("DATASET SUMMARY")
    print("="*80)
    for key, value in explorer.summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:,.2f}")
        else:
            print(f"{key}: {value:,}")
    
    print("\n" + "="*80)
    print("TOP 10 ARTISTS BY REVENUE")
    print("="*80)
    top_revenue = explorer.top_artists_by('revenue', n=10)
    for i, (artist, data) in enumerate(top_revenue, 1):
        print(f"{i}. {artist}: ${data['estimated_total_revenue']:,.2f} "
              f"({data['total_songs']} songs, {data['hit_rate']:.1f}% hit rate)")
    
    print("\n" + "="*80)
    print("GENRE ANALYSIS")
    print("="*80)
    genres = explorer.genre_analysis()
    for genre, stats in sorted(genres.items(), 
                               key=lambda x: x[1]['total_revenue'], 
                               reverse=True)[:10]:
        print(f"\n{genre.upper()}")
        print(f"  Artists: {stats['artists']}")
        print(f"  Songs: {stats['total_songs']}")
        print(f"  Hits: {stats['total_hits']}")
        print(f"  Avg Hit Rate: {stats['avg_hit_rate']:.1f}%")
        print(f"  Total Revenue: ${stats['total_revenue']:,.2f}")
    
    print("\n" + "="*80)
    print("CAREER STAGE ANALYSIS")
    print("="*80)
    stages = explorer.career_stage_analysis()
    for stage, stats in stages.items():
        print(f"\n{stage}")
        print(f"  Artists: {stats['count']}")
        print(f"  Avg Hit Rate: {stats['avg_hit_rate']:.1f}%")
        print(f"  Avg Songs: {stats['avg_songs']:.1f}")
        print(f"  Avg Revenue: ${stats['avg_revenue']:,.2f}")
    
    # Example: Print detailed profile for first artist
    if explorer.artists:
        first_artist = list(explorer.artists.keys())[0]
        explorer.print_artist_profile(first_artist)
