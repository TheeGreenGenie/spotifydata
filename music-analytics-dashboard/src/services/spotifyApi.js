/**
 * Spotify Web API Service
 * Fetches artist images and basic information from Spotify
 */

const SPOTIFY_API_BASE = 'https://api.spotify.com/v1';
let accessToken = null;
let tokenExpiry = null;

/**
 * Get Spotify access token using Client Credentials flow
 * You'll need to set up a Spotify app at https://developer.spotify.com/dashboard
 */
async function getAccessToken() {
  // Check if we have a valid token
  if (accessToken && tokenExpiry && Date.now() < tokenExpiry) {
    return accessToken;
  }

  try {
    // For development, you can store these in environment variables
    // Create a .env file in music-analytics-dashboard/ with:
    // REACT_APP_SPOTIFY_CLIENT_ID=your_client_id
    // REACT_APP_SPOTIFY_CLIENT_SECRET=your_client_secret
    const clientId = process.env.REACT_APP_SPOTIFY_CLIENT_ID;
    const clientSecret = process.env.REACT_APP_SPOTIFY_CLIENT_SECRET;

    console.log('🔍 Spotify API Debug:', {
      hasClientId: !!clientId,
      hasClientSecret: !!clientSecret,
      clientIdLength: clientId?.length,
      clientIdPreview: clientId ? clientId.substring(0, 8) + '...' : 'missing'
    });

    if (!clientId || !clientSecret) {
      console.error('❌ Spotify API credentials not configured. Artist images will not be available.');
      console.log('Make sure your .env file has:');
      console.log('REACT_APP_SPOTIFY_CLIENT_ID=your_id_here');
      console.log('REACT_APP_SPOTIFY_CLIENT_SECRET=your_secret_here');
      console.log('(No quotes around the values!)');
      return null;
    }

    const response = await fetch('https://accounts.spotify.com/api/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + btoa(`${clientId}:${clientSecret}`)
      },
      body: 'grant_type=client_credentials'
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Spotify API token request failed:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      throw new Error(`Failed to get Spotify access token: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    accessToken = data.access_token;
    // Set expiry to 5 minutes before actual expiry for safety
    tokenExpiry = Date.now() + ((data.expires_in - 300) * 1000);

    console.log('✅ Successfully obtained Spotify access token');
    return accessToken;
  } catch (error) {
    console.error('❌ Error getting Spotify access token:', error);
    return null;
  }
}

/**
 * Search for an artist on Spotify by name
 * @param {string} artistName - The name of the artist to search for
 * @returns {Promise<Object|null>} Artist data or null if not found
 */
export async function searchArtist(artistName) {
  try {
    const token = await getAccessToken();
    if (!token) {
      return null;
    }

    const encodedName = encodeURIComponent(artistName);
    const response = await fetch(
      `${SPOTIFY_API_BASE}/search?q=${encodedName}&type=artist&limit=1`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to search for artist');
    }

    const data = await response.json();

    if (data.artists.items.length === 0) {
      return null;
    }

    return data.artists.items[0];
  } catch (error) {
    console.error(`Error searching for artist "${artistName}":`, error);
    return null;
  }
}

/**
 * Get artist information including image and basic details
 * @param {string} artistName - The name of the artist
 * @returns {Promise<Object>} Artist information with fallbacks to "N/A"
 */
export async function getArtistInfo(artistName) {
  const defaultInfo = {
    name: artistName,
    image: null,
    followers: 'N/A',
    popularity: 'N/A',
    genres: 'N/A',
    spotifyUrl: null
  };

  try {
    console.log(`🎵 Searching Spotify for artist: "${artistName}"`);
    const artistData = await searchArtist(artistName);

    if (!artistData) {
      console.log(`❌ Artist "${artistName}" not found on Spotify`);
      return defaultInfo;
    }

    console.log(`✅ Found artist on Spotify:`, {
      name: artistData.name,
      hasImage: !!(artistData.images && artistData.images.length > 0),
      followers: artistData.followers?.total,
      popularity: artistData.popularity
    });

    // Get the highest resolution image available
    const image = artistData.images && artistData.images.length > 0
      ? artistData.images[0].url
      : null;

    return {
      name: artistData.name || artistName,
      image: image,
      followers: artistData.followers?.total
        ? artistData.followers.total.toLocaleString()
        : 'N/A',
      popularity: artistData.popularity !== undefined
        ? artistData.popularity
        : 'N/A',
      genres: artistData.genres && artistData.genres.length > 0
        ? artistData.genres.join(', ')
        : 'N/A',
      spotifyUrl: artistData.external_urls?.spotify || null
    };
  } catch (error) {
    console.error(`Error getting artist info for "${artistName}":`, error);
    return defaultInfo;
  }
}

/**
 * Batch get artist info for multiple artists with caching
 */
const artistCache = new Map();

export async function getArtistInfoCached(artistName) {
  if (artistCache.has(artistName)) {
    return artistCache.get(artistName);
  }

  const info = await getArtistInfo(artistName);
  artistCache.set(artistName, info);
  return info;
}

/**
 * Clear the artist info cache
 */
export function clearArtistCache() {
  artistCache.clear();
}
