import streamlit as st
import requests
import logging
import ast
import hashlib
import re
import os
from dotenv import load_dotenv
import json
from pathlib import Path
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000/")
API_BASE_URL = "http://localhost:5000/"

# Set page configuration with professional appearance
st.set_page_config(
    page_title="Clinical Research Paper Assistant",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a professional UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #3498db;
        --primary-dark: #2980b9;
        --secondary-color: #2c3e50;
        --accent-color: #e74c3c;
        --accent-light: #f39c12;
        --light-bg: #f5f7fa;
        --card-bg: #ffffff;
        --text-color: #34495e;
        --light-text: #7f8c8d;
        --sidebar-bg: #2c3e50;
        --success-color: #2ecc71;
        --warning-color: #f1c40f;
        --error-color: #e74c3c;
        --border-radius: 10px;
        --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Global styles */
    body {
        font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica', sans-serif;
        color: var(--text-color);
        background-color: var(--light-bg);
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica', sans-serif;
        font-weight: 600;
        color: var(--secondary-color);
    }
    
    h1 {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        margin-bottom: 1.5rem !important;
        color: var(--secondary-color);
    }
    
    h2 {
        font-size: 1.8rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(0,0,0,0.1);
    }
    
    h3 {
        font-size: 1.4rem !important;
        margin-top: 1rem !important;
        margin-bottom: 0.8rem !important;
        color: var(--primary-dark);
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-12oz5g7 {
        background-color: var(--sidebar-bg);
    }
    
    .sidebar-content {
        padding: 1.5rem;
    }
    
    /* Cards for content sections */
    .card {
        background-color: var(--card-bg);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--card-shadow);
        margin-bottom: 1.5rem;
        border: none;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    .small-card {
        background-color: var(--card-bg);
        border-radius: var(--border-radius);
        padding: 1rem;
        box-shadow: var(--card-shadow);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        border-left: 4px solid var(--primary-color);
    }
    
    .feature-card {
        background-color: var(--card-bg);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--card-shadow);
        margin-bottom: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card i {
        font-size: 2.5rem;
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
        text-transform: none !important;
    }
    
    .stButton > button:hover {
        background-color: var(--primary-dark) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    .primary-btn {
        background-color: var(--primary-color) !important;
    }
    
    .secondary-btn {
        background-color: var(--secondary-color) !important;
    }
    
    .accent-btn {
        background-color: var(--accent-color) !important;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 1px solid #e0e0e0 !important;
        padding: 12px !important;
        box-shadow: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2) !important;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        padding: 2rem;
        border: 2px dashed var(--primary-color);
        border-radius: var(--border-radius);
        background-color: rgba(52, 152, 219, 0.05);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    [data-testid="stFileUploader"]:hover {
        background-color: rgba(52, 152, 219, 0.1);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px 10px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
        border: none;
        color: var(--text-color);
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Status messages */
    .success-box {
        background-color: rgba(46, 204, 113, 0.1);
        color: var(--success-color);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--success-color);
        margin-bottom: 1rem;
        font-weight: 500;
        display: flex;
        align-items: center;
    }
    
    .success-box:before {
        content: "✓";
        display: inline-block;
        margin-right: 10px;
        font-weight: bold;
    }
    
    .error-box {
        background-color: rgba(231, 76, 60, 0.1);
        color: var(--error-color);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--error-color);
        margin-bottom: 1rem;
        font-weight: 500;
        display: flex;
        align-items: center;
    }
    
    .error-box:before {
        content: "×";
        display: inline-block;
        margin-right: 10px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .info-box {
        background-color: rgba(52, 152, 219, 0.1);
        color: var(--primary-color);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    /* Custom checkbox styling */
    [data-testid="stCheckbox"] > label {
        font-weight: 500;
        color: var(--text-color);
    }
    
    /* Text area enhancements */
    .stTextArea textarea {
        min-height: 150px;
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Code blocks */
    code {
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-size: 0.9rem;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        background-color: #f7f9fb;
        color: var(--primary-dark);
        border: 1px solid #eaeaea;
    }
    
    pre {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: var(--border-radius);
        border: 1px solid #eaeaea;
        overflow-x: auto;
    }
    
    /* Divider with text */
    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 1.5rem 0;
        color: var(--light-text);
    }
    
    .divider::before, .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .divider span {
        padding: 0 1rem;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Citations styling */
    .citation-box {
        background-color: #f8f9fa;
        border-left: 3px solid var(--primary-color);
        padding: 0.8rem 1rem;
        margin-top: 1rem;
        border-radius: 0 var(--border-radius) var(--border-radius) 0;
        font-size: 0.9rem;
        color: var(--light-text);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: var(--primary-color);
        border-radius: 100px;
        height: 8px !important;
    }
    
    .stProgress > div > div {
        background-color: #e0e0e0;
        border-radius: 100px;
        height: 8px !important;
    }

    /* Header and logo styling */
    .dashboard-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(0,0,0,0.1);
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        margin-right: 2rem;
    }
    
    .logo-img {
        width: 40px;
        height: 40px;
        margin-right: 10px;
    }
    
    .logo-text {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--secondary-color);
    }
    
    /* Sidebar nav item */
    .nav-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        color: rgba(255, 255, 255, 0.7);
        text-decoration: none;
    }
    
    .nav-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .nav-item.active {
        background-color: var(--primary-color);
        color: white;
        font-weight: 500;
    }
    
    .nav-item i {
        margin-right: 10px;
        font-size: 1.1rem;
    }
    
    /* Tags and labels */
    .tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .tag-primary {
        background-color: rgba(52, 152, 219, 0.1);
        color: var(--primary-color);
    }
    
    .tag-success {
        background-color: rgba(46, 204, 113, 0.1);
        color: var(--success-color);
    }
    
    .tag-warning {
        background-color: rgba(241, 196, 15, 0.1);
        color: var(--warning-color);
    }
    
    .tag-danger {
        background-color: rgba(231, 76, 60, 0.1);
        color: var(--error-color);
    }
    
    /* Dashboard stats */
    .stat-card {
        background-color: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--card-shadow);
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stat-card .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0.5rem 0;
    }
    
    .stat-card .stat-label {
        color: var(--light-text);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a1a1a1;
    }
    
    /* Endpoint selection list */
    .endpoint-item {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        background-color: white;
        margin-bottom: 0.5rem;
        border-left: 3px solid transparent;
        transition: all 0.2s ease;
    }
    
    .endpoint-item:hover {
        background-color: #f8f9fa;
        border-left-color: var(--primary-color);
    }
    
    .endpoint-item.selected {
        background-color: rgba(52, 152, 219, 0.1);
        border-left-color: var(--primary-color);
    }
    
    /* Selected prompt styling */
    .selected-prompt {
        background-color: #f8f9fa;
        border-radius: var(--border-radius);
        padding: 1rem;
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
    }
    
    /* Response styling */
    .response-container {
        background-color: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--card-shadow);
        margin-top: 1.5rem;
    }
    
    /* Search box */
    .search-container {
        position: relative;
        margin-bottom: 1rem;
    }
    
    .search-container input {
        width: 100%;
        padding: 0.75rem 1rem 0.75rem 2.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        font-size: 0.9rem;
    }
    
    .search-container:before {
        content: "🔍";
        position: absolute;
        left: 0.75rem;
        top: 50%;
        transform: translateY(-50%);
        color: var(--light-text);
    }
    
    /* Custom file uploader */
    .custom-uploader {
        border: 2px dashed var(--primary-color);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        background-color: rgba(52, 152, 219, 0.05);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .custom-uploader:hover {
        background-color: rgba(52, 152, 219, 0.1);
    }
    
    .custom-uploader i {
        font-size: 3rem;
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    
    /* Icons */
    .icon {
        display: inline-block;
        width: 1.5rem;
        height: 1.5rem;
        text-align: center;
        margin-right: 0.5rem;
    }
    
    /* Font awesome icon equivalents using emojis */
    .fa-file-medical:before { content: "📄"; }
    .fa-flask:before { content: "🧪"; }
    .fa-chart-bar:before { content: "📊"; }
    .fa-lightbulb:before { content: "💡"; }
    .fa-comment:before { content: "💬"; }
    .fa-check-circle:before { content: "✅"; }
    .fa-download:before { content: "⬇️"; }
    .fa-upload:before { content: "⬆️"; }
    .fa-save:before { content: "💾"; }
    .fa-play:before { content: "▶️"; }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem 0;
        margin-top: 2rem;
        color: var(--light-text);
        font-size: 0.9rem;
        border-top: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
def initialize_session_state():
    """Initialize all session state variables for the application."""
    default_sections = ["introduction", "methods", "discussion", "results", "conclusion"]
    
    # General session states
    for key in ["file_name", "assistant_id", "vector_id", "current_thread_id", "current_checkbox_thread_id", 
                "current_method_checkbox_thread_id", "edited_response", "response", "citations", 
                "checkbox_response", "methods_checkbox_response", "checkbox_citations", "methods_checkbox_citations", 
                "methods_general_checkbox_response", "methods_general_checkbox_citations", 
                "general_results_prompt_citations", "general_results_prompt_response", "dependent", 
                "checkbox_dependent", "user_query", "selected_bullet", "selected_category", 
                "selected_endpoints_for_general_results", "conclusion_selected_endpoints_for_methods",
                "conclusion_methods_categorized_endpoints", "conclusion_selected_endpoint",
                "conclusion_selected_category", "conclusion_main_endpoint_name", "conclusion_subgroup_bullet",
                "conclusion_dynamic_prompt_selector", "conclusion_checkbox_dependent_endpoint",
                "conclusion_user_query", "conclusion_methods_checkbox_response",
                "conclusion_methods_checkbox_citations", "current_conclusion_checkbox_thread_id",
                "active_tab", "file_uploaded"]:
        if key not in st.session_state:
            if key in ["dependent", "checkbox_dependent"]:
                st.session_state[key] = True
            elif key in ["selected_bullet", "selected_category"]:
                st.session_state[key] = None
            elif key == "file_uploaded":
                st.session_state[key] = False
            elif key == "active_tab":
                st.session_state[key] = 0
            else:
                st.session_state[key] = ""
    
    # Section-specific session states
    for section in default_sections:
        if section not in st.session_state:
            st.session_state[section] = ""
        for sub_key in [
            f"{section}_thread_id",
            f"{section}_citations",
            f"{section}_prompt",
            f"{section}_chat",
            f"{section}_chat_citations",
            f"initialise_new_chat_for{section}_thread_id",
            f"initialise_new_chat_for_outside_{section}_thread_id",
            f"outside_{section}_thread_id",
            f"outside_{section}_citations",
            f"outside_{section}_prompt",
            f"outside_{section}_chat",
            f"outside_{section}_chat_citations",
        ]:
            if sub_key not in st.session_state:
                st.session_state[sub_key] = [] if 'citations' in sub_key else ""
    
    # Initialize additional session state variables for outside queries
    for key in ["selected_queries_outside", "selected_responses_outside", "results_outside", 
                "final_edited_responses_outside", "view_final_edited_outside", 
                "show_results", "show_selected_query", "assistant_response"]:
        if key not in st.session_state:
            if key == "view_final_edited_outside":
                st.session_state[key] = False
            else:
                st.session_state[key] = []

# Call initialization
initialize_session_state()

# Function to clear session state when a new file is uploaded
def clear_session():
    """Clear all session state variables for a fresh start."""
    # Set file_uploaded to False
    st.session_state["file_uploaded"] = False
    
    # General session states to clear
    for key in ["file_name", "assistant_id", "vector_id", "current_thread_id", "current_checkbox_thread_id", 
                "current_method_checkbox_thread_id", "edited_response", "response", "citations", 
                "checkbox_response", "methods_checkbox_response", "checkbox_citations", "methods_checkbox_citations", 
                "methods_general_checkbox_response", "methods_general_checkbox_citations", 
                "general_results_prompt_citations", "general_results_prompt_response", "dependent", 
                "checkbox_dependent", "user_query", "selected_bullet", "selected_category", 
                "selected_endpoints_for_general_results", "conclusion_selected_endpoints_for_methods",
                "conclusion_methods_categorized_endpoints", "conclusion_selected_endpoint",
                "conclusion_selected_category", "conclusion_main_endpoint_name", "conclusion_subgroup_bullet",
                "conclusion_dynamic_prompt_selector", "conclusion_checkbox_dependent_endpoint",
                "conclusion_user_query", "conclusion_methods_checkbox_response",
                "conclusion_methods_checkbox_citations", "current_conclusion_checkbox_thread_id"]:
        if key in ["dependent", "checkbox_dependent"]:
            st.session_state[key] = True
        elif key in ["selected_bullet", "selected_category"]:
            st.session_state[key] = None
        else:
            st.session_state[key] = ""
    
    # Section-specific session states to clear
    default_sections = ["introduction", "methods", "discussion", "results", "conclusion"]
    for section in default_sections:
        st.session_state[section] = ""
        for sub_key in [
            f"{section}_thread_id",
            f"{section}_citations",
            f"{section}_prompt",
            f"{section}_chat",
            f"{section}_chat_citations",
            f"initialise_new_chat_for{section}_thread_id",
            f"initialise_new_chat_for_outside_{section}_thread_id",
            f"outside_{section}_thread_id",
            f"outside_{section}_citations",
            f"outside_{section}_prompt",
            f"outside_{section}_chat",
            f"outside_{section}_chat_citations",
        ]:
            st.session_state[sub_key] = [] if 'citations' in sub_key else ""
    
    # Clear additional session state variables for outside queries
    for key in ["selected_queries_outside", "selected_responses_outside", "results_outside", 
                "final_edited_responses_outside", "view_final_edited_outside", 
                "show_results", "show_selected_query", "assistant_response"]:
        if key == "view_final_edited_outside":
            st.session_state[key] = False
        else:
            st.session_state[key] = []

# Function to generate unique key for each checkbox
def generate_unique_key(*args):
    """Generate a unique key for UI elements based on their arguments."""
    return hashlib.md5("".join(map(str, args)).encode('utf-8')).hexdigest()

# Main layout with sidebar and content area
def main():
    """Main application layout and functionality."""
    # Create sidebar for navigation
    with st.sidebar:
        # Logo and header
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0; margin-bottom: 2rem;">
            <img src="https://img.icons8.com/fluency/96/000000/medical-document.png" style="width: 60px; margin-bottom: 0.5rem;">
            <h2 style="margin: 0; color: white; font-size: 1.5rem; font-weight: 600;">CRP Assistant</h2>
            <p style="margin: 0; color: rgba(255,255,255,0.6); font-size: 0.9rem;">Research Paper Generator</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu with icons
        st.markdown("<div style='padding: 0 1rem;'>", unsafe_allow_html=True)
        
        # Define menu items with icons and labels
        menu_items = [
            {"icon": "📄", "label": "Upload Paper", "tooltip": "Upload and process your clinical paper"},
            {"icon": "📊", "label": "Results", "tooltip": "Generate and edit results section"},
            {"icon": "🧪", "label": "Methods", "tooltip": "Generate and edit methods section"},
            {"icon": "📝", "label": "Conclusion", "tooltip": "Generate and edit conclusion section"},
            {"icon": "📚", "label": "Introduction", "tooltip": "Generate and edit introduction section"},
            {"icon": "💬", "label": "Discussion", "tooltip": "Generate and edit discussion section"},
            {"icon": "📥", "label": "Export Document", "tooltip": "Export your final paper"}
        ]
        
        # Display menu items
        for i, item in enumerate(menu_items):
            active_class = "active" if st.session_state.active_tab == i else ""
            if st.markdown(f"""
                <div class="nav-item {active_class}" title="{item['tooltip']}" 
                     onclick="document.querySelectorAll('.nav-item')[{i}].click();">
                    <span class="icon">{item['icon']}</span>
                    <span>{item['label']}</span>
                </div>
                """, unsafe_allow_html=True):
                st.session_state.active_tab = i
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Divider
        st.markdown("<div class='divider'><span>SESSION INFO</span></div>", unsafe_allow_html=True)
        
        # Session information
        if st.session_state.file_uploaded:
            st.markdown(f"""
            <div class="small-card" style="background-color: rgba(255,255,255,0.1); color: white; border-left-color: rgba(255,255,255,0.3);">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="width: 30px;">📄</span>
                    <span style="font-weight: 500;">File:</span>
                    <span style="margin-left: auto; font-weight: 400; opacity: 0.8; overflow: hidden; text-overflow: ellipsis;">{st.session_state.file_name}</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="width: 30px;">🤖</span>
                    <span style="font-weight: 500;">Assistant:</span>
                    <span style="margin-left: auto; font-weight: 400; opacity: 0.8;">{st.session_state.assistant_id[:8]}...</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="width: 30px;">🔍</span>
                    <span style="font-weight: 500;">Vector ID:</span>
                    <span style="margin-left: auto; font-weight: 400; opacity: 0.8;">{st.session_state.vector_id[:8]}...</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="padding: 1rem; background-color: rgba(255,255,255,0.1); border-radius: 8px; color: rgba(255,255,255,0.7); margin-bottom: 1rem;">
                <p style="margin: 0;">No active session. Please upload a document to begin.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div style="position: absolute; bottom: 1rem; left: 0; right: 0; text-align: center; padding: 1rem;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; margin: 0;">© 2023 Clinical Research Paper Assistant</p>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem; margin: 0;">Version 2.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    # Add a header to the main content area
    st.markdown("""
    <div class="dashboard-header">
        <div class="logo-container">
            <img src="https://img.icons8.com/fluency/96/000000/medical-document.png" class="logo-img" alt="Logo">
            <div class="logo-text">Clinical Research Paper Assistant</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Content based on active tab
    if st.session_state.active_tab == 0:
        show_upload_screen()
    elif st.session_state.active_tab == 1:
        show_results_tab()
    elif st.session_state.active_tab == 2:
        show_methods_tab()
    elif st.session_state.active_tab == 3:
        show_conclusion_tab()
    elif st.session_state.active_tab == 4:
        show_introduction_tab()
    elif st.session_state.active_tab == 5:
        show_discussion_tab()
    elif st.session_state.active_tab == 6:
        show_export_tab()

def show_upload_screen():
    """Display the file upload screen with a modern dashboard look."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h2 style="margin-top: 0;">Upload Research Paper</h2>
            <p style="margin-bottom: 2rem;">
                Upload your clinical research paper to begin analysis and content generation. 
                We support PDF, TXT, CSV, and JSON formats.
            </p>
            
            <div class="custom-uploader">
                <span style="font-size: 3rem; color: var(--primary-color); margin-bottom: 1rem; display: block;">⬆️</span>
                <h3 style="margin-bottom: 0.5rem;">Drag and drop your file here</h3>
                <p style="color: var(--light-text); margin-bottom: 1.5rem;">or click to browse files</p>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader("Choose a file to upload", type=["txt", "csv", "json", "pdf"], label_visibility="collapsed")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Process button
        process_col1, process_col2, process_col3 = st.columns([1, 2, 1])
        with process_col2:
            upload_button = st.button("🚀 Process Document", type="primary", use_container_width=True)
        
        # Processing logic
        if upload_button and uploaded_file is not None:
            with st.spinner("Processing your document..."):
                try:
                    # Clear session state before uploading a new file
                    clear_session()
                    
                    # Create progress bar
                    progress_bar = st.progress(0)
                    
                    # Upload the file
                    files = {"file": uploaded_file}
                    
                    # Simulate progress steps
                    progress_bar.progress(20)
                    st.info("Uploading document...")
                    
                    # Make API call
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    progress_bar.progress(60)
                    st.info("Analyzing content...")
                    
                    # Simulate more progress
                    progress_bar.progress(80)
                    st.info("Preparing AI assistant...")
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, dict):
                            # Update progress
                            progress_bar.progress(100)
                            
                            # Update session state
                            st.session_state.file_name = uploaded_file.name
                            st.session_state.assistant_id = result.get("assistant_id", "")
                            st.session_state.vector_id = result.get("vector_store_id", "")
                            st.session_state.current_thread_id = result.get("thread_id", "")
                            st.session_state.file_uploaded = True
                            
                            # Success message
                            st.markdown("""
                            <div class="success-box">
                                Document processed successfully! Navigate to the different sections to generate content.
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show metadata
                            st.markdown("""
                            <div class="small-card">
                                <h3 style="margin-top: 0;">Document Metadata</h3>
                                <div style="display: flex; flex-wrap: wrap; gap: 1rem;">
                                    <div style="flex: 1; min-width: 200px;">
                                        <p><strong>Filename:</strong> {}</p>
                                        <p><strong>File Size:</strong> {:.2f} KB</p>
                                    </div>
                                    <div style="flex: 1; min-width: 200px;">
                                        <p><strong>Upload Time:</strong> {}</p>
                                        <p><strong>Status:</strong> <span class="tag tag-success">Ready</span></p>
                                    </div>
                                </div>
                            </div>
                            """.format(
                                st.session_state.file_name,
                                uploaded_file.size / 1024,
                                result.get('upload_time', 'Now')
                            ), unsafe_allow_html=True)
                            
                            # Call to action
                            st.markdown("""
                            <div class="info-box">
                                <strong>Next Steps:</strong> Select "Results" or "Methods" from the sidebar to start generating content.
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.success("File processed successfully!")
                    else:
                        # Error message
                        st.markdown("""
                        <div class="error-box">
                            Failed to process document. Please try again.
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    # Error message
                    st.markdown(f"""
                    <div class="error-box">
                        An error occurred: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
        elif upload_button and uploaded_file is None:
            # Warning for no file
            st.markdown("""
            <div class="error-box">
                Please select a file to upload.
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)  # Close card div
    
    # Right column with info/features
    with col2:
        # Stats card
        st.markdown("""
        <div class="card">
            <h2 style="margin-top: 0;">Process Overview</h2>
            
            <div class="stat-card" style="margin-bottom: 1rem;">
                <div style="font-size: 0.9rem; color: var(--light-text);">AVERAGE PROCESSING TIME</div>
                <div class="stat-value">45s</div>
                <div style="font-size: 0.9rem; color: var(--light-text);">per document</div>
            </div>
            
            <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem;">
                <div style="flex: 1; text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);">5</div>
                    <div style="font-size: 0.8rem; color: var(--light-text);">SECTIONS</div>
                </div>
                <div style="flex: 1; text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);">20+</div>
                    <div style="font-size: 0.8rem; color: var(--light-text);">PROMPTS</div>
                </div>
                <div style="flex: 1; text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);">4</div>
                    <div style="font-size: 0.8rem; color: var(--light-text);">FORMATS</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # How it works section
        st.markdown("""
        <div class="card">
            <h2 style="margin-top: 0;">How It Works</h2>
            
            <div style="display: flex; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #f0f0f0;">
                <div style="width: 40px; height: 40px; background-color: var(--primary-color); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">1</div>
                <div>
                    <h4 style="margin: 0 0 0.25rem 0;">Upload</h4>
                    <p style="margin: 0; color: var(--light-text); font-size: 0.9rem;">Upload your clinical research paper</p>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #f0f0f0;">
                <div style="width: 40px; height: 40px; background-color: var(--primary-color); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">2</div>
                <div>
                    <h4 style="margin: 0 0 0.25rem 0;">Analyze</h4>
                    <p style="margin: 0; color: var(--light-text); font-size: 0.9rem;">AI extracts key information for sections</p>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #f0f0f0;">
                <div style="width: 40px; height: 40px; background-color: var(--primary-color); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">3</div>
                <div>
                    <h4 style="margin: 0 0 0.25rem 0;">Generate</h4>
                    <p style="margin: 0; color: var(--light-text); font-size: 0.9rem;">Create structured content for each section</p>
                </div>
            </div>
            
            <div style="display: flex; align-items: center;">
                <div style="width: 40px; height: 40px; background-color: var(--primary-color); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">4</div>
                <div>
                    <h4 style="margin: 0 0 0.25rem 0;">Export</h4>
                    <p style="margin: 0; color: var(--light-text); font-size: 0.9rem;">Download your complete research paper</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Supported formats
        st.markdown("""
        <div class="card">
            <h2 style="margin-top: 0;">Supported Formats</h2>
            
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                <div class="tag tag-primary">PDF</div>
                <div class="tag tag-primary">TXT</div>
                <div class="tag tag-primary">CSV</div>
                <div class="tag tag-primary">JSON</div>
            </div>
            
            <div style="margin-top: 1rem; padding: 0.75rem; background-color: rgba(52, 152, 219, 0.1); border-radius: 8px; font-size: 0.9rem;">
                <strong>Note:</strong> For best results, use PDF documents with searchable text.
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_results_tab():
    """Display the results tab with a modern interface."""
    if not st.session_state.get("file_uploaded", False):
        display_upload_reminder()
        return
    
    st.markdown("""
    <div class="section-header">
        <h1>Results Section</h1>
        <p class="subtitle">Generate and view results content for your research paper</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different approaches
    tab1, tab2 = st.tabs(["📊 General Results Queries", "🔍 Custom Results Queries"])
    
    with tab1:
        st.markdown("""
        <div class="card">
            <h2 style="margin-top: 0;">General Results Prompts</h2>
            <p>Select from these common results section prompts to generate content:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Static prompts for Results section
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            prompts = [
                "Summarize the key results of the study",
                "Identify statistical significance in results",
                "List primary outcomes and measurements",
                "Extract tables and figures explanations",
                "Analyze demographic data from the study",
                "Extract efficacy results",
                "Extract safety and adverse events",
                "Compare results with hypothesis"
            ]
            
            selected_prompt = st.selectbox(
                "Choose a prompt:", 
                prompts, 
                key="results_prompt_select", 
                index=0
            )
            
            # Execute prompt button
            execute_col1, execute_col2, execute_col3 = st.columns([1, 2, 1])
            with execute_col2:
                execute_button = st.button("Execute Prompt", key="execute_results_prompt", type="primary", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional options card
            st.markdown("""
            <div class="card">
                <h3 style="margin-top: 0;">Response Options</h3>
            """, unsafe_allow_html=True)
            
            result_format = st.selectbox(
                "Response Format:", 
                ["Paragraph", "Bullet Points", "Table", "Academic Style"], 
                key="results_format_select"
            )
            
            word_limit = st.slider(
                "Word Limit:", 
                min_value=100, 
                max_value=1000, 
                value=300, 
                step=50,
                key="results_word_limit"
            )
            
            st.markdown("""
            <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                <div class="tag tag-primary">APA Format</div>
                <div class="tag tag-secondary">Includes p-values</div>
                <div class="tag tag-accent">Statistical terminology</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Results box
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin-top: 0;">Generated Content</h3>', unsafe_allow_html=True)
            
            if "results_response" not in st.session_state:
                st.session_state.results_response = ""
                st.markdown("""
                <div style="height: 300px; display: flex; justify-content: center; align-items: center; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="text-align: center; color: var(--light-text);">
                        <span style="font-size: 3rem;">📝</span>
                        <p>Generated results will appear here</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.session_state.results_response:
                    results_container = st.container()
                    results_container.markdown(f"""
                    <div style="border-left: 4px solid var(--primary-color); padding-left: 1rem; margin-bottom: 1rem;">
                        {st.session_state.results_response}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="height: 300px; display: flex; justify-content: center; align-items: center; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;">
                        <div style="text-align: center; color: var(--light-text);">
                            <span style="font-size: 3rem;">📝</span>
                            <p>Generated results will appear here</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            col_save1, col_save2 = st.columns([4, 1])
            with col_save2:
                save_button = st.button("💾 Save", key="save_results", type="secondary", use_container_width=True)
                
            col_copy1, col_copy2 = st.columns([4, 1])
            with col_copy2:
                copy_button = st.button("📋 Copy", key="copy_results", type="secondary", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        if execute_button:
            # Prepare the prompt and execute
            with st.spinner("Generating results content..."):
                try:
                    # Create progress bar for visual feedback
                    progress_bar = st.progress(0)
                    
                    # Format options to add to the prompt
                    format_options = f"Format the response as {result_format} with approximately {word_limit} words."
                    
                    # Combine prompt with formatting options
                    final_prompt = f"{selected_prompt}. {format_options}"
                    
                    # Simulate progress while waiting for API response
                    progress_bar.progress(25)
                    time.sleep(0.5)
                    progress_bar.progress(50)
                    
                    # Make API call
                    response = requests.post(
                        f"{API_BASE_URL}/query",
                        json={
                            "assistant_id": st.session_state.assistant_id,
                            "thread_id": st.session_state.current_thread_id,
                            "query": final_prompt
                        }
                    )
                    
                    progress_bar.progress(75)
                    time.sleep(0.3)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, dict) and "response" in result:
                            # Update progress and save response
                            progress_bar.progress(100)
                            st.session_state.results_response = result["response"]
                            
                            # Rerun to update the UI
                            st.rerun()
                        else:
                            st.markdown("""
                            <div class="error-box">
                                Unexpected API response format.
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="error-box">
                            API request failed with status code: {response.status_code}
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-box">
                        An error occurred: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
        
        if save_button and st.session_state.results_response:
            # Save the response for later use
            if "saved_results" not in st.session_state:
                st.session_state.saved_results = []
            
            # Format saved result with prompt and timestamp
            saved_result = {
                "prompt": selected_prompt,
                "response": st.session_state.results_response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "format": result_format,
            }
            
            st.session_state.saved_results.append(saved_result)
            st.toast("Results saved successfully!", icon="✅")
    
    with tab2:
        st.markdown("""
        <div class="card">
            <h2 style="margin-top: 0;">Custom Results Query</h2>
            <p>Ask specific questions about your research paper results:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            # Custom prompt input
            custom_prompt = st.text_area(
                "Enter your query:",
                placeholder="e.g., Extract the p-values for the primary outcome",
                height=150,
                key="custom_results_prompt"
            )
            
            # Execute custom prompt button
            execute_custom_col1, execute_custom_col2, execute_custom_col3 = st.columns([1, 2, 1])
            with execute_custom_col2:
                execute_custom_button = st.button("Execute Query", key="execute_custom_results", type="primary", use_container_width=True)
            
            # Examples of custom queries
            st.markdown("""
            <h4>Examples:</h4>
            <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; cursor: pointer;" class="example-prompt">
                What are the confidence intervals for the primary outcomes?
            </div>
            <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; cursor: pointer;" class="example-prompt">
                Extract all numerical data from Table 2 and explain its significance
            </div>
            <div style="background-color: #f8f9fa; padding: 0.75rem; border-radius: 8px; cursor: pointer;" class="example-prompt">
                Compare the intervention group results with the control group
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Results box for custom query
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin-top: 0;">Query Response</h3>', unsafe_allow_html=True)
            
            if "custom_results_response" not in st.session_state:
                st.session_state.custom_results_response = ""
                st.markdown("""
                <div style="height: 300px; display: flex; justify-content: center; align-items: center; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="text-align: center; color: var(--light-text);">
                        <span style="font-size: 3rem;">🔍</span>
                        <p>Query responses will appear here</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.session_state.custom_results_response:
                    custom_results_container = st.container()
                    custom_results_container.markdown(f"""
                    <div style="border-left: 4px solid var(--accent-color); padding-left: 1rem; margin-bottom: 1rem;">
                        {st.session_state.custom_results_response}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="height: 300px; display: flex; justify-content: center; align-items: center; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;">
                        <div style="text-align: center; color: var(--light-text);">
                            <span style="font-size: 3rem;">🔍</span>
                            <p>Query responses will appear here</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            col_save_custom1, col_save_custom2 = st.columns([4, 1])
            with col_save_custom2:
                save_custom_button = st.button("💾 Save", key="save_custom_results", type="secondary", use_container_width=True)
                
            col_copy_custom1, col_copy_custom2 = st.columns([4, 1])
            with col_copy_custom2:
                copy_custom_button = st.button("📋 Copy", key="copy_custom_results", type="secondary", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        if execute_custom_button and custom_prompt:
            # Process custom prompt
            with st.spinner("Processing custom query..."):
                try:
                    # Create progress bar
                    progress_bar = st.progress(0)
                    
                    # Simulate processing steps
                    progress_bar.progress(30)
                    time.sleep(0.3)
                    
                    # Make API call
                    response = requests.post(
                        f"{API_BASE_URL}/query",
                        json={
                            "assistant_id": st.session_state.assistant_id,
                            "thread_id": st.session_state.current_thread_id,
                            "query": custom_prompt
                        }
                    )
                    
                    progress_bar.progress(70)
                    time.sleep(0.3)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, dict) and "response" in result:
                            # Update progress and save response
                            progress_bar.progress(100)
                            st.session_state.custom_results_response = result["response"]
                            
                            # Rerun to update the UI
                            st.rerun()
                        else:
                            st.markdown("""
                            <div class="error-box">
                                Unexpected API response format.
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="error-box">
                            API request failed with status code: {response.status_code}
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-box">
                        An error occurred: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
        elif execute_custom_button and not custom_prompt:
            st.markdown("""
            <div class="error-box">
                Please enter a query before executing.
            </div>
            """, unsafe_allow_html=True)
        
        if save_custom_button and st.session_state.custom_results_response:
            # Save the custom response
            if "saved_results" not in st.session_state:
                st.session_state.saved_results = []
            
            # Format saved result
            saved_result = {
                "prompt": custom_prompt,
                "response": st.session_state.custom_results_response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "format": "Custom Query",
            }
            
            st.session_state.saved_results.append(saved_result)
            st.toast("Custom results saved successfully!", icon="✅")
    
    # Display saved results if available
    if st.session_state.get("saved_results"):
        st.markdown("""
        <div class="section-divider">
            <div class="line"></div>
            <div class="title">Saved Results</div>
            <div class="line"></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        for i, saved in enumerate(st.session_state.saved_results):
            with st.expander(f"{saved['prompt']} ({saved['timestamp']})"):
                st.markdown(f"**Format:** {saved['format']}")
                st.markdown(saved["response"])
                
                col1, col2, col3 = st.columns([5, 1, 1])
                with col2:
                    if st.button("Edit", key=f"edit_result_{i}"):
                        st.session_state.editing_result = i
                with col3:
                    if st.button("Delete", key=f"delete_result_{i}"):
                        st.session_state.saved_results.pop(i)
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export all saved results
        export_col1, export_col2, export_col3 = st.columns([3, 2, 3])
        with export_col2:
            if st.button("Export All Results", type="secondary", use_container_width=True):
                # Generate export data
                export_data = ""
                for saved in st.session_state.saved_results:
                    export_data += f"# {saved['prompt']}\n"
                    export_data += f"*{saved['timestamp']} - {saved['format']}*\n\n"
                    export_data += f"{saved['response']}\n\n"
                    export_data += "---\n\n"
                
                # Create download button for the data
                st.download_button(
                    label="Download Results",
                    data=export_data,
                    file_name="results_export.txt",
                    mime="text/plain"
                )

def show_methods_tab():
    """Display the methods section interface."""
    if not st.session_state.file_uploaded:
        st.warning("Please upload a document first to access the Methods section.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Methods Section")
    
    # Create tabs for endpoint-based and general prompts
    tab1, tab2 = st.tabs(["📊 Endpoint-Based Prompts", "🔎 General Prompts"])
    
    with tab1:
        show_methods_endpoints()
    
    with tab2:
        show_methods_general_prompts()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_methods_endpoints():
    """Show methods section's endpoint-based functionality."""
    # Initialize session state for selected endpoints if not already done
    if "selected_endpoints_for_methods" not in st.session_state:
        st.session_state["selected_endpoints_for_methods"] = []
    
    # Variables to track selection
    selected_endpoint = None
    selected_category = None
    main_endpoint_name = None
    subgroup_bullet = None
    
    # Load endpoints
    with st.spinner("Loading endpoints..."):
        if "file_name" in st.session_state and st.session_state.file_name:
            try:
                params = {'file_name': st.session_state.file_name}
                response = requests.get(f"{API_BASE_URL}/methods/get_endpoints_for_methods", params=params)
                
                if response.status_code == 200:
                    categorized_endpoints = response.json().get("endpoints", {})
                    st.session_state["methods_categorized_endpoints"] = categorized_endpoints
                    
                    endpoint_count = sum(len(ep) for ep in categorized_endpoints.values())
                    st.success(f"{endpoint_count} endpoints loaded from {len(categorized_endpoints)} categories")
                else:
                    st.error(f"API Error: {response.json().get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        elif "methods_categorized_endpoints" not in st.session_state:
            st.error("Please upload a file first")
    
    # Display endpoints
    if "methods_categorized_endpoints" in st.session_state:
        st.markdown("## Endpoints Selected in Results Section")
        
        # Track whether a subgroup was selected
        subgroup_selected = False
        
        # Container for endpoints with search
        with st.container():
            # Add search filter
            search_term = st.text_input("🔍 Filter endpoints", key="methods_endpoint_search")
            
            # Display endpoints by category with filtering
            for category, endpoints in st.session_state["methods_categorized_endpoints"].items():
                # Display category if it contains matching endpoints or if no search
                matching_endpoints = [e for e in endpoints if not search_term or search_term.lower() in e.get("endpoint_name", "").lower()]
                
                if matching_endpoints:
                    with st.expander(f"**{category}** ({len(matching_endpoints)} endpoints)", expanded=not search_term):
                        for endpoint in matching_endpoints:
                            eid = endpoint.get("endpoint_id")
                            ename = endpoint.get("endpoint_name")
                            
                            endpoint_checked = st.checkbox(
                                ename,
                                key=f"methods_endpoint_{eid}",
                                help=f"Select this endpoint to generate method details"
                            )
                            
                            if endpoint_checked:
                                # Add to selected endpoints if not already there
                                if eid not in [ep['endpoint_id'] for ep in st.session_state["selected_endpoints_for_methods"]]:
                                    st.session_state["selected_endpoints_for_methods"].append(endpoint)
                                
                                # Handle subgroups
                                subgroup_responses = endpoint.get('subgroup_assistant_responses', [])
                                if subgroup_responses:
                                    with st.expander(f"Subgroups for '{ename}'", expanded=True):
                                        st.markdown("Select a subgroup for more detailed analysis:")
                                        
                                        for s_idx, subgroup_text in enumerate(subgroup_responses):
                                            bullet_points = re.findall(r'^\s*-\s(.+?)(?=^\s*-\s|\Z)', subgroup_text, re.DOTALL | re.MULTILINE)
                                            
                                            for b_idx, bullet in enumerate(bullet_points):
                                                bullet_clean = bullet.strip().replace('\n', ' ')
                                                bullet_key = f"{eid}_sub_{s_idx}_bullet_{b_idx}"
                                                
                                                bullet_selected = st.checkbox(
                                                    bullet_clean,
                                                    key=bullet_key,
                                                    help="Select this subgroup for analysis"
                                                )
                                                
                                                if bullet_selected:
                                                    subgroup_bullet = bullet_clean
                                                    selected_category = category
                                                    selected_endpoint = ename
                                                    subgroup_selected = True
                                
                                # If no subgroup selected, use the main endpoint
                                if not subgroup_selected:
                                    selected_endpoint = ename
                                    selected_category = category
                                    main_endpoint_name = ename
                            else:
                                # Remove from selected endpoints if unchecked
                                st.session_state["selected_endpoints_for_methods"] = [
                                    ep for ep in st.session_state["selected_endpoints_for_methods"] 
                                    if ep.get("endpoint_id") != eid
                                ]
        
        # If an endpoint is selected, show prompt options
        if selected_endpoint:
            st.session_state["selected_endpoint"] = selected_endpoint
            st.session_state["selected_category"] = selected_category
            
            if main_endpoint_name is None:
                main_endpoint_name = selected_endpoint
            
            st.markdown("---")
            st.markdown("## 🔸 Generate Content for Selected Endpoint")
            
            # Build dynamic prompts based on selection
            dynamic_prompts = []
            
            if main_endpoint_name and not subgroup_bullet:
                dynamic_prompts.append(
                    f"Please can you provide details of the outcome {main_endpoint_name}. Please can you provide details, including how and when they are evaluated. For when they were evaluated please can you provide exact timepoints (i.e. which days or weeks). Please can you provide this information as a bulleted list."
                )
            elif main_endpoint_name and subgroup_bullet:
                dynamic_prompts.append(
                    f"Please can you provide details of the outcome {main_endpoint_name}. Please can you provide details for the subgroup {subgroup_bullet}, including how and when they are evaluated. For when they were evaluated please can you provide exact timepoints (i.e. which days or weeks). Please can you provide this information as a bulleted list."
                )
            
            # Prompt selection
            dynamic_prompt_selection = st.selectbox(
                "Select a prompt:",
                dynamic_prompts,
                key="methods_dynamic_prompt_selector"
            )
            
            # Display selected prompt in a code block
            st.code(dynamic_prompt_selection, language="")
            
            # Thread dependency option
            dependent_endpoint = st.checkbox(
                "Thread dependent (maintains conversation context)",
                True,
                key="methods_section_dependent_checkbox_endpoint"
            )
            st.session_state["checkbox_dependent_endpoint"] = dependent_endpoint
            
            # Execute button
            if st.button("▶️ Execute Prompt", key="methods_use_dynamic_prompt"):
                run_methods_endpoint_prompt(dynamic_prompt_selection, dependent_endpoint)
            
            # Display and edit response
            if st.session_state.get("methods_checkbox_response"):
                st.markdown("---")
                st.markdown("### 💬 AI Response")
                
                with st.expander("Edit Response", expanded=True):
                    edited_response = st.text_area(
                        "Edit AI response:",
                        st.session_state["methods_checkbox_response"],
                        height=300,
                        key="methods_response_text"
                    )
                    
                    if st.session_state.current_method_checkbox_thread_id:
                        st.info(f"Thread ID: {st.session_state.current_method_checkbox_thread_id}")
                    
                    # Citations display
                    if st.session_state.get("methods_checkbox_citations"):
                        with st.expander("📚 Citations", expanded=False):
                            for i, citation in enumerate(st.session_state["methods_checkbox_citations"]):
                                st.markdown(f"**Citation {i+1}:** {citation}")
                    
                    # Save button
                    if st.button("💾 Save Response", key="save_methods_response_button"):
                        save_methods_response(edited_response)

def run_methods_endpoint_prompt(prompt, dependent):
    """Run a methods endpoint prompt."""
    st.session_state['user_query'] = prompt
    
    with st.spinner("Processing your query..."):
        try:
            payload = {
                "question": prompt,
                "file_name": st.session_state.file_name,
                "assistant_id": st.session_state.assistant_id,
                "vector_id": st.session_state.vector_id,
                "current_thread_id": st.session_state.current_method_checkbox_thread_id or None,
                "dependent": dependent,
            }
            
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                res = response.json()
                st.session_state["methods_checkbox_response"] = res.get("response", "")
                st.session_state["methods_checkbox_citations"] = res.get("citations", [])
                st.session_state.current_method_checkbox_thread_id = res.get("thread_id")
                st.success("Query processed successfully!")
            else:
                st.error("Failed to process your query.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def save_methods_response(edited_response):
    """Save the methods response."""
    with st.spinner("Saving your response..."):
        try:
            save_payload = {
                'file_name': st.session_state.file_name,
                'user_query': st.session_state.user_query,
                'assistant_response': edited_response,
                'citations': st.session_state.methods_checkbox_citations,
                'thread_id': st.session_state.current_method_checkbox_thread_id,
                'selected_endpoint': st.session_state.selected_endpoint,
                'selected_category': st.session_state.selected_category
            }
            
            save_response = requests.post(f"{API_BASE_URL}/methods/save_methods_response", json=save_payload)
            
            if save_response.status_code == 200:
                st.success("Methods response saved successfully!")
            else:
                st.error("Error saving methods response.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def show_methods_general_prompts():
    """Show methods section's general prompts functionality."""
    st.markdown("## 🔹 General Prompts")
    st.markdown("These prompts don't require endpoint selection and focus on general methodology aspects.")
    
    # Define static prompts
    static_prompts = [
        "1. Summarise study design: Based upon the methods sections of the report please can you provide details of the trial design, including the number of centres it was conducted in and also the countries it was conducted in. Please can you provide this information as a bulleted list",
        "2. Inclusion criteria: Please can you summarise the inclusion criteria for patients in the study. Please can you provide this information as a bulleted list",
        "3. Exclusion criteria: Please can you summarise the exclusion criteria for patients in the study. Please can you provide this information as a bulleted list",
        "4. Ethics criteria: Please can you provide details of ethical approval for this trial, and also funding. Please can you provide this information as a bulleted list",
        "5. Randomisation: Please can you provide details of how people were randomised in the study, including the tool used for randomisation and any stratification. Please can you provide this information as a bulleted list",
        "6. Study structure: Please can you provide details of how the study was structured, including details of each different study period. Please can you provide this information as a bulleted list",
        "7. Treatment: Please can you provide details of how patients received the treatment. Please can you provide this information as a bulleted list",
        "8. Trial amendments: Please can you provide trial amendments information as a bulleted list"
    ]
    
    # Two column layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        static_prompt_selection = st.radio(
            "Select a general prompt:",
            static_prompts,
            key="static_prompt_selector_general_methods"
        )
    
    with col2:
        # Display selected prompt in a code block
        st.code(static_prompt_selection, language="")
        
        # Thread dependency option
        dependent_general = st.checkbox(
            "Thread dependent",
            True,
            key="methods_general_dependent_checkbox"
        )
        
        # Execute button
        if st.button("▶️ Execute Prompt", key="methods_run_static_prompt"):
            run_methods_general_prompt(static_prompt_selection, dependent_general)
    
    # Display and edit response
    if st.session_state.get("methods_general_checkbox_response"):
        st.markdown("---")
        st.markdown("### 💬 AI Response")
        
        with st.expander("Edit Response", expanded=True):
            edited_response = st.text_area(
                "Edit AI response:",
                st.session_state["methods_general_checkbox_response"],
                height=300,
                key="methods_general_response_text"
            )
            
            if st.session_state.current_method_checkbox_thread_id:
                st.info(f"Thread ID: {st.session_state.current_method_checkbox_thread_id}")
            
            # Citations display
            if st.session_state.get("methods_general_checkbox_citations"):
                with st.expander("📚 Citations", expanded=False):
                    for i, citation in enumerate(st.session_state["methods_general_checkbox_citations"]):
                        st.markdown(f"**Citation {i+1}:** {citation}")
            
            # Save button
            if st.button("💾 Save Response", key="save_methods_general_response_button"):
                save_methods_general_response(edited_response, static_prompt_selection)

def run_methods_general_prompt(prompt, dependent):
    """Run a methods general prompt."""
    st.session_state['user_query'] = prompt
    
    with st.spinner("Processing your query..."):
        try:
            payload = {
                "question": prompt,
                "file_name": st.session_state.file_name,
                "assistant_id": st.session_state.assistant_id,
                "vector_id": st.session_state.vector_id,
                "current_thread_id": st.session_state.current_method_checkbox_thread_id or None,
                "dependent": dependent,
            }
            
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                res = response.json()
                st.session_state["methods_general_checkbox_response"] = res.get("response", "")
                st.session_state["methods_general_checkbox_citations"] = res.get("citations", [])
                st.session_state.current_method_checkbox_thread_id = res.get("thread_id")
                st.success("Query processed successfully!")
            else:
                st.error("Failed to process your query.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def save_methods_general_response(edited_response, prompt):
    """Save the methods general response."""
    with st.spinner("Saving your response..."):
        try:
            save_payload = {
                'file_name': st.session_state.file_name,
                'user_query': st.session_state.user_query,
                'assistant_response': edited_response,
                'citations': st.session_state.methods_general_checkbox_citations,
                'thread_id': st.session_state.current_method_checkbox_thread_id,
                'selected_endpoint': None,
                'selected_category': prompt.split(":", 1)[0].strip()  # Extract prompt number/category
            }
            
            save_response = requests.post(f"{API_BASE_URL}/methods/save_methods_response", json=save_payload)
            
            if save_response.status_code == 200:
                st.success("General prompt response saved successfully!")
            else:
                st.error("Error saving general prompt response.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def show_conclusion_tab():
    """Display the conclusion section interface."""
    if not st.session_state.file_uploaded:
        st.warning("Please upload a document first to access the Conclusion section.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Conclusion Section")
    
    # Create tabs for endpoint-based and general prompts
    tab1, tab2 = st.tabs(["📊 Endpoint-Based Prompts", "🔎 General Prompts"])
    
    with tab1:
        show_conclusion_endpoints()
    
    with tab2:
        show_conclusion_general_prompts()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_conclusion_endpoints():
    """Show conclusion section's endpoint-based functionality."""
    # Initialize session state for selected endpoints if not already done
    if "conclusion_selected_endpoints_for_methods" not in st.session_state:
        st.session_state["conclusion_selected_endpoints_for_methods"] = []
    
    # Variables to track selection
    conclusion_selected_endpoint = None
    conclusion_selected_category = None
    conclusion_main_endpoint_name = None
    conclusion_subgroup_bullet = None
    
    # Load endpoints
    with st.spinner("Loading endpoints..."):
        if "file_name" in st.session_state and st.session_state.file_name:
            try:
                params = {'file_name': st.session_state.file_name}
                response = requests.get(f"{API_BASE_URL}/methods/get_endpoints_for_methods", params=params)
                
                if response.status_code == 200:
                    conclusion_categorized_endpoints = response.json().get("endpoints", {})
                    st.session_state["conclusion_methods_categorized_endpoints"] = conclusion_categorized_endpoints
                    
                    endpoint_count = sum(len(ep) for ep in conclusion_categorized_endpoints.values())
                    st.success(f"{endpoint_count} endpoints loaded from {len(conclusion_categorized_endpoints)} categories")
                else:
                    st.error(f"API Error: {response.json().get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        elif "conclusion_methods_categorized_endpoints" not in st.session_state:
            st.error("Please upload a file first")
    
    # Display endpoints
    if "conclusion_methods_categorized_endpoints" in st.session_state:
        st.markdown("## Endpoints Selected in Results Section")
        
        # Track whether a subgroup was selected
        conclusion_subgroup_selected = False
        
        # Container for endpoints with search
        with st.container():
            # Add search filter
            search_term = st.text_input("🔍 Filter endpoints", key="conclusion_endpoint_search")
            
            # Display endpoints by category with filtering
            for category, endpoints in st.session_state["conclusion_methods_categorized_endpoints"].items():
                # Display category if it contains matching endpoints or if no search
                matching_endpoints = [e for e in endpoints if not search_term or search_term.lower() in e.get("endpoint_name", "").lower()]
                
                if matching_endpoints:
                    with st.expander(f"**{category}** ({len(matching_endpoints)} endpoints)", expanded=not search_term):
                        for endpoint in matching_endpoints:
                            eid = endpoint.get("endpoint_id")
                            ename = endpoint.get("endpoint_name")
                            
                            endpoint_checked = st.checkbox(
                                ename,
                                key=f"conclusion_methods_endpoint_{eid}",
                                help=f"Select this endpoint to generate conclusion details"
                            )
                            
                            if endpoint_checked:
                                # Add to selected endpoints if not already there
                                if eid not in [ep['endpoint_id'] for ep in st.session_state["conclusion_selected_endpoints_for_methods"]]:
                                    st.session_state["conclusion_selected_endpoints_for_methods"].append(endpoint)
                                
                                # Handle subgroups
                                subgroup_responses = endpoint.get('subgroup_assistant_responses', [])
                                if subgroup_responses:
                                    with st.expander(f"Subgroups for '{ename}'", expanded=True):
                                        st.markdown("Select a subgroup for more detailed analysis:")
                                        
                                        for s_idx, subgroup_text in enumerate(subgroup_responses):
                                            bullet_points = re.findall(r'^\s*-\s(.+?)(?=^\s*-\s|\Z)', subgroup_text, re.DOTALL | re.MULTILINE)
                                            
                                            for b_idx, bullet in enumerate(bullet_points):
                                                bullet_clean = bullet.strip().replace('\n', ' ')
                                                bullet_key = f"{eid}_sub_{s_idx}_bullet_{b_idx}"
                                                
                                                bullet_selected = st.checkbox(
                                                    bullet_clean,
                                                    key=f"conclusion_{bullet_key}",
                                                    help="Select this subgroup for analysis"
                                                )
                                                
                                                if bullet_selected:
                                                    conclusion_subgroup_bullet = bullet_clean
                                                    conclusion_selected_category = category
                                                    conclusion_selected_endpoint = ename
                                                    conclusion_subgroup_selected = True
                                
                                # If no subgroup selected, use the main endpoint
                                if not conclusion_subgroup_selected:
                                    conclusion_selected_endpoint = ename
                                    conclusion_selected_category = category
                                    conclusion_main_endpoint_name = ename
                            else:
                                # Remove from selected endpoints if unchecked
                                st.session_state["conclusion_selected_endpoints_for_methods"] = [
                                    ep for ep in st.session_state["conclusion_selected_endpoints_for_methods"] 
                                    if ep.get("endpoint_id") != eid
                                ]
        
        # If an endpoint is selected, show prompt options
        if conclusion_selected_endpoint:
            st.session_state["conclusion_selected_endpoint"] = conclusion_selected_endpoint
            st.session_state["conclusion_selected_category"] = conclusion_selected_category
            
            if conclusion_main_endpoint_name is None:
                conclusion_main_endpoint_name = conclusion_selected_endpoint
            
            st.markdown("---")
            st.markdown("## 🔸 Generate Content for Selected Endpoint")
            
            # Build dynamic prompts based on selection
            conclusion_dynamic_prompts = []
            
            if conclusion_main_endpoint_name and not conclusion_subgroup_bullet:
                conclusion_dynamic_prompts.append(
                    f"In bullet points please could you propose a maximum of 2 sentences describing any conclusions drawn in the report on the endpoint {conclusion_main_endpoint_name} and any key learnings relating to it"
                )
            elif conclusion_main_endpoint_name and conclusion_subgroup_bullet:
                conclusion_dynamic_prompts.append(
                    f"In bullet points please could you propose a maximum of 2 sentences describing any conclusions drawn in the report on the endpoint {conclusion_main_endpoint_name} for the {conclusion_subgroup_bullet} any key learnings relating to it"
                )
            
            # Prompt selection
            conclusion_dynamic_prompt_selection = st.selectbox(
                "Select a prompt:",
                conclusion_dynamic_prompts,
                key="conclusion_dynamic_prompt_selector"
            )
            
            # Display selected prompt in a code block
            st.code(conclusion_dynamic_prompt_selection, language="")
            
            # Thread dependency option
            conclusion_dependent_endpoint = st.checkbox(
                "Thread dependent (maintains conversation context)",
                True,
                key="conclusion_methods_section_dependent_checkbox_endpoint"
            )
            st.session_state["conclusion_checkbox_dependent_endpoint"] = conclusion_dependent_endpoint
            
            # Execute button
            if st.button("▶️ Execute Prompt", key="conclusion_use_dynamic_prompt"):
                run_conclusion_endpoint_prompt(conclusion_dynamic_prompt_selection, conclusion_dependent_endpoint)
            
            # Display and edit response
            if st.session_state.get("conclusion_methods_checkbox_response"):
                st.markdown("---")
                st.markdown("### 💬 AI Response")
                
                with st.expander("Edit Response", expanded=True):
                    conclusion_edited_response = st.text_area(
                        "Edit AI response:",
                        st.session_state["conclusion_methods_checkbox_response"],
                        height=300,
                        key="conclusion_methods_response_text"
                    )
                    
                    if st.session_state.current_conclusion_checkbox_thread_id:
                        st.info(f"Thread ID: {st.session_state.current_conclusion_checkbox_thread_id}")
                    
                    # Citations display
                    if st.session_state.get("conclusion_methods_checkbox_citations"):
                        with st.expander("📚 Citations", expanded=False):
                            for i, citation in enumerate(st.session_state["conclusion_methods_checkbox_citations"]):
                                st.markdown(f"**Citation {i+1}:** {citation}")
                    
                    # Save button
                    if st.button("💾 Save Response", key="save_conclusion_methods_response_button"):
                        save_conclusion_response(conclusion_edited_response)

def run_conclusion_endpoint_prompt(prompt, dependent):
    """Run a conclusion endpoint prompt."""
    st.session_state['conclusion_user_query'] = prompt
    
    with st.spinner("Processing your query..."):
        try:
            payload = {
                "question": prompt,
                "file_name": st.session_state.file_name,
                "assistant_id": st.session_state.assistant_id,
                "vector_id": st.session_state.vector_id,
                "current_thread_id": st.session_state.current_conclusion_checkbox_thread_id or None,
                "dependent": dependent,
            }
            
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                res = response.json()
                st.session_state["conclusion_methods_checkbox_response"] = res.get("response", "")
                st.session_state["conclusion_methods_checkbox_citations"] = res.get("citations", [])
                st.session_state.current_conclusion_checkbox_thread_id = res.get("thread_id")
                st.success("Query processed successfully!")
            else:
                st.error("Failed to process your query.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def save_conclusion_response(edited_response):
    """Save the conclusion response."""
    with st.spinner("Saving your response..."):
        try:
            save_payload = {
                'file_name': st.session_state.file_name,
                'user_query': st.session_state.conclusion_user_query,
                'assistant_response': edited_response,
                'citations': st.session_state.conclusion_methods_checkbox_citations,
                'thread_id': st.session_state.current_conclusion_checkbox_thread_id,
                'selected_endpoint': st.session_state.conclusion_selected_endpoint,
                'selected_category': st.session_state.conclusion_selected_category
            }
            
            save_response = requests.post(f"{API_BASE_URL}/conclusion/save_conclusion_response", json=save_payload)
            
            if save_response.status_code == 200:
                st.success("Conclusion response saved successfully!")
            else:
                st.error("Error saving conclusion response.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def show_conclusion_general_prompts():
    """Show conclusion section's general prompts functionality."""
    st.markdown("## 🔹 General Conclusion Prompts")
    st.markdown("These prompts help generate high-level conclusions about the study.")
    
    # Define static prompts for conclusion
    conclusion_static_prompts = [
        "1. Please can you summarize the main findings of this study in bullet points.",
        "2. Based on the discussion section, what were the main limitations of this study? Please respond in bullet points.",
        "3. What are the key strengths of this study design and findings? Please respond in bullet points.",
        "4. What are the potential implications of these findings for clinical practice? Please respond in bullet points.",
        "5. What future research directions were suggested in this study? Please respond in bullet points.",
        "6. Please write a concluding paragraph that summarizes the study findings, contextualizes the results, and mentions potential implications."
    ]
    
    # Two column layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        conclusion_static_prompt_selection = st.radio(
            "Select a general prompt:",
            conclusion_static_prompts,
            key="static_prompt_selector_general_conclusion"
        )
    
    with col2:
        # Display selected prompt in a code block
        st.code(conclusion_static_prompt_selection, language="")
        
        # Thread dependency option
        conclusion_dependent_general = st.checkbox(
            "Thread dependent",
            True,
            key="conclusion_general_dependent_checkbox"
        )
        
        # Execute button
        if st.button("▶️ Execute Prompt", key="conclusion_run_static_prompt"):
            run_conclusion_general_prompt(conclusion_static_prompt_selection, conclusion_dependent_general)
    
    # Display and edit response
    if st.session_state.get("conclusion_general_checkbox_response"):
        st.markdown("---")
        st.markdown("### 💬 AI Response")
        
        with st.expander("Edit Response", expanded=True):
            edited_response = st.text_area(
                "Edit response:",
                st.session_state["conclusion_general_checkbox_response"],
                height=300,
                key="conclusion_general_response_text"
            )
            
            # Display citations
            if st.session_state.get("conclusion_general_checkbox_citations"):
                with st.expander("📚 Citations", expanded=False):
                    for i, citation in enumerate(st.session_state["conclusion_general_checkbox_citations"]):
                        st.markdown(f"**Citation {i+1}:** {citation}")
            
            # Save button
            if st.button("💾 Save Response", key="save_conclusion_general_response_button"):
                save_conclusion_general_response(edited_response, conclusion_static_prompt_selection)

def run_conclusion_general_prompt(prompt, dependent):
    """Run a conclusion general prompt."""
    st.session_state['conclusion_general_user_query'] = prompt
    
    with st.spinner("Processing your query..."):
        try:
            payload = {
                "question": prompt,
                "file_name": st.session_state.file_name,
                "assistant_id": st.session_state.assistant_id,
                "vector_id": st.session_state.vector_id,
                "current_thread_id": st.session_state.current_conclusion_checkbox_thread_id or None,
                "dependent": dependent,
            }
            
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                res = response.json()
                st.session_state["conclusion_general_checkbox_response"] = res.get("response", "")
                st.session_state["conclusion_general_checkbox_citations"] = res.get("citations", [])
                st.session_state.current_conclusion_checkbox_thread_id = res.get("thread_id")
                st.success("Query processed successfully!")
            else:
                st.error("Failed to process your query.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def save_conclusion_general_response(edited_response, prompt):
    """Save the conclusion general response."""
    with st.spinner("Saving your response..."):
        try:
            save_payload = {
                'file_name': st.session_state.file_name,
                'user_query': st.session_state.conclusion_general_user_query,
                'assistant_response': edited_response,
                'citations': st.session_state.conclusion_general_checkbox_citations,
                'thread_id': st.session_state.current_conclusion_checkbox_thread_id,
                'selected_endpoint': None,
                'selected_category': prompt.split(".", 1)[0].strip()  # Extract prompt number/category
            }
            
            save_response = requests.post(f"{API_BASE_URL}/conclusion/save_conclusion_response", json=save_payload)
            
            if save_response.status_code == 200:
                st.success("General conclusion response saved successfully!")
            else:
                st.error("Error saving general conclusion response.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def show_discussion_tab():
    """Display the discussion section interface."""
    if not st.session_state.file_uploaded:
        st.warning("Please upload a document first to access the Discussion section.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Discussion Section")
    
    # Two tabs for different query types
    tab1, tab2 = st.tabs(["🔎 General Prompts", "💬 Custom Queries"])
    
    with tab1:
        show_discussion_general_prompts()
    
    with tab2:
        show_discussion_custom_queries()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_discussion_general_prompts():
    """Show discussion section's general prompts functionality."""
    st.markdown("## 🔹 General Discussion Prompts")
    st.markdown("These prompts help generate content for the discussion section.")
    
    # Define static prompts for discussion
    discussion_static_prompts = [
        "1. Please summarize the key findings of this study in context of prior literature. Please respond in bullet points.",
        "2. What are the strengths and limitations of this study as mentioned in the discussion? Please respond in bullet points.",
        "3. What are the clinical implications of these findings according to the discussion? Please respond in bullet points.",
        "4. How do the results of this study compare with previous research? Please respond in bullet points.",
        "5. What unexpected or novel findings were highlighted in the discussion? Please respond in bullet points.",
        "6. What future research directions were suggested? Please respond in bullet points.",
        "7. Please provide a comprehensive summary of the discussion section in bullet points."
    ]
    
    # Two column layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        discussion_static_prompt_selection = st.radio(
            "Select a general prompt:",
            discussion_static_prompts,
            key="static_prompt_selector_general_discussion"
        )
    
    with col2:
        # Display selected prompt in a code block
        st.code(discussion_static_prompt_selection, language="")
        
        # Thread dependency option
        discussion_dependent_general = st.checkbox(
            "Thread dependent",
            True,
            key="discussion_general_dependent_checkbox"
        )
        
        # Execute button
        if st.button("▶️ Execute Prompt", key="discussion_run_static_prompt"):
            run_discussion_general_prompt(discussion_static_prompt_selection, discussion_dependent_general)
    
    # Display and edit response
    if st.session_state.get("discussion_general_checkbox_response"):
        st.markdown("---")
        st.markdown("### 💬 AI Response")
        
        with st.expander("Edit Response", expanded=True):
            edited_response = st.text_area(
                "Edit AI response:",
                st.session_state["discussion_general_checkbox_response"],
                height=300,
                key="discussion_general_response_text"
            )
            
            if st.session_state.get("discussion_general_thread_id"):
                st.info(f"Thread ID: {st.session_state.discussion_general_thread_id}")
            
            # Citations display
            if st.session_state.get("discussion_general_checkbox_citations"):
                with st.expander("📚 Citations", expanded=False):
                    for i, citation in enumerate(st.session_state["discussion_general_checkbox_citations"]):
                        st.markdown(f"**Citation {i+1}:** {citation}")
            
            # Save button
            if st.button("💾 Save Response", key="save_discussion_general_response_button"):
                save_discussion_general_response(edited_response, discussion_static_prompt_selection)

def run_discussion_general_prompt(prompt, dependent):
    """Run a discussion general prompt."""
    st.session_state['discussion_general_user_query'] = prompt
    
    with st.spinner("Processing your query..."):
        try:
            payload = {
                "question": prompt,
                "file_name": st.session_state.file_name,
                "assistant_id": st.session_state.assistant_id,
                "vector_id": st.session_state.vector_id,
                "current_thread_id": st.session_state.get("discussion_general_thread_id"),
                "dependent": dependent,
            }
            
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                res = response.json()
                st.session_state["discussion_general_checkbox_response"] = res.get("response", "")
                st.session_state["discussion_general_checkbox_citations"] = res.get("citations", [])
                st.session_state["discussion_general_thread_id"] = res.get("thread_id")
                st.success("Query processed successfully!")
            else:
                st.error("Failed to process your query.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def save_discussion_general_response(edited_response, prompt):
    """Save the discussion general response."""
    with st.spinner("Saving your response..."):
        try:
            save_payload = {
                'file_name': st.session_state.file_name,
                'user_query': st.session_state.discussion_general_user_query,
                'assistant_response': edited_response,
                'citations': st.session_state.discussion_general_checkbox_citations,
                'thread_id': st.session_state.get("discussion_general_thread_id"),
                'selected_endpoint': None,
                'selected_category': prompt.split(".", 1)[0].strip()  # Extract prompt number/category
            }
            
            save_response = requests.post(f"{API_BASE_URL}/discussion/save_discussion_response", json=save_payload)
            
            if save_response.status_code == 200:
                st.success("Discussion response saved successfully!")
            else:
                st.error("Error saving discussion response.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def show_discussion_custom_queries():
    """Show discussion section's custom query chat interface."""
    st.markdown("## 💬 Custom Discussion Queries")
    st.markdown("Ask specific questions about the discussion section.")
    
    # Initialize thread ID for the discussion chat if not set
    if "discussion_chat_thread_id" not in st.session_state:
        st.session_state["discussion_chat_thread_id"] = ""
    
    # Thread dependency option
    dependent = st.checkbox(
        "Thread dependent (maintains conversation context)",
        value=True,
        key="discussion_chat_dependent_checkbox"
    )
    
    # Text input for custom query
    user_message = st.text_area(
        "Enter your query about the discussion section:",
        key="discussion_custom_message",
        height=100,
        placeholder="e.g., How does this study compare with Smith et al. 2019?"
    )
    
    # Execute button
    if st.button("💬 Send Query", key="send_discussion_custom_message"):
        if user_message and st.session_state.file_uploaded:
            with st.spinner("Processing your query..."):
                try:
                    # Prepare payload
                    payload = {
                        'question': user_message,
                        'file_name': st.session_state.file_name,
                        'assistant_id': st.session_state.assistant_id,
                        'vector_id': st.session_state.vector_id,
                        'thread_id': st.session_state["discussion_chat_thread_id"],
                        'dependent': dependent,
                    }
                    
                    # Send request
                    response = requests.post(f"{API_BASE_URL}/discussion/chat_discussion", json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state["discussion_chat_response"] = result.get("response", "")
                        st.session_state["discussion_chat_citations"] = result.get("citations", [])
                        st.session_state["discussion_chat_thread_id"] = result.get("thread_id", "")
                        
                        st.success("Response received!")
                    else:
                        error_message = response.json().get("error", "Failed to process the query.")
                        st.error(error_message)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            if not user_message:
                st.error("Please enter a query to send.")
            else:
                st.error("Please upload a paper first.")
    
    # Display response if available
    if st.session_state.get("discussion_chat_response"):
        st.markdown("---")
        st.markdown("### 💬 AI Response")
        
        with st.expander("Response", expanded=True):
            chat_response = st.text_area(
                "Edit response:",
                st.session_state["discussion_chat_response"],
                height=300,
                key="discussion_chat_response_text"
            )
            
            if st.session_state["discussion_chat_thread_id"]:
                st.info(f"Thread ID: {st.session_state['discussion_chat_thread_id']}")
            
            # Citations display
            if st.session_state.get("discussion_chat_citations"):
                with st.expander("📚 Citations", expanded=False):
                    for i, citation in enumerate(st.session_state["discussion_chat_citations"]):
                        st.markdown(f"**Citation {i+1}:** {citation}")
            
            # Save button
            if st.button("💾 Save Response", key="save_discussion_chat_response_button"):
                with st.spinner("Saving your response..."):
                    try:
                        save_payload = {
                            'file_name': st.session_state.file_name,
                            'user_query': user_message,
                            'assistant_response': chat_response,
                            'citations': st.session_state["discussion_chat_citations"],
                            'thread_id': st.session_state["discussion_chat_thread_id"]
                        }
                        
                        save_response = requests.post(f"{API_BASE_URL}/discussion/save_discussion_chat_response", json=save_payload)
                        
                        if save_response.status_code == 200:
                            st.success("Discussion chat response saved successfully!")
                        else:
                            st.error("Error saving discussion chat response.")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

def show_export_tab():
    """Display the export document interface."""
    if not st.session_state.file_uploaded:
        st.warning("Please upload a document first to access the Export function.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Export Document")
    
    st.markdown("""
    ## 📄 Generate Final Research Paper
    
    This section allows you to compile all the saved content from different sections into a cohesive research paper document.
    You can customize the format and export options below.
    """)
    
    # Get saved content
    with st.spinner("Loading saved content..."):
        try:
            params = {'file_name': st.session_state.file_name}
            response = requests.get(f"{API_BASE_URL}/export/get_saved_responses", params=params)
            
            if response.status_code == 200:
                saved_content = response.json()
                
                # Check if there's any content to display
                has_content = any(saved_content.get(section, []) for section in 
                                ["introduction", "methods", "results", "discussion", "conclusion"])
                
                if has_content:
                    # Layout with sections side by side
                    col1, col2 = st.columns(2)
                    
                    # Format options
                    with col1:
                        st.markdown("### Export Options")
                        
                        export_format = st.selectbox(
                            "Select export format:",
                            ["DOCX", "PDF", "HTML", "Markdown"],
                            key="export_format_selection"
                        )
                        
                        include_citations = st.checkbox(
                            "Include citations",
                            value=True,
                            key="include_citations_checkbox"
                        )
                        
                        include_tables = st.checkbox(
                            "Include tables",
                            value=True,
                            key="include_tables_checkbox"
                        )
                        
                        include_figures = st.checkbox(
                            "Include figures",
                            value=True,
                            key="include_figures_checkbox"
                        )
                    
                    # Section selection
                    with col2:
                        st.markdown("### Sections to Include")
                        
                        include_abstract = st.checkbox(
                            "Abstract",
                            value=True,
                            key="include_abstract_checkbox"
                        )
                        
                        include_introduction = st.checkbox(
                            "Introduction",
                            value=True,
                            key="include_introduction_checkbox",
                            disabled=not saved_content.get("introduction", [])
                        )
                        
                        include_methods = st.checkbox(
                            "Methods",
                            value=True,
                            key="include_methods_checkbox",
                            disabled=not saved_content.get("methods", [])
                        )
                        
                        include_results = st.checkbox(
                            "Results",
                            value=True,
                            key="include_results_checkbox",
                            disabled=not saved_content.get("results", [])
                        )
                        
                        include_discussion = st.checkbox(
                            "Discussion",
                            value=True,
                            key="include_discussion_checkbox",
                            disabled=not saved_content.get("discussion", [])
                        )
                        
                        include_conclusion = st.checkbox(
                            "Conclusion",
                            value=True,
                            key="include_conclusion_checkbox",
                            disabled=not saved_content.get("conclusion", [])
                        )
                    
                    # Preview section
                    st.markdown("### Document Preview")
                    
                    # Create tabs for previewing each section
                    section_tabs = st.tabs(["Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion"])
                    
                    # Populate tabs with content
                    with section_tabs[0]:
                        if include_abstract:
                            st.markdown("#### Abstract")
                            # Abstract generation logic would go here
                            abstract_btn = st.button("Generate Abstract")
                            if abstract_btn:
                                with st.spinner("Generating abstract..."):
                                    # Placeholder for abstract generation API call
                                    st.session_state["generated_abstract"] = "This is a placeholder for the automatically generated abstract based on other sections."
                            
                            if "generated_abstract" in st.session_state:
                                st.text_area(
                                    "Edit abstract:",
                                    st.session_state["generated_abstract"],
                                    height=200,
                                    key="abstract_edit_area"
                                )
                        else:
                            st.info("Abstract section is not included in the export.")
                    
                    # Introduction tab
                    with section_tabs[1]:
                        if include_introduction and saved_content.get("introduction", []):
                            st.markdown("#### Introduction")
                            intro_content = "\n\n".join([item.get("assistant_response", "") 
                                                       for item in saved_content.get("introduction", [])])
                            st.markdown(intro_content)
                        else:
                            st.info("Introduction section is not included in the export or has no saved content.")
                    
                    # Methods tab
                    with section_tabs[2]:
                        if include_methods and saved_content.get("methods", []):
                            st.markdown("#### Methods")
                            methods_content = "\n\n".join([item.get("assistant_response", "") 
                                                         for item in saved_content.get("methods", [])])
                            st.markdown(methods_content)
                        else:
                            st.info("Methods section is not included in the export or has no saved content.")
                    
                    # Results tab
                    with section_tabs[3]:
                        if include_results and saved_content.get("results", []):
                            st.markdown("#### Results")
                            results_content = "\n\n".join([item.get("assistant_response", "") 
                                                         for item in saved_content.get("results", [])])
                            st.markdown(results_content)
                        else:
                            st.info("Results section is not included in the export or has no saved content.")
                    
                    # Discussion tab
                    with section_tabs[4]:
                        if include_discussion and saved_content.get("discussion", []):
                            st.markdown("#### Discussion")
                            discussion_content = "\n\n".join([item.get("assistant_response", "") 
                                                            for item in saved_content.get("discussion", [])])
                            st.markdown(discussion_content)
                        else:
                            st.info("Discussion section is not included in the export or has no saved content.")
                    
                    # Conclusion tab
                    with section_tabs[5]:
                        if include_conclusion and saved_content.get("conclusion", []):
                            st.markdown("#### Conclusion")
                            conclusion_content = "\n\n".join([item.get("assistant_response", "") 
                                                           for item in saved_content.get("conclusion", [])])
                            st.markdown(conclusion_content)
                        else:
                            st.info("Conclusion section is not included in the export or has no saved content.")
                    
                    # Export buttons
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col2:
                        export_btn = st.button("🔄 Export Document", type="primary", use_container_width=True)
                        
                        if export_btn:
                            with st.spinner(f"Generating {export_format} document..."):
                                # Prepare payload for export
                                export_payload = {
                                    'file_name': st.session_state.file_name,
                                    'format': export_format.lower(),
                                    'include_citations': include_citations,
                                    'include_tables': include_tables,
                                    'include_figures': include_figures,
                                    'sections': {
                                        'abstract': include_abstract and st.session_state.get("generated_abstract", ""),
                                        'introduction': include_introduction,
                                        'methods': include_methods,
                                        'results': include_results,
                                        'discussion': include_discussion,
                                        'conclusion': include_conclusion
                                    }
                                }
                                
                                # Call export API (placeholder)
                                # In a real implementation, this would call the API and handle the file download
                                
                                # Simulate success for demo
                                st.success(f"Document exported successfully as {export_format}!")
                                st.markdown(f"""
                                <div style="text-align: center; margin-top: 20px;">
                                    <a href="#" download="research_paper.{export_format.lower()}" 
                                       style="padding: 10px 20px; background-color: #0066CC; color: white; 
                                              text-decoration: none; border-radius: 4px;">
                                        Download Document
                                    </a>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.warning("No saved content found for export. Please generate and save content in the different sections first.")
            else:
                st.error("Failed to load saved content.")
        except Exception as e:
            st.error(f"An error occurred while loading content: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_introduction_tab():
    """Display the introduction section interface."""
    if not st.session_state.file_uploaded:
        st.warning("Please upload a document first to access the Introduction section.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Introduction Section")
    
    # Two tabs for different query types
    tab1, tab2 = st.tabs(["🔎 General Prompts", "💬 Custom Queries"])
    
    with tab1:
        show_introduction_general_prompts()
    
    with tab2:
        show_introduction_custom_queries()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_introduction_general_prompts():
    """Show introduction section's general prompts functionality."""
    st.markdown("## 🔹 General Introduction Prompts")
    st.markdown("These prompts help generate content for the introduction section.")
    
    # Define static prompts for introduction
    introduction_static_prompts = [
        "1. Please summarize the background context for this study in bullet points.",
        "2. What is the disease or condition being studied? Please provide an overview with epidemiology, pathophysiology, and current treatment options in bullet points.",
        "3. What gaps in knowledge or unmet needs does this study address? Please respond in bullet points.",
        "4. What are the primary and secondary objectives of this study? Please respond in bullet points.",
        "5. What is the hypothesis or research question being tested in this study? Please respond in bullet points.",
        "6. What is the rationale for the study design chosen? Please respond in bullet points.",
        "7. Please draft a comprehensive introduction paragraph that could be used in a clinical research paper based on this study."
    ]
    
    # Two column layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        introduction_static_prompt_selection = st.radio(
            "Select a general prompt:",
            introduction_static_prompts,
            key="static_prompt_selector_general_introduction"
        )
    
    with col2:
        # Display selected prompt in a code block
        st.code(introduction_static_prompt_selection, language="")
        
        # Thread dependency option
        introduction_dependent_general = st.checkbox(
            "Thread dependent",
            True,
            key="introduction_general_dependent_checkbox"
        )
        
        # Execute button
        if st.button("▶️ Execute Prompt", key="introduction_run_static_prompt"):
            run_introduction_general_prompt(introduction_static_prompt_selection, introduction_dependent_general)
    
    # Display and edit response
    if st.session_state.get("introduction_general_checkbox_response"):
        st.markdown("---")
        st.markdown("### 💬 AI Response")
        
        with st.expander("Edit Response", expanded=True):
            introduction_edited_general_response = st.text_area(
                "Edit AI response:",
                st.session_state["introduction_general_checkbox_response"],
                height=300,
                key="introduction_general_response_text"
            )
            
            if st.session_state.get("introduction_general_thread_id"):
                st.info(f"Thread ID: {st.session_state.introduction_general_thread_id}")
            
            # Citations display
            if st.session_state.get("introduction_general_checkbox_citations"):
                with st.expander("📚 Citations", expanded=False):
                    for i, citation in enumerate(st.session_state["introduction_general_checkbox_citations"]):
                        st.markdown(f"**Citation {i+1}:** {citation}")
            
            # Save button
            if st.button("💾 Save Response", key="save_introduction_general_response_button"):
                save_introduction_general_response(introduction_edited_general_response, introduction_static_prompt_selection)

def run_introduction_general_prompt(prompt, dependent):
    """Run an introduction general prompt."""
    st.session_state['introduction_general_user_query'] = prompt
    
    with st.spinner("Processing your query..."):
        try:
            payload = {
                "question": prompt,
                "file_name": st.session_state.file_name,
                "assistant_id": st.session_state.assistant_id,
                "vector_id": st.session_state.vector_id,
                "current_thread_id": st.session_state.get("introduction_general_thread_id"),
                "dependent": dependent,
            }
            
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                res = response.json()
                st.session_state["introduction_general_checkbox_response"] = res.get("response", "")
                st.session_state["introduction_general_checkbox_citations"] = res.get("citations", [])
                st.session_state["introduction_general_thread_id"] = res.get("thread_id")
                st.success("Query processed successfully!")
            else:
                st.error("Failed to process your query.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def save_introduction_general_response(edited_response, prompt):
    """Save the introduction general response."""
    with st.spinner("Saving your response..."):
        try:
            save_payload = {
                'file_name': st.session_state.file_name,
                'user_query': st.session_state.introduction_general_user_query,
                'assistant_response': edited_response,
                'citations': st.session_state.introduction_general_checkbox_citations,
                'thread_id': st.session_state.get("introduction_general_thread_id"),
                'selected_endpoint': None,
                'selected_category': prompt.split(".", 1)[0].strip()  # Extract prompt number/category
            }
            
            save_response = requests.post(f"{API_BASE_URL}/introduction/save_introduction_response", json=save_payload)
            
            if save_response.status_code == 200:
                st.success("Introduction response saved successfully!")
            else:
                st.error("Error saving introduction response.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def show_introduction_custom_queries():
    """Show introduction section's custom query chat interface."""
    st.markdown("## 💬 Custom Introduction Queries")
    st.markdown("Ask specific questions about the background or context of the study.")
    
    # Initialize thread ID for the introduction chat if not set
    if "introduction_chat_thread_id" not in st.session_state:
        st.session_state["introduction_chat_thread_id"] = ""
    
    # Thread dependency option
    dependent = st.checkbox(
        "Thread dependent (maintains conversation context)",
        value=True,
        key="introduction_chat_dependent_checkbox"
    )
    
    # Text input for custom query
    user_message = st.text_area(
        "Enter your query about the introduction/background:",
        key="introduction_custom_message",
        height=100,
        placeholder="e.g., What is the prevalence of this condition in the population?"
    )
    
    # Execute button
    if st.button("💬 Send Query", key="send_introduction_custom_message"):
        if user_message and st.session_state.file_uploaded:
            with st.spinner("Processing your query..."):
                try:
                    # Prepare payload
                    payload = {
                        'question': user_message,
                        'file_name': st.session_state.file_name,
                        'assistant_id': st.session_state.assistant_id,
                        'vector_id': st.session_state.vector_id,
                        'thread_id': st.session_state["introduction_chat_thread_id"],
                        'dependent': dependent,
                    }
                    
                    # Send request
                    response = requests.post(f"{API_BASE_URL}/introduction/chat_introduction", json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state["introduction_chat_response"] = result.get("response", "")
                        st.session_state["introduction_chat_citations"] = result.get("citations", [])
                        st.session_state["introduction_chat_thread_id"] = result.get("thread_id", "")
                        
                        st.success("Response received!")
                    else:
                        error_message = response.json().get("error", "Failed to process the query.")
                        st.error(error_message)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            if not user_message:
                st.error("Please enter a query to send.")
            else:
                st.error("Please upload a paper first.")
    
    # Display response if available
    if st.session_state.get("introduction_chat_response"):
        st.markdown("---")
        st.markdown("### 💬 AI Response")
        
        with st.expander("Response", expanded=True):
            chat_response = st.text_area(
                "Edit response:",
                st.session_state["introduction_chat_response"],
                height=300,
                key="introduction_chat_response_text"
            )
            
            if st.session_state["introduction_chat_thread_id"]:
                st.info(f"Thread ID: {st.session_state['introduction_chat_thread_id']}")
            
            # Citations display
            if st.session_state.get("introduction_chat_citations"):
                with st.expander("📚 Citations", expanded=False):
                    for i, citation in enumerate(st.session_state["introduction_chat_citations"]):
                        st.markdown(f"**Citation {i+1}:** {citation}")
            
            # Save button
            if st.button("💾 Save Response", key="save_introduction_chat_response_button"):
                with st.spinner("Saving your response..."):
                    try:
                        save_payload = {
                            'file_name': st.session_state.file_name,
                            'user_query': user_message,
                            'assistant_response': chat_response,
                            'citations': st.session_state["introduction_chat_citations"],
                            'thread_id': st.session_state["introduction_chat_thread_id"]
                        }
                        
                        save_response = requests.post(f"{API_BASE_URL}/introduction/save_introduction_chat_response", json=save_payload)
                        
                        if save_response.status_code == 200:
                            st.success("Introduction chat response saved successfully!")
                        else:
                            st.error("Error saving introduction chat response.")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

# Main execution function
if __name__ == "__main__":
    main()
