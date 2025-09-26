import streamlit as st
import requests
import pandas as pd

# Define the data fetching function here, as it's the core of the home page
@st.cache_data
def get_full_well_history(well_no):
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx8loPCXL1Ox5s54p5kMOxHlKvd0gP2SU2_4MWqnQkb8Lpscme9I7dGCBK8h1uRlm_Z/exec"
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

st.set_page_config(
    page_title="Groundwater DSS - Home",
    page_icon="🏠",
    layout="wide"
)

st.title("Groundwater Analytics & Forecasting 🏠")
st.markdown("---")
st.header("Welcome!")
st.info(
    "This application provides historical data analytics and AI-powered forecasting for groundwater wells in India. "
    "**Start by entering a Well Number below and clicking 'Fetch Data'.** Then, use the navigation on the left to explore the analytics and forecasts."
)

# --- User Input Section ---
well_no_input = st.text_input("Enter the Well Number:", value="W154337073501201")

if st.button("Fetch Data", type="primary"):
    if well_no_input:
        with st.spinner(f"Fetching full history for {well_no_input}..."):
            df = get_full_well_history(well_no_input)
            if df is not None and not df.empty:
                # Store the fetched data and well number in the session state
                st.session_state['data'] = df
                st.session_state['well_no'] = well_no_input
                st.success(f"Data for {well_no_input} loaded successfully! Please select a page from the sidebar to continue.")
            else:
                st.error("Could not fetch data for the specified Well Number.")
    else:
        st.warning("Please enter a Well Number.")