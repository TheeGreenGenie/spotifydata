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
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
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

  // Sort function
  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
    setCurrentPage(1); // Reset to first page when sorting
  };

  // Filter and sort artists
  const filteredAndSortedArtists = useMemo(() => {
    let filtered = combinedArtists.filter(artist =>
      artist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (artist.primary_genre && artist.primary_genre.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    // Apply sorting
    if (sortConfig.key) {
      filtered.sort((a, b) => {
        let aValue, bValue;

        switch (sortConfig.key) {
          case 'name':
            aValue = a.name.toLowerCase();
            bValue = b.name.toLowerCase();
            break;
          case 'total_songs':
            aValue = a.total_songs || 0;
            bValue = b.total_songs || 0;
            break;
          case 'hit_rate':
            aValue = a.hit_rate || 0;
            bValue = b.hit_rate || 0;
            break;
          case 'revenue':
            aValue = a.estimated_total_revenue || 0;
            bValue = b.estimated_total_revenue || 0;
            break;
          case 'predicted_tier':
            const tierOrder = { hit: 4, good: 3, mid: 2, bust: 1, 'N/A': 0 };
            aValue = tierOrder[a.predictions.predicted_tier] || 0;
            bValue = tierOrder[b.predictions.predicted_tier] || 0;
            break;
          case 'hit_probability':
            aValue = a.predictions.hit_probability || 0;
            bValue = b.predictions.hit_probability || 0;
            break;
          case 'hotness':
            aValue = a.predictions.hotness_score || 0;
            bValue = b.predictions.hotness_score || 0;
            break;
          default:
            return 0;
        }

        if (aValue < bValue) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }

    return filtered;
  }, [combinedArtists, searchTerm, sortConfig]);

  const totalPages = Math.ceil(filteredAndSortedArtists.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const currentArtists = filteredAndSortedArtists.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  // Sort indicator component
  const SortIndicator = ({ columnKey }) => {
    if (sortConfig.key !== columnKey) {
      return <span className="sort-indicator">⇅</span>;
    }
    return <span className="sort-indicator active">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>;
  };

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
        Showing {startIndex + 1}-{Math.min(startIndex + ITEMS_PER_PAGE, filteredAndSortedArtists.length)} of {filteredAndSortedArtists.length} artists
        (Total in database: {Object.keys(artistsData.artists || {}).length})
      </div>

      <div className="artists-table-container">
        <div className="artists-table">
          <div className="artists-table-header">
            <span className="sortable" onClick={() => handleSort('name')}>
              Artist(s) <SortIndicator columnKey="name" />
            </span>
            <span>Genre</span>
            <span className="sortable" onClick={() => handleSort('total_songs')}>
              Total Songs <SortIndicator columnKey="total_songs" />
            </span>
            <span className="sortable" onClick={() => handleSort('hit_rate')}>
              Hit Rate <SortIndicator columnKey="hit_rate" />
            </span>
            <span className="sortable" onClick={() => handleSort('revenue')}>
              Revenue <SortIndicator columnKey="revenue" />
            </span>
            <span className="sortable" onClick={() => handleSort('predicted_tier')}>
              Predicted Tier <SortIndicator columnKey="predicted_tier" />
            </span>
            <span className="sortable" onClick={() => handleSort('hit_probability')}>
              Hit Probability <SortIndicator columnKey="hit_probability" />
            </span>
            <span className="sortable" onClick={() => handleSort('hotness')}>
              Hotness <SortIndicator columnKey="hotness" />
            </span>
          </div>
          {currentArtists.map(artist => (
            <div
              key={artist.name}
              className={`artists-table-row tier-${artist.predictions.predicted_tier || 'unknown'}`}
              onClick={() => handleArtistClick(artist)}
            >
              <span className="artist-name-cell">{artist.name}</span>
              <span className="genre-cell">{artist.primary_genre}</span>
              <span>{artist.total_songs}</span>
              <span>{artist.hit_rate}%</span>
              <span>
                {artist.estimated_total_revenue >= 1000000
                  ? `$${(artist.estimated_total_revenue / 1000000).toFixed(1)}M`
                  : `$${(artist.estimated_total_revenue / 1000).toFixed(0)}k`}
              </span>
              <span>
                <span className={`tier-badge ${artist.predictions.predicted_tier || 'unknown'}`}>
                  {artist.predictions.predicted_tier || 'N/A'}
                </span>
              </span>
              <span>{artist.predictions.hit_probability || 0}%</span>
              <span>{artist.predictions.hotness_score || 0}/100</span>
            </div>
          ))}
        </div>
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

            {/* First page */}
            <button
              onClick={() => handlePageChange(1)}
              className={currentPage === 1 ? 'active' : ''}
            >
              1
            </button>

            {/* Show ellipsis if current page is far from start */}
            {currentPage > 3 && <span className="pagination-ellipsis">...</span>}

            {/* Pages around current page */}
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter(pageNum => {
                // Show pages around current page (1 before and 1 after)
                return pageNum > 1 && pageNum < totalPages && Math.abs(pageNum - currentPage) <= 1;
              })
              .map(pageNum => (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum)}
                  className={currentPage === pageNum ? 'active' : ''}
                >
                  {pageNum}
                </button>
              ))}

            {/* Show ellipsis if current page is far from end */}
            {currentPage < totalPages - 2 && <span className="pagination-ellipsis">...</span>}

            {/* Last page */}
            {totalPages > 1 && (
              <button
                onClick={() => handlePageChange(totalPages)}
                className={currentPage === totalPages ? 'active' : ''}
              >
                {totalPages}
              </button>
            )}

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
  const [songSortConfig, setSongSortConfig] = useState({ key: null, direction: 'asc' });

  // Song sorting handler
  const handleSongSort = (key) => {
    let direction = 'asc';
    if (songSortConfig.key === key && songSortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSongSortConfig({ key, direction });
  };

  // Sort indicator component for songs table
  const SongSortIndicator = ({ columnKey }) => {
    if (songSortConfig.key !== columnKey) {
      return <span className="sort-indicator">⇅</span>;
    }
    return <span className="sort-indicator active">{songSortConfig.direction === 'asc' ? '↑' : '↓'}</span>;
  };

  // Sorted songs
  const sortedSongs = useMemo(() => {
    if (!artist || !artist.songs || artist.songs.length === 0) return [];

    const songs = [...artist.songs];

    if (songSortConfig.key) {
      songs.sort((a, b) => {
        let aValue, bValue;

        switch (songSortConfig.key) {
          case 'title':
            aValue = (a.title || '').toLowerCase();
            bValue = (b.title || '').toLowerCase();
            break;
          case 'popularity':
            aValue = a.popularity || 0;
            bValue = b.popularity || 0;
            break;
          case 'tier':
            const tierOrder = { hit: 4, good: 3, mid: 2, bust: 1 };
            aValue = tierOrder[a.tier] || 0;
            bValue = tierOrder[b.tier] || 0;
            break;
          case 'revenue':
            aValue = a.revenue || 0;
            bValue = b.revenue || 0;
            break;
          case 'release_date':
            aValue = a.release_date ? new Date(a.release_date).getTime() : 0;
            bValue = b.release_date ? new Date(b.release_date).getTime() : 0;
            break;
          default:
            return 0;
        }

        if (aValue < bValue) {
          return songSortConfig.direction === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
          return songSortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }

    return songs;
  }, [artist, songSortConfig]);

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

  // Calculate revenue split among stakeholders
  // Based on typical music industry revenue split percentages
  const calculateRevenueStakeholders = () => {
    const totalRevenue = artist.estimated_total_revenue || 0;

    // Typical industry split (approximate percentages)
    const splits = {
      artist: totalRevenue * 0.15,           // Artist gets ~15%
      label: totalRevenue * 0.45,            // Record label gets ~45%
      producers: totalRevenue * 0.12,        // Producers get ~12%
      distributors: totalRevenue * 0.08,     // Physical/Digital distributors get ~8%
      streaming: totalRevenue * 0.10,        // Streaming platforms get ~10%
      other: totalRevenue * 0.10             // Other (marketing, management, etc.) ~10%
    };

    return splits;
  };

  const revenueStakeholders = calculateRevenueStakeholders();

  // Revenue stakeholder distribution pie chart data
  const stakeholderDistributionData = {
    labels: ['Record Label', 'Artist', 'Producers', 'Streaming Platforms', 'Distributors', 'Other (Marketing/Mgmt)'],
    datasets: [
      {
        data: [
          revenueStakeholders.label,
          revenueStakeholders.artist,
          revenueStakeholders.producers,
          revenueStakeholders.streaming,
          revenueStakeholders.distributors,
          revenueStakeholders.other
        ],
        backgroundColor: [
          '#667eea', // Purple for label
          '#4CAF50', // Green for artist
          '#FFC107', // Yellow for producers
          '#E91E63', // Pink for streaming
          '#00BCD4', // Cyan for distributors
          '#9E9E9E'  // Grey for other
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
              <div className="stat-value">
                {artist.estimated_total_revenue >= 1000000
                  ? `$${(artist.estimated_total_revenue / 1000000).toFixed(1)}M`
                  : `$${(artist.estimated_total_revenue / 1000).toFixed(0)}k`}
              </div>
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

          <div className="info-card">
            <h2>Revenue Distribution - Stakeholder Split</h2>
            <p className="chart-subtitle">Estimated revenue breakdown based on industry standards</p>
            <div className="chart-container">
              <Doughnut
                data={stakeholderDistributionData}
                options={{
                  ...chartOptions,
                  plugins: {
                    ...chartOptions.plugins,
                    tooltip: {
                      callbacks: {
                        label: function(context) {
                          const label = context.label || '';
                          const value = context.parsed || 0;
                          const total = context.dataset.data.reduce((a, b) => a + b, 0);
                          const percentage = ((value / total) * 100).toFixed(1);
                          const formattedValue = value >= 1000000
                            ? `$${(value / 1000000).toFixed(2)}M`
                            : `$${(value / 1000).toFixed(0)}k`;
                          return `${label}: ${formattedValue} (${percentage}%)`;
                        }
                      }
                    }
                  }
                }}
                height={250}
              />
            </div>
            <div className="revenue-breakdown">
              <div className="revenue-item stakeholder-label">
                <span className="revenue-label">
                  <span className="color-indicator" style={{backgroundColor: '#667eea'}}></span>
                  Record Label:
                </span>
                <span className="revenue-value">
                  ${revenueStakeholders.label >= 1000000
                    ? `${(revenueStakeholders.label / 1000000).toFixed(2)}M`
                    : `${(revenueStakeholders.label / 1000).toFixed(0)}k`}
                  {' '}(45%)
                </span>
              </div>
              <div className="revenue-item stakeholder-artist">
                <span className="revenue-label">
                  <span className="color-indicator" style={{backgroundColor: '#4CAF50'}}></span>
                  Artist:
                </span>
                <span className="revenue-value">
                  ${revenueStakeholders.artist >= 1000000
                    ? `${(revenueStakeholders.artist / 1000000).toFixed(2)}M`
                    : `${(revenueStakeholders.artist / 1000).toFixed(0)}k`}
                  {' '}(15%)
                </span>
              </div>
              <div className="revenue-item stakeholder-producers">
                <span className="revenue-label">
                  <span className="color-indicator" style={{backgroundColor: '#FFC107'}}></span>
                  Producers:
                </span>
                <span className="revenue-value">
                  ${revenueStakeholders.producers >= 1000000
                    ? `${(revenueStakeholders.producers / 1000000).toFixed(2)}M`
                    : `${(revenueStakeholders.producers / 1000).toFixed(0)}k`}
                  {' '}(12%)
                </span>
              </div>
              <div className="revenue-item stakeholder-streaming">
                <span className="revenue-label">
                  <span className="color-indicator" style={{backgroundColor: '#E91E63'}}></span>
                  Streaming Platforms:
                </span>
                <span className="revenue-value">
                  ${revenueStakeholders.streaming >= 1000000
                    ? `${(revenueStakeholders.streaming / 1000000).toFixed(2)}M`
                    : `${(revenueStakeholders.streaming / 1000).toFixed(0)}k`}
                  {' '}(10%)
                </span>
              </div>
              <div className="revenue-item stakeholder-distributors">
                <span className="revenue-label">
                  <span className="color-indicator" style={{backgroundColor: '#00BCD4'}}></span>
                  Distributors:
                </span>
                <span className="revenue-value">
                  ${revenueStakeholders.distributors >= 1000000
                    ? `${(revenueStakeholders.distributors / 1000000).toFixed(2)}M`
                    : `${(revenueStakeholders.distributors / 1000).toFixed(0)}k`}
                  {' '}(8%)
                </span>
              </div>
              <div className="revenue-item stakeholder-other">
                <span className="revenue-label">
                  <span className="color-indicator" style={{backgroundColor: '#9E9E9E'}}></span>
                  Other (Marketing/Mgmt):
                </span>
                <span className="revenue-value">
                  ${revenueStakeholders.other >= 1000000
                    ? `${(revenueStakeholders.other / 1000000).toFixed(2)}M`
                    : `${(revenueStakeholders.other / 1000).toFixed(0)}k`}
                  {' '}(10%)
                </span>
              </div>
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
              <span className="sortable" onClick={() => handleSongSort('title')}>
                Title <SongSortIndicator columnKey="title" />
              </span>
              <span className="sortable" onClick={() => handleSongSort('popularity')}>
                Popularity <SongSortIndicator columnKey="popularity" />
              </span>
              <span className="sortable" onClick={() => handleSongSort('tier')}>
                Tier <SongSortIndicator columnKey="tier" />
              </span>
              <span className="sortable" onClick={() => handleSongSort('revenue')}>
                Revenue <SongSortIndicator columnKey="revenue" />
              </span>
              <span className="sortable" onClick={() => handleSongSort('release_date')}>
                Release Date <SongSortIndicator columnKey="release_date" />
              </span>
            </div>
            {sortedSongs.map((song, index) => (
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