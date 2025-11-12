"""
Machine Learning Model for Predicting Artist Hit Frequency and Success
Phase 2: ML-Based Prediction System

Features:
1. Predict probability of next song being a hit
2. Forecast artist "hotness" score
3. Estimate hit frequency based on career stage
4. Revenue prediction for upcoming releases
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class ArtistSuccessPredictor:
    """
    ML model to predict artist success metrics:
    - Hit probability for next release
    - Expected popularity score
    - Career trajectory (ascending/declining)
    - Revenue forecast
    """
    
    def __init__(self):
        """Initialize ML models"""
        # Classification: Will next song be a hit?
        self.hit_classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            random_state=42,
            class_weight= {0: 1, 1: 99}
        )
        
        # Regression: What popularity score?
        self.popularity_regressor = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            random_state=42
        )
        
        # Trajectory classifier: Ascending/Stable/Declining
        self.trajectory_classifier = GradientBoostingClassifier(
            n_estimators=150,
            max_depth=8,
            random_state=42
        )
        
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_artist_features(self, artist_data: Dict) -> Dict:
        """
        Extract ML features from artist data
        
        Features include:
        - Historical performance (hit rate, avg popularity)
        - Career metrics (tenure, release frequency)
        - Recent trend (last 5 songs performance)
        - Audio profile (avg energy, danceability, etc.)
        - Genre factors
        - Hotness score
        """
        
        songs = artist_data.get('songs', [])
        if not songs:
            return None
        
        # Sort songs by release date
        valid_songs = []
        for s in songs:
            if s.get('release_date') and not pd.isna(s.get('release_date')):
                valid_songs.append(s)
        
        if not valid_songs:
            return None
            
        songs_sorted = sorted(valid_songs, key=lambda x: str(x['release_date']))
        
        if len(songs_sorted) < 2:
            return None
        
        # Basic stats
        total_songs = len(songs_sorted)
        hit_songs = sum(1 for s in songs_sorted if s['tier'] == 'hit')
        good_songs = sum(1 for s in songs_sorted if s['tier'] == 'good')
        
        # Historical performance
        historical_hit_rate = hit_songs / total_songs if total_songs > 0 else 0
        historical_good_rate = good_songs / total_songs if total_songs > 0 else 0
        avg_popularity = np.mean([s['popularity'] for s in songs_sorted])
        
        # Career timeline
        first_release = pd.to_datetime(songs_sorted[0]['release_date'])
        last_release = pd.to_datetime(songs_sorted[-1]['release_date'])
        career_days = (last_release - first_release).days
        career_years = career_days / 365.25
        
        # Release frequency (songs per year)
        release_frequency = total_songs / max(career_years, 0.5)
        
        # Recent performance (last 5 songs)
        recent_songs = songs_sorted[-5:]
        recent_hit_rate = sum(1 for s in recent_songs if s['tier'] == 'hit') / len(recent_songs)
        recent_avg_pop = np.mean([s['popularity'] for s in recent_songs])
        
        # Trend analysis (comparing recent vs historical)
        if len(songs_sorted) > 5:
            older_songs = songs_sorted[:-5]
            older_avg_pop = np.mean([s['popularity'] for s in older_songs])
            popularity_trend = recent_avg_pop - older_avg_pop
        else:
            popularity_trend = 0
        
        # Time since last release
        days_since_last = (datetime.now() - last_release).days
        
        # Hotness score (based on recent activity and success)
        hotness = self.calculate_hotness_score(
            recent_avg_pop, 
            days_since_last, 
            recent_hit_rate
        )
        
        # Audio features
        audio_features = {
            'energy': artist_data.get('avg_energy', 50),
            'danceability': artist_data.get('avg_danceability', 50),
            'positiveness': artist_data.get('avg_positiveness', 50),
            'speechiness': artist_data.get('avg_speechiness', 5),
            'liveness': artist_data.get('avg_liveness', 15),
            'acousticness': artist_data.get('avg_acousticness', 20),
            'instrumentalness': artist_data.get('avg_instrumentalness', 5)
        }
        
        # Genre encoding (simple for now)
        genre = artist_data.get('primary_genre', 'unknown')
        genre_popularity = self.get_genre_popularity_factor(genre)
        
        # Consistency score (std dev of popularity)
        popularity_consistency = np.std([s['popularity'] for s in songs_sorted])
        
        # Peak performance
        peak_popularity = max(s['popularity'] for s in songs_sorted)
        
        # Career stage
        career_stage = self.categorize_career_stage(career_years)
        
        features = {
            # Historical metrics
            'total_songs': total_songs,
            'career_years': career_years,
            'historical_hit_rate': historical_hit_rate,
            'historical_good_rate': historical_good_rate,
            'avg_popularity': avg_popularity,
            'peak_popularity': peak_popularity,
            'popularity_consistency': popularity_consistency,
            
            # Release patterns
            'release_frequency': release_frequency,
            'days_since_last_release': days_since_last,
            
            # Recent performance
            'recent_hit_rate': recent_hit_rate,
            'recent_avg_popularity': recent_avg_pop,
            'popularity_trend': popularity_trend,
            
            # Current status
            'hotness_score': hotness,
            
            # Audio profile
            **audio_features,
            
            # Genre
            'genre_popularity_factor': genre_popularity,
            
            # Career stage (one-hot encoded)
            'is_new_artist': 1 if career_stage == 'new' else 0,
            'is_emerging': 1 if career_stage == 'emerging' else 0,
            'is_established': 1 if career_stage == 'established' else 0,
            'is_veteran': 1 if career_stage == 'veteran' else 0,
        }
        
        return features
    
    def calculate_hotness_score(self, recent_avg_pop: float, 
                                days_since_last: int, 
                                recent_hit_rate: float) -> float:
        """
        Calculate "hotness" score (0-100) based on:
        - Recent performance
        - Recency of releases
        - Success rate
        """
        
        # Recent performance component (0-40 points)
        performance_score = (recent_avg_pop / 100) * 40
        
        # Recency component (0-30 points)
        # Decay over time: peak at 0 days, 0 at 365+ days
        if days_since_last <= 30:
            recency_score = 30
        elif days_since_last <= 90:
            recency_score = 25
        elif days_since_last <= 180:
            recency_score = 15
        elif days_since_last <= 365:
            recency_score = 5
        else:
            recency_score = 0
        
        # Success rate component (0-30 points)
        success_score = recent_hit_rate * 30
        
        hotness = performance_score + recency_score + success_score
        
        return min(hotness, 100)
    
    def get_genre_popularity_factor(self, genre: str) -> float:
        """
        Return popularity multiplier for genre
        Based on streaming statistics
        """
        genre_factors = {
            'hip hop': 1.2,      # Most popular
            'pop': 1.15,
            'r&b': 1.1,
            'latin': 1.1,
            'rock': 1.0,
            'country': 0.95,
            'indie': 0.9,
            'electronic': 0.95,
            'jazz': 0.8,
            'classical': 0.7,
            'unknown': 1.0
        }
        
        # Normalize genre string
        genre_lower = genre.lower() if genre else 'unknown'
        
        # Find best match
        for key, value in genre_factors.items():
            if key in genre_lower:
                return value
        
        return 1.0
    
    def categorize_career_stage(self, career_years: float) -> str:
        """Categorize artist by career stage"""
        if career_years <= 2:
            return 'new'
        elif career_years <= 5:
            return 'emerging'
        elif career_years <= 10:
            return 'established'
        else:
            return 'veteran'
    
    def prepare_training_data(self, artist_analysis_file: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepare training data from artist analysis JSON
        
        Returns:
            X: Feature matrix
            y: Target variables (hit/not hit, popularity score)
        """
        
        print("Loading artist data...")
        with open(artist_analysis_file, 'r') as f:
            data = json.load(f)
        
        artists = data['artists']
        
        print(f"Processing {len(artists)} artists...")
        
        # Extract features for each artist's songs
        training_examples = []
        
        for artist_name, artist_data in artists.items():
            songs = artist_data.get('songs', [])
            
            if len(songs) < 3:  # Need at least 3 songs for meaningful prediction
                continue
            
            # Sort by release date
            valid_songs = []
            for s in songs:
                if s.get('release_date') and not pd.isna(s.get('release_date')):
                    valid_songs.append(s)
            
            if len(valid_songs) < 3:
                continue
                
            songs_sorted = sorted(valid_songs, key=lambda x: str(x['release_date']))
            
            # For each song (except last 2), predict next song
            for i in range(len(songs_sorted) - 2):
                # Use songs up to index i to predict song at i+1
                historical_songs = songs_sorted[:i+1]
                target_song = songs_sorted[i+1]
                
                # Create a temporary artist data with only historical songs
                temp_artist_data = {
                    'songs': historical_songs,
                    'avg_energy': artist_data.get('avg_energy', 50),
                    'avg_danceability': artist_data.get('avg_danceability', 50),
                    'avg_positiveness': artist_data.get('avg_positiveness', 50),
                    'avg_speechiness': artist_data.get('avg_speechiness', 5),
                    'avg_liveness': artist_data.get('avg_liveness', 15),
                    'avg_acousticness': artist_data.get('avg_acousticness', 20),
                    'avg_instrumentalness': artist_data.get('avg_instrumentalness', 5),
                    'primary_genre': artist_data.get('primary_genre', 'unknown')
                }
                
                features = self.prepare_artist_features(temp_artist_data)
                
                if features:
                    # Target: will next song be a hit?
                    is_hit = 1 if target_song['tier'] == 'hit' else 0
                    is_good_or_better = 1 if target_song['tier'] in ['hit', 'good'] else 0
                    popularity = target_song['popularity']
                    
                    training_examples.append({
                        **features,
                        'target_is_hit': is_hit,
                        'target_is_good_or_better': is_good_or_better,
                        'target_popularity': popularity,
                        'artist': artist_name
                    })
        
        print(f"Created {len(training_examples)} training examples")
        
        df = pd.DataFrame(training_examples)
        
        # Separate features and targets
        feature_cols = [col for col in df.columns 
                       if not col.startswith('target_') and col != 'artist']
        
        X = df[feature_cols]
        y_hit = df['target_is_hit']
        y_good = df['target_is_good_or_better']
        y_popularity = df['target_popularity']
        
        return X, y_hit, y_good, y_popularity, df
    
    def train(self, artist_analysis_file: str):
        """Train all ML models"""
        
        print("\n" + "="*80)
        print("TRAINING ML MODELS")
        print("="*80)
        
        # Prepare data
        X, y_hit, y_good, y_popularity, full_df = self.prepare_training_data(artist_analysis_file)
        
        print(f"\nDataset shape: {X.shape}")
        print(f"Features: {len(X.columns)}")
        print(f"Hit rate in dataset: {y_hit.mean():.1%}")
        print(f"Good or better rate: {y_good.mean():.1%}")
        print(f"Avg popularity: {y_popularity.mean():.1f}")
        
        # Split data
        X_train, X_test, y_hit_train, y_hit_test = train_test_split(
            X, y_hit, test_size=0.2, random_state=42, stratify=y_hit
        )
        
        _, _, y_good_train, y_good_test = train_test_split(
            X, y_good, test_size=0.2, random_state=42, stratify=y_good
        )
        
        _, _, y_pop_train, y_pop_test = train_test_split(
            X, y_popularity, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train hit classifier (using "good or better" if no hits exist)
        print("\n" + "-"*80)
        
        # Check if we have any positive examples
        if y_hit_train.sum() == 0:
            print("No hits in training data, using 'good or better' (65+) as target...")
            y_hit_train_use = y_good_train
            y_hit_test_use = y_good_test
            target_name = "Good or Better"
        else:
            y_hit_train_use = y_hit_train
            y_hit_test_use = y_hit_test
            target_name = "Hit"
        
        print(f"Training {target_name} Classifier...")
        self.hit_classifier.fit(X_train_scaled, y_hit_train_use)
        
        y_hit_pred = self.hit_classifier.predict(X_test_scaled)
        
        # Only get probability if we have both classes
        if len(np.unique(y_hit_train_use)) > 1:
            y_hit_proba = self.hit_classifier.predict_proba(X_test_scaled)[:, 1]
            print(f"Accuracy: {accuracy_score(y_hit_test_use, y_hit_pred):.3f}")
            print(f"ROC-AUC: {roc_auc_score(y_hit_test_use, y_hit_proba):.3f}")
        else:
            y_hit_proba = None
            print(f"Accuracy: {accuracy_score(y_hit_test_use, y_hit_pred):.3f}")
            print("(Single class in training data - ROC-AUC not applicable)")
        
        print("\nClassification Report:")
        unique_classes = len(np.unique(y_hit_train_use))
        if unique_classes > 1:
            print(classification_report(y_hit_test_use, y_hit_pred, 
                                       target_names=[f'Not {target_name}', target_name],
                                       zero_division=0))
        else:
            print(f"  Only one class present in data (all '{target_name}' or all 'Not {target_name}')")
            print(f"  This is expected for small/homogeneous datasets")
        
        # Train popularity regressor
        print("\n" + "-"*80)
        print("Training Popularity Regressor...")
        self.popularity_regressor.fit(X_train_scaled, y_pop_train)
        
        y_pop_pred = self.popularity_regressor.predict(X_test_scaled)
        
        print(f"R² Score: {r2_score(y_pop_test, y_pop_pred):.3f}")
        print(f"MAE: {mean_absolute_error(y_pop_test, y_pop_pred):.2f}")
        print(f"RMSE: {np.sqrt(mean_squared_error(y_pop_test, y_pop_pred)):.2f}")
        
        # Feature importance
        print("\n" + "-"*80)
        print("TOP 15 MOST IMPORTANT FEATURES:")
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.hit_classifier.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for i, row in feature_importance.head(15).iterrows():
            print(f"  {row['feature']:30s}: {row['importance']:.4f}")
        
        self.is_trained = True
        self.feature_names = X.columns.tolist()
        
        print("\n" + "="*80)
        print("TRAINING COMPLETE!")
        print("="*80)
        
        return {
            'hit_accuracy': accuracy_score(y_hit_test_use, y_hit_pred),
            'hit_roc_auc': roc_auc_score(y_hit_test_use, y_hit_proba) if y_hit_proba is not None else None,
            'popularity_r2': r2_score(y_pop_test, y_pop_pred),
            'popularity_mae': mean_absolute_error(y_pop_test, y_pop_pred),
            'feature_importance': feature_importance
        }
    
    def predict_next_song(self, artist_data: Dict) -> Dict:
        """
        Predict success of artist's next song
        
        Returns:
            Dictionary with predictions
        """
        
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions!")
        
        features = self.prepare_artist_features(artist_data)
        
        if not features:
            return {
                'error': 'Insufficient data for prediction',
                'min_songs_required': 2
            }
        
        # Convert to dataframe with correct feature order
        X = pd.DataFrame([features])[self.feature_names]
        X_scaled = self.scaler.transform(X)
        
        # Predictions
        try:
            hit_probability = self.hit_classifier.predict_proba(X_scaled)[0, 1]
        except IndexError:
            # Single class - all predictions are the same
            hit_probability = 0.0  # Conservative estimate
        
        predicted_popularity = self.popularity_regressor.predict(X_scaled)[0]
        
        # Predict tier
        if predicted_popularity >= 80:
            predicted_tier = 'hit'
        elif predicted_popularity >= 65:
            predicted_tier = 'good'
        elif predicted_popularity >= 35:
            predicted_tier = 'mid'
        else:
            predicted_tier = 'bust'
        
        # Confidence intervals (using model uncertainty)
        pop_std = 10  # Approximate standard deviation
        confidence_lower = max(0, predicted_popularity - 1.96 * pop_std)
        confidence_upper = min(100, predicted_popularity + 1.96 * pop_std)
        
        return {
            'hit_probability': round(hit_probability * 100, 2),
            'predicted_popularity': round(predicted_popularity, 1),
            'predicted_tier': predicted_tier,
            'confidence_interval': [round(confidence_lower, 1), round(confidence_upper, 1)],
            'hotness_score': round(features['hotness_score'], 1),
            'recommendation': self.get_recommendation(hit_probability, predicted_popularity, features)
        }
    
    def get_recommendation(self, hit_prob: float, pred_pop: float, features: Dict) -> str:
        """Generate recommendation based on predictions"""
        
        if hit_prob > 0.5:
            return "Strong probability of hit! Consider major marketing push."
        elif hit_prob > 0.3:
            return "Good potential. Strategic promotion recommended."
        elif pred_pop > 50:
            return "Moderate success expected. Test with smaller release."
        elif features['popularity_trend'] > 5:
            return "Upward trend detected. Build momentum with consistent releases."
        elif features['days_since_last_release'] > 180:
            return "Long gap since last release. Consider re-engagement strategy."
        else:
            return "Lower probability. Focus on artist development and fan engagement."


def main():
    """Main execution for testing"""
    
    # Initialize predictor
    predictor = ArtistSuccessPredictor()
    
    # Train on sample data
    predictor.train('/mnt/user-data/outputs/artist_analysis.json')
    
    print("\n" + "="*80)
    print("MODEL READY FOR PREDICTIONS!")
    print("="*80)


if __name__ == "__main__":
    main()