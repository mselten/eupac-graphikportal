import pandas as pd
import plotly.express as px
import os


def generate_histogram(df, column_name):
    """
    Generate a bar chart (histogram) for a given column.

    Parameters:
    - df: DataFrame containing the data
    - column_name: Name of the column to plot

    Returns:
    - Plotly Figure object
    """
    # Split by semicolons for specific columns
    if column_name in ['subject_translated', 'nationalityOfArtist']:
        values = df[column_name].str.split(';').explode().dropna().str.strip()
    else:
        values = df[column_name].dropna()

    # Filter out categories with less than 4 occurrences
    counts = values.value_counts()
    filtered = counts[counts >= 1]
    sorted_counts = filtered.sort_values(ascending=False)

    # Convert to DataFrame for Plotly compatibility
    df_plot = sorted_counts.reset_index()
    df_plot.columns = ['category', 'count']

    # Create the plot
    fig = px.bar(
        df_plot,
        x='category',
        y='count',
        labels={'category': column_name, 'count': 'Count'},
        title=f'Histogram of {column_name}',
        color_discrete_sequence=['orange']
    )
    return fig

def save_figures(figs, base_dir='../output/02-brem-init-analysis'):
    """
    Save figures as HTML and PNG to the specified directory.
    """
    os.makedirs(base_dir, exist_ok=True)

    for i, fig in enumerate(figs):
        filename = f"histogram_{i + 1}"
        fig.write_html(os.path.join(base_dir, f"{filename}.html"))
        fig.write_image(os.path.join(base_dir, f"{filename}.png"))
        fig.show()


# Load the data
df = pd.read_csv('../output_csv/bremen_data_V4_translated.csv')

# Filter for female artists
df_female = df[df['genderOfArtist'] == 'Frau']

# Generate original histograms
gender_fig = generate_histogram(df, 'genderOfArtist')
nationality_fig = generate_histogram(df, 'placeOfActivity')
subject_fig = generate_histogram(df, 'subject_translated')

# Generate new histograms for female artists
nationality_female_fig = generate_histogram(df_female, 'placeOfActivity')
subject_female_fig = generate_histogram(df_female, 'subject_translated')

# Save all figures
save_figures([
    gender_fig,
    nationality_fig,
    subject_fig,
    nationality_female_fig,
    subject_female_fig
])