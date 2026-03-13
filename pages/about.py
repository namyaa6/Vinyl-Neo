import streamlit as st

st.set_page_config(layout="wide", page_title="About - Vinyl")

st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; font-size: 3rem;">ℹ️ ABOUT VINYL</h1>', unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    ### About This Project
    
    VINYL is an AI-powered music recommendation system that combines:
    
    - **Neural Networks** for predicting user preferences
    - **Content-Based Filtering** for finding similar songs
    - **Hybrid Approach** for best recommendations
    
    ### Features
    
    - 🔍 Smart search by song name or artist
    - 🎵 AI-powered recommendations
    - 📚 Playlist management
    - 🌟 Genre discovery
    - ❤️ Like and save favorite songs
    
    ### Built With
    
    - Python
    - TensorFlow & scikit-learn
    - Streamlit
    - 114,000+ songs dataset
    
    ---
    
    **Developed as a machine learning project** showcasing neural networks and recommendation systems.
    """)

st.markdown('<br><br>', unsafe_allow_html=True)
if st.button('🏠 Back to Home'):
    st.switch_page("app.py")