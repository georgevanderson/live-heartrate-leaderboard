import streamlit as st

# Page config
st.set_page_config(
    page_title="Live Heart Rate Monitor",
    page_icon="❤️",
    layout="wide"
)

# Title
st.title("Live Heart Rate Monitor")

# Placeholder text
st.write("Welcome to the Live Heart Rate Monitor!")
st.write("This app will display real-time heart rate data from connected devices.")

# Add a button to start monitoring
if st.button("Start Monitoring"):
    st.write("Monitoring will be implemented soon...")

# Add some mock data visualization placeholders
col1, col2 = st.columns(2)

with col1:
    st.subheader("Current Heart Rates")
    st.write("User data will appear here...")

with col2:
    st.subheader("Statistics")
    st.write("Stats will appear here...")

# Footer
st.markdown("---")
st.write("Built with Streamlit ❤️")
