import re
import streamlit as st
import requests
import json
import logging
import streamlit as st
import uuid
import ast
import hashlib

import os
from dotenv import load_dotenv
load_dotenv()


# Set page configuration
st.set_page_config(
    page_title="CRP",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Custom CSS to apply styles
st.markdown("""
    <style>
        /* Apply custom font-family, font-size, and color */
        .st-emotion-cache-wq5ihp {
            font-family: "Source Sans Pro", sans-serif;
            font-size: 1.3rem;
            color: inherit;
        }
    </style>
""", unsafe_allow_html=True)

# API Base URL
API_BASE_URL = "http://localhost:5000/"

# Initialize session state variables
def initialize_session_state():
    default_sections = ["introduction", "methods", "discussion", "results", "conclusion"]
    
    # General session states
    for key in ["file_name", "assistant_id", "vector_id", "current_thread_id", "current_checkbox_thread_id", "edited_response", "response", "citations", "checkbox_response", "checkbox_citations", "dependent", "checkbox_dependent", "user_query", "selected_bullet", "selected_category"]:
        if key not in st.session_state:
            if key in ["dependent", "checkbox_dependent"]:
                st.session_state[key] = True
            else:
                st.session_state[key] = "" if key not in ["selected_bullet", "selected_category"] else None
    
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
    for key in ["selected_queries_outside", "selected_responses_outside", "results_outside", "final_edited_responses_outside", "view_final_edited_outside", "show_results", "show_selected_query", "assistant_response"]:
        if key not in st.session_state:
            if key == "view_final_edited_outside":
                st.session_state[key] = False
            else:
                st.session_state[key] = []

initialize_session_state()

# Function to clear session state when a new file is uploaded
def clear_session():
    # General session states to clear
    for key in ["file_name", "assistant_id", "vector_id", "current_thread_id", "current_checkbox_thread_id", "edited_response", "response", "citations", "checkbox_response", "checkbox_citations", "dependent", "checkbox_dependent", "user_query", "selected_bullet", "selected_category"]:
        if key in ["dependent", "checkbox_dependent"]:
            st.session_state[key] = True
        else:
            st.session_state[key] = "" if key not in ["selected_bullet", "selected_category"] else None
    
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
    for key in ["selected_queries_outside", "selected_responses_outside", "results_outside", "final_edited_responses_outside", "view_final_edited_outside", "show_results", "show_selected_query", "assistant_response"]:
        if key in st.session_state:
            if key == "view_final_edited_outside":
                st.session_state[key] = False
            else:
                st.session_state[key] = []

# Title and Instructions
st.title("CLINICAL RESEARCH PAPER")

# File Upload Section
st.header("📁 Upload File")
uploaded_file = st.file_uploader("Choose a file to upload", type=["txt", "csv", "json", "pdf"])

col1, col2 = st.columns([3, 1])
with col1:
    pass  # Placeholder for alignment
with col2:
    if st.button("Upload File"):
        if uploaded_file is not None:
            try:
                # Clear session state before uploading a new file
                clear_session()

                files = {"file": uploaded_file}
                response = requests.post(f"{API_BASE_URL}/upload", files=files)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict):
                        st.success(result.get("message", "File uploaded successfully!"))
                        # Pre-fill session metadata fields from the response
                        st.session_state.file_name = uploaded_file.name
                        st.session_state.assistant_id = result.get("assistant_id", "")
                        st.session_state.vector_id = result.get("vector_store_id", "")
                        st.session_state.current_thread_id = result.get("thread_id", "")
                    else:
                        st.success("File processed successfully!")
                else:
                    st.error(response.json().get("error", "Failed to upload file."))
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.error("Please select a file to upload.")

# Metadata Input Section
st.header("📝 Session Metadata")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.text_input("**File Name**", st.session_state.file_name, key="meta_file_name")
with col2:
    st.text_input("**Assistant ID**", st.session_state.assistant_id, key="meta_assistant_id")
with col3:
    st.text_input("**Vector ID**", st.session_state.vector_id, key="meta_vector_id")
with col4:
    st.text_input("**Current Thread ID**", st.session_state.current_thread_id or "", key="meta_thread_id")

# User Input: Query Section
st.header("❓  Initiate a New General Query")
user_query = st.text_area("Enter your query", "", height=100)

dependent = st.checkbox("Dependent on thread", value=True)
st.session_state["dependent"] = dependent

get_dependent_status = lambda: "ON" if st.session_state['dependent'] else "OFF"
st.write(f"Conversation: {get_dependent_status()}")

if st.button("Ask Assistant"):
    if user_query:
        try:
            st.session_state["response"] = ""
            st.session_state["citations"] = []

            payload = {
                "question": user_query,
                "file_name": st.session_state.file_name,
                "assistant_id": st.session_state.assistant_id,
                "vector_id": st.session_state.vector_id,
                "current_thread_id": st.session_state.current_thread_id or None,
                "dependent": st.session_state["dependent"], 
            }
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            if response.status_code == 200:
                result = response.json()
                assistant_response = result.get("response", "")
                citations = result.get("citations", [])
                thread_id = result.get("thread_id", None)

                st.session_state.current_thread_id = thread_id
                st.session_state["response"] = assistant_response
                st.session_state["citations"] = citations

                st.success("Assistant responded to your query!")
            else:
                st.error(response.json().get("error", "Please upload the file to start your query"))
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter a query before asking.")

# Display editable text area for the query response
if "response" in st.session_state and st.session_state["response"]:
    st.header("💬 Response")
    response_text = st.text_area("Response:", st.session_state["response"], height=200, key="response_text")
    citations = st.session_state["citations"]

    if st.session_state.current_thread_id:
        st.markdown(f"**Thread ID:** {st.session_state.current_thread_id}")

    # Save Response Button
    if st.button("Save Response"):
        payload = {
            'file_name': st.session_state.file_name,
            'user_query': user_query,
            'assistant_response': response_text,
            'citations': citations,
            'thread_id': st.session_state.current_thread_id
        }
        try:
            save_response = requests.post(f"{API_BASE_URL}/save_response", json=payload)
            if save_response.status_code == 200:
                st.success("Response saved successfully!")
            else:
                st.error("Error saving response.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Function to generate a unique key for each checkbox
def generate_unique_key(*args):
    return hashlib.md5("".join(map(str, args)).encode('utf-8')).hexdigest()

# Function to display endpoints without recursion
def display_endpoints(name, item):
    stack = [(name, item)]
    while stack:
        current_name, current_item = stack.pop()
        
        if isinstance(current_item, dict):
            st.subheader(current_name)
            st.session_state.selected_category = current_name
            for sub_key, sub_value in current_item.items():
                if isinstance(sub_value, dict):
                    stack.append((f"{sub_key} (nested dictionary)", sub_value))
                elif isinstance(sub_value, list):
                    st.subheader(f"{sub_key} (list)")
                    for list_item in sub_value:
                        list_item_key = generate_unique_key(sub_key, list_item)
                        if st.checkbox(str(list_item), key=list_item_key):
                            st.session_state.selected_bullet = str(list_item)
                else:
                    sub_key_value_key = generate_unique_key(sub_key, sub_value)
                    if st.checkbox(f"{sub_key}: {sub_value}", key=sub_key_value_key):
                        st.session_state.selected_bullet = f"{sub_key}: {sub_value}"
                        
        elif isinstance(current_item, list):
            st.subheader(current_name)
            st.session_state.selected_category = current_name
            for list_item in current_item:
                list_item_key = generate_unique_key(current_name, list_item)
                if st.checkbox(str(list_item), key=list_item_key):
                    st.session_state.selected_bullet = str(list_item)
        
        else:
            base_key = generate_unique_key(current_name, current_item)
            if st.checkbox(f"{current_name}: {current_item}", key=base_key):
                st.session_state.selected_bullet = f"{current_name}: {current_item}"

# Reusable function to handle each section
def handle_section(section_name, display_name):
    st.subheader(display_name)

    if section_name == "results":
        generate_button = st.button(f"Generate {display_name} with predefined prompts", key=f"generate_{section_name}")
        if generate_button:
            if st.session_state.assistant_id and st.session_state.vector_id:
                try:
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
                        error_message = response.json().get("error", f"Failed to generate {display_name.lower()}.")
                        st.error(error_message)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
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
                st.write("No match found.")

            st.title("Endpoints")

            # Output the keys and their corresponding values
            for major_category, endpoints_dict in response_dict.items():
                display_endpoints(major_category, endpoints_dict)

            # Display prompt selection after all checkboxes
            if st.session_state.selected_bullet:
                st.write("You selected:", st.session_state.selected_bullet)

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

                st.write("Selected Prompt:")
                st.markdown(prompt_selection)

                # Set user_query as the selected prompt
                st.session_state['user_query'] = prompt_selection

                checkbox_dependent = st.checkbox("Dependent on threads", value=True)
                st.session_state["checkbox_dependent"] = checkbox_dependent

                get_checkbox_dependent_status = lambda: "ON" if st.session_state['checkbox_dependent'] else "OFF"
                st.write(f"Conversation: {get_checkbox_dependent_status()}")

                if st.button("Run for selected prompts for checkbox"):
                    checkbox_user_query = st.session_state.get('user_query', '')
                    
                    if checkbox_user_query:
                        try:
                            st.session_state["checkbox_response"] = ""
                            st.session_state["checkbox_citations"] = []

                            payload = {
                                "question": checkbox_user_query,
                                "file_name": st.session_state.file_name,
                                "assistant_id": st.session_state.assistant_id,
                                "vector_id": st.session_state.vector_id,
                                "current_thread_id": st.session_state.current_checkbox_thread_id or None,
                                "dependent": st.session_state["checkbox_dependent"], 
                            }
                            response = requests.post(f"{API_BASE_URL}/query", json=payload)
                            if response.status_code == 200:
                                result = response.json()
                                assistant_response = result.get("response", "")
                                citations = result.get("citations", [])
                                thread_id = result.get("thread_id", None)

                                st.session_state.current_checkbox_thread_id = thread_id
                                st.session_state["checkbox_response"] = assistant_response
                                st.session_state["checkbox_citations"] = citations

                                st.success("Assistant responded to your query!")
                            else:
                                st.error(response.json().get("error", "Please upload the file to start your query"))
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    else:
                        st.error("Please enter a query before asking.")

                # Display editable text area for the query response
                if st.session_state["checkbox_response"]:
                    st.header("💬 Response")
                    response_text = st.text_area("Response:", st.session_state["checkbox_response"], height=200, key="checkbox_response_text")
                    citations = st.session_state["checkbox_citations"]

                    if st.session_state.current_checkbox_thread_id:
                        st.markdown(f"**Thread ID:** {st.session_state.current_checkbox_thread_id}")

                    if "user_query" in st.session_state and st.session_state["checkbox_response"]:
                        if st.button("Save Response", key="save_checkbox_response_button"): 
                            payload = {
                                'file_name': st.session_state.file_name,
                                'user_query': st.session_state.user_query,
                                'assistant_response': st.session_state.checkbox_response,
                                'citations': st.session_state.checkbox_citations,
                                'thread_id': st.session_state.current_checkbox_thread_id
                            }
                            try:
                                save_response = requests.post(f"{API_BASE_URL}/save_checkbox_response", json=payload)
                                if save_response.status_code == 200:
                                    st.success("Response saved successfully!")
                                else:
                                    st.error("Error saving response.")
                            except Exception as e:
                                st.error(f"An error occurred: {e}")

    # Chat Functionality
    with st.expander(f"Initialise New chat for {display_name}"):
        user_message = st.text_input(f"Enter your message for the {display_name}:", key=f"user_message_outside_{section_name}")

        if st.button("Run", key=f"send_message_outside_{section_name}"):
            if user_message and st.session_state.assistant_id and st.session_state.vector_id:
                try:
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
                        error_message = response.json().get("error", "Failed to process the chat.")
                        st.error(error_message)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("Please upload your paper to send a message.")

        if st.session_state[f"outside_{section_name}_chat"]:
            chat_text = st.text_area(f"{display_name} Chat:", st.session_state[f"outside_{section_name}_chat"], key=f"chat_text_outside_{section_name}")
            chat_citations = st.session_state[f"{section_name}_chat_citations"]
            st.write(f"thread ID {st.session_state[f'initialise_new_chat_for_outside_{section_name}_thread_id']}")

            if st.button(f"Save {display_name} Chat", key=f"save_chat_outside_{section_name}"):
                payload = {
                    'file_name': st.session_state.file_name,
                    'user_query': user_message,
                    'assistant_response': chat_text,
                    'citations': chat_citations,
                    'thread_id': st.session_state[f"initialise_new_chat_for_outside_{section_name}_thread_id"]
                }
                try:
                    save_response = requests.post(f"{API_BASE_URL}/{section_name}/save_outside_{section_name}_chat_response", json=payload)
                    if save_response.status_code == 200:
                        st.success(f"{display_name} Chat saved successfully!")
                    else:
                        st.error(f"Error saving {display_name.lower()} chat.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# Tabs for Document Sections
st.header("📄 Document Sections")
tabs = st.tabs(["**Results**", "**Methods**", "**Introduction**", "**Discussion**", "**Conclusion**"])

sections = ["results", "methods", "introduction", "discussion", "conclusion"]
display_names = ["Results", "Methods", "Introduction", "Discussion", "Conclusion"]

for tab, section, display_name in zip(tabs, sections, display_names):
    with tab:
        handle_section(section, display_name) 