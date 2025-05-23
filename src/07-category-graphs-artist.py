import pandas as pd
import plotly.graph_objects as go
import os
import numpy as np
import re
from scipy.ndimage import gaussian_filter1d

def extract_year(date_str):
    if not isinstance(date_str, str):
        return np.nan
    match = re.search(r'\b(1[6-9][0-9]{2}|20[0-2][0-9])\b', date_str)
    return int(match.group(0)) if match else np.nan

print("Loading data...")
df = pd.read_csv('../output_csv/bremen_data_VX_categories.csv')

print("Processing columns...")
df['custom_category'] = df['custom_category'].dropna().str.split(';').apply(lambda x: [c.strip() for c in x])
df = df.explode('custom_category')
df = df[df['custom_category'].notna() & (df['custom_category'] != '')]


df['year'] = df['displayDate'].apply(extract_year)
df = df.dropna(subset=['year'])
df['year'] = df['year'].astype(int)

output_dir = '../output/04-artists-over-time'
os.makedirs(output_dir, exist_ok=True)

print("Creating figure...")
fig = go.Figure()

print("Adding all works timeline...")
all_counts = df.groupby('year').size().sort_index()
all_smoothed = gaussian_filter1d(all_counts.values, sigma=3)
fig.add_trace(go.Scatter(
    x=all_counts.index,
    y=all_smoothed,
    line_shape='spline',
    name='All Works'
))

print("Adding top 5 artists timelines...")
top_artists = df['artistName (preferred)'].value_counts().head(5).index.tolist()
for artist in top_artists:
    sub = df[df['artistName (preferred)'] == artist]
    count_by_year = sub.groupby('year').size().sort_index()
    smoothed = gaussian_filter1d(count_by_year.values, sigma=3)
    fig.add_trace(go.Scatter(
        x=count_by_year.index,
        y=smoothed,
        line_shape='spline',
        name=f"Artist: {artist}"
    ))

print("Adding custom category timelines...")
for cat in sorted(df['custom_category'].unique()):
    sub = df[df['custom_category'] == cat]
    count_by_year = sub.groupby('year').size().sort_index()
    smoothed = gaussian_filter1d(count_by_year.values, sigma=3)
    fig.add_trace(go.Scatter(
        x=count_by_year.index,
        y=smoothed,
        line_shape='spline',
        name=f"Category: {cat}"
    ))

fig.update_layout(
    title='Artworks Over Time – Categories, Top 5 Artists, and All Works (Gaussian Smoothed)',
    xaxis_title='Year',
    yaxis_title='Number of Artworks',
    legend_title='Legend',
    legend=dict(itemclick='toggle', itemdoubleclick='toggleothers')
)

fig.write_html(f'{output_dir}/artists_and_categories_timeline.html')
fig.write_image(f'{output_dir}/artists_and_categories_timeline.png')
fig.show()
