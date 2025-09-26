import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from datetime import timedelta

st.set_page_config(page_title="DSS Forecast", page_icon="🚀", layout="wide")

@st.cache_resource
def load_model():
    try:
        model = joblib.load('groundwater_model.joblib')
        return model
    except FileNotFoundError:
        return None

st.title("DSS Predictive Forecast 🚀")

model = load_model()

if model is None:
    st.error("Model file 'groundwater_model.joblib' not found. Please run the train_model.py script first.")
elif 'data' in st.session_state:
    df = st.session_state['data']
    well_no = st.session_state['well_no']

    st.header(f"Forecast for Well: {well_no}")
    
    days_to_forecast = st.slider("Select number of days to forecast:", 30, 365, 90)

    if st.button("Generate Forecast", type="primary"):
        with st.spinner("Calculating future predictions..."):
            
            # --- FIXED CODE BLOCK ---
            # Prepare future data for prediction using pd.concat
            
            # 1. Create a DataFrame from historical data with a proper DatetimeIndex
            historical_df = df.set_index('date')
            
            # 2. Generate future dates
            last_date = historical_df.index.max()
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_to_forecast)
            
            # 3. Create an empty DataFrame for the future dates
            future_df_shell = pd.DataFrame(index=future_dates)
            
            # 4. Combine historical and future shells using pd.concat
            full_df_for_features = pd.concat([historical_df, future_df_shell])
            # --- END OF FIXED CODE BLOCK ---
            
            # --- Feature Engineering for the future dates ---
            full_df_for_features['day_of_year'] = full_df_for_features.index.dayofyear
            full_df_for_features['month'] = full_df_for_features.index.month
            full_df_for_features['year'] = full_df_for_features.index.year
            full_df_for_features['week_of_year'] = full_df_for_features.index.isocalendar().week
            
            # Calculate lag features using the combined data
            full_df_for_features['lag_7d'] = full_df_for_features['value'].shift(7)
            full_df_for_features['lag_30d'] = full_df_for_features['value'].shift(30)
            
            # Select only the future part that needs prediction
            future_df_features = full_df_for_features.loc[future_dates].copy()
            
            # --- Make Predictions ---
            features_for_model = ['day_of_year', 'month', 'year', 'week_of_year', 'lag_7d', 'lag_30d']
            future_predictions = model.predict(future_df_features[features_for_model])
            
            forecast_df = pd.DataFrame({'date': future_dates, 'value': future_predictions})
            
            # --- Visualize ---
            fig_forecast = go.Figure()
            fig_forecast.add_trace(go.Scatter(x=df['date'], y=df['value'], mode='lines', name='Historical Level'))
            fig_forecast.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['value'], mode='lines', name='Forecasted Level', line=dict(color='red', dash='dash')))
            st.plotly_chart(fig_forecast, use_container_width=True)

else:
    st.warning("Please go to the Home page and enter a Well Number to fetch data first.")