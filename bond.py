import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="FPI & Bond Yield Dashboard", layout="wide")
st.title("📊 FPI Net Change vs Bond Yield (T10Y2Y)")


fpi_df = pd.read_csv("Cleaned_FPI_Data_Formatted.csv")
fpi_df.columns = fpi_df.columns.str.lower().str.strip()


fpi_df.rename(columns={
    'date': 'Date',
    'net fpi change': 'Net FPI Change',
    'sector': 'Sector'
}, inplace=True)


fpi_df['Date'] = pd.to_datetime(fpi_df['Date'], format="%d-%b-%y")


yield_df = pd.read_csv("T10Y2Y_Formatted.csv")
yield_df.columns = yield_df.columns.str.lower().str.strip()
yield_df.rename(columns={'observation_date': 'Date', 't10y2y': 'T10Y2Y'}, inplace=True)
yield_df['Date'] = pd.to_datetime(yield_df['Date'], format="%d-%b-%y")


merged_df = pd.merge(fpi_df, yield_df, on='Date', how='inner')


selected_sector = st.sidebar.selectbox("Select a sector", merged_df['Sector'].unique())
sector_data = merged_df[merged_df['Sector'] == selected_sector]


fig = go.Figure()

# Net FPI Change Bar Chart
fig.add_trace(go.Bar(
    x=sector_data['Date'],
    y=sector_data['Net FPI Change'],
    name='Net FPI Change',
    marker_color='indianred',
    yaxis='y1'
))


fig.add_trace(go.Scatter(
    x=sector_data['Date'],
    y=sector_data['T10Y2Y'],
    name='T10Y2Y Bond Yield Spread',
    mode='lines+markers',
    marker=dict(color='royalblue'),
    yaxis='y2'
))


fig.update_layout(
    title=f"Net FPI Change vs T10Y2Y Spread - Sector: {selected_sector}",
    xaxis=dict(title='Date'),
    yaxis=dict(title='Net FPI Change', side='left'),
    yaxis2=dict(title='T10Y2Y Spread', overlaying='y', side='right'),
    legend=dict(x=0.01, y=0.99),
    template="plotly_white",
    height=600
)

st.plotly_chart(fig, use_container_width=True)








