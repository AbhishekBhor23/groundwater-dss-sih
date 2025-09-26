import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Historical Analytics", page_icon="📊", layout="wide")

st.title("Historical Data Analytics 📊")

# Check if data has been loaded in the session state from the Home page
if 'data' in st.session_state:
    df = st.session_state['data']
    well_no = st.session_state['well_no']

    st.header(f"Analysis for Well: {well_no}")

    # --- Data Engineering ---
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.strftime('%B')
    df['day_of_year'] = df['date'].dt.dayofyear
    df['rolling_avg_30d'] = df['value'].rolling(window=30).mean()

    # --- Key Statistics ---
    # (Identical to before)
    
    # --- Tabs for Visualizations ---
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trend Analysis", "📊 Yearly Comparison", "🗓️ Seasonal Range", "🕸️ Monthly Profile"])

    with tab1:
        # (Enhanced Time Series Line Graph code from before)
        st.subheader("Time Series with Trend Analysis")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=df['date'], y=df['value'], mode='lines', name='Daily Water Level', line=dict(color='lightblue')))
        fig_line.add_trace(go.Scatter(x=df['date'], y=df['rolling_avg_30d'], mode='lines', name='30-Day Rolling Avg', line=dict(color='orange', width=3)))
        trend_fig = px.scatter(df, x="date", y="value", trendline="ols", trendline_color_override="red")
        fig_line.add_trace(trend_fig.data[1])
        fig_line.data[2].name = 'Overall Trend'
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        # (Yearly Average Bar Chart code from before)
        st.subheader("Year-over-Year Average Water Level")
        yearly_avg = df.groupby('year')['value'].mean().reset_index()
        fig_bar = px.bar(yearly_avg, x='year', y='value', title='Average Annual Groundwater Level')
        st.plotly_chart(fig_bar, use_container_width=True)

    # (Add other tabs/charts here as desired)

else:
    st.warning("Please go to the Home page and enter a Well Number to fetch data first.")