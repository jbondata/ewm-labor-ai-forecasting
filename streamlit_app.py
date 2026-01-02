"""Streamlit dashboard for Labor Forecasting."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.models.prophet_model import LaborForecastModel
from src.allocation.task_allocator import TaskAllocator

st.set_page_config(
    page_title="AI-Driven Labor Forecasting",
    page_icon="👥",
    layout="wide"
)

st.title("👥 AI-Driven Labor Forecasting & Task Assignment")
st.markdown("**Predictive labor demand forecasting complementing SAP EWM Labor Management**")

# Sidebar
st.sidebar.header("Configuration")
workers_available = st.sidebar.slider("Workers Available", 10, 100, 50)
forecast_horizon = st.sidebar.slider("Forecast Horizon (days)", 7, 30, 14)

# File upload
uploaded_file = st.sidebar.file_uploader("Upload Labor History CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['date'] = pd.to_datetime(df['date'])
    
    st.success("Data loaded successfully!")
    
    # Generate forecast
    if st.button("Generate Forecast", type="primary"):
        with st.spinner("Training model and generating forecast..."):
            model = LaborForecastModel()
            forecast = model.forecast_workers_needed(df, horizon_days=forecast_horizon)
            
            # Allocate workers
            allocator = TaskAllocator()
            allocation = allocator.allocate_workers(forecast, workers_available)
            
            # Display results
            st.subheader("Forecast Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_workers = forecast['forecast_workers_needed'].mean()
                st.metric("Avg Workers Needed", f"{avg_workers:.1f}")
            with col2:
                max_workers = forecast['forecast_workers_needed'].max()
                st.metric("Peak Workers Needed", f"{max_workers:.1f}")
            with col3:
                overtime_days = allocation['overtime_risk'].sum()
                st.metric("Overtime Risk Days", overtime_days)
            
            # Forecast chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=forecast['date'],
                y=forecast['forecast_workers_needed'],
                name='Forecast',
                line=dict(color='blue', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=forecast['date'],
                y=forecast['workers_needed_upper'],
                name='Upper Bound',
                line=dict(color='lightblue', dash='dash'),
                fill=None
            ))
            fig.add_trace(go.Scatter(
                x=forecast['date'],
                y=forecast['workers_needed_lower'],
                name='Lower Bound',
                line=dict(color='lightblue', dash='dash'),
                fill='tonexty'
            ))
            fig.add_hline(
                y=workers_available,
                line_dash="dash",
                line_color="red",
                annotation_text="Workers Available"
            )
            fig.update_layout(
                title="Labor Demand Forecast",
                xaxis_title="Date",
                yaxis_title="Workers Needed",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Allocation table
            st.subheader("Task Allocation")
            st.dataframe(allocation, use_container_width=True)
else:
    st.info("Please upload a CSV file with columns: date, workers_needed")
    st.markdown("""
    **Sample CSV format:**
    ```
    date,workers_needed
    2024-01-01,45
    2024-01-02,52
    2024-01-03,48
    ```
    """)

