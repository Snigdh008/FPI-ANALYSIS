import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 FPI & Currency Dashboard")


@st.cache_data
def load_data():
    fpi = pd.read_csv("Fortnightly_Total_FPI.csv")
    jpy = pd.read_csv("Fortnightly_Returns_USD_JPY.csv")
    cny = pd.read_csv("Fortnightly_Returns_USD_CNY.csv")

    
    for df in [fpi, jpy, cny]:
        df.columns = df.columns.str.strip().str.title()

    
    for df in [jpy, cny]:
        df.rename(columns={"Price": "Close"}, inplace=True)

    
    fpi["Date"] = pd.to_datetime(fpi["Date"])
    jpy["Date"] = pd.to_datetime(jpy["Date"])
    cny["Date"] = pd.to_datetime(cny["Date"])

    return fpi, jpy, cny

fpi_df, jpy_df, cny_df = load_data()


year = st.sidebar.selectbox("Select Year", sorted(fpi_df["Date"].dt.year.unique()))
currency_choice = st.sidebar.selectbox("Select Currency", ["JPY", "CNY"])


fpi_filtered = fpi_df[fpi_df["Date"].dt.year == year]
currency_df = jpy_df if currency_choice == "JPY" else cny_df
currency_filtered = currency_df[currency_df["Date"].dt.year == year]


fig = go.Figure()


fig.add_trace(go.Bar(
    x=fpi_filtered["Date"],
    y=fpi_filtered["Net Fpi Change"],
    name="Net FPI (INR Cr)",
    marker_color="royalblue",
    yaxis="y1"
))


fig.add_trace(go.Candlestick(
    x=currency_filtered["Date"],
    open=currency_filtered["Open"],
    high=currency_filtered["High"],
    low=currency_filtered["Low"],
    close=currency_filtered["Close"],
    name=f"USD/{currency_choice}",
    increasing_line_color="green",
    decreasing_line_color="red",
    yaxis="y2"
))


fig.update_layout(
    title=f"USD/{currency_choice} vs Net FPI in {year}",
    xaxis_title="Date",
    yaxis=dict(title="Net FPI (INR Cr)", side="left"),
    yaxis2=dict(
        title=f"USD/{currency_choice}",
        overlaying="y",
        side="right"
    ),
    legend=dict(x=0.01, y=0.99),
    height=700
)


st.plotly_chart(fig, use_container_width=True)
