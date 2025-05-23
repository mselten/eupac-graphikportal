import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

fig = make_subplots(
    rows=4, cols=1,
    shared_xaxes=False,
    vertical_spacing=0.06,
    subplot_titles=[f"{c} / {csv_names[c]}" for c in gdp],
    specs=[[{"secondary_y": True}] for _ in range(4)]
)

for i, (country, gvals) in enumerate(gdp.items(), 1):
    sub = df[df["associatedCountry"] == csv_names[country]]
    counts = sub.groupby("year").size().groupby(level=0).first().sort_index()
    smooth = gaussian_filter1d(counts.values, sigma=3) if len(counts) > 3 else counts.values

    fig.add_trace(go.Scatter(
        x=counts.index, y=smooth, name=f"{country} Artworks",
        line=dict(color="blue")
    ), row=i, col=1, secondary_y=False)

    fig.add_trace(go.Scatter(
        x=years_gdp, y=gvals, name=f"{country} GDP",
        line=dict(color="orange")
    ), row=i, col=1, secondary_y=True)

    fig.update_yaxes(title_text="Artworks", row=i, col=1, secondary_y=False)
    fig.update_yaxes(title_text="GDP", row=i, col=1, secondary_y=True)
    fig.update_xaxes(title_text="Year", row=i, col=1, range=[1800, 2000])

fig.update_layout(height=1500, width=1000, title_text="Artworks and GDP over Time by Country")

output_dir = "../output/05-GDP"
os.makedirs(output_dir, exist_ok=True)
fig.write_html(f"{output_dir}/gdp_artworks.html")
fig.write_image(f"{output_dir}/gdp_artworks.png")
fig.show()
