import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load your data
df = pd.read_csv('scenarios-local-interpretation.csv')

# Scenario options (add 1 for display)
scenarios = df['instance'].unique()
scenario_options = [
    {"label": f"Scenario {i+1}", "value": i} for i in scenarios
]

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Local Interpretation"),
    dcc.Dropdown(
        id="scenario-dropdown",
        options=scenario_options,
        value=scenarios[0],  # default first scenario
        style={"width": "50%"}
    ),
    html.Div(id="scenario-info"),
    dcc.Graph(id="factor-bar-chart")
])

@app.callback(
    Output("factor-bar-chart", "figure"),
    Output("scenario-info", "children"),
    Input("scenario-dropdown", "value")
)
def update_chart(scenario_id):
    data = df[df['instance'] == scenario_id].copy()
    data = data.sort_values("score", ascending=False)
    # Create label for legend and color
    data['ScoreType'] = data['score'].apply(lambda x: 'Protective' if x < 0 else 'Risk')
    color_discrete_map = {'Protective': 'yellowgreen', 'Risk': 'orchid'}
    fig = px.bar(
        data,
        x="score",
        y="feature",
        orientation="h",
        text="value_label",
        color="ScoreType",
        color_discrete_map=color_discrete_map,
        labels={"score": "Weighting", "feature": "Factors", "ScoreType": "Type"},
        title=f"Top Influential Factors for Scenario {scenario_id+1}"
    )
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        legend_title="Type",
        xaxis_title="Impact",
        yaxis_title="Factors",
        template="simple_white",
        width=1100,
        height=600
    )
    fig.update_traces(textposition='auto')
    info = html.Div([
        html.P(f"Scenario {scenario_id+1}")
    ])
    return fig, info



if __name__ == "__main__":
    app.run_server(debug=True)
