import streamlit as st
import requests
import time
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timezone
import numpy as np

# Page config
st.set_page_config(
    page_title="Live Heart Rate Monitor",
    page_icon="❤️",
    layout="wide"
)

# Initialize session state
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None
if 'hr_data' not in st.session_state:
    st.session_state.hr_data = pd.DataFrame(columns=['timestamp', 'heart_rate', 'hr_zone', 'estimated_power', 'cumulative_calories_burned'])

# Title and description
st.title("❤️ Live Heart Rate Monitor")
st.markdown("""
This app displays real-time heart rate data and performance metrics for users.
Monitor individual performance and see how users rank against each other!
""")

# Sidebar for user selection and controls
with st.sidebar:
    st.header("Controls")
    
    # User selection
    try:
        response = requests.get("http://localhost:4000/consumption/getLeaderboard?time_window_seconds=300&limit=100")
        if response.status_code == 200:
            users = [entry["user_name"] for entry in response.json()["entries"]]
            selected_user = st.selectbox("Select User", users)
            if selected_user != st.session_state.selected_user:
                st.session_state.selected_user = selected_user
                st.session_state.hr_data = pd.DataFrame(columns=['timestamp', 'heart_rate', 'hr_zone', 'estimated_power', 'cumulative_calories_burned'])
    except Exception as e:
        st.error(f"Failed to fetch users: {str(e)}")
        users = []
    
    # Time window selection for leaderboard
    time_window = st.slider("Leaderboard Time Window (seconds)", 
                          min_value=60, 
                          max_value=3600, 
                          value=300,
                          step=60)

# Main content area with two columns
col1, col2 = st.columns([3, 2])

# Function to update the live graph
def update_live_graph():
    try:
        if st.session_state.selected_user:
            response = requests.get(
                f"http://localhost:4000/consumption/getUserLiveHeartRateStats?user_name={st.session_state.selected_user}&window_seconds=60"
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Convert data to DataFrame
                    new_data = pd.DataFrame([{
                        'timestamp': datetime.fromisoformat(d['processed_timestamp'].replace('Z', '+00:00')),
                        'heart_rate': d['heart_rate'],
                        'hr_zone': d['hr_zone'],
                        'estimated_power': d['estimated_power'],
                        'cumulative_calories_burned': d['cumulative_calories_burned']
                    } for d in data])
                    
                    # Update session state data
                    st.session_state.hr_data = pd.concat([st.session_state.hr_data, new_data]).drop_duplicates(subset=['timestamp'])
                    
                    # Keep only last 60 seconds of data
                    cutoff_time = datetime.now(timezone.utc) - pd.Timedelta(seconds=60)
                    st.session_state.hr_data = st.session_state.hr_data[st.session_state.hr_data['timestamp'] > cutoff_time]
                    st.session_state.hr_data = st.session_state.hr_data.sort_values('timestamp')
                    
                    return new_data.iloc[0] if not new_data.empty else None
    except Exception as e:
        st.error(f"Failed to update graph: {str(e)}")
    return None

# Function to update the leaderboard
def update_leaderboard():
    try:
        response = requests.get(f"http://localhost:4000/consumption/getLeaderboard?time_window_seconds={time_window}&limit=10")
        if response.status_code == 200:
            data = response.json()["entries"]
            df = pd.DataFrame(data)
            
            # Display only relevant columns
            display_cols = ['rank', 'user_name', 'avg_heart_rate', 'avg_power', 'total_calories']
            df_display = df[display_cols].copy()
            return df_display
    except Exception as e:
        st.error(f"Failed to update leaderboard: {str(e)}")
    return None

with col1:
    st.subheader("Live Heart Rate Monitor")
    
    # Create metrics
    metrics_cols = st.columns(4)
    
    # Update data and metrics
    latest_data = update_live_graph()
    
    if latest_data is not None:
        # Update metrics
        metrics_cols[0].metric(
            "Heart Rate", 
            f"{latest_data['heart_rate']} BPM",
            delta=None
        )
        metrics_cols[1].metric(
            "Zone", 
            f"Zone {latest_data['hr_zone']}",
            delta=None
        )
        metrics_cols[2].metric(
            "Power", 
            f"{latest_data['estimated_power']}W",
            delta=None
        )
        metrics_cols[3].metric(
            "Calories", 
            f"{latest_data['cumulative_calories_burned']:.1f} kcal",
            delta=None
        )

    # Create and update graph
    if not st.session_state.hr_data.empty:
        fig = go.Figure()
        
        # Add heart rate trace
        fig.add_trace(go.Scatter(
            x=st.session_state.hr_data['timestamp'],
            y=st.session_state.hr_data['heart_rate'],
            mode='lines+markers',
            name='Heart Rate',
            line=dict(color='#FF4B4B', width=2),
            fill='tozeroy'
        ))
        
        # Add zone lines
        zone_colors = ['rgba(255,255,255,0.3)'] * 4
        zone_labels = ['Zone 1-2', 'Zone 2-3', 'Zone 3-4', 'Zone 4-5']
        zone_values = [120, 140, 160, 180]
        
        for value, label, color in zip(zone_values, zone_labels, zone_colors):
            fig.add_hline(
                y=value,
                line_dash="dash",
                line_color=color,
                annotation_text=label,
                annotation_position="right"
            )
        
        # Update layout
        fig.update_layout(
            title=f"Heart Rate Over Time - {st.session_state.selected_user}",
            xaxis_title="Time",
            yaxis_title="Heart Rate (BPM)",
            showlegend=False,
            height=400,
            margin=dict(l=0, r=0, t=40, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                range=[
                    st.session_state.hr_data['timestamp'].min(),
                    st.session_state.hr_data['timestamp'].max()
                ]
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                range=[
                    max(0, st.session_state.hr_data['heart_rate'].min() - 10),
                    st.session_state.hr_data['heart_rate'].max() + 10
                ]
            )
        )
        
        # Display the graph
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available yet. Please wait for data to appear.")

with col2:
    st.subheader("🏆 Leaderboard")
    
    leaderboard_df = update_leaderboard()
    if leaderboard_df is not None:
        st.dataframe(leaderboard_df, use_container_width=True)
    else:
        st.info("Loading leaderboard data...")

# Update frequency
time.sleep(1)
st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    Built with Streamlit ❤️ | Monitoring heart rates in real-time
</div>
""", unsafe_allow_html=True)
