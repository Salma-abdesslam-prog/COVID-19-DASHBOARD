# Import necessary libraries
import pandas as pd
import numpy as np
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

# Load a state-of-the-art dataset: "COVID-19 Data from Johns Hopkins University"
# URL: https://github.com/CSSEGISandData/COVID-19
url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

# Load data into DataFrame
data = pd.read_csv(url)

# Transform data for analysis
data = data.drop(['Province/State', 'Lat', 'Long'], axis=1).groupby('Country/Region').sum().T

# Convert date strings to datetime objects
data.index = pd.to_datetime(data.index, errors='coerce')
data = data.dropna()  # Drop any rows with invalid dates

# Create new feature: daily new cases
daily_cases = data.diff().fillna(0)

# Set up Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Required for deployment

# Layout for the dashboard
app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("COVID-19 Dashboard", className="text-center text-primary mb-4"), width=12)
    ),
    dbc.Row([
        dbc.Col([
            html.Label("Select Country:"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in data.columns],
                value='France',
                multi=False,
                className="mb-3"
            )
        ], width=4),
        dbc.Col([
            html.Label("Select Date Range:"),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=data.index.min(),
                end_date=data.index.max(),
                display_format='YYYY-MM-DD',
                className="mb-3"
            )
        ], width=8)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='cumulative-cases-plot')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='daily-cases-plot')
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='top-countries-cumulative')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='top-countries-daily')
        ], width=6)
    ])
], fluid=True)

# Define callback for updating graphs
@app.callback(
    [Output('cumulative-cases-plot', 'figure'),
     Output('daily-cases-plot', 'figure'),
     Output('top-countries-cumulative', 'figure'),
     Output('top-countries-daily', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(selected_country, start_date, end_date):
    if not selected_country or not start_date or not end_date:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    filtered_data = data.loc[start_date:end_date]
    filtered_daily = daily_cases.loc[start_date:end_date]

    # Plot Cumulative Cases
    fig_cumulative = px.line(
        filtered_data,
        x=filtered_data.index,
        y=selected_country,
        title=f'Cumulative COVID-19 Cases in {selected_country}',
        labels={'x': 'Date', 'y': 'Number of Cases'},
        template='plotly_white'
    )

    # Plot Daily New Cases
    fig_daily = px.bar(
        filtered_daily,
        x=filtered_daily.index,
        y=selected_country,
        title=f'Daily New COVID-19 Cases in {selected_country}',
        labels={'x': 'Date', 'y': 'Number of New Cases'},
        template='plotly_white'
    )

    # Top 5 countries by cumulative cases
    top_countries = filtered_data.iloc[-1].sort_values(ascending=False).head(5).index
    fig_top_cumulative = px.line(
        filtered_data[top_countries],
        x=filtered_data.index,
        y=top_countries,
        title='Top 5 Countries by Cumulative COVID-19 Cases',
        labels={'x': 'Date', 'y': 'Number of Cases'},
        template='plotly_white'
    )

    # Top 5 countries by daily cases
    fig_top_daily = px.line(
        filtered_daily[top_countries],
        x=filtered_daily.index,
        y=top_countries,
        title='Top 5 Countries by Daily New COVID-19 Cases',
        labels={'x': 'Date', 'y': 'Number of New Cases'},
        template='plotly_white'
    )

    return fig_cumulative, fig_daily, fig_top_cumulative, fig_top_daily

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
