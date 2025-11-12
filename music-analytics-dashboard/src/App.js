import React, { useState, useEffect, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useParams, useLocation } from 'react-router-dom'; // FIXED: = to -
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import './App.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

// Sample data generator
const generateSampleData = (count) => {
  const artists = {};
  for (let i = 0; i < count; i++) {
    artists[`Artist ${i + 1}`] = {
      total_songs: Math.floor(Math.random() * 20) + 1,
      hit_songs: Math.floor(Math.random() * 5),
      good_songs: Math.floor(Math.random() * 5),
      mid_songs: Math.floor(Math.random() * 10),
      bust_songs: Math.floor(Math.random() * 10),
      hit_rate: (Math.random() * 20).toFixed(1),
      estimated_total_revenue: Math.floor(Math.random() * 1000000),
      primary_genre: ['Rock', 'Pop', 'Hip Hop', 'Jazz', 'Electronic'][Math.floor(Math.random() * 5)],
      songs: []
    };
  }
  return artists;
};

const ArtistList = () => {
  const [artistsData, setArtistsData] = useState({});
  const [predictionsData, setPredictionsData] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();
  const ITEMS_PER_PAGE = 25;

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load both JSON files from the public/data directory
        const [artistsResponse, predictionsResponse] = await Promise.all([
          fetch('/data/artists-data.json'),
          fetch('/data/predictions-data.json')
        ]);
        
        if (!artistsResponse.ok || !predictionsResponse.ok) {
          throw new Error('Failed to load data files');
        }
        
        const artistsJson = await artistsResponse.json();
        const predictionsJson = await predictionsResponse.json();
        
        console.log('Loaded artists data:', Object.keys(artistsJson.artists).length, 'artists');
        console.log('Loaded predictions data:', Object.keys(predictionsJson).length, 'predictions');
        
        setArtistsData(artistsJson);
        setPredictionsData(predictionsJson);
      } catch (error) {
        console.error('Error loading data:', error);
        alert('Error loading data files. Check console for details.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Combine artist data with predictions
  const combinedArtists = useMemo(() => {
    if (!artistsData.artists) return [];
    
    return Object.entries(artistsData.artists).map(([artistName, artistData]) => {
      const prediction = predictionsData[artistName] || {};
      return {
        name: artistName,
        ...artistData,
        predictions: prediction.predictions || {},
        timestamp: prediction.timestamp
      };
    });
  }, [artistsData, predictionsData]);

  // Filter artists based on search term
  const filteredArtists = useMemo(() => {
    return combinedArtists.filter(artist =>
      artist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (artist.primary_genre && artist.primary_genre.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [combinedArtists, searchTerm]);

  const totalPages = Math.ceil(filteredArtists.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const currentArtists = filteredArtists.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  const handleArtistClick = (artist) => {
    navigate(`/artist/${encodeURIComponent(artist.name)}`, { state: { artist } });
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo(0, 0);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading artist data...</p>
      </div>
    );
  }

  if (combinedArtists.length === 0) {
    return (
      <div className="loading">
        <p>No artist data found. Please check your JSON files.</p>
        <p>Expected files: <code>public/data/artists-data.json</code> and <code>public/data/predictions-data.json</code></p>
      </div>
    );
  }

  return (
    <div className="artist-list">
      <div className="search-container">
        <input
          type="text"
          placeholder="Search artists by name or genre..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
          className="search-input"
        />
      </div>

      <div className="pagination-info">
        Showing {startIndex + 1}-{Math.min(startIndex + ITEMS_PER_PAGE, filteredArtists.length)} of {filteredArtists.length} artists
        (Total in database: {Object.keys(artistsData.artists || {}).length})
      </div>

      <div className="artists-grid">
        {currentArtists.map(artist => (
          <div
            key={artist.name}
            className={`artist-card tier-${artist.predictions.predicted_tier || 'unknown'}`}
            onClick={() => handleArtistClick(artist)}
          >
            <div className="artist-header">
              <h3 className="artist-name">{artist.name}</h3>
              <span className={`tier-badge ${artist.predictions.predicted_tier || 'unknown'}`}>
                {artist.predictions.predicted_tier || 'N/A'}
              </span>
            </div>
            
            <div className="artist-stats">
              <div className="stat-row">
                <span className="stat-label">Hit Rate:</span>
                <span className="stat-value">{artist.hit_rate}%</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Songs:</span>
                <span className="stat-value">{artist.total_songs}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Revenue:</span>
                <span className="stat-value">${(artist.estimated_total_revenue / 1000).toFixed(0)}k</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Genre:</span>
                <span className="stat-value genre">{artist.primary_genre}</span>
              </div>
            </div>

            <div className="prediction-info">
              <div className="hit-probability">
                <span>Hit Probability: </span>
                <strong>{artist.predictions.hit_probability || 0}%</strong>
              </div>
              <div className="hotness-score">
                Hotness: {artist.predictions.hotness_score || 0}/100
              </div>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="pagination-section">
          <div className="pagination">
            <button
              disabled={currentPage === 1}
              onClick={() => handlePageChange(currentPage - 1)}
            >
              Previous
            </button>
            
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const pageNum = i + 1;
              return (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum)}
                  className={currentPage === pageNum ? 'active' : ''}
                >
                  {pageNum}
                </button>
              );
            })}

            <button
              disabled={currentPage === totalPages}
              onClick={() => handlePageChange(currentPage + 1)}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const ArtistDetail = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { artistName } = useParams();
  const artist = location.state?.artist;

  if (!artist) {
    return (
      <div className="error">
        <h2>Artist "{artistName}" not found</h2>
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
          artist.hit_songs || 0,
          artist.good_songs || 0,
          artist.mid_songs || 0,
          artist.bust_songs || 0
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

  // Audio features data for bar chart
  const audioFeaturesData = {
    labels: ['Energy', 'Danceability', 'Positiveness', 'Speechiness', 'Liveness', 'Acousticness', 'Instrumentalness'],
    datasets: [
      {
        label: 'Average Values',
        data: [
          artist.avg_energy || 0,
          artist.avg_danceability || 0,
          artist.avg_positiveness || 0,
          artist.avg_speechiness || 0,
          artist.avg_liveness || 0,
          artist.avg_acousticness || 0,
          artist.avg_instrumentalness || 0
        ],
        backgroundColor: 'rgba(75, 192, 192, 0.8)',
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
        <div className="artist-basic-info">
          <h1>{artist.name}</h1>
          <div className="genre-tags">
            <span className="genre-tag">{artist.primary_genre}</span>
            <span className={`tier-badge large ${artist.predictions.predicted_tier || 'unknown'}`}>
              Predicted: {artist.predictions.predicted_tier || 'N/A'}
            </span>
          </div>

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
              <div className="stat-value">{artist.career_span_years?.toFixed(1) || 0}y</div>
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
                <span className="highlight">{artist.predictions.hit_probability || 0}%</span>
              </div>
              <div className="prediction-row">
                <span>Predicted Popularity:</span>
                <span>{artist.predictions.predicted_popularity || 'N/A'}</span>
              </div>
              <div className="prediction-row">
                <span>Confidence Interval:</span>
                <span>{artist.predictions.confidence_interval?.join(' - ') || 'N/A'}</span>
              </div>
              <div className="prediction-row">
                <span>Hotness Score:</span>
                <span>{artist.predictions.hotness_score || 0}/100</span>
              </div>
            </div>

            <div className="recommendation">
              <h3>Recommendation</h3>
              <p>{artist.predictions.recommendation || 'No recommendation available'}</p>
            </div>
          </div>

          <div className="info-card">
            <h2>Audio Features</h2>
            <div className="chart-container">
              <Bar
                data={audioFeaturesData}
                options={chartOptions}
                height={250}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Songs List */}
      {artist.songs && artist.songs.length > 0 && (
        <div className="info-card full-width">
          <h2>Song Catalog ({artist.songs.length} songs)</h2>
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
                <span>${song.revenue?.toLocaleString() || 0}</span>
                <span>{song.release_date || 'Unknown'}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Main App component
function App() {
  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <h1>Music Analytics Dashboard</h1>
          <p>Artist Performance & Predictions</p>
        </header>
        <Routes>
          <Route path="/" element={<ArtistList />} />
          <Route path="/artist/:artistName" element={<ArtistDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;