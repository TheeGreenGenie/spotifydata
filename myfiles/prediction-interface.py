"""
Artist Success Prediction Interface
Make predictions for specific artists
"""

import json
from datetime import datetime
from ml_hit_predictor import ArtistSuccessPredictor


class PredictionInterface:
    """Interface for making artist predictions"""
    
    def __init__(self, model_file: str, artist_data_file: str):
        """Initialize with trained model and artist data"""
        self.predictor = ArtistSuccessPredictor()
        
        # Train the model
        print("Training model...")
        self.predictor.train(artist_data_file)
        
        # Load artist data for predictions
        with open(artist_data_file, 'r') as f:
            data = json.load(f)
        self.artists = data['artists']
        
        print(f"\nLoaded {len(self.artists)} artists")
        print("Model ready for predictions!\n")
    
    def predict_artist(self, artist_name: str):
        """Make prediction for a specific artist"""
        
        if artist_name not in self.artists:
            # Try case-insensitive search
            matches = [name for name in self.artists.keys() 
                      if artist_name.lower() in name.lower()]
            
            if not matches:
                print(f"Artist '{artist_name}' not found!")
                return None
            elif len(matches) == 1:
                artist_name = matches[0]
                print(f"Found: {artist_name}")
            else:
                print(f"Multiple matches found:")
                for i, name in enumerate(matches, 1):
                    print(f"  {i}. {name}")
                return None
        
        artist_data = self.artists[artist_name]
        
        # Make prediction
        prediction = self.predictor.predict_next_song(artist_data)
        
        # Display results
        self.display_prediction(artist_name, artist_data, prediction)
        
        return prediction
    
    def display_prediction(self, artist_name: str, artist_data: dict, prediction: dict):
        """Display prediction results in readable format"""
        
        print("\n" + "="*80)
        print(f"PREDICTION FOR: {artist_name}")
        print("="*80)
        
        # Artist current stats
        print(f"\n📊 CURRENT STATUS:")
        print(f"  Total Songs: {artist_data['total_songs']}")
        print(f"  Hit Rate: {artist_data['hit_rate']:.1f}%")
        print(f"  Career Span: {artist_data['career_span_years']:.1f} years")
        print(f"  Average Popularity: {artist_data.get('songs', [{}])[0].get('popularity', 'N/A') if artist_data.get('songs') else 'N/A'}")
        
        # Check for error
        if 'error' in prediction:
            print(f"\n❌ {prediction['error']}")
            return
        
        # Predictions
        print(f"\n🔮 NEXT SONG PREDICTIONS:")
        print(f"  Hit Probability: {prediction['hit_probability']:.1f}%")
        print(f"  Predicted Popularity: {prediction['predicted_popularity']:.1f}")
        print(f"  Predicted Tier: {prediction['predicted_tier'].upper()}")
        print(f"  Confidence Interval: [{prediction['confidence_interval'][0]:.1f}, {prediction['confidence_interval'][1]:.1f}]")
        
        # Hotness
        hotness = prediction['hotness_score']
        if hotness >= 70:
            status = "🔥 VERY HOT"
        elif hotness >= 50:
            status = "🌡️  HOT"
        elif hotness >= 30:
            status = "😐 WARM"
        else:
            status = "🧊 COLD"
        
        print(f"\n🌡️  HOTNESS SCORE: {hotness:.1f}/100 - {status}")
        
        # Recommendation
        print(f"\n💡 RECOMMENDATION:")
        print(f"  {prediction['recommendation']}")
        
        print("="*80 + "\n")
    
    def predict_top_artists(self, n: int = 10):
        """Predict for top N artists by song count"""
        
        # Sort by song count
        sorted_artists = sorted(
            self.artists.items(),
            key=lambda x: x[1]['total_songs'],
            reverse=True
        )[:n]
        
        results = []
        
        for artist_name, artist_data in sorted_artists:
            if artist_data['total_songs'] < 2:
                continue
                
            prediction = self.predictor.predict_next_song(artist_data)
            
            if 'error' not in prediction:
                results.append({
                    'artist': artist_name,
                    'current_songs': artist_data['total_songs'],
                    'hit_rate': artist_data['hit_rate'],
                    'predicted_hit_prob': prediction['hit_probability'],
                    'predicted_popularity': prediction['predicted_popularity'],
                    'hotness': prediction['hotness_score']
                })
        
        # Sort by predicted hit probability
        results_sorted = sorted(results, key=lambda x: x['predicted_hit_prob'], reverse=True)
        
        print("\n" + "="*80)
        print(f"TOP {len(results_sorted)} ARTISTS BY PREDICTED HIT PROBABILITY")
        print("="*80)
        print(f"\n{'Artist':<30} {'Songs':>6} {'Hit Rate':>9} {'Next Hit %':>10} {'Pred Pop':>9} {'Hotness':>8}")
        print("-"*80)
        
        for r in results_sorted:
            print(f"{r['artist']:<30} {r['current_songs']:>6} {r['hit_rate']:>8.1f}% "
                  f"{r['predicted_hit_prob']:>9.1f}% {r['predicted_popularity']:>9.1f} "
                  f"{r['hotness']:>8.1f}")
        
        print("="*80 + "\n")
        
        return results_sorted
    
    def find_rising_stars(self, min_songs: int = 3, max_songs: int = 20):
        """Find emerging artists with high potential"""
        
        results = []
        
        for artist_name, artist_data in self.artists.items():
            song_count = artist_data['total_songs']
            
            if song_count < min_songs or song_count > max_songs:
                continue
            
            prediction = self.predictor.predict_next_song(artist_data)
            
            if 'error' not in prediction:
                # Rising star criteria
                is_rising = (
                    prediction.get('hit_probability', 0) > 30 and
                    prediction.get('hotness_score', 0) > 40 and
                    artist_data['career_span_years'] < 5
                )
                
                if is_rising:
                    results.append({
                        'artist': artist_name,
                        'songs': song_count,
                        'career_years': artist_data['career_span_years'],
                        'predicted_hit_prob': prediction['hit_probability'],
                        'hotness': prediction['hotness_score'],
                        'current_hit_rate': artist_data['hit_rate']
                    })
        
        results_sorted = sorted(results, key=lambda x: x['hotness'], reverse=True)
        
        print("\n" + "="*80)
        print(f"🌟 RISING STARS (Emerging artists with high potential)")
        print("="*80)
        print(f"\n{'Artist':<30} {'Songs':>6} {'Years':>6} {'Hit %':>7} {'Hotness':>9}")
        print("-"*80)
        
        for r in results_sorted:
            print(f"{r['artist']:<30} {r['songs']:>6} {r['career_years']:>6.1f} "
                  f"{r['predicted_hit_prob']:>6.1f}% {r['hotness']:>9.1f}")
        
        print("="*80 + "\n")
        
        return results_sorted


    def save_all_predictions(self, output_file: str = 'predictions_output.json'):
        """
        Generate predictions for all artists and save to JSON
        """
        print("\n" + "="*80)
        print("GENERATING PREDICTIONS FOR ALL ARTISTS")
        print("="*80)
        
        all_predictions = {}
        
        for artist_name, artist_data in self.artists.items():
            if artist_data['total_songs'] < 2:
                continue
            
            prediction = self.predictor.predict_next_song(artist_data)
            
            if 'error' not in prediction:
                all_predictions[artist_name] = {
                    'current_status': {
                        'total_songs': artist_data['total_songs'],
                        'hit_rate': artist_data['hit_rate'],
                        'career_span_years': artist_data['career_span_years'],
                        'total_revenue': artist_data.get('estimated_total_revenue', 0),
                        'primary_genre': artist_data.get('primary_genre', 'unknown')
                    },
                    'predictions': prediction,
                    'timestamp': datetime.now().isoformat()
                }
        
        # Save to JSON
        with open(output_file, 'w') as f:
            json.dump(all_predictions, f, indent=2)
        
        print(f"\n✓ Saved predictions for {len(all_predictions)} artists to: {output_file}")
        return all_predictions


def main():
    """Example usage"""
    
    # Initialize interface
    interface = PredictionInterface(
        model_file=None,  # Model trained on the fly
        artist_data_file='artist_analysis.json'
    )
    
    # Show top artists by prediction
    top_artists = interface.predict_top_artists(n=10)
    
    # Find rising stars
    rising_stars = interface.find_rising_stars()
    
    # Predict for specific artist (example)
    if '!!!' in interface.artists:
        interface.predict_artist('!!!')
    
    # Save all predictions to JSON file
    output_path = 'ml_predictions.json'
    all_predictions = interface.save_all_predictions(output_path)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✓ Analyzed {len(interface.artists)} artists")
    print(f"✓ Generated {len(all_predictions)} predictions")
    print(f"✓ Output saved to: {output_path}")
    print("="*80)


if __name__ == "__main__":
    main()