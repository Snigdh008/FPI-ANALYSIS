import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

file_path = r"C:\Users\ASUS\Downloads\fpi_dash.csv"
df = pd.read_csv(file_path)

df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y")
df["AUC as on Date"] = pd.to_numeric(df["AUC as on Date"], errors="coerce")
unique_dates = sorted(df["Date"].unique())

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("📊 FII/FPI AUC Change Heatmap", style={"textAlign": "center"}),

    html.Label("Select Start Date:"),
    dcc.Dropdown(
        id="start-date",
        options=[{"label": date.strftime("%d-%b-%Y"), "value": date} for date in unique_dates],
        value=unique_dates[0],
        clearable=False,
    ),

    html.Label("Select End Date:"),
    dcc.Dropdown(
        id="end-date",
        options=[{"label": date.strftime("%d-%b-%Y"), "value": date} for date in unique_dates],
        value=unique_dates[-1],
        clearable=False,
    ),

    dcc.Graph(id="heatmap-chart"),
])

@app.callback(
    dash.dependencies.Output("heatmap-chart", "figure"),
    [dash.dependencies.Input("start-date", "value"), dash.dependencies.Input("end-date", "value")]
)
def update_chart(start_date, end_date):
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    filtered_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    pivot_df = filtered_df.pivot(index="Sector", columns="Date", values="AUC as on Date").apply(pd.to_numeric, errors="coerce")
    auc_change = pivot_df.iloc[:, -1] - pivot_df.iloc[:, 0]

    fig = px.imshow(
        pivot_df.subtract(pivot_df.iloc[:, 0], axis=0),
        labels={"x": "Date", "y": "Sector", "color": "AUC Difference"},
        color_continuous_scale="RdYlGn",
        title=f"AUC Change from {start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')}"
    )

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)


