import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load your data
df = pd.read_csv('scenarios-local-interpretation.csv')

# Scenario options
scenarios = df['instance'].unique()
scenario_options = [
    {"label": f"Scenario {i+1}", "value": i} for i in scenarios
]

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Local Interpretation Dashboard"),
    dcc.Dropdown(
        id="scenario-dropdown",
        options=scenario_options,
        value=scenarios[0],  # Default first scenario
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
    # Top 10 by absolute score and drop empty features
    data = data.loc[data['score'].abs().sort_values(ascending=False).index]
    data = data.head(10)
    data = data.dropna(subset=['feature'])
    data = data[data['feature'].astype(str).str.strip() != '']
    data = data.sort_values("score", ascending=True)
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
        labels={
            "score": "Impact Score",
            "feature": "Feature",
            "ScoreType": "Type"
        },
        title=f"Top 10 Influential Factors for Scenario {scenario_id+1}"
    )
    fig.update_layout(
        yaxis={
            'categoryorder': 'array',
            'categoryarray': data['feature'].tolist()
        },
        legend_title="Type",
        xaxis_title="Impact",
        yaxis_title="Factors",
        template="simple_white",
        width=1100,
        height=600
    )
    fig.update_traces(textposition='auto')

    # Model prediction and confidence
    pred = data['predicted'].iloc[0]
    confidence = round(float(data['predicted_score'].iloc[0]) * 100) if data['predicted_score'].iloc[0] <= 1 else round(float(data['predicted_score'].iloc[0]))

    # Top 3 risk and protective factors
    top_risk = data[data['ScoreType'] == 'Risk'].sort_values('score', ascending=False).head(3)
    top_protective = data[data['ScoreType'] == 'Protective'].sort_values('score').head(3)

    risk_list = [
        html.Li([
            html.Span(f"{row['long_label']}", style={'fontWeight': 'bold', 'color': 'orchid'}),
            html.Span(f" for ", style={'color': '#888'}),
            html.Span(f"{row['value_label']}", style={'fontStyle': 'italic', 'color': 'orchid'})
        ]) for _, row in top_risk.iterrows()
    ]
    protective_list = [
        html.Li([
            html.Span(f"{row['long_label']}", style={'fontWeight': 'bold', 'color': 'yellowgreen'}),
            html.Span(f" for ", style={'color': '#888'}),
            html.Span(f"{row['value_label']}", style={'fontStyle': 'italic', 'color': 'yellowgreen'})
        ]) for _, row in top_protective.iterrows()
    ]


    info = html.Div([
        html.P([
            "The model prediction is ",
            html.Strong(pred, style={'color': 'orchid' if pred == 'High risk' else 'yellowgreen'}),
            f" with ",
            html.Strong(f"{confidence}%"),
            " confidence."
        ], style={'fontSize': '18px'}),
        html.Br(),
        html.Span("Top 3 risk factors:", style={'fontWeight': 'bold', 'color': 'orchid', 'fontSize': '16px'}),
        html.Ul(risk_list),
        html.Br(),
        html.Span("Top 3 protective factors:", style={'fontWeight': 'bold', 'color': 'yellowgreen', 'fontSize': '16px'}),
        html.Ul(protective_list)
    ], style={'lineHeight': '2'})

    return fig, info




if __name__ == "__main__":
    app.run_server(debug=True)