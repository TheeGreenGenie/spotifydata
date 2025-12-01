# Spotify Music Analytics Dashboard

A comprehensive machine learning-powered analytics platform for analyzing Spotify music data, predicting artist success, and visualizing music trends.

## Overview

This project analyzes Spotify music datasets to provide insights into artist performance, predict hit songs using machine learning, and present interactive visualizations through a React-based dashboard.

### Key Features

- **Artist Performance Analysis**: Track metrics like hit rate, revenue estimates, career span, and song classifications
- **ML-Powered Predictions**: Predict probability of next song being a hit, forecast artist popularity, and estimate revenue
- **Interactive Dashboard**: Browse thousands of artists, view detailed analytics, and explore predictions
- **Spotify Integration**: Fetch real-time artist images and metadata from Spotify API

## Important: Data Not Included

**This repository does NOT include the processed data files required to run the dashboard.** This is a demonstration of our analysis workflow and results. The following files are gitignored:

### Gitignored Files
- `spotify_dataset.csv` - Raw Spotify music data (source)
- `artist_analysis.json` - Processed artist analytics (~197 MB)
- `ml_predictions.json` - ML model predictions (~20 MB)
- `music-analytics-dashboard/public/data/artists-data.json` - Frontend artist data
- `music-analytics-dashboard/public/data/predictions-data.json` - Frontend predictions data
- `music-analytics-dashboard/.env` - Spotify API credentials

This repository serves as a portfolio piece showing our data science and web development capabilities.

## How We Used This Project

This project was developed to analyze a large Spotify dataset containing detailed track information including audio features, popularity metrics, and artist data. The workflow consisted of:

1. **Data Collection**: Started with a CSV file (`spotify_dataset.csv`) containing thousands of tracks with features like energy, danceability, popularity, tempo, etc.

2. **Data Processing & Analysis**:
   - Used Python scripts to clean and analyze the raw data
   - Classified songs into tiers: Hit (80+ popularity), Good (60-79), Mid (40-59), Bust (<40)
   - Calculated artist-level metrics including hit rates and revenue estimates

3. **Machine Learning Predictions**:
   - Trained Random Forest models to predict song success
   - Generated predictions for artist trajectories and next-release probabilities
   - Created confidence scores and tier predictions

4. **Interactive Visualization**:
   - Built a React dashboard to browse and explore the analysis
   - Integrated Spotify API for real-time artist images
   - Created detailed artist pages with charts and prediction data

### Results

Our dashboard successfully analyzed **99,594 artists** from the dataset, providing comprehensive insights and predictions:

#### Main Dashboard - Artist List View
![Artist List Overview](WorkingAppImages/Screenshot%202025-11-30%20155932.png)
*The main artist list showing thousands of artists with sortable columns including genre, total songs, hit rate, revenue, predicted tier, hit probability, and hotness score.*

#### Sorting and Filtering
![Sorted by Total Songs](WorkingAppImages/Screenshot%202025-11-30%20160002.png)
*Artists sorted by total songs - showing prolific artists like L.A.B. (1,435 songs), Gucci Mane (1,029 songs), and Lil Wayne (876 songs).*

![Top Performers by Revenue](WorkingAppImages/Screenshot%202025-11-30%20160027.png)
*High-performing artists sorted by revenue with GOOD predictions - including Frank Ocean (60.78% hit rate), Billie Eilish (60.78% hit rate), and Kendrick Lamar (29.56% hit rate).*

![Sorted by Hit Probability](WorkingAppImages/Screenshot%202025-11-30%20160047.png)
*Artists sorted by next hit probability - showing predictions ranging from 30% to 95%, with artists like Ariana Grande, SZA, and Sabrina Carpenter all predicted at 95% probability.*

#### Artist Detail Pages
![Artist Detail - Billie Eilish Spotify Info](WorkingAppImages/Screenshot%202025-11-30%20160120.png)
*Individual artist page showing Spotify integration with real-time data - Billie Eilish has 119M+ followers and 92 popularity score.*

![Artist Detail - Billie Eilish Analytics](WorkingAppImages/Screenshot%202025-11-30%20160148.png)
*Detailed analytics for Billie Eilish including:*
- *102 total songs with 60.78% hit rate*
- *$851.5M estimated total revenue*
- *7.5 year career span*
- *Revenue distribution breakdown across stakeholders*
- *Song tier distribution (Hit/Good/Mid/Bust)*

![Artist Detail - Predictions & Song Catalog](WorkingAppImages/Screenshot%202025-11-30%20160158.png)
*ML predictions and audio features visualization:*
- *95% hit probability for next release*
- *Predicted popularity: 96*
- *Confidence interval: 93.2 - 98.3*
- *Hotness score: 100/100*
- *Audio features bar chart showing energy, danceability, etc.*
- *Complete song catalog with popularity tiers and revenue estimates*

