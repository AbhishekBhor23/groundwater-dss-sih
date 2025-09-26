import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests # Make sure to import requests

st.set_page_config(page_title="Historical Analytics", page_icon="📊", layout="wide")

# --- Define the data fetching function here, or import it from a shared util.py ---
@st.cache_data
def get_full_well_history(well_no):
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwYz0qXjiJD3k6vIuJ5eNdthQV4Tf14EyiyuT8VTE0-NWN-aoY5qZXBBzUDK2LZjGsL/exec"
    api_url = f"{APPS_SCRIPT_URL}?wellNo={well_no}&mode=full"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            st.error(data["error"])
            return None
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date').reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        return None
# --- End of data fetching function ---

st.title("Historical Data Analytics 📊")

# --- NEW LOGIC: Read wellNo from URL or Session State ---
query_params = st.query_params

well_no_from_url = query_params.get("wellNo", None)

if well_no_from_url:
    current_well_no = well_no_from_url
    # Store in session state for consistency if navigating within Streamlit later
    st.session_state['well_no'] = current_well_no 
elif 'well_no' in st.session_state:
    current_well_no = st.session_state['well_no']
else:
    current_well_no = None

df = None # Initialize df outside the if blocks

if current_well_no:
    with st.spinner(f"Loading historical data for well: {current_well_no}..."):
        df = get_full_well_history(current_well_no)
        # Store df in session state if it's new, so other pages can use it
        if df is not None:
            st.session_state['data'] = df
            st.success(f"Data for {current_well_no} loaded successfully!")
        else:
            st.error(f"Failed to load data for well: {current_well_no}. Please check the Well Number or try again.")
            
if df is not None and not df.empty:
    st.header(f"Analysis for Well: {current_well_no}")

    # --- Data Engineering ---
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.strftime('%B')
    df['day_of_year'] = df['date'].dt.dayofyear
    df['rolling_avg_30d'] = df['value'].rolling(window=30).mean()

    # --- Key Statistics ---
    # (Optional: Add your key statistics display here if desired)
    # E.g., st.write(f"Latest Water Level: {df['value'].iloc[-1]:.2f}m")

    # --- Tabs for Visualizations ---
    tab1, tab2, tab3 = st.tabs(["📈 Trend Analysis", "📊 Yearly Comparison", "🗓️ Seasonal Range"]) # Removed Monthly Profile for brevity, you can add it back

    with tab1:
        st.subheader("Time Series with Trend Analysis")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=df['date'], y=df['value'], mode='lines', name='Daily Water Level', line=dict(color='lightblue')))
        fig_line.add_trace(go.Scatter(x=df['date'], y=df['rolling_avg_30d'], mode='lines', name='30-Day Rolling Avg', line=dict(color='orange', width=3)))
        trend_fig = px.scatter(df, x="date", y="value", trendline="ols", trendline_color_override="red")
        fig_line.add_trace(trend_fig.data[1])
        fig_line.data[2].name = 'Overall Trend'
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        st.subheader("Year-over-Year Average Water Level")
        yearly_avg = df.groupby('year')['value'].mean().reset_index()
        fig_bar = px.bar(yearly_avg, x='year', y='value', title='Average Annual Groundwater Level')
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab3: # Example of a new tab for Seasonal Range
        st.subheader("Seasonal Water Level Range")
        df['month_num'] = df['date'].dt.month # For sorting
        monthly_range = df.groupby(['month', 'month_num'])['value'].agg(['min', 'max', 'mean']).reset_index().sort_values('month_num')
        
        fig_range = go.Figure()
        fig_range.add_trace(go.Scatter(x=monthly_range['month'], y=monthly_range['max'], mode='lines', name='Max Level', fill=None, line_color='rgba(0,100,80,1)'))
        fig_range.add_trace(go.Scatter(x=monthly_range['month'], y=monthly_range['min'], mode='lines', name='Min Level', fill='tonexty', fillcolor='rgba(0,100,80,0.2)', line_color='rgba(0,100,80,1)'))
        fig_range.add_trace(go.Scatter(x=monthly_range['month'], y=monthly_range['mean'], mode='lines', name='Average Level', line=dict(color='blue', dash='dot')))
        fig_range.update_layout(title='Monthly Water Level Range and Average',
                                xaxis_title='Month', yaxis_title='Water Level (m)')
        st.plotly_chart(fig_range, use_container_width=True)


else:
    if current_well_no is None:
        st.warning("No Well Number provided. Please use the map or manually enter a Well Number on the Home page.")
    # If df is None, an error message would have been shown by get_full_well_history