import pandas as pd
import json

with open('ml_predictions.json', 'r') as f:
    data = json.load(f)

records = []
for artist, info in data.items():
    # Flatten nested dictionaries manually
    record = {
        "artist": artist,
        **{f"{k}": v for k, v in info["current_status"].items()},
        **{f"{k}": v for k, v in info["predictions"].items()},
        "timestamp": info["timestamp"]
    }
    records.append(record)

df = pd.DataFrame(records)
df['hits'] = round((df['hit_rate']/100)*df['total_songs'])
ourcolumns = ['artist', 'total_songs', 'hit_rate', 'career_span_years',
       'total_revenue', 'primary_genre', 'hit_probability',
       'predicted_popularity', 'predicted_tier', 'confidence_interval',
       'hotness_score', 'hits']
df = df[ourcolumns] 
df.sort_values('hits', ascending=False, inplace=True)
highdf = df[df['hit_probability']>=25]
highdf.sort_values('hits', ascending=False, inplace=True)

print(df.head())

print(highdf.head(50))