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
        --primary-color: #0066CC;
        --secondary-color: #00336A;
        --accent-color: #FFBB00;
        --light-bg: #F8F9FA;
        --dark-text: #333333;
        --light-text: #FFFFFF;
        --sidebar-bg: #0A4D94;
        --card-border: #E0E0E0;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --error-color: #dc3545;
    }
    
    /* Typography */
    html, body, [class*="css"] {
        font-family: 'Roboto', 'Segoe UI', 'Arial', sans-serif;
    }
    
    h1, h2, h3 {
        font-weight: 600;
        color: var(--secondary-color);
    }
    
    h1 {
        font-size: 2.2rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    h2 {
        font-size: 1.8rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.4rem !important;
        margin-top: 1rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Main containers */
    .main {
        background-color: var(--light-bg);
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-12oz5g7 {
        background-color: var(--sidebar-bg);
    }
    
    .sidebar-content {
        background-color: var(--light-bg);
        border-radius: 8px;
        padding: 20px;
        margin: 10px;
    }
    
    /* Cards for content sections */
    .card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border-left: 4px solid var(--primary-color);
    }
    
    /* Button styling */
    .stButton > button, div.stButton > button:hover, div.stButton > button:focus {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: white;
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 8px 12px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 1px var(--primary-color);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 5px 5px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Status messages */
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin-bottom: 20px;
    }
    
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin-bottom: 20px;
    }
    
    /* Custom checkbox styling */
    [data-testid="stCheckbox"] > label {
        font-weight: 500;
    }
    
    [data-testid="stCheckbox"] > div {
        background-color: white;
        border-radius: 4px;
    }
    
    /* Text area enhancements */
    .stTextArea textarea {
        border-radius: 6px;
        border: 1px solid #ccc;
        background-color: white;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 1px var(--primary-color);
    }
    
    /* Custom tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: var(--dark-text);
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Divider with text */
    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 20px 0;
    }
    
    .divider::before, .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #ced4da;
    }
    
    .divider span {
        padding: 0 10px;
        color: #6c757d;
        font-size: 0.9rem;
    }
    
    /* Citations styling */
    .citation-box {
        background-color: #f8f9fa;
        border-left: 3px solid var(--primary-color);
        padding: 10px;
        margin-top: 10px;
        border-radius: 0 5px 5px 0;
        font-size: 0.9rem;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: var(--primary-color);
    }

    /* Logo and header styling */
    .logo-img {
        max-width: 50px;
        margin-right: 10px;
    }
    
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    
    /* For endpoint selection highlight */
    .selected-endpoint {
        background-color: rgba(0, 102, 204, 0.1);
        border-radius: 4px;
        padding: 5px;
        border-left: 3px solid var(--primary-color);
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
        st.markdown("""
        <div class="header-container">
            <img src="https://img.icons8.com/color/96/000000/health-data.png" class="logo-img">
            <h2>CRP Assistant</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sidebar navigation
        nav_options = ["Upload Paper", "Results", "Methods", "Conclusion", "Introduction", "Discussion", "Export Document"]
        
        for i, option in enumerate(nav_options):
            if st.sidebar.button(f"{option}", key=f"nav_{i}"):
                st.session_state.active_tab = i
        
        st.markdown("---")
        
        # Session information in sidebar
        if st.session_state.file_uploaded:
            st.sidebar.markdown("### Session Information")
            st.sidebar.markdown(f"**File:** {st.session_state.file_name}")
            st.sidebar.markdown(f"**Assistant ID:** {st.session_state.assistant_id[:10]}...")
            st.sidebar.markdown(f"**Vector ID:** {st.session_state.vector_id[:10]}...")
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.markdown("© 2023 Clinical Research Paper Assistant")
    
    # Main content area
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
    """Display the file upload screen."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.markdown("""
    # Clinical Research Paper Assistant
    
    This tool helps you analyze clinical research papers and generate structured content for various sections.
    """)
    
    st.markdown("""
    <div class="divider">
        <span>UPLOAD YOUR DOCUMENT</span>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload with drop area styling
    st.markdown("""
    <style>
        [data-testid="stFileUploader"] {
            padding: 2rem;
            border: 2px dashed #0066CC;
            border-radius: 8px;
            background-color: rgba(0, 102, 204, 0.05);
            margin-bottom: 20px;
        }
        .upload-text {
            text-align: center;
            color: #6c757d;
            margin-bottom: 10px;
        }
    </style>
    <div class="upload-text">
        Drag and drop your file here or browse
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a file to upload", type=["txt", "csv", "json", "pdf"], label_visibility="collapsed")
    
    # Upload button area with two columns for better layout
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        upload_button = st.button("🚀 Process Document", type="primary", use_container_width=True)
    
    # Processing logic
    if upload_button and uploaded_file is not None:
        with st.spinner("Processing your document... This may take a moment."):
            try:
                # Clear session state before uploading a new file
                clear_session()
                
                # Create progress bar
                progress_bar = st.progress(0)
                
                # Upload the file
                files = {"file": uploaded_file}
                response = requests.post(f"{API_BASE_URL}/upload", files=files)
                progress_bar.progress(50)
                
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
                            <strong>Success!</strong> Your document has been processed. Navigate to the different sections using the sidebar.
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Metadata display
                        st.markdown("### Document Metadata")
                        metadata_col1, metadata_col2 = st.columns(2)
                        with metadata_col1:
                            st.markdown(f"**Filename:** {st.session_state.file_name}")
                            st.markdown(f"**Status:** Ready for analysis")
                        with metadata_col2:
                            st.markdown(f"**Upload Time:** {result.get('upload_time', 'Now')}")
                            st.markdown(f"**File Size:** {uploaded_file.size / 1024:.2f} KB")
                    else:
                        st.success("File processed successfully!")
                else:
                    # Error message
                    st.markdown("""
                    <div class="error-box">
                        <strong>Error!</strong> Failed to process document. Please try again.
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                # Error message
                st.markdown(f"""
                <div class="error-box">
                    <strong>Error:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)
    elif upload_button and uploaded_file is None:
        # Warning for no file
        st.markdown("""
        <div class="error-box">
            <strong>Warning!</strong> Please select a file to upload.
        </div>
        """, unsafe_allow_html=True)
    
    # Information cards at the bottom
    st.markdown("""
    <div class="divider">
        <span>HOW IT WORKS</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; height: 200px;">
            <h3 style="color: #0066CC;">📤 Upload</h3>
            <p>Upload your clinical research paper. We support PDF, TXT, CSV, and JSON formats.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; height: 200px;">
            <h3 style="color: #0066CC;">🔍 Analyze</h3>
            <p>Our AI assistant will analyze the document and extract key information for each section.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; height: 200px;">
            <h3 style="color: #0066CC;">📝 Generate</h3>
            <p>Generate structured content for introduction, methods, results, discussion, and conclusion sections.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_results_tab():
    """Display the results section interface."""
    if not st.session_state.file_uploaded:
        st.warning("Please upload a document first to access the Results section.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Results Section")
    
    # Generate endpoints button
    if st.button("🔍 Generate Endpoints", key="generate_results_endpoints", type="primary"):
        with st.spinner("Generating endpoints... This may take a moment."):
            if st.session_state.assistant_id and st.session_state.vector_id:
                try:
                    # Clear previous data for the section
                    st.session_state["results"] = ""
                    st.session_state["results_citations"] = []
                    
                    # Prepare the payload
                    payload = {
                        'assistant_id': st.session_state.assistant_id,
                        'vector_id': st.session_state.vector_id
                    }
                    
                    # Send the request to the backend
                    response = requests.post(f"{API_BASE_URL}/results/generate_results_of_checkbox_prompts", json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state["results"] = result.get("results", "")
                        st.session_state["results_citations"] = result.get("citations", [])
                        st.session_state["results_thread_id"] = result.get("thread_id", None)
                        st.session_state["results_prompt"] = result.get("results_prompt", "")
                        
                        st.success("Endpoints generated successfully!")
                    else:
                        error_message = response.json().get("error", "Failed to generate results.")
                        st.error(error_message)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.error("Please upload your paper to generate this section.")
    
    # If we have results data
    if st.session_state["results"]:
        # Parse and display endpoints
        try:
            response = st.session_state["results"]
            
            # Try matching either 'endpoints = {...}' or just a raw dictionary
            match = re.search(r"endpoints\s*=\s*({.*})", response, re.DOTALL)
            if not match:
                match = re.search(r"({\s*['\"]primary['\"].*})", response, re.DOTALL)
            
            if match:
                endpoints_str = match.group(1)
                try:
                    # Convert the string representation to a Python dictionary
                    endpoints_dict = ast.literal_eval(endpoints_str)
                    
                    # Create tabs for different endpoint categories
                    endpoint_tabs = list(endpoints_dict.keys())
                    
                    tab1, tab2 = st.tabs(["📊 Endpoints", "🔎 General Queries"])
                    
                    with tab1:
                        # Display endpoints in a more structured way
                        st.markdown("### Available Endpoints")
                        
                        # Two column layout
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            # Category selection
                            selected_category = st.radio(
                                "Select Category",
                                endpoint_tabs,
                                key="results_category_selector"
                            )
                        
                        with col2:
                            # Display endpoints for the selected category
                            if selected_category:
                                st.markdown(f"#### {selected_category} Endpoints")
                                
                                endpoints_list = endpoints_dict[selected_category]
                                
                                # Process and display the endpoints
                                if isinstance(endpoints_list, dict):
                                    for key, value in endpoints_list.items():
                                        process_endpoint_item(key, value, selected_category)
                                elif isinstance(endpoints_list, list):
                                    for item in endpoints_list:
                                        endpoint_key = generate_unique_key(selected_category, item)
                                        if st.checkbox(str(item), key=endpoint_key):
                                            st.session_state["selected_bullet"] = str(item)
                                            st.session_state["selected_category"] = selected_category
                                            show_prompt_selection(selected_category == "safety")
                        
                        # Show response area if we have a selected endpoint
                        if st.session_state.get("checkbox_response"):
                            st.markdown("---")
                            st.markdown("### 💬 AI Response")
                            
                            with st.expander("Edit Response", expanded=True):
                                response_text = st.text_area(
                                    "Edit AI response:",
                                    st.session_state["checkbox_response"],
                                    height=300,
                                    key="checkbox_response_text"
                                )
                                
                                if st.session_state.current_checkbox_thread_id:
                                    st.info(f"Thread ID: {st.session_state.current_checkbox_thread_id}")
                                
                                # Citations display
                                if st.session_state.get("checkbox_citations"):
                                    with st.expander("📚 Citations", expanded=False):
                                        for i, citation in enumerate(st.session_state["checkbox_citations"]):
                                            st.markdown(f"**Citation {i+1}:** {citation}")
                                
                                # Save button for the response
                                if st.button("💾 Save Response", key="save_checkbox_response_button"):
                                    save_endpoint_response(response_text)
                    
                    with tab2:
                        show_general_results_queries()
                
                except Exception as e:
                    st.error(f"Error parsing endpoints: {e}")
            else:
                st.warning("No endpoints found in the response. Please try generating endpoints again.")
        except Exception as e:
            st.error(f"Error processing results: {e}")

def process_endpoint_item(key, value, selected_category):
    """Process and display endpoint items."""
    if isinstance(value, dict):
        # It's a dictionary, we'll create an expandable section
        with st.expander(f"{key}"):
            for sub_key, sub_value in value.items():
                process_endpoint_item(sub_key, sub_value, selected_category)
    elif isinstance(value, list):
        # It's a list, we'll create bullet points
        with st.expander(f"{key}"):
            for item in value:
                item_key = generate_unique_key(key, item)
                if st.checkbox(str(item), key=item_key):
                    st.session_state["selected_bullet"] = str(item)
                    st.session_state["selected_category"] = selected_category
                    show_prompt_selection(selected_category == "safety")
    else:
        # It's a leaf node, create a checkbox
        item_key = generate_unique_key(key, value)
        if st.checkbox(f"{key}: {value}", key=item_key):
            st.session_state["selected_bullet"] = f"{key}: {value}"
            st.session_state["selected_category"] = selected_category
            show_prompt_selection(selected_category == "safety")

def show_prompt_selection(is_safety_endpoint):
    """Display the prompt selection interface."""
    st.markdown("---")
    st.markdown("### 📝 Prompt Selection")
    
    selected_bullet = st.session_state["selected_bullet"]
    selected_category = st.session_state["selected_category"]
    
    st.markdown(f"""
    <div class="selected-endpoint">
        <strong>Selected endpoint:</strong> {selected_bullet}
    </div>
    """, unsafe_allow_html=True)
    
    # Different prompts for safety vs. regular endpoints
    if is_safety_endpoint:
        prompt_options = [
            f"1. Please can you describe the {selected_bullet} results relating to safety and tolerability. Referring to text and tables describing any safety or tolerability, please can you draft a paragraph describing these results and summarizing the data for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points. ",
            
            f"""2. Please can you provide the following data for each study arm as a bulleted list, relating to safety and tolerability, if it is available:
                1. Patient years of exposure
                2. The number and proportion of patients reporting at least one:
                    a. Adverse event
                    b. Treatment-emergent adverse event
                    c. Serious adverse event
                    d. Adverse event resulting in study discontinuation
                    e. Death
                3. The number and proportion of patients reporting at least one: Severe adverse event (please note that serious adverse events are different from severe adverse events)""",
                
            f"3. For each study arm please can you provide details of the 10 most common treatment emergent adverse events. If an adverse event is common in any one arm please provide the numbers for that adverse event for all study arms.",
            
            f"4. For each study arm please can you provide details of the serious adverse events that were reported. For each and every serious adverse event please provide the number and proportion of patients reporting it and provide a summary of the outcomes of the events.",
            
            f"5. For each study arm please can you provide details of the adverse events leading to discontinuation that were reported. For each and every adverse event please provide the number and proportion of patients reporting it and provide a summary of the outcomes of the events.",
            
            f"6. Please can you describe the results relating to adverse events resulting in death. Referring to text and tables describing any safety or tolerability, please can you draft a paragraph describing this endpoint and summarizing causes. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points."
        ]
    else:
        prompt_options = [
            f"1. Please can you describe the results for the endpoint of {selected_bullet}. Refer to text and tables describing all analyses, please can you draft a paragraph describing this endpoint and summarizing the outcomes for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points",
            
            f"2. For the endpoint {selected_bullet}, please provide a list of any subgroups the endpoint was evaluated in. Please can you provide the output as bullet points.",
            
            f"3. Please can you describe the results for any subgroup analyses of the endpoint of {selected_bullet}. Refer to text and tables describing all analyses, please can you draft a paragraph describing this endpoint and summarizing the outcomes for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points"
        ]
    
    # Prompt selection dropdown
    prompt_selection = st.selectbox(
        "Select a prompt template:",
        prompt_options,
        key="results_prompt_selector"
    )
    
    # Display the selected prompt in a code block for better visibility
    st.code(prompt_selection, language="")
    
    # Thread dependency option
    checkbox_dependent = st.checkbox(
        "Thread dependent (maintains conversation context)",
        value=True,
        key="results_thread_dependency"
    )
    st.session_state["checkbox_dependent"] = checkbox_dependent
    
    # Execute button
    if st.button("▶️ Execute Prompt", key="execute_results_prompt"):
        run_endpoint_prompt(prompt_selection, checkbox_dependent)

def run_endpoint_prompt(prompt, dependent):
    """Run the selected endpoint prompt."""
    # Store the prompt in session state
    st.session_state['user_query'] = prompt
    
    # Store the current selection to restore later
    temp_selected_bullet = st.session_state["selected_bullet"]
    temp_selected_category = st.session_state["selected_category"]
    
    with st.spinner("Processing your query..."):
        try:
            # Clear previous response and citations
            st.session_state["checkbox_response"] = ""
            st.session_state["checkbox_citations"] = []
            
            # Prepare payload
            payload = {
                "question": prompt,
                "file_name": st.session_state.file_name,
                "assistant_id": st.session_state.assistant_id,
                "vector_id": st.session_state.vector_id,
                "current_thread_id": st.session_state.current_checkbox_thread_id or None,
                "dependent": dependent, 
            }
            
            # Send request
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                assistant_response = result.get("response", "")
                citations = result.get("citations", [])
                thread_id = result.get("thread_id", None)
                
                # Update session state
                st.session_state.current_checkbox_thread_id = thread_id
                st.session_state["checkbox_response"] = assistant_response
                st.session_state["checkbox_citations"] = citations
                
                # Restore selections
                st.session_state["selected_bullet"] = temp_selected_bullet
                st.session_state["selected_category"] = temp_selected_category
                
                st.success("Query processed successfully!")
            else:
                # Restore selections on error
                st.session_state["selected_bullet"] = temp_selected_bullet
                st.session_state["selected_category"] = temp_selected_category
                st.error(response.json().get("error", "Please upload the file to start your query"))
        except Exception as e:
            # Restore selections on exception
            st.session_state["selected_bullet"] = temp_selected_bullet
            st.session_state["selected_category"] = temp_selected_category
            st.error(f"Error: {str(e)}")

def save_endpoint_response(response_text):
    """Save the edited endpoint response."""
    with st.spinner("Saving your response..."):
        try:
            payload = {
                'file_name': st.session_state.file_name,
                'user_query': st.session_state.user_query,
                'assistant_response': response_text,
                'citations': st.session_state.checkbox_citations,
                'thread_id': st.session_state.current_checkbox_thread_id,
                'selected_bullet': st.session_state.selected_bullet,
                'selected_category': st.session_state.selected_category
            }
            
            save_response = requests.post(f"{API_BASE_URL}/save_endpoint_response", json=payload)
            
            if save_response.status_code == 200:
                st.success("Response saved successfully!")
            else:
                st.error(f"Error saving response: {save_response.json().get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def show_general_results_queries():
    """Display the general queries interface for results."""
    st.markdown("### 🔎 General Results Queries")
    st.markdown("These queries provide general information about the clinical trial results.")
    
    # Define general prompts
    general_prompts = {
        "1. Describe overall trial population": "You are writing a clinical trial paper for publication in a medical journal. Please write a paragraph providing a concise overview of the trial population and their demographics and clinical characteristics. Refer to specific tables where relevant. Do not evaluate or interpret the data. Please provide the information as bullet points.",
        
        "2. Identifying any subgroups": "You are writing a clinical trial paper for publication in a medical journal. Looking at the methods and results sections, please can you identify whether any subgroups of patients were evaluated during this trial. Please can you list any subgroups as a bulleted list.",
        
        "3. Summarize the study design": "You are writing a clinical trial paper for publication in a medical journal. Refer to text and tables describing subject disposition. Please describe the number of patients who completed the trial and the number who discontinued the drug, including the reasons for discontinuation. Please also describe any dose changes. Refer to specific tables where relevant. Please provide the output as bullet points",
        
        "4. Describe overall study 'flow'": "You are writing a clinical trial paper for publication in a medical journal. Refer to text and tables describing subject disposition. Please describe the number of patients who completed the trial and the number who discontinued the drug, including the reasons for discontinuation. Please also describe any dose changes. Refer to specific tables where relevant. Please provide the output as bullet points",
        
        "5. If a CONSORT diagram is needed": """For the study please can you provide the following details:
            - Number of people assessed for eligibility
            - Number of people randomized to treatment
            - Of those not randomized the number of people who did not meet the inclusion criteria and the number who declined to participate
            - Then for each study arm:
                1. Number allocated
                2. Number who received the intervention
                3. Number who did not and why
                4. Number lost to follow-up
                5. Number who discontinued treatment
                6. Reasons for discontinuation
                7. Number included in analysis
                8. Number not included and reasons
        """,
        
        "6. Create CONSORT flow diagram": "Create a consort diagram flow chart for this clinical trial details.",
        
        "7.a Describe study treatment (Prompt 1)": "Please can you describe how many people received at least one dose of the investigational treatment, and the number who completed each treatment period. Please can you describe the completion rates for each treatment period and the number and proportion of participants in each treatment arm who discontinued treatment. Please can you also describe the most common reasons for discontinuation and the number in each arm who discontinued for each cause. Please can you also describe any deaths during the study and the connection of any deaths with the treatment received. Please provide teh output as bullet points",
        
        "7.b Describe study treatment (Prompt 2)": "Refer to text and tables describing study duration. Write a paragraph describing the mean actual duration of treatment for each study arm. Please also include the study dates, including first patient first visit and last patient last visit. Refer to specific tables where relevant. Please provide teh output as bullet points"
    }
    
    # Two-column layout for prompt selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_prompt_label = st.radio(
            "Select a general prompt:",
            list(general_prompts.keys()),
            key="static_prompt_selector_general_results"
        )
    
    with col2:
        selected_prompt_text = general_prompts[selected_prompt_label]
        st.code(selected_prompt_text, language="")
        
        dependent_general = st.checkbox(
            "Thread dependent",
            True,
            key="general_results_dependent_checkbox"
        )
        
        if st.button("▶️ Execute", key="run_general_prompt_button"):
            run_general_prompt(selected_prompt_label, selected_prompt_text, dependent_general)
    
    # Display response if available
    if st.session_state.get("general_results_prompt_response"):
        st.markdown("---")
        st.markdown("### 💬 AI Response")
        
        with st.expander("Edit Response", expanded=True):
            edited_response = st.text_area(
                "Edit response:",
                st.session_state["general_results_prompt_response"],
                height=300,
                key="general_results_response_text"
            )
            
            # Display citations
            if st.session_state.get("general_results_prompt_citations"):
                with st.expander("📚 Citations", expanded=False):
                    for i, citation in enumerate(st.session_state.general_results_prompt_citations):
                        st.markdown(f"**Citation {i+1}:** {citation}")
            
            # Save button
            if st.button("💾 Save Response", key="save_general_prompt_results_response_button"):
                save_general_prompt_response(edited_response, selected_prompt_label)
        
        # Special handling for subgroup identification (Prompt 2)
        if selected_prompt_label.startswith("2.") and st.session_state.get("subgroup_response_text"):
            show_subgroup_details()

def run_general_prompt(prompt_label, prompt_text, dependent):
    """Run a general results prompt."""
    st.session_state['user_query'] = prompt_text
    
    with st.spinner("Processing your query..."):
        payload = {
            "question": prompt_text,
            "file_name": st.session_state.file_name,
            "assistant_id": st.session_state.assistant_id,
            "vector_id": st.session_state.vector_id,
            "current_thread_id": st.session_state.current_method_checkbox_thread_id or None,
            "dependent": dependent,
        }
        
        response = requests.post(f"{API_BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            res = response.json()
            thread_id = res.get("thread_id")
            response_text = res.get("response", "")
            citations = res.get("citations", [])
            
            st.session_state["general_results_prompt_response"] = response_text
            st.session_state["general_results_prompt_citations"] = citations
            st.session_state.current_method_checkbox_thread_id = thread_id
            
            # Save subgroup data if prompt 2
            if prompt_label.startswith("2."):
                st.session_state["subgroup_response_text"] = response_text
            
            st.success("Query processed successfully!")
        else:
            st.error("Failed to process your query.")

def save_general_prompt_response(edited_response, prompt_label):
    """Save the general prompt response."""
    with st.spinner("Saving your response..."):
        try:
            save_payload = {
                'file_name': st.session_state.file_name,
                'user_query': st.session_state.user_query,
                'assistant_response': edited_response,
                'citations': st.session_state.get("general_results_prompt_citations", []),
                'thread_id': st.session_state.current_method_checkbox_thread_id,
                'selected_endpoint': None,
                'selected_category': prompt_label
            }
            
            save_response = requests.post(f"{API_BASE_URL}/results/save_general_prompt_results_response", json=save_payload)
            
            if save_response.status_code == 200:
                st.success("Response saved successfully!")
            else:
                st.error("Failed to save response.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def show_subgroup_details():
    """Show subgroup details options (when Prompt 2 was selected)."""
    st.markdown("### 👥 Subgroups Identified")
    
    # Extract list items from bullet points
    subgroups = [
        line.strip("-• ").strip()
        for line in st.session_state["subgroup_response_text"].splitlines()
        if line.strip().startswith(("-", "•"))
    ]
    
    # Create a multiselect for choosing subgroups
    with st.expander("Select subgroups to describe", expanded=True):
        selected_subgroups = []
        
        # Display checkboxes for each subgroup
        for subgroup in subgroups:
            if st.checkbox(subgroup, key=f"subgroup_checkbox_{subgroup}"):
                selected_subgroups.append(subgroup)
        
        if selected_subgroups:
            sub_str = ", ".join(selected_subgroups)
            prompt_3 = f"Please write a paragraph providing a concise overview of the Subgroup of {sub_str} and their demographics and clinical characteristics. Refer to specific tables where relevant. Do not evaluate or interpret the data. Please provide the information as bullet points"
            
            st.markdown('<h4 style="color:var(--primary-color);">Prompt for selected subgroups:</h4>', unsafe_allow_html=True)
            st.code(prompt_3, language="")
            
            if st.button("▶️ Execute Subgroup Analysis", key="run_prompt_3_button"):
                with st.spinner("Analyzing selected subgroups..."):
                    payload = {
                        "question": prompt_3,
                        "file_name": st.session_state.file_name,
                        "assistant_id": st.session_state.assistant_id,
                        "vector_id": st.session_state.vector_id,
                        "current_thread_id": st.session_state.current_method_checkbox_thread_id or None,
                        "dependent": True,
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/query", json=payload)
                    
                    if response.status_code == 200:
                        res = response.json()
                        st.session_state["prompt_3_response"] = res.get("response", "")
                        st.session_state["general_results_prompt_citations"] = res.get("citations", [])
                        st.success("Subgroup analysis complete!")
                    else:
                        st.error("Failed to analyze subgroups.")
    
    # Show subgroup analysis response
    if st.session_state.get("prompt_3_response"):
        st.markdown("### 💬 Subgroup Analysis")
        
        with st.expander("Edit Subgroup Analysis", expanded=True):
            edited_response_3 = st.text_area(
                "Edit subgroup description:",
                st.session_state["prompt_3_response"],
                height=300,
                key="subgroup_description_text"
            )
            
            if st.button("💾 Save Subgroup Analysis", key="save_prompt_3_response"):
                with st.spinner("Saving subgroup analysis..."):
                    try:
                        save_payload = {
                            'file_name': st.session_state.file_name,
                            'user_query': prompt_3,
                            'assistant_response': edited_response_3,
                            'citations': st.session_state.get("general_results_prompt_citations", []),
                            'thread_id': st.session_state.current_method_checkbox_thread_id,
                            'selected_endpoint': None,
                            'selected_category': selected_subgroups
                        }
                        
                        save_response = requests.post(f"{API_BASE_URL}/results/save_general_prompt_results_response", json=save_payload)
                        
                        if save_response.status_code == 200:
                            st.success("Subgroup analysis saved successfully!")
                        else:
                            st.error("Failed to save subgroup analysis.")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

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