![Song Catalog Detail](WorkingAppImages/Screenshot%202025-11-30%20160206.png)
*Individual song breakdowns showing titles, popularity scores, tier classifications (Hit/Good/Mid), revenue estimates, and release dates.*

## Project Structure

```
SpotifyProj/
├── spotify_dataset.csv              # (GITIGNORED) Raw Spotify data
├── myfiles/
│   ├── artist_analysis.json         # (GITIGNORED) Generated analytics
│   ├── ml_predictions.json          # (GITIGNORED) ML predictions
│   ├── artist_explorer.py           # Script to query artist data
│   ├── ml_hit_predictor.py          # ML model for predictions
│   └── comprehensive_revenue_model.py
├── music-analytics-dashboard/       # React frontend
│   ├── public/data/
│   │   ├── artists-data.json        # (GITIGNORED) Frontend data
│   │   └── predictions-data.json    # (GITIGNORED) Frontend data
│   ├── src/
│   │   ├── App.js                   # Main application
│   │   ├── components/
│   │   └── services/spotifyApi.js   # Spotify API integration
│   └── .env                         # (GITIGNORED) API credentials
└── README.md
```

## Our Data Processing Pipeline

Our analysis pipeline consisted of the following stages:

### 1. Data Source
We worked with a comprehensive Spotify dataset (`spotify_dataset.csv`) containing detailed track information with features including:
- Artist and song metadata
- Popularity scores (0-100)
- Audio features: Energy, Danceability, Tempo, Loudness, Key, Time Signature
- Musical characteristics: Speechiness, Acousticness, Instrumentalness, Liveness, Positiveness
- Genre and release date information

### 2. Python Data Processing
Using Python scripts in the `myfiles/` directory, we:
- Cleaned and normalized the raw CSV data
- Implemented song classification logic:
  - **Hit**: Popularity ≥ 80
  - **Good**: Popularity 60-79
  - **Mid**: Popularity 40-59
  - **Bust**: Popularity < 40
- Aggregated track-level data into artist-level analytics
- Generated `artist_analysis.json` (~197 MB) containing metrics for thousands of artists

### 3. Machine Learning Model Training
The `ml_hit_predictor.py` script:
- Trained Random Forest classifiers and regressors on the dataset
- Engineered features from artist career history and audio characteristics
- Generated predictions including:
  - Probability of next song being a hit
  - Expected popularity scores
  - Career trajectory forecasts
  - Confidence intervals for predictions
- Produced `ml_predictions.json` (~20 MB) with prediction data

### 4. Frontend Data Preparation
- Copied the generated JSON files to `music-analytics-dashboard/public/data/`:
  - `artists-data.json` - Artist analytics for the dashboard
  - `predictions-data.json` - ML predictions for visualization
- Configured Spotify API credentials in `.env` file for real-time artist image fetching

### 5. Dashboard Deployment
- Built a React-based interactive dashboard
- Integrated Chart.js for data visualizations
- Implemented pagination, search, and sorting for exploring artists
- Connected to Spotify Web API for enriched artist profiles

## Features Explained

### Artist Analytics
- **Hit Rate**: Percentage of songs with 80+ popularity
- **Revenue Estimates**: Based on song popularity and streaming estimates
- **Career Metrics**: Career span, total songs, genre classification
- **Song Distribution**: Classification into Hit/Good/Mid/Bust tiers

### ML Predictions
- **Next Hit Probability**: Likelihood of artist's next song being a hit
- **Popularity Forecast**: Expected popularity score for next release
- **Trajectory Analysis**: Career trend (ascending/declining/stable)
- **Tier Predictions**: Predicted performance tier with confidence scores

### Dashboard Features
- **Artist List**: Paginated, searchable, sortable table of all artists
- **Artist Detail Pages**: Individual artist profiles with charts and predictions
- **Search & Filter**: Find artists by name
- **Sort Options**: Sort by any metric (revenue, hit rate, songs, etc.)
- **Spotify Integration**: Real-time artist images and follower counts

## Technical Stack

### Backend/Data Processing
- **Python 3.8+**
- **pandas** - Data manipulation
- **numpy** - Numerical operations
- **scikit-learn** - Machine learning models
  - RandomForestClassifier for hit prediction
  - RandomForestRegressor for popularity forecasting
  - GradientBoostingClassifier for trajectory analysis

### Frontend
- **React 19.2** - UI framework
- **React Router** - Navigation
- **Chart.js** with react-chartjs-2 - Data visualization
- **Spotify Web API** - Artist metadata

## Model Performance

The ML models were trained on historical Spotify data with the following approaches:

- **Hit Classification**: Binary classification (hit vs. non-hit) using artist history
- **Popularity Regression**: Continuous prediction of expected popularity scores
- **Feature Engineering**: Includes career metrics, genre trends, and temporal patterns
- **Cross-validation**: Models validated using k-fold cross-validation


## License

This project is provided as-is for educational and research purposes.

## Credits

Developed to analyze Spotify music trends and predict artist success using machine learning techniques.
