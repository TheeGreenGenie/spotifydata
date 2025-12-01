// components/ArtistDetail.js
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { getArtistInfoCached } from '../services/spotifyApi';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const ArtistDetail = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { artistName } = useParams();
  const artist = location.state?.artist;

  // State for Spotify artist info (image, followers, etc.)
  const [spotifyInfo, setSpotifyInfo] = useState({
    image: null,
    followers: 'N/A',
    popularity: 'N/A',
    genres: 'N/A',
    spotifyUrl: null
  });
  const [loadingSpotifyInfo, setLoadingSpotifyInfo] = useState(true);

  // Fetch Spotify artist info on mount
  useEffect(() => {
    const fetchArtistInfo = async () => {
      if (artist?.name) {
        setLoadingSpotifyInfo(true);
        const info = await getArtistInfoCached(artist.name);
        setSpotifyInfo(info);
        setLoadingSpotifyInfo(false);
      }
    };

    fetchArtistInfo();
  }, [artist?.name]);

  if (!artist) {
    return (
      <div className="error">
        <h2>Artist not found</h2>
        <button onClick={() => navigate('/')}>Back to Artists</button>
      </div>
    );
  }

  // Prepare song tier distribution data
  const tierData = {
    labels: ['Hit', 'Good', 'Mid', 'Bust'],
    datasets: [
      {
        data: [
          artist.hit_songs,
          artist.good_songs,
          artist.mid_songs,
          artist.bust_songs
        ],
        backgroundColor: [
          '#4CAF50', // Green for hit
          '#8BC34A', // Light green for good
          '#FFC107', // Yellow for mid
          '#F44336'  // Red for bust
        ],
        borderWidth: 2,
        borderColor: '#fff'
      }
    ]
  };

  // Song revenue distribution
  const revenueByTierData = {
    labels: ['Hit', 'Good', 'Mid', 'Bust'],
    datasets: [
      {
        label: 'Average Revenue per Song',
        data: [
          artist.hit_songs > 0 ? (artist.estimated_total_revenue * (artist.hit_rate / 100)) / artist.hit_songs : 0,
          artist.good_songs > 0 ? (artist.estimated_total_revenue * (artist.good_rate / 100)) / artist.good_songs : 0,
          artist.mid_songs > 0 ? (artist.estimated_total_revenue * (artist.mid_rate / 100)) / artist.mid_songs : 0,
          artist.bust_songs > 0 ? (artist.estimated_total_revenue * (artist.bust_rate / 100)) / artist.bust_songs : 0,
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.8)',
      }
    ]
  };

  // Audio features radar chart data
  const audioFeaturesData = {
    labels: ['Energy', 'Danceability', 'Positiveness', 'Speechiness', 'Liveness', 'Acousticness', 'Instrumentalness'],
    datasets: [
      {
        label: 'Average Values',
        data: [
          artist.avg_energy,
          artist.avg_danceability,
          artist.avg_positiveness,
          artist.avg_speechiness,
          artist.avg_liveness,
          artist.avg_acousticness,
          artist.avg_instrumentalness
        ],
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(75, 192, 192, 1)'
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      }
    }
  };

  return (
    <div className="artist-detail">
      <button className="back-button" onClick={() => navigate('/')}>
        ← Back to Artists
      </button>

      {/* Artist Header */}
      <div className="artist-header">
        {/* Artist Image */}
        <div className="artist-image-container">
          {loadingSpotifyInfo ? (
            <div className="artist-image-placeholder loading">
              <div className="spinner"></div>
            </div>
          ) : spotifyInfo.image ? (
            <img
              src={spotifyInfo.image}
              alt={artist.name}
              className="artist-image"
            />
          ) : (
            <div className="artist-image-placeholder">
              <span className="placeholder-text">No Image</span>
            </div>
          )}
        </div>

        {/* Artist Basic Info */}
        <div className="artist-basic-info">
          <h1>{artist.name}</h1>

          {/* Spotify Link */}
          {spotifyInfo.spotifyUrl && (
            <a
              href={spotifyInfo.spotifyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="spotify-link"
            >
              🎵 View on Spotify
            </a>
          )}

          {/* Genre and Tier Tags */}
          <div className="genre-tags">
            <span className="genre-tag">{artist.primary_genre}</span>
            <span className={`tier-badge large ${artist.predictions.predicted_tier || 'unknown'}`}>
              Predicted: {artist.predictions.predicted_tier || 'N/A'}
            </span>
          </div>

          {/* Spotify Info Grid */}
          <div className="spotify-info-grid">
            <div className="spotify-info-item">
              <span className="info-label">Spotify Followers</span>
              <span className="info-value">{spotifyInfo.followers}</span>
            </div>
            <div className="spotify-info-item">
              <span className="info-label">Spotify Popularity</span>
              <span className="info-value">{spotifyInfo.popularity}</span>
            </div>
            <div className="spotify-info-item full-width">
              <span className="info-label">Spotify Genres</span>
              <span className="info-value">{spotifyInfo.genres}</span>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{artist.total_songs}</div>
              <div className="stat-label">Total Songs</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{artist.hit_rate}%</div>
              <div className="stat-label">Hit Rate</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">${(artist.estimated_total_revenue / 1000).toFixed(0)}k</div>
              <div className="stat-label">Total Revenue</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{artist.career_span_years}y</div>
              <div className="stat-label">Career Span</div>
            </div>
          </div>
        </div>
      </div>

      <div className="detail-grid">
        {/* Left Column - Current Performance */}
        <div className="detail-column">
          <div className="info-card">
            <h2>Current Performance</h2>
            <div className="performance-stats">
              <div className="performance-row">
                <span>Hit Songs:</span>
                <span>{artist.hit_songs} ({artist.hit_rate}%)</span>
              </div>
              <div className="performance-row">
                <span>Good Songs:</span>
                <span>{artist.good_songs} ({artist.good_rate}%)</span>
              </div>
              <div className="performance-row">
                <span>Mid Songs:</span>
                <span>{artist.mid_songs} ({artist.mid_rate}%)</span>
              </div>
              <div className="performance-row">
                <span>Bust Songs:</span>
                <span>{artist.bust_songs} ({artist.bust_rate}%)</span>
              </div>
              <div className="performance-row">
                <span>Explicit Ratio:</span>
                <span>{artist.explicit_ratio}%</span>
              </div>
            </div>
          </div>

          <div className="info-card">
            <h2>Song Tier Distribution</h2>
            <div className="chart-container">
              <Doughnut 
                data={tierData} 
                options={chartOptions}
                height={250}
              />
            </div>
          </div>
        </div>

        {/* Right Column - Predictions */}
        <div className="detail-column">
          <div className="info-card prediction-card">
            <h2>AI Predictions</h2>
            <div className="prediction-stats">
              <div className="prediction-row">
                <span>Hit Probability:</span>
                <span className="highlight">{artist.predictions.hit_probability}%</span>
              </div>
              <div className="prediction-row">
                <span>Predicted Popularity:</span>
                <span>{artist.predictions.predicted_popularity}</span>
              </div>
              <div className="prediction-row">
                <span>Confidence Interval:</span>
                <span>{artist.predictions.confidence_interval?.join(' - ')}</span>
              </div>
              <div className="prediction-row">
                <span>Hotness Score:</span>
                <span>{artist.predictions.hotness_score}/100</span>
              </div>
            </div>
            
            <div className="recommendation">
              <h3>Recommendation</h3>
              <p>{artist.predictions.recommendation}</p>
            </div>
          </div>

          <div className="info-card">
            <h2>Revenue by Tier</h2>
            <div className="chart-container">
              <Bar 
                data={revenueByTierData} 
                options={chartOptions}
                height={250}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Audio Features */}
      <div className="info-card full-width">
        <h2>Audio Features Analysis</h2>
        <div className="audio-features-grid">
          <div className="audio-feature">
            <span className="feature-label">Energy</span>
            <div className="feature-bar">
              <div 
                className="feature-fill" 
                style={{width: `${artist.avg_energy}%`}}
              ></div>
            </div>
            <span className="feature-value">{artist.avg_energy}%</span>
          </div>
          <div className="audio-feature">
            <span className="feature-label">Danceability</span>
            <div className="feature-bar">
              <div 
                className="feature-fill" 
                style={{width: `${artist.avg_danceability}%`}}
              ></div>
            </div>
            <span className="feature-value">{artist.avg_danceability}%</span>
          </div>
          <div className="audio-feature">
            <span className="feature-label">Positiveness</span>
            <div className="feature-bar">
              <div 
                className="feature-fill" 
                style={{width: `${artist.avg_positiveness}%`}}
              ></div>
            </div>
            <span className="feature-value">{artist.avg_positiveness}%</span>
          </div>
          <div className="audio-feature">
            <span className="feature-label">Speechiness</span>
            <div className="feature-bar">
              <div 
                className="feature-fill" 
                style={{width: `${artist.avg_speechiness}%`}}
              ></div>
            </div>
            <span className="feature-value">{artist.avg_speechiness}%</span>
          </div>
          <div className="audio-feature">
            <span className="feature-label">Liveness</span>
            <div className="feature-bar">
              <div 
                className="feature-fill" 
                style={{width: `${artist.avg_liveness}%`}}
              ></div>
            </div>
            <span className="feature-value">{artist.avg_liveness}%</span>
          </div>
          <div className="audio-feature">
            <span className="feature-label">Acousticness</span>
            <div className="feature-bar">
              <div 
                className="feature-fill" 
                style={{width: `${artist.avg_acousticness}%`}}
              ></div>
            </div>
            <span className="feature-value">{artist.avg_acousticness}%</span>
          </div>
          <div className="audio-feature">
            <span className="feature-label">Instrumentalness</span>
            <div className="feature-bar">
              <div 
                className="feature-fill" 
                style={{width: `${artist.avg_instrumentalness}%`}}
              ></div>
            </div>
            <span className="feature-value">{artist.avg_instrumentalness}%</span>
          </div>
        </div>
      </div>

      {/* Songs List */}
      <div className="info-card full-width">
        <h2>Song Catalog</h2>
        <div className="songs-table">
          <div className="table-header">
            <span>Title</span>
            <span>Popularity</span>
            <span>Tier</span>
            <span>Revenue</span>
            <span>Release Date</span>
          </div>
          {artist.songs.map((song, index) => (
            <div key={index} className={`table-row tier-${song.tier}`}>
              <span className="song-title">{song.title}</span>
              <span>{song.popularity}</span>
              <span className={`tier-badge small ${song.tier}`}>{song.tier}</span>
              <span>${song.revenue.toLocaleString()}</span>
              <span>{song.release_date || 'Unknown'}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ArtistDetail;