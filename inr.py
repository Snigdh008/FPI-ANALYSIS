import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="FPI vs INR Return Dashboard", layout="wide")
st.title("💸 Fortnightly Net FPI Change vs INR Return (%)")


fpi_df = pd.read_csv("Fortnightly_Total_FPI.csv")
inr_df = pd.read_csv("Formatted_Fortnightly_Returns_USD_INR.csv")


fpi_df["Date"] = pd.to_datetime(fpi_df["Date"], format="%d-%b-%y")
inr_df["Date"] = pd.to_datetime(inr_df["Date"], format="%d-%b-%y")


merged_df = pd.merge(fpi_df, inr_df, on="Date", how="inner")


merged_df["Year"] = merged_df["Date"].dt.year


years = merged_df["Year"].unique()
selected_year = st.sidebar.selectbox("Select a Year", sorted(years))


yearly_data = merged_df[merged_df["Year"] == selected_year].reset_index(drop=True)


fig = go.Figure()


fig.add_trace(go.Bar(
    x=yearly_data["Date"],
    y=yearly_data["Net FPI Change"],
    name="Net FPI Change",
    marker_color="blue",
    yaxis="y1"
))


fig.add_trace(go.Bar(
    x=yearly_data["Date"],
    y=yearly_data["Fortnight Return (%)"],
    name="INR Fortnight Return (%)",
    marker_color="red",
    yaxis="y2"
))


fig.update_layout(
    title=f"Fortnightly Net FPI Change vs INR Return ({selected_year})",
    xaxis=dict(title="Date"),
    yaxis=dict(
        title=dict(text="Net FPI Change (₹ Crores)", font=dict(color="blue")),
        tickfont=dict(color="blue")
    ),
    yaxis2=dict(
        title=dict(text="INR Return (%)", font=dict(color="red")),
        tickfont=dict(color="red"),
        overlaying='y',
        side='right'
    ),
    legend=dict(x=0.01, y=0.99),
    barmode='group',
    template="plotly_white",
    height=600
)


st.plotly_chart(fig, use_container_width=True)

