import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import re
import numpy as np
from scipy.ndimage import gaussian_filter1d

def extract_year(date_str):
    if not isinstance(date_str, str):
        return np.nan
    match = re.search(r'\b(1[6-9][0-9]{2}|20[0-2][0-9])\b', date_str)
    return int(match.group(0)) if match else np.nan

print("Loading data...")
df = pd.read_csv('../output_csv/bremen_data_VX_categories.csv')

print("Processing custom_category and associatedCountry...")
df['custom_category'] = df['custom_category'].dropna().str.split(';').apply(lambda x: [c.strip() for c in x])
df['associatedCountry'] = df['associatedCountry'].dropna().str.split(';').apply(lambda x: [c.strip() for c in x])
df = df.explode('custom_category')
df = df.explode('associatedCountry')
df = df[df['custom_category'].notna() & (df['custom_category'] != '')]
df = df[df['associatedCountry'].notna() & (df['associatedCountry'] != '')]

output_dir = '../output/03-categories'
os.makedirs(output_dir, exist_ok=True)

print("Generating histogram...")
cat_counts = df['custom_category'].value_counts().reset_index()
cat_counts.columns = ['category', 'count']
fig_hist = px.bar(cat_counts, x='category', y='count', title='Category Histogram', color_discrete_sequence=['orange'])
fig_hist.write_html(f'{output_dir}/category_histogram.html')
fig_hist.write_image(f'{output_dir}/category_histogram.png')
fig_hist.show()


print("Generating normalized heatmap by country with text annotations...")
raw_matrix = pd.crosstab(df['associatedCountry'], df['custom_category'])
filtered = raw_matrix[raw_matrix.sum(axis=1) >= 10]

total_counts = filtered.sum(axis=1).sort_values(ascending=True)
filtered = filtered.loc[total_counts.index]

normalized = filtered.div(filtered.sum(axis=1), axis=0) * 100

normalized.index = [f"{country} ({total_counts[country]})" for country in normalized.index]

text_vals = normalized.round(1).astype(str) + '%'

fig_heatmap = go.Figure(data=go.Heatmap(
    z=normalized.values,
    x=normalized.columns,
    y=normalized.index,
    text=text_vals.values,
    texttemplate="%{text}",
    textfont={"size":12},
    colorscale='Viridis',
    # colorscale='cividis',
    hoverongaps=False
))

fig_heatmap.update_layout(
    title='Percentage of Artworks per Category by Country (Normalized)',
    xaxis_title='Category',
    yaxis_title='Country'
)
fig_heatmap.write_html(f'{output_dir}/category_country_heatmap_normalized.html')
fig_heatmap.write_image(f'{output_dir}/category_country_heatmap_normalized.png')
fig_heatmap.show()


print("Generating strongly smoothed interactive timeline...")
df['year'] = df['displayDate'].apply(extract_year)
df = df.dropna(subset=['year'])
df['year'] = df['year'].astype(int)

fig_time = go.Figure()
for cat in sorted(df['custom_category'].unique()):
    sub = df[df['custom_category'] == cat]
    count_by_year = sub.groupby('year').size().sort_index()
    smoothed = gaussian_filter1d(count_by_year.values, sigma=3)
    fig_time.add_trace(go.Scatter(
        x=count_by_year.index,
        y=smoothed,
        # mode='lines',
        line_shape='spline',
        name=cat,
        visible=True
    ))

fig_time.update_layout(
    title='Artworks Over Time by Category (Gaussian Smoothed)',
    xaxis_title='Year',
    yaxis_title='Number of Artworks',
    legend_title='Category',
    legend=dict(itemclick='toggle', itemdoubleclick='toggleothers')
)
fig_time.write_html(f'{output_dir}/category_timeline.html')
fig_time.write_image(f'{output_dir}/category_timeline.png')
fig_time.show()
