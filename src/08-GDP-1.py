import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter1d

gdp = {
    "France": [1135, 1594, 2876, 5271],
    # "Netherlands": [1838, 2371, 3485, 5996],
    "Belgium": [1319, 2697, 4220, 5462],
    "Japan": [669, 737, 1180, 1921],
}
years_gdp = [1820, 1850, 1900, 1950]
csv_names = {
    "France": "Frankreich",
    "Netherlands": "Niederlande",
    "Belgium": "Belgien",
    "Japan": "Japan",
}

df = pd.read_csv("../output_csv/bremen_data_VX_categories.csv")
df["custom_category"] = df["custom_category"].dropna().str.split(";").apply(lambda x: [c.strip() for c in x])
df["associatedCountry"] = df["associatedCountry"].dropna().str.split(";").apply(lambda x: [c.strip() for c in x])
df = df.explode("custom_category").explode("associatedCountry")
df = df[df["custom_category"].notna() & df["associatedCountry"].notna()]
df["year"] = pd.to_numeric(df["displayDate"], errors="coerce")
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

fig = go.Figure()

# Define color palette for countries
country_colors = {
    "France": "blue",
    "Belgium": "green",
    "Japan": "red",
    # "Netherlands": "purple"
}

for country, gvals in gdp.items():
    sub = df[df["associatedCountry"] == csv_names[country]]
    counts = sub.groupby("year").size().groupby(level=0).first().sort_index()
    smooth = gaussian_filter1d(counts.values, sigma=3) if len(counts) > 3 else counts.values

    # Artworks (left y-axis)
    fig.add_trace(go.Scatter(
        x=counts.index, y=smooth, name=f"{country} Artworks",
        line=dict(color=country_colors[country])
    ))

    # GDP (right y-axis)
    fig.add_trace(go.Scatter(
        x=years_gdp, y=gvals, name=f"{country} GDP",
        line=dict(color=country_colors[country]),
        yaxis="y2"  # Assign to the second y-axis
    ))

fig.update_layout(
    title_text="Artworks and GDP over Time by Country",
    xaxis_title="Year",
    yaxis_title="Number of Artworks",
    yaxis2=dict(
        title="GDP",
        overlaying='y',
        side='right',
        showgrid=False  # Optional: remove grid lines for GDP axis
    ),
    # legend=dict(x=0.5, y=-0.5, orientation='h'),
    height=1000,
    width=1200
)

output_dir = "../output/05-GDP"
os.makedirs(output_dir, exist_ok=True)
fig.write_html(f"{output_dir}/gdp_artworks.html")
fig.write_image(f"{output_dir}/gdp_artworks.png")
fig.show()