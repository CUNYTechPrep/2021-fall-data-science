import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import datetime
import numpy as np


app = Dash(__name__)

# Import your data 
df_years = pd.read_csv('data/covid_by_year.csv')
df_daily = pd.read_csv('data/covid-19-by-state-by-day.csv')
master_df = pd.read_csv('data/covid-by-region-by-day.csv')


# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", 
        style={'text-align': 'center'}),
    
    html.Br(),


    # --------------------------------------------------------------------------------
    # First Chart

    # First we include a dropdown slector
    dcc.Dropdown(id="selected_year",
                 options=[
                     {"label": "2020", "value": 2020},
                     {"label": "2021", "value": 2021}
                     ],
                 multi=False,
                 value=2020,
                 style={'width': "40%"}
                 ),

    #  Now we include the graph.
    dcc.Graph(
        id='my_covid_map', 
        figure={}),



    # --------------------------------------------------------------------------------
    # Second and Thrid Charts

    ## Time series dropdown
    dcc.Dropdown(
        id="state_selected",
        options=[{"label": x, "value": x} 
                 for x in df_daily.state.unique()],
        value='New York',
        style={'width': "40%"},
        clearable=False,
    ),

    # Div where the time series graphs will go.
    html.Div( 
        children=[
            # The state time series chart will go in here
            dcc.Graph(
                id="state-time-series-chart", 
                style={'display': 'inline-block'}),

            # The second time series chart will go in here
            dcc.Graph(
                id="usa-time-series-chart", 
                style={'display': 'inline-block'})
            ]
    ),
    
    # Div where the output of the the selected state will go
    html.Div(id='output_container', children=[]),


    # --------------------------------------------------------------------------------
    # Fourth Chart

    # A graph component that we will fill with the scatter-plot
    dcc.Graph(id='scatter-plot'),
    html.Div(id='scatter_plot_value')
])
# @end of app.layout


# ------------------------------------------------------------------------------
# First map chart and connecting the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='my_covid_map', component_property='figure'),
    [Input(component_id='selected_year', component_property='value')]
)
def covid_map(selected_year):
    print(selected_year)
    print(type(selected_year))

    tmp_df = df_years.copy()

    # Just removing the rows where the values are the total USA.
    tmp_df = tmp_df[tmp_df.state != 'USA']

    # Selecting just the rows that the data is the input from the user.
    tmp_df = tmp_df[tmp_df['year'] == selected_year]


    #Plotly Graph Objects (GO)
    fig = go.Figure(
        data=[go.Choropleth(
            locationmode='USA-states',
            locations=tmp_df['state code'],
            z=tmp_df["death_rate"].astype(float)
        )]
    )
    
    # Adding some customizations.
    fig.update_layout(
        title_text="Covid Death Rates Per Year",
        title_xanchor="center",
        title_font=dict(size=42),
        title_x=0.5,
        geo=dict(scope='usa'),
    )

    return fig


# ----------------------------------------------------------------
# Time series charts 
@app.callback(
    [Output(component_id="state-time-series-chart", component_property="figure"),
    Output(component_id="usa-time-series-chart", component_property="figure"),
    Output(component_id='output_container', component_property='children')], 
    [Input("state_selected", "value")])

def display_time_series(state_selected):

    # Use the input from the user to render some text and return it
    display_text = "The state chosen by user was: {}".format(state_selected)

    # Get just the data of the US, not the states.
    usa_df = df_daily[df_daily['state'] == 'USA']

    # Make a bar chart of the US daily cases
    usa_figure = px.bar(
        usa_df, 
        x='date', 
        y='daily_cases',
        title="Daily Cases in all USA")

    # Little sanity check you can see in your terminal.
    print(state_selected)

    # Use the users input to select just the selected state.
    tmp_df = df_daily[df_daily['state'] == state_selected]

    # Make a bar chart of just the selected state.
    state_figure = px.bar(
        tmp_df, 
        x='date', 
        y='daily_cases',
        title=("Daily Cases in %s" % state_selected))

    return state_figure, usa_figure, display_text



# ----------------------------------------------------------------
# Scatter Plot Chart
@app.callback(
    Output("scatter-plot", "figure"),
    [Input('scatter_plot_value', 'children')])

def display_scatter(scatter_plot_value):

    # Making a temporary copy of the data frame
    tmp_df = master_df.copy()

    # Removing the values for the total USA.
    tmp_df = tmp_df[tmp_df['state'] != 'USA']

    # Making a scatter plot
    fig = px.scatter(
        tmp_df, 
        x="case_rate", 
        y="death_rate", 
        text='state',
        size="popestimate2019", 
        color='region', 
        hover_name="state",
        log_x=False, 
        size_max=25)

    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, port=6969)