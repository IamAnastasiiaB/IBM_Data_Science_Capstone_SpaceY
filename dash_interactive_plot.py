# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = int(spacex_df['Payload Mass (kg)'].max())
min_payload = spacex_df['Payload Mass (kg)'].min()
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(
                                        id='site-dropdown',
                                        options=site_options,
                                        value='ALL',
                                        placeholder="Select a Launch Site here",
                                        searchable=True
                                    ),
                                    html.Br(),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site

                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),


                                # Add the payload range slider to the layout
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,  # Set the minimum value of the slider to the min payload
                                    max=max_payload,  # Use the integer version of max_payload
                                    step=1000,  # Step value for the slider intervals
                                    marks={i: str(i) for i in range(0, max_payload + 1, 2000)},  # Add marks at intervals of 2000 Kg
                                    value=[min_payload, max_payload]  # Default value range is the full range of payloads
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # If 'ALL' is selected, use the entire dataset
    if entered_site == 'ALL':
        success_counts = spacex_df['class'].value_counts()  # 'Class' column for success/failure
        fig = px.pie(
            names=success_counts.index,
            values=success_counts.values,
            title='Total Launch Success vs Failed'
        )
        return fig
    else:
        # If a specific site is selected, filter the dataframe
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts()  # 'Class' column for success/failure
        fig = px.pie(
            names=success_counts.index,
            values=success_counts.values,
            title=f"Launch Success vs Failed for Site: {entered_site}"
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Unpack the selected payload range
    min_payload, max_payload = payload_range

    # Filter the dataframe based on the selected payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= min_payload) & 
        (spacex_df['Payload Mass (kg)'] <= max_payload)
    ]

    # If a specific site is selected, filter the data further by launch site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    # Create the scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',  # X-axis is Payload Mass
        y='class',  # Y-axis is the outcome (0 for failed, 1 for success), use 'class' (lowercase)
        color='Booster Version Category',  # Color the points by Booster Version Category
        title=f"Payload vs. Launch Success for Site: {selected_site}" if selected_site != 'ALL' else "Payload vs. Launch Success for All Sites",
        labels={"Payload Mass (kg)": "Payload Mass (Kg)", "class": "Launch Outcome (Success/Failure)"}
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()