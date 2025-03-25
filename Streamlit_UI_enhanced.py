import re
import streamlit as st
import requests
import json
import logging
import uuid
import ast
import hashlib
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Set page configuration with custom theme
st.set_page_config(
    page_title="Clinical Research Paper Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Custom CSS for better UI
st.markdown("""
    <style>
        /* Main title styling */
        .main-title {
            color: #1f77b4;
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            padding: 1rem;
            margin-bottom: 2rem;
        }
        
        /* Section headers */
        .section-header {
            color: #2c3e50;
            font-size: 1.8rem;
            font-weight: bold;
            padding: 0.5rem 0;
            border-bottom: 2px solid #3498db;
            margin-bottom: 1rem;
        }
        
        /* Card styling */
        .st-emotion-cache-1r6slb0 {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: #2980b9;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        /* Checkbox styling */
        .stCheckbox>label {
            color: #2c3e50;
            font-weight: 500;
        }
        
        /* Text input styling */
        .stTextInput>div>div>input {
            border-radius: 5px;
            border: 1px solid #bdc3c7;
        }
        
        /* Selectbox styling */
        .stSelectbox>div>div>select {
            border-radius: 5px;
            border: 1px solid #bdc3c7;
        }
        
        /* Success message styling */
        .stSuccess {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        
        /* Error message styling */
        .stError {
            background-color: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            margin: 0 0.5rem;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #3498db;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# API Base URL
API_BASE_URL = "http://localhost:5000/"

# Initialize session state variables with better organization
def initialize_session_state():
    # Core session states
    core_states = {
        "file_name": "",
        "assistant_id": "",
        "vector_id": "",
        "current_thread_id": "",
        "current_checkbox_thread_id": "",
        "user_query": "",
        "selected_bullet": None,
        "selected_category": None,
        "dependent": True,
        "checkbox_dependent": True,
        "last_upload_time": None,
        "session_id": str(uuid.uuid4()),
        "is_processing": False
    }
    
    # Response states
    response_states = {
        "response": "",
        "citations": [],
        "checkbox_response": "",
        "checkbox_citations": [],
        "edited_response": ""
    }
    
    # Section states
    sections = ["introduction", "methods", "discussion", "results", "conclusion"]
    section_states = {}
    for section in sections:
        section_states.update({
            section: "",
            f"{section}_thread_id": "",
            f"{section}_citations": [],
            f"{section}_prompt": "",
            f"{section}_chat": "",
            f"{section}_chat_citations": [],
            f"initialise_new_chat_for{section}_thread_id": "",
            f"initialise_new_chat_for_outside_{section}_thread_id": "",
            f"outside_{section}_thread_id": "",
            f"outside_{section}_citations": [],
            f"outside_{section}_prompt": "",
            f"outside_{section}_chat": "",
            f"outside_{section}_chat_citations": []
        })
    
    # Initialize all states
    for state_dict in [core_states, response_states, section_states]:
        for key, default_value in state_dict.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

initialize_session_state()

# Function to clear session state with better organization
def clear_session():
    st.session_state.clear()
    initialize_session_state()
    st.session_state.last_upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to show loading state
def show_loading():
    st.session_state.is_processing = True
    with st.spinner("Processing..."):
        st.empty()

def hide_loading():
    st.session_state.is_processing = False

# Title with custom styling
st.markdown('<h1 class="main-title">Clinical Research Paper Assistant</h1>', unsafe_allow_html=True)

# File Upload Section with better UI
st.markdown('<h2 class="section-header">📁 Upload File</h2>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a file to upload", type=["txt", "csv", "json", "pdf"])

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("Upload File", key="upload_button"):
        if uploaded_file is not None:
            try:
                show_loading()
                clear_session()
                
                files = {"file": uploaded_file}
                response = requests.post(f"{API_BASE_URL}/upload", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict):
                        st.session_state.file_name = uploaded_file.name
                        st.session_state.assistant_id = result.get("assistant_id", "")
                        st.session_state.vector_id = result.get("vector_store_id", "")
                        st.session_state.current_thread_id = result.get("thread_id", "")
                        st.session_state.last_upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        st.success("File uploaded successfully!")
                    else:
                        st.success("File processed successfully!")
                else:
                    st.error(response.json().get("error", "Failed to upload file."))
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                hide_loading()
        else:
            st.error("Please select a file to upload.")

# Metadata Section with better organization
st.markdown('<h2 class="section-header">📝 Session Metadata</h2>', unsafe_allow_html=True)
metadata_cols = st.columns(4)
with metadata_cols[0]:
    st.text_input("**File Name**", st.session_state.file_name, key="meta_file_name")
with metadata_cols[1]:
    st.text_input("**Assistant ID**", st.session_state.assistant_id, key="meta_assistant_id")
with metadata_cols[2]:
    st.text_input("**Vector ID**", st.session_state.vector_id, key="meta_vector_id")
with metadata_cols[3]:
    st.text_input("**Current Thread ID**", st.session_state.current_thread_id or "", key="meta_thread_id")

if st.session_state.last_upload_time:
    st.info(f"Last upload: {st.session_state.last_upload_time}")

# Query Section with enhanced UI
st.markdown('<h2 class="section-header">❓ Initiate a New General Query</h2>', unsafe_allow_html=True)
user_query = st.text_area("Enter your query", "", height=100)

col1, col2 = st.columns([3, 1])
with col1:
    dependent = st.checkbox("Dependent on thread", value=st.session_state.dependent)
    st.session_state.dependent = dependent
    get_dependent_status = lambda: "ON" if st.session_state.dependent else "OFF"
    st.info(f"Conversation Mode: {get_dependent_status()}")

with col2:
    if st.button("Ask Assistant", key="ask_assistant_button"):
        if user_query:
            try:
                show_loading()
                st.session_state.response = ""
                st.session_state.citations = []

                payload = {
                    "question": user_query,
                    "file_name": st.session_state.file_name,
                    "assistant_id": st.session_state.assistant_id,
                    "vector_id": st.session_state.vector_id,
                    "current_thread_id": st.session_state.current_thread_id or None,
                    "dependent": st.session_state.dependent,
                }
                
                response = requests.post(f"{API_BASE_URL}/query", json=payload)
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.current_thread_id = result.get("thread_id", None)
                    st.session_state.response = result.get("response", "")
                    st.session_state.citations = result.get("citations", [])
                    st.success("Assistant responded to your query!")
                else:
                    st.error(response.json().get("error", "Please upload the file to start your query"))
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                hide_loading()
        else:
            st.error("Please enter a query before asking.")

# Response Section with better formatting
if st.session_state.response:
    st.markdown('<h2 class="section-header">💬 Response</h2>', unsafe_allow_html=True)
    response_text = st.text_area("Response:", st.session_state.response, height=200, key="response_text")
    citations = st.session_state.citations

    if st.session_state.current_thread_id:
        st.info(f"**Thread ID:** {st.session_state.current_thread_id}")

    if st.button("Save Response", key="save_response_button"):
        try:
            show_loading()
            payload = {
                'file_name': st.session_state.file_name,
                'user_query': user_query,
                'assistant_response': response_text,
                'citations': citations,
                'thread_id': st.session_state.current_thread_id
            }
            
            save_response = requests.post(f"{API_BASE_URL}/save_response", json=payload)
            if save_response.status_code == 200:
                st.success("Response saved successfully!")
            else:
                st.error("Error saving response.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            hide_loading()

# Function to generate a unique key for each checkbox
def generate_unique_key(*args):
    return hashlib.md5("".join(map(str, args)).encode('utf-8')).hexdigest()

# Function to display endpoints with enhanced UI
def display_endpoints(name, item):
    stack = [(name, item)]
    while stack:
        current_name, current_item = stack.pop()
        
        if isinstance(current_item, dict):
            st.markdown(f'<h3 class="section-header">{current_name}</h3>', unsafe_allow_html=True)
            st.session_state.selected_category = current_name
            for sub_key, sub_value in current_item.items():
                if isinstance(sub_value, dict):
                    stack.append((f"{sub_key} (nested dictionary)", sub_value))
                elif isinstance(sub_value, list):
                    st.markdown(f'<h4 class="section-header">{sub_key} (list)</h4>', unsafe_allow_html=True)
                    for list_item in sub_value:
                        list_item_key = generate_unique_key(sub_key, list_item)
                        if st.checkbox(str(list_item), key=list_item_key):
                            st.session_state.selected_bullet = str(list_item)
                else:
                    sub_key_value_key = generate_unique_key(sub_key, sub_value)
                    if st.checkbox(f"{sub_key}: {sub_value}", key=sub_key_value_key):
                        st.session_state.selected_bullet = f"{sub_key}: {sub_value}"
                        
        elif isinstance(current_item, list):
            st.markdown(f'<h3 class="section-header">{current_name}</h3>', unsafe_allow_html=True)
            st.session_state.selected_category = current_name
            for list_item in current_item:
                list_item_key = generate_unique_key(current_name, list_item)
                if st.checkbox(str(list_item), key=list_item_key):
                    st.session_state.selected_bullet = str(list_item)
        
        else:
            base_key = generate_unique_key(current_name, current_item)
            if st.checkbox(f"{current_name}: {current_item}", key=base_key):
                st.session_state.selected_bullet = f"{current_name}: {current_item}"

# Reusable function to handle each section with enhanced UI
def handle_section(section_name, display_name):
    st.markdown(f'<h2 class="section-header">{display_name}</h2>', unsafe_allow_html=True)

    if section_name == "results":
        if st.button(f"Generate {display_name} with predefined prompts", key=f"generate_{section_name}"):
            if st.session_state.assistant_id and st.session_state.vector_id:
                try:
                    show_loading()
                    st.session_state[section_name] = ""
                    st.session_state[f"{section_name}_citations"] = []
                    
                    payload = {
                        'assistant_id': st.session_state.assistant_id,
                        'vector_id': st.session_state.vector_id
                    }

                    response = requests.post(f"{API_BASE_URL}/{section_name}/generate_results_of_checkbox_prompts", json=payload)

                    if response.status_code == 200:
                        result = response.json()
                        st.session_state[section_name] = result.get(section_name, "")
                        st.session_state[f"{section_name}_citations"] = result.get("citations", [])
                        st.session_state[f"{section_name}_thread_id"] = result.get("thread_id", None)
                        st.session_state[f"{section_name}_prompt"] = result.get(f"{section_name}_prompt", "")
                        st.success(f"{display_name} generated successfully!")
                    else:
                        st.error(response.json().get("error", f"Failed to generate {display_name.lower()}."))
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    hide_loading()
            else:
                st.error("Please upload your paper to generate this section.")

        if st.session_state[section_name]:
            edited_text = st.text_area(f"{display_name}:", st.session_state[section_name], key=f"text_{section_name}")

        if st.session_state[section_name]:
            response = st.session_state[section_name]

            match = re.search(r"endpoints = ({.*})", response, re.DOTALL)

            if match:
                endpoints_str = match.group(1)
                endpoints_dict = ast.literal_eval(endpoints_str)
                response_dict = endpoints_dict
            else:
                st.warning("No endpoints found in the response.")

            st.markdown('<h2 class="section-header">Endpoints</h2>', unsafe_allow_html=True)

            # Output the keys and their corresponding values
            for major_category, endpoints_dict in response_dict.items():
                display_endpoints(major_category, endpoints_dict)

            # Display prompt selection after all checkboxes
            if st.session_state.selected_bullet:
                st.info(f"Selected: {st.session_state.selected_bullet}")

                # Check if the selected category is 'safety' and display appropriate prompts
                is_safety_endpoint = st.session_state.selected_category.lower() == "safety"

                if is_safety_endpoint:
                    prompt_selection = st.selectbox(
                        "Select a Prompt for Safety Endpoint",
                        [
                            f"Prompt 1. Please can you describe the {st.session_state.selected_bullet} results relating to safety and tolerability. Referring to text and tables describing any safety or tolerability, please can you draft a paragraph describing these results and summarizing the data for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points. ",
                            
                            f"Prompt 2: Please can you provide  the following data for each study arm as a bulleted list, relating to safety and tolerability, if it is available:\n"
                            "1. Patient years of exposure\n"
                            "2. The number and proportion of patients reporting at least one:\n"
                            "    a. Adverse event\n"
                            "    b. Treatment-emergent adverse event\n"
                            "    c. Serious adverse event\n"
                            "    d. Adverse event resulting in study discontinuation\n"
                            "    e. Death\n"
                            "3. The number and proportion of patients reporting at least one: Severe adverse event (please note that serious adverse events are different from severe adverse events)",
                            
                            f"Prompt 3: For each study arm please can you provide details of the 10 most common treatment emergent adverse events. If an adverse event is common in any one arm please provide the numbers for that adverse event for all study arms.",
                            
                            f"Prompt 4: For each study arm please can you provide details of the serious adverse events that were reported. For each and every serious adverse event please provide the number and proportion of patients reporting it and provide a summary of the outcomes of the events.",
                            
                            f"Prompt 5: For each study arm please can you provide details of the adverse events leading to discontinuation that were reported. For each and every adverse event please provide the number and proportion of patients reporting it and provide a summary of the outcomes of the events."
                        ]
                    )
                else:
                    prompt_selection = st.selectbox(
                        "Select a Prompt",
                        [
                            f"Prompt 1: Please can you describe the results for the endpoint of {st.session_state.selected_bullet}. Refer to text and tables describing all analyses, please can you draft a paragraph describing this endpoint and summarizing the outcomes for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points",

                            f"Prompt 2: Please can you describe the results for any subgroup analyses of the endpoint of {st.session_state.selected_bullet}. Refer to text and tables describing all analyses, please can you draft a paragraph describing this endpoint and summarizing the outcomes for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points"
                        ]
                    )

                st.markdown("**Selected Prompt:**")
                st.markdown(prompt_selection)

                # Set user_query as the selected prompt
                st.session_state['user_query'] = prompt_selection

                col1, col2 = st.columns([2, 1])
                with col1:
                    checkbox_dependent = st.checkbox("Dependent on threads", value=st.session_state.checkbox_dependent)
                    st.session_state.checkbox_dependent = checkbox_dependent
                    get_checkbox_dependent_status = lambda: "ON" if st.session_state.checkbox_dependent else "OFF"
                    st.info(f"Conversation Mode: {get_checkbox_dependent_status()}")

                with col2:
                    if st.button("Run for selected prompts", key="run_prompts_button"):
                        checkbox_user_query = st.session_state.get('user_query', '')
                        
                        if checkbox_user_query:
                            try:
                                show_loading()
                                st.session_state["checkbox_response"] = ""
                                st.session_state["checkbox_citations"] = []

                                payload = {
                                    "question": checkbox_user_query,
                                    "file_name": st.session_state.file_name,
                                    "assistant_id": st.session_state.assistant_id,
                                    "vector_id": st.session_state.vector_id,
                                    "current_thread_id": st.session_state.current_checkbox_thread_id or None,
                                    "dependent": st.session_state.checkbox_dependent,
                                }
                                
                                response = requests.post(f"{API_BASE_URL}/query", json=payload)
                                if response.status_code == 200:
                                    result = response.json()
                                    st.session_state.current_checkbox_thread_id = result.get("thread_id", None)
                                    st.session_state["checkbox_response"] = result.get("response", "")
                                    st.session_state["checkbox_citations"] = result.get("citations", [])
                                    st.success("Assistant responded to your query!")
                                else:
                                    st.error(response.json().get("error", "Please upload the file to start your query"))
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                            finally:
                                hide_loading()
                        else:
                            st.error("Please enter a query before asking.")

                # Display editable text area for the query response
                if st.session_state["checkbox_response"]:
                    st.markdown('<h2 class="section-header">💬 Response</h2>', unsafe_allow_html=True)
                    response_text = st.text_area("Response:", st.session_state["checkbox_response"], height=200, key="checkbox_response_text")
                    citations = st.session_state["checkbox_citations"]

                    if st.session_state.current_checkbox_thread_id:
                        st.info(f"**Thread ID:** {st.session_state.current_checkbox_thread_id}")

                    if "user_query" in st.session_state and st.session_state["checkbox_response"]:
                        if st.button("Save Response", key="save_checkbox_response_button"):
                            try:
                                show_loading()
                                payload = {
                                    'file_name': st.session_state.file_name,
                                    'user_query': st.session_state.user_query,
                                    'assistant_response': st.session_state.checkbox_response,
                                    'citations': st.session_state.checkbox_citations,
                                    'thread_id': st.session_state.current_checkbox_thread_id
                                }
                                
                                save_response = requests.post(f"{API_BASE_URL}/save_checkbox_response", json=payload)
                                if save_response.status_code == 200:
                                    st.success("Response saved successfully!")
                                else:
                                    st.error("Error saving response.")
                            except Exception as e:
                                st.error(f"An error occurred: {e}")
                            finally:
                                hide_loading()

    # Chat Functionality with enhanced UI
    with st.expander(f"💬 Chat for {display_name}", expanded=False):
        user_message = st.text_input(f"Enter your message for the {display_name}:", key=f"user_message_outside_{section_name}")

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Send Message", key=f"send_message_outside_{section_name}"):
                if user_message and st.session_state.assistant_id and st.session_state.vector_id:
                    try:
                        show_loading()
                        payload = {
                            'assistant_id': st.session_state.assistant_id,
                            'vector_id': st.session_state.vector_id,
                            'thread_id': st.session_state[f'initialise_new_chat_for_outside_{section_name}_thread_id'],
                            'message': user_message
                        }

                        response = requests.post(f"{API_BASE_URL}/{section_name}/chat_{section_name}", json=payload)

                        if response.status_code == 200:
                            result = response.json()
                            st.session_state[f"outside_{section_name}_chat"] = result.get("response", "")
                            st.session_state[f"outside_{section_name}_chat_citations"] = result.get("citations", [])
                            st.session_state[f"initialise_new_chat_for_outside_{section_name}_thread_id"] = result.get("thread_id", None)
                            st.success("Message sent successfully!")
                        else:
                            st.error(response.json().get("error", "Failed to process the chat."))
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                    finally:
                        hide_loading()
                else:
                    st.error("Please upload your paper to send a message.")

        if st.session_state[f"outside_{section_name}_chat"]:
            chat_text = st.text_area(f"{display_name} Chat:", st.session_state[f"outside_{section_name}_chat"], key=f"chat_text_outside_{section_name}")
            chat_citations = st.session_state[f"{section_name}_chat_citations"]
            
            if st.session_state[f'initialise_new_chat_for_outside_{section_name}_thread_id']:
                st.info(f"Thread ID: {st.session_state[f'initialise_new_chat_for_outside_{section_name}_thread_id']}")

            if st.button(f"Save Chat", key=f"save_chat_outside_{section_name}"):
                try:
                    show_loading()
                    payload = {
                        'file_name': st.session_state.file_name,
                        'user_query': user_message,
                        'assistant_response': chat_text,
                        'citations': chat_citations,
                        'thread_id': st.session_state[f"initialise_new_chat_for_outside_{section_name}_thread_id"]
                    }
                    
                    save_response = requests.post(f"{API_BASE_URL}/{section_name}/save_outside_{section_name}_chat_response", json=payload)
                    if save_response.status_code == 200:
                        st.success(f"{display_name} Chat saved successfully!")
                    else:
                        st.error(f"Error saving {display_name.lower()} chat.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                finally:
                    hide_loading()

# Tabs for Document Sections with enhanced styling
st.markdown('<h2 class="section-header">📄 Document Sections</h2>', unsafe_allow_html=True)
tabs = st.tabs(["**Results**", "**Methods**", "**Introduction**", "**Discussion**", "**Conclusion**"])

sections = ["results", "methods", "introduction", "discussion", "conclusion"]
display_names = ["Results", "Methods", "Introduction", "Discussion", "Conclusion"]

for tab, section, display_name in zip(tabs, sections, display_names):
    with tab:
        handle_section(section, display_name) 