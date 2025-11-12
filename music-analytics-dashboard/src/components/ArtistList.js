// components/ArtistList.js
import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

const ITEMS_PER_PAGE = 25;

const ArtistList = () => {
  const [artistsData, setArtistsData] = useState({});
  const [predictionsData, setPredictionsData] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    genre: '',
    tier: '',
    minHitRate: 0,
    minRevenue: 0
  });
  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load both JSON files
        const [artistsResponse, predictionsResponse] = await Promise.all([
          fetch('/data/artists-data.json'),
          fetch('/data/predictions-data.json')
        ]);
        
        const artistsJson = await artistsResponse.json();
        const predictionsJson = await predictionsResponse.json();
        
        setArtistsData(artistsJson.artists);
        setPredictionsData(predictionsJson);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Combine artist data with predictions
  const combinedArtists = useMemo(() => {
    return Object.entries(artistsData).map(([artistName, artistData]) => {
      const prediction = predictionsData[artistName] || {};
      return {
        name: artistName,
        ...artistData,
        predictions: prediction.predictions || {},
        timestamp: prediction.timestamp
      };
    });
  }, [artistsData, predictionsData]);

  // Filter artists based on search term and filters
  const filteredArtists = useMemo(() => {
    return combinedArtists.filter(artist => {
      const matchesSearch = artist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          artist.primary_genre.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesGenre = !filters.genre || artist.primary_genre === filters.genre;
      const matchesTier = !filters.tier || artist.predictions.predicted_tier === filters.tier;
      const matchesHitRate = artist.hit_rate >= filters.minHitRate;
      const matchesRevenue = artist.estimated_total_revenue >= filters.minRevenue;

      return matchesSearch && matchesGenre && matchesTier && matchesHitRate && matchesRevenue;
    });
  }, [combinedArtists, searchTerm, filters]);

  // Calculate pagination
  const totalPages = Math.ceil(filteredArtists.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const currentArtists = filteredArtists.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  // Get unique genres for filter dropdown
  const uniqueGenres = useMemo(() => {
    const genres = new Set();
    combinedArtists.forEach(artist => {
      if (artist.primary_genre) {
        genres.add(artist.primary_genre);
      }
    });
    return Array.from(genres).sort();
  }, [combinedArtists]);

  const handleArtistClick = (artist) => {
    navigate(`/artist/${encodeURIComponent(artist.name)}`, { state: { artist } });
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo(0, 0);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
    setCurrentPage(1);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading artist data...</p>
      </div>
    );
  }

  return (
    <div className="artist-list">
      {/* Search and Filters */}
      <div className="filters-section">
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

        <div className="filter-grid">
          <div className="filter-group">
            <label>Genre:</label>
            <select 
              value={filters.genre} 
              onChange={(e) => handleFilterChange('genre', e.target.value)}
            >
              <option value="">All Genres</option>
              {uniqueGenres.map(genre => (
                <option key={genre} value={genre}>{genre}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Predicted Tier:</label>
            <select 
              value={filters.tier} 
              onChange={(e) => handleFilterChange('tier', e.target.value)}
            >
              <option value="">All Tiers</option>
              <option value="hit">Hit</option>
              <option value="good">Good</option>
              <option value="mid">Mid</option>
              <option value="bust">Bust</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Min Hit Rate: {filters.minHitRate}%</label>
            <input
              type="range"
              min="0"
              max="100"
              value={filters.minHitRate}
              onChange={(e) => handleFilterChange('minHitRate', parseInt(e.target.value))}
            />
          </div>

          <div className="filter-group">
            <label>Min Revenue: ${(filters.minRevenue / 1000).toFixed(0)}k</label>
            <input
              type="range"
              min="0"
              max="10000000"
              step="100000"
              value={filters.minRevenue}
              onChange={(e) => handleFilterChange('minRevenue', parseInt(e.target.value))}
            />
          </div>
        </div>
      </div>

      {/* Artists Grid */}
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

      {/* Pagination */}
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
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }

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

          <div className="pagination-info">
            Showing {startIndex + 1}-{Math.min(startIndex + ITEMS_PER_PAGE, filteredArtists.length)} of {filteredArtists.length} artists
          </div>
        </div>
      )}
    </div>
  );
};

export default ArtistList;