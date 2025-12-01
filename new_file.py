import pandas as pd

mydf = pd.read_csv("spotify_dataset.csv")

mydf['artist_lower'] = mydf['Artist(s)'].str.lower().str.strip()
mydf['song_lower'] = mydf['song'].str.lower().str.strip()

mydf = mydf.drop_duplicates(subset=['artist_lower', 'song_lower'], keep='first')

mydf = mydf.drop(columns=['artist_lower', 'song_lower'])

