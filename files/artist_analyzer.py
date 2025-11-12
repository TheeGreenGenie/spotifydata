"""
Artist Performance and Revenue Analyzer
Analyzes songs from CSV to build artist performance dictionary with revenue predictions
"""

import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
import json

class ArtistAnalyzer:
    def __init__(self, csv_path):
        """Initialize analyzer with CSV data"""
        print("Loading data...")
        self.df = pd.read_csv(csv_path)
        print(f"Loaded {len(self.df)} songs")
        
        # Revenue benchmark based on research and reference songs
        # These are estimated total revenues (streaming + sales + other) per popularity tier
        self.revenue_benchmarks = self._create_revenue_benchmarks()
        
        # Song classification tiers
        self.tier_definitions = {
            'hit': (80, 100),      # 80-100
            'good': (65, 79),      # 65-79
            'mid': (35, 64),       # 35-64
            'bust': (0, 34)        # 0-34
        }
        
    def _create_revenue_benchmarks(self):
        """
        Create revenue estimation model based on popularity scores
        
        Reference songs and their estimated revenues:
        - 100 (HMT Billie Eilish): ~$30M (7B+ streams, album part)
        - 90 (One Dance Drake): ~$15M (3B+ streams, massive hit)
        - 80 (Cash n Gas Kaash Paige): ~$2M (moderate hit)
        - 70 ($uicideboy$ song): ~$800K (good performance)
        - 60 ($ilkMoney song): ~$350K (decent streams)
        - 50 (Whoa in Woeful): ~$150K (average performance)
        - 40 (Handy Weird Al): ~$75K (below average)
        - 30 (Skipper Dan): ~$30K (low streams)
        - 20 (Cool of Lullaby): ~$12K (very low)
        - 10 (Confidence Mayday): ~$5K (minimal)
        - 0 (Very Bieber Christmas): ~$500 (almost none)
        
        Model: Exponential growth as popularity increases
        """
        benchmarks = {
            0: 500,
            10: 5000,
            20: 12000,
            30: 30000,
            40: 75000,
            50: 150000,
            60: 350000,
            70: 800000,
            80: 2000000,
            90: 15000000,
            100: 30000000
        }
        return benchmarks
    
    def estimate_song_revenue(self, popularity):
        """
        Estimate revenue for a song based on its popularity score
        Uses interpolation between benchmark points
        """
        if pd.isna(popularity):
            return 0
        
        popularity = int(popularity)
        
        # Find the two nearest benchmark points
        lower_bound = (popularity // 10) * 10
        upper_bound = min(lower_bound + 10, 100)
        
        if lower_bound == upper_bound:
            return self.revenue_benchmarks[lower_bound]
        
        # Linear interpolation between benchmark points
        lower_revenue = self.revenue_benchmarks[lower_bound]
        upper_revenue = self.revenue_benchmarks[upper_bound]
        
        # Calculate interpolated value
        fraction = (popularity - lower_bound) / 10
        estimated_revenue = lower_revenue + (upper_revenue - lower_revenue) * fraction
        
        return estimated_revenue
    
    def classify_song(self, popularity):
        """Classify song into tier based on popularity"""
        if pd.isna(popularity):
            return 'unknown'
        
        for tier, (min_pop, max_pop) in self.tier_definitions.items():
            if min_pop <= popularity <= max_pop:
                return tier
        return 'unknown'
    
    def parse_artists(self, artist_string):
        """
        Parse artist string to handle multiple artists
        Handles formats like: "Artist1,Artist2" or "Artist1"
        """
        if pd.isna(artist_string):
            return []
        
        # Split by comma and clean up
        artists = [a.strip() for a in str(artist_string).split(',')]
        return [a for a in artists if a]  # Remove empty strings
    
    def parse_release_date(self, date_string):
        """Parse release date string to datetime"""
        if pd.isna(date_string):
            return None
        try:
            return pd.to_datetime(date_string)
        except:
            return None
    
    def analyze_artists(self):
        """
        Main analysis function to build artist dictionary
        Returns comprehensive artist performance data
        """
        print("\nAnalyzing artists...")
        artist_data = defaultdict(lambda: {
            'songs': [],
            'total_songs': 0,
            'hit_songs': 0,
            'good_songs': 0,
            'mid_songs': 0,
            'bust_songs': 0,
            'total_revenue': 0,
            'genres': defaultdict(int),
            'explicit_count': 0,
            'release_dates': [],
            'audio_features': {
                'energy': [],
                'danceability': [],
                'positiveness': [],
                'speechiness': [],
                'liveness': [],
                'acousticness': [],
                'instrumentalness': []
            }
        })
        
        # Process each song
        for idx, row in self.df.iterrows():
            artists = self.parse_artists(row['Artist(s)'])
            popularity = row['Popularity']
            tier = self.classify_song(popularity)
            revenue = self.estimate_song_revenue(popularity)
            
            # Update data for each artist on the song
            for artist in artists:
                data = artist_data[artist]
                
                # Basic counts
                data['total_songs'] += 1
                data['songs'].append({
                    'title': row['song'],
                    'popularity': popularity,
                    'tier': tier,
                    'revenue': revenue,
                    'release_date': row['Release Date']
                })
                
                # Tier counts
                if tier == 'hit':
                    data['hit_songs'] += 1
                elif tier == 'good':
                    data['good_songs'] += 1
                elif tier == 'mid':
                    data['mid_songs'] += 1
                elif tier == 'bust':
                    data['bust_songs'] += 1
                
                # Revenue
                data['total_revenue'] += revenue
                
                # Genre tracking
                if not pd.isna(row['Genre']):
                    data['genres'][row['Genre']] += 1
                
                # Explicit content
                if row['Explicit'] == 'Yes':
                    data['explicit_count'] += 1
                
                # Release dates
                release_date = self.parse_release_date(row['Release Date'])
                if release_date:
                    data['release_dates'].append(release_date)
                
                # Audio features
                for feature in data['audio_features'].keys():
                    if feature.capitalize() in row and not pd.isna(row[feature.capitalize()]):
                        data['audio_features'][feature].append(row[feature.capitalize()])
        
        print(f"Analyzed {len(artist_data)} unique artists")
        
        # Calculate derived metrics
        print("Calculating derived metrics...")
        final_data = {}
        
        for artist, data in artist_data.items():
            # Calculate rates
            total = data['total_songs']
            hit_rate = (data['hit_songs'] / total * 100) if total > 0 else 0
            good_rate = (data['good_songs'] / total * 100) if total > 0 else 0
            mid_rate = (data['mid_songs'] / total * 100) if total > 0 else 0
            bust_rate = (data['bust_songs'] / total * 100) if total > 0 else 0
            
            # Average revenue per song
            avg_revenue = data['total_revenue'] / total if total > 0 else 0
            
            # Explicit content ratio
            explicit_ratio = (data['explicit_count'] / total * 100) if total > 0 else 0
            
            # Primary genre (most common)
            primary_genre = max(data['genres'].items(), key=lambda x: x[1])[0] if data['genres'] else None
            
            # Calculate average audio features
            avg_features = {}
            for feature, values in data['audio_features'].items():
                avg_features[f'avg_{feature}'] = np.mean(values) if values else 0
            
            # Career timeline
            if data['release_dates']:
                first_release = min(data['release_dates'])
                last_release = max(data['release_dates'])
                career_span_days = (last_release - first_release).days
                career_span_years = career_span_days / 365.25
            else:
                first_release = None
                last_release = None
                career_span_years = 0
            
            # Build final artist dictionary
            final_data[artist] = {
                # Basic counts
                'total_songs': total,
                'hit_songs': data['hit_songs'],
                'good_songs': data['good_songs'],
                'mid_songs': data['mid_songs'],
                'bust_songs': data['bust_songs'],
                
                # Rates
                'hit_rate': round(hit_rate, 2),
                'good_rate': round(good_rate, 2),
                'mid_rate': round(mid_rate, 2),
                'bust_rate': round(bust_rate, 2),
                
                # Revenue
                'estimated_total_revenue': round(data['total_revenue'], 2),
                'avg_revenue_per_song': round(avg_revenue, 2),
                
                # Genre & Content
                'primary_genre': primary_genre,
                'genre_distribution': dict(data['genres']),
                'explicit_ratio': round(explicit_ratio, 2),
                
                # Timeline
                'first_release': str(first_release.date()) if first_release else None,
                'last_release': str(last_release.date()) if last_release else None,
                'career_span_years': round(career_span_years, 2),
                
                # Audio features
                **{k: round(v, 2) for k, v in avg_features.items()},
                
                # Raw song list (for reference)
                'songs': data['songs']
            }
        
        return final_data
    
    def get_summary_stats(self, artist_data):
        """Generate summary statistics across all artists"""
        total_artists = len(artist_data)
        total_songs = sum(data['total_songs'] for data in artist_data.values())
        total_revenue = sum(data['estimated_total_revenue'] for data in artist_data.values())
        
        avg_songs_per_artist = total_songs / total_artists if total_artists > 0 else 0
        avg_revenue_per_artist = total_revenue / total_artists if total_artists > 0 else 0
        
        # Hit rate statistics
        hit_rates = [data['hit_rate'] for data in artist_data.values()]
        
        return {
            'total_artists': total_artists,
            'total_songs': total_songs,
            'total_estimated_revenue': round(total_revenue, 2),
            'avg_songs_per_artist': round(avg_songs_per_artist, 2),
            'avg_revenue_per_artist': round(avg_revenue_per_artist, 2),
            'avg_hit_rate': round(np.mean(hit_rates), 2) if hit_rates else 0,
            'median_hit_rate': round(np.median(hit_rates), 2) if hit_rates else 0
        }
    
    def save_results(self, artist_data, output_path):
        """Save results to JSON file"""
        print(f"\nSaving results to {output_path}...")
        
        # Add summary stats
        summary = self.get_summary_stats(artist_data)
        
        output = {
            'summary': summary,
            'artists': artist_data
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Saved {len(artist_data)} artists to {output_path}")
        
    def print_top_artists(self, artist_data, n=10):
        """Print top N artists by various metrics"""
        print("\n" + "="*80)
        print("TOP ARTISTS ANALYSIS")
        print("="*80)
        
        # Top by total revenue
        print(f"\nTop {n} Artists by Total Revenue:")
        sorted_by_revenue = sorted(artist_data.items(), 
                                   key=lambda x: x[1]['estimated_total_revenue'], 
                                   reverse=True)[:n]
        for i, (artist, data) in enumerate(sorted_by_revenue, 1):
            print(f"{i}. {artist}: ${data['estimated_total_revenue']:,.2f} "
                  f"({data['total_songs']} songs, {data['hit_rate']:.1f}% hit rate)")
        
        # Top by hit rate (minimum 5 songs)
        print(f"\nTop {n} Artists by Hit Rate (minimum 5 songs):")
        eligible = {k: v for k, v in artist_data.items() if v['total_songs'] >= 5}
        sorted_by_hit_rate = sorted(eligible.items(), 
                                    key=lambda x: x[1]['hit_rate'], 
                                    reverse=True)[:n]
        for i, (artist, data) in enumerate(sorted_by_hit_rate, 1):
            print(f"{i}. {artist}: {data['hit_rate']:.1f}% hit rate "
                  f"({data['hit_songs']}/{data['total_songs']} hits)")
        
        # Most prolific
        print(f"\nTop {n} Most Prolific Artists:")
        sorted_by_songs = sorted(artist_data.items(), 
                                key=lambda x: x[1]['total_songs'], 
                                reverse=True)[:n]
        for i, (artist, data) in enumerate(sorted_by_songs, 1):
            print(f"{i}. {artist}: {data['total_songs']} songs "
                  f"({data['hit_songs']} hits, ${data['avg_revenue_per_song']:,.0f} avg per song)")


def main():
    """Main execution function"""
    # Initialize analyzer
    analyzer = ArtistAnalyzer('/mnt/user-data/uploads/claude.csv')
    
    # Run analysis
    artist_data = analyzer.analyze_artists()
    
    # Print top artists
    analyzer.print_top_artists(artist_data)
    
    # Print summary statistics
    summary = analyzer.get_summary_stats(artist_data)
    print("\n" + "="*80)
    print("DATASET SUMMARY")
    print("="*80)
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:,.2f}")
        else:
            print(f"{key}: {value:,}")
    
    # Save results
    analyzer.save_results(artist_data, '/mnt/user-data/outputs/artist_analysis.json')
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()