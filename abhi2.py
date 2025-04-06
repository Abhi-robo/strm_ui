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


API_BASE_URL = "http://localhost:5000/"


# Initialize session state variables
def initialize_session_state():
    default_sections = ["introduction", "methods", "discussion", "results", "conclusion"]
    
    # General session states
    for key in ["file_name", "assistant_id", "vector_id", "current_thread_id", "current_checkbox_thread_id", 
                "edited_response", "response", "citations", "checkbox_response", "checkbox_citations", 
                "dependent", "checkbox_dependent", "user_query", "selected_bullet", "selected_category"]:
        if key not in st.session_state:
            if key in ["dependent", "checkbox_dependent"]:
                st.session_state[key] = True
            elif key in ["selected_bullet", "selected_category"]:
                st.session_state[key] = None
            else:
                st.session_state[key] = ""
    
    # Methods-specific session states
    if "selected_endpoints_for_methods" not in st.session_state:
        st.session_state["selected_endpoints_for_methods"] = []
    
    if "methods_categorized_endpoints" not in st.session_state:
        st.session_state["methods_categorized_endpoints"] = {}
    
    if "methods_checkbox_states" not in st.session_state:
        st.session_state["methods_checkbox_states"] = {}
    
    for methods_key in ["methods_selected_bullet", "methods_selected_category", "methods_response", 
                       "methods_citations", "methods_user_query", "methods_thread_id", 
                       "methods_dependent", "methods_checkbox_clicked"]:
        if methods_key not in st.session_state:
            if methods_key == "methods_dependent":
                st.session_state[methods_key] = True
            elif methods_key == "methods_checkbox_clicked":
                st.session_state[methods_key] = False
            elif methods_key == "methods_citations":
                st.session_state[methods_key] = []
            elif methods_key in ["methods_selected_bullet", "methods_selected_category"]:
                st.session_state[methods_key] = None
            else:
                st.session_state[methods_key] = ""
    
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
            f"initialise_new_chat_for{section}_thread_id",  # Add this line

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
                st.session_state[key] = False  # Boolean value for "view_final_edited_outside"
            else:
                st.session_state[key] = []  # Default to empty list for the others


initialize_session_state()



# Function to clear session state when a new file is uploaded
def clear_session():
    # General session states to clear
    for key in ["file_name", "assistant_id", "vector_id", "current_thread_id", "current_checkbox_thread_id", 
                "edited_response", "response", "citations", "checkbox_response", "checkbox_citations", 
                "dependent", "checkbox_dependent", "user_query", "selected_bullet", "selected_category"]:
        if key in ["dependent", "checkbox_dependent"]:
            st.session_state[key] = True
        elif key in ["selected_bullet", "selected_category"]:
            st.session_state[key] = None
        else:
            st.session_state[key] = ""
    
    # Methods-specific session states to clear
    st.session_state["selected_endpoints_for_methods"] = []
    st.session_state["methods_categorized_endpoints"] = {}  # Always initialize as empty dict, not None
    
    for methods_key in ["methods_selected_bullet", "methods_selected_category", "methods_response", 
                      "methods_citations", "methods_user_query", "methods_thread_id", 
                      "methods_dependent", "methods_checkbox_clicked"]:
        if methods_key == "methods_dependent":
            st.session_state[methods_key] = True
        elif methods_key == "methods_checkbox_clicked":
            st.session_state[methods_key] = False
        elif methods_key == "methods_citations":
            st.session_state[methods_key] = []
        elif methods_key in ["methods_selected_bullet", "methods_selected_category"]:
            st.session_state[methods_key] = None
        else:
            st.session_state[methods_key] = ""
    
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
            f"initialise_new_chat_for{section}_thread_id",  # Add this line to clear the new session variable

            f"initialise_new_chat_for_outside_{section}_thread_id",
            f"outside_{section}_thread_id",
            f"outside_{section}_citations",
            f"outside_{section}_prompt",
            f"outside_{section}_chat",
            f"outside_{section}_chat_citations",
        ]:
            st.session_state[sub_key] = [] if 'citations' in sub_key else ""
    
    # Clear additional session state variables for outside queries
    for key in ["selected_queries_outside", "selected_responses_outside", "results_outside", "final_edited_responses_outside", "view_final_edited_outside",  "show_results", "show_selected_query", "assistant_response"]:
        if key in st.session_state:
            if key == "view_final_edited_outside":
                st.session_state[key] = False  # Reset to False
            else:
                st.session_state[key] = []  # Clear by setting to an empty list



 

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
                        st.session_state.current_thread_id = result.get("thread_id", "")  # Adjust based on your response
                    else:
                        # Handle other response structures if necessary
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

# Display the conversation status
st.write(f"Conversation: {get_dependent_status()}")


if st.button("Ask Assistant"):
    if user_query:
        try:
            # Clear previous response and citations from the session state
            st.session_state["response"] = ""
            st.session_state["citations"] = []

            # Send metadata and the user query to the backend
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

                st.session_state.current_thread_id = thread_id  # Update current thread ID
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
    # Use a hash of the arguments to create a unique key
    return hashlib.md5("".join(map(str, args)).encode('utf-8')).hexdigest()

# Modified function to display endpoints without immediate prompt selection
def display_endpoints(name, item):
    selected_bullet = None  # To store the selected bullet point
    selected_category = None  # To store the selected category
    show_button = False  # To track if we should show the button

    stack = [(name, item)]  # Initialize stack with the root level
    while stack:
        current_name, current_item = stack.pop()  # Pop from stack for processing
        
        if isinstance(current_item, dict):
            # If it's a dictionary, loop through the key-value pairs
            st.subheader(current_name)  # Display the category name (subheader)
            selected_category = current_name  # Capture the selected category
            for sub_key, sub_value in current_item.items():
                if isinstance(sub_value, dict):
                    # If the value is another dictionary, add to stack
                    stack.append((f"{sub_key} (nested dictionary)", sub_value))
                elif isinstance(sub_value, list):
                    # If the value is a list, process it directly
                    st.subheader(f"{sub_key} (list)")
                    for list_item in sub_value:
                        list_item_key = generate_unique_key(sub_key, list_item)  # Ensure unique key for list items
                        if st.checkbox(str(list_item), key=list_item_key):
                            selected_bullet = str(list_item)  # Capture the selected item
                            show_button = True  # User selected a checkbox
                            # Store selection in session state
                            st.session_state["selected_bullet"] = selected_bullet
                            st.session_state["selected_category"] = selected_category
                else:
                    # Otherwise, display the key and value as a checkbox
                    sub_key_value_key = generate_unique_key(sub_key, sub_value)  # Ensure unique key for key-value pairs
                    if st.checkbox(f"{sub_key}: {sub_value}", key=sub_key_value_key):
                        selected_bullet = f"{sub_key}: {sub_value}"  # Capture the selected bullet
                        show_button = True  # User selected a checkbox
                        # Store selection in session state
                        st.session_state["selected_bullet"] = selected_bullet
                        st.session_state["selected_category"] = selected_category
                        
        elif isinstance(current_item, list):
            # If it's a list, display each item as a checkbox
            st.subheader(current_name)  # Display the category name (subheader)
            selected_category = current_name  # Capture the selected category
            for list_item in current_item:
                list_item_key = generate_unique_key(current_name, list_item)  # Ensure unique key for list items
                if st.checkbox(str(list_item), key=list_item_key):
                    selected_bullet = str(list_item)  # Capture the selected item
                    show_button = True  # User selected a checkbox
                    # Store selection in session state
                    st.session_state["selected_bullet"] = selected_bullet
                    st.session_state["selected_category"] = selected_category
        
        else:
            # Base case: Directly display the name and item as a checkbox
            base_key = generate_unique_key(current_name, current_item)  # Ensure unique key for base case
            if st.checkbox(f"{current_name}: {current_item}", key=base_key):
                selected_bullet = f"{current_name}: {current_item}"  # Capture the selected bullet
                show_button = True  # User selected a checkbox
                # Store selection in session state
                st.session_state["selected_bullet"] = selected_bullet
                st.session_state["selected_category"] = selected_category

    # Just return whether any checkbox was selected, prompt selection happens after all endpoints are displayed
    return show_button


# Reusable function to handle each section
def handle_section(section_name, display_name):
    st.subheader(display_name)

    if section_name == "results":
        generate_button = st.button(f"Generate {display_name} with predefined prompts", key=f"generate_{section_name}")
        if generate_button:
            if st.session_state.assistant_id and st.session_state.vector_id:
                try:
                    # Clear previous data for the section
                    st.session_state[section_name] = ""
                    st.session_state[f"{section_name}_citations"] = []
                    
                    # Prepare the payload
                    payload = {
                        'assistant_id': st.session_state.assistant_id,
                        'vector_id': st.session_state.vector_id
                    }

                    # Send the request to the backend
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
            # Editable text area for the section
            edited_text = st.text_area(f"{display_name}:", st.session_state[section_name], key=f"text_{section_name}")

        if st.session_state[section_name]:
            response = st.session_state[section_name]

            match = re.search(r"endpoints = ({.*})", response, re.DOTALL)

            if match:
                endpoints_str = match.group(1)
                # Convert the string representation to an actual Python dictionary
                endpoints_dict = ast.literal_eval(endpoints_str)
                response_dict = endpoints_dict
                # st.write(endpoints_dict)
            else:
                st.write("No match found.")
                return  # Exit if no endpoints found

            # Start the Streamlit app
            st.title("Endpoints")

            # Track whether the "Ask Assistant" button should be displayed
            show_button = False

            # Output the keys and their corresponding values
            for major_category, endpoints_dict in response_dict.items():
                show_button |= display_endpoints(major_category, endpoints_dict)

            # Now show the prompt selection AFTER all endpoints have been displayed
            if show_button:
                st.markdown("---")
                st.header("Prompt Selection")
                
                selected_bullet = st.session_state["selected_bullet"]
                selected_category = st.session_state["selected_category"]
                
                st.write("You selected:", selected_bullet)
                
                # Check if the selected category is 'safety' and display appropriate prompts
                is_safety_endpoint = selected_category.lower() == "safety"
                
                if is_safety_endpoint:
                    prompt_selection = st.selectbox(
                        "Select a Prompt for Safety Endpoint",
                        [
                            f"Prompt 1. Please can you describe the {selected_bullet} results relating to safety and tolerability. Referring to text and tables describing any safety or tolerability, please can you draft a paragraph describing these results and summarizing the data for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points. ",
                            
                            f"Prompt 2: Please can you provide the following data for each study arm as a bulleted list, relating to safety and tolerability, if it is available:\n"
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
                            f"Prompt 1: Please can you describe the results for the endpoint of {selected_bullet}. Refer to text and tables describing all analyses, please can you draft a paragraph describing this endpoint and summarizing the outcomes for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points",

                            f"Prompt 2: Please can you describe the results for any subgroup analyses of the endpoint of {selected_bullet}. Refer to text and tables describing all analyses, please can you draft a paragraph describing this endpoint and summarizing the outcomes for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points"
                        ]
                    )
                
                st.write("Selected Prompt:")
                st.markdown(prompt_selection)
                
                # Set user_query as the selected prompt
                st.session_state['user_query'] = prompt_selection  # Save the selected prompt as user_query

                checkbox_dependent = st.checkbox("Dependent on threads", value=True)
                st.session_state["checkbox_dependent"] = checkbox_dependent

                get_checkbox_dependent_status = lambda: "ON" if st.session_state['checkbox_dependent'] else "OFF"

                # Display the conversation status
                st.write(f"Conversation: {get_checkbox_dependent_status()}")

                # Show "Run for selected prompts for checkbox" button
                if st.button("Run for selected prompts for checkbox"):
                    # Store the current selection to restore later
                    temp_selected_bullet = st.session_state["selected_bullet"]
                    temp_selected_category = st.session_state["selected_category"]
                    
                    checkbox_user_query = st.session_state.get('user_query', '')
                    
                    if checkbox_user_query:
                        try:
                            # Clear previous response and citations from the session state
                            st.session_state["checkbox_response"] = ""
                            st.session_state["checkbox_citations"] = []

                            # Send metadata and the user query to the backend
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

                                st.session_state.current_checkbox_thread_id = thread_id  # Update current thread ID
                                st.session_state["checkbox_response"] = assistant_response
                                st.session_state["checkbox_citations"] = citations
                                
                                # Restore selections
                                st.session_state["selected_bullet"] = temp_selected_bullet
                                st.session_state["selected_category"] = temp_selected_category

                                st.success("Assistant responded to your query!")
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
                    else:
                        # Restore selections if no query
                        st.session_state["selected_bullet"] = temp_selected_bullet
                        st.session_state["selected_category"] = temp_selected_category
                        st.error("Please enter a query before asking.")

            # Display editable text area for the query response
            if st.session_state.get("checkbox_response"):
                st.header("💬 Response")
                response_text = st.text_area("Response:", st.session_state["checkbox_response"], height=200, key="checkbox_response_text")
                citations = st.session_state["checkbox_citations"]

                if st.session_state.current_checkbox_thread_id:
                    st.markdown(f"**Thread ID:** {st.session_state.current_checkbox_thread_id}")

                if "user_query" in st.session_state and st.session_state["checkbox_response"]:
                    # Save Response Button
                    if st.button("Save Response", key="save_checkbox_response_button"): 
                        payload = {
                            'file_name': st.session_state.file_name,
                            'user_query': st.session_state.user_query,
                            'assistant_response': st.session_state.checkbox_response,
                            'citations': st.session_state.checkbox_citations,
                            'thread_id': st.session_state.current_checkbox_thread_id,
                            'selected_bullet': st.session_state.selected_bullet,
                            'selected_category': st.session_state.selected_category
                        }
                        try:
                            # Use the new endpoint-specific API
                            save_response = requests.post(f"{API_BASE_URL}/save_endpoint_response", json=payload)
                            if save_response.status_code == 200:
                                st.success("Endpoint response saved successfully!")
                            else:
                                st.error(f"Error saving response: {save_response.json().get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"An error occurred: {e}")

            # Add a section to view saved endpoints for this category
            if selected_category:
                with st.expander(f"View Saved Endpoints for {selected_category}"):
                    # Button to refresh the endpoint data
                    if st.button("Load Saved Endpoints", key=f"load_endpoints_{selected_category}"):
                        try:
                            # Prepare the request to get endpoints for this category
                            params = {
                                'file_name': st.session_state.file_name,
                                'category': selected_category
                            }
                            
                            # Make the request to the backend
                            response = requests.get(f"{API_BASE_URL}/get_endpoints", params=params)
                            
                            if response.status_code == 200:
                                result = response.json()
                                endpoints = result.get("endpoints", [])
                                
                                # Store endpoints in session state
                                st.session_state[f"saved_endpoints_{selected_category}"] = endpoints
                                
                                if endpoints:
                                    st.success(f"Loaded {len(endpoints)} saved endpoints")
                                else:
                                    st.info(f"No saved endpoints found for category: {selected_category}")
                            else:
                                st.error(f"Error loading endpoints: {response.json().get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                    
                    # Display saved endpoints if available
                    if f"saved_endpoints_{selected_category}" in st.session_state and st.session_state[f"saved_endpoints_{selected_category}"]:
                        endpoints = st.session_state[f"saved_endpoints_{selected_category}"]
                        
                        # Create a list of endpoint names for the selectbox
                        endpoint_options = [f"{endpoint['endpoint_name']} (Updated: {endpoint['updated_at'][:16].replace('T', ' ')})" for endpoint in endpoints]
                        
                        # Display a select box for choosing an endpoint
                        selected_endpoint_idx = st.selectbox(
                            "Select a saved endpoint response",
                            range(len(endpoint_options)),
                            format_func=lambda i: endpoint_options[i]
                        )
                        
                        # Display the selected endpoint data
                        if selected_endpoint_idx is not None:
                            selected_endpoint = endpoints[selected_endpoint_idx]
                            
                            st.markdown(f"### Endpoint: {selected_endpoint['endpoint_name']}")
                            st.markdown(f"**Category:** {selected_endpoint['endpoint_category']}")
                            st.markdown(f"**Prompt:** {selected_endpoint['user_query']}")
                            st.markdown("**Response:**")
                            st.text_area(
                                "Saved Response",
                                selected_endpoint['assistant_response'],
                                height=200,
                                key=f"view_saved_response_{selected_endpoint_idx}"
                            )
                            
                            if 'citations' in selected_endpoint and selected_endpoint['citations']:
                                st.markdown("**Citations:**")
                                for i, citation in enumerate(selected_endpoint['citations']):
                                    st.markdown(f"{i+1}. {citation}")

    # Add endpoint selection interface for Methods section
    elif section_name == "methods":
        # Initialize session state for selected endpoints if not already done
        if "selected_endpoints_for_methods" not in st.session_state:
            st.session_state["selected_endpoints_for_methods"] = []
        
        # Add a button to load endpoints
        col1, col2 = st.columns([1, 3])
        with col1:
            load_button = st.button("Load Saved Endpoints", key="load_endpoints_for_methods", type="primary")
        with col2:
            # Safely access methods_categorized_endpoints even if it's None
            if st.session_state.get("methods_categorized_endpoints"):
                endpoints_dict = st.session_state["methods_categorized_endpoints"]
                endpoint_count = sum(len(endpoints) for endpoints in endpoints_dict.values())
                st.markdown(f"**{endpoint_count}** endpoints loaded from **{len(endpoints_dict)}** categories")
                # Show the file we're working with
                if st.session_state.file_name:
                    st.markdown(f"File: **{st.session_state.file_name}**")
            else:
                # Display a message if no endpoints are loaded yet
                st.markdown("No endpoints loaded yet. Click the button to load endpoints.")
        
        if load_button:
            try:
                if st.session_state.file_name:
                    # Show loading message
                    with st.spinner(f"Loading endpoints for {st.session_state.file_name}..."):
                        # Make request to get all endpoints for this file
                        params = {
                            'file_name': st.session_state.file_name
                        }
                        
                        response = requests.get(f"{API_BASE_URL}/methods/get_endpoints_for_methods", params=params)
                        
                        if response.status_code == 200:
                            result = response.json()
                            categorized_endpoints = result.get("endpoints", {})
                            
                            # Store in session state
                            st.session_state["methods_categorized_endpoints"] = categorized_endpoints
                            
                            if categorized_endpoints:
                                total_endpoints = sum(len(endpoints) for endpoints in categorized_endpoints.values())
                                st.success(f"Loaded {total_endpoints} endpoints from {len(categorized_endpoints)} categories for {st.session_state.file_name}")
                            else:
                                st.info(f"No saved endpoints found for {st.session_state.file_name}. Please generate endpoints in the Results section first.")
                        else:
                            st.error(f"Error loading endpoints: {response.json().get('error', 'Unknown error')}")
                else:
                    st.error("Please upload a file first")
            except Exception as e:
                st.error(f"An error occurred: {e}")

        # Add description text
        if "methods_categorized_endpoints" in st.session_state and st.session_state["methods_categorized_endpoints"]:
            st.markdown("""
            ### Instructions
            1. Check the boxes next to the endpoints you want to include in your Methods section
            2. Review your selected endpoints below
            3. Click "Generate Methods from Selected Endpoints" to create your Methods section
            """)

        # If endpoints are loaded, display them as checkboxes
        if st.session_state.get("methods_categorized_endpoints") and len(st.session_state["methods_categorized_endpoints"]) > 0:
            st.subheader("Select Endpoints to Include in Methods Section")
            
            # Display endpoints by category
            for category, endpoints in st.session_state["methods_categorized_endpoints"].items():
                # Skip empty categories
                if not endpoints:
                    continue
                    
                # Display category as a heading
                st.subheader(category)  # Use subheader instead of markdown for consistency with display_endpoints
                
                # Display all endpoints in this category as checkboxes
                for endpoint in endpoints:
                    endpoint_id = endpoint.get("endpoint_id")
                    endpoint_name = endpoint.get("endpoint_name")
                    
                    # Skip endpoints with missing data
                    if not endpoint_id or not endpoint_name:
                        continue
                    
                    # Create a unique key for this checkbox
                    checkbox_key = f"methods_endpoint_{endpoint_id}"
                    
                    # Check if this endpoint is already selected
                    is_selected = endpoint_id in [e.get("endpoint_id") for e in st.session_state["selected_endpoints_for_methods"]]
                    
                    # Use the helper function to handle checkbox state
                    update_checkbox_state(checkbox_key, endpoint, is_selected, category, endpoint_name)
                
                # Removed spacing between categories

            # Display prompts if an endpoint is selected
            if st.session_state.get("methods_selected_bullet"):
                st.markdown("---")
                st.header("Prompt Selection for Methods")
                
                selected_bullet = st.session_state["methods_selected_bullet"]
                selected_category = st.session_state["methods_selected_category"]
                
                st.write("You selected:", selected_bullet)
                
                # Check if the selected category is 'safety' and display appropriate prompts
                is_safety_endpoint = selected_category and selected_category.lower() == "safety"
                
                if is_safety_endpoint:
                    prompt_selection = st.selectbox(
                        "Select a Prompt for Safety Endpoint",
                        [
                            f"Prompt 1: Please can you describe the results for the endpoint of {selected_bullet}. Refer to text and tables describing all analyses, please can you draft a paragraph describing this endpoint and summarizing the outcomes for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points",
                            
                            f"Prompt 2: Please can you describe the results for any subgroup analyses of the endpoint of {selected_bullet}. Refer to text and tables describing all analyses, please can you draft a paragraph describing this endpoint and summarizing the outcomes for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points",
                            
                            f"Prompt 3: For each study arm please can you provide details of the 10 most common treatment emergent adverse events. If an adverse event is common in any one arm please provide the numbers for that adverse event for all study arms.",
                            
                            f"Prompt 4: For each study arm please can you provide details of the serious adverse events that were reported. For each and every serious adverse event please provide the number and proportion of patients reporting it and provide a summary of the outcomes of the events.",
                            
                            f"Prompt 5: For each study arm please can you provide details of the adverse events leading to discontinuation that were reported. For each and every adverse event please provide the number and proportion of patients reporting it and provide a summary of the outcomes of the events."
                        ],
                        key="methods_prompt_selection_safety"
                    )
                else:
                    prompt_selection = st.selectbox(
                        "Select a Prompt",
                        [
                            f"Prompt 1: Please can you describe the results for the endpoint of {selected_bullet}. Refer to text and tables describing all analyses, please can you draft a paragraph describing this endpoint and summarizing the outcomes for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points",

                            f"Prompt 2: Please can you describe the results for any subgroup analyses of the endpoint of {selected_bullet}. Refer to text and tables describing all analyses, please can you draft a paragraph describing this endpoint and summarizing the outcomes for it. Please can you add references to any tables or figures that would be relevant to include in a paper. Please can you provide the output as bullet points",
                            
                            f"Prompt 3: For each study arm please can you provide details of the 10 most common treatment emergent adverse events. If an adverse event is common in any one arm please provide the numbers for that adverse event for all study arms.",
                            
                            f"Prompt 4: For each study arm please can you provide details of the serious adverse events that were reported. For each and every serious adverse event please provide the number and proportion of patients reporting it and provide a summary of the outcomes of the events.",
                            
                            f"Prompt 5: For each study arm please can you provide details of the adverse events leading to discontinuation that were reported. For each and every adverse event please provide the number and proportion of patients reporting it and provide a summary of the outcomes of the events."
                        ],
                        key="methods_prompt_selection"
                    )
                
                st.write("Selected Prompt:")
                st.markdown(prompt_selection)
                
                # Set user_query as the selected prompt
                st.session_state['methods_user_query'] = prompt_selection  # Save the selected prompt
                
                methods_checkbox_dependent = st.checkbox("Dependent on threads", value=True, key="methods_checkbox_dependent")
                st.session_state["methods_dependent"] = methods_checkbox_dependent
                
                get_methods_dependent_status = lambda: "ON" if st.session_state['methods_dependent'] else "OFF"
                
                # Display the conversation status
                st.write(f"Conversation: {get_methods_dependent_status()}")
                
                # Show "Run for selected prompts" button
                if st.button("Run for selected prompt", key="run_methods_prompt"):
                    # Store current selections to restore later
                    temp_methods_selected_bullet = st.session_state["methods_selected_bullet"]
                    temp_methods_selected_category = st.session_state["methods_selected_category"]
                    
                    methods_user_query = st.session_state.get('methods_user_query', '')
                    
                    if methods_user_query:
                        try:
                            # Clear previous response and citations
                            st.session_state["methods_response"] = ""
                            st.session_state["methods_citations"] = []
                            
                            # Send request to the backend
                            payload = {
                                "question": methods_user_query,
                                "file_name": st.session_state.file_name,
                                "assistant_id": st.session_state.assistant_id,
                                "vector_id": st.session_state.vector_id,
                                "current_thread_id": st.session_state.get("methods_thread_id") or None,
                                "dependent": st.session_state["methods_dependent"],
                            }
                            
                            response = requests.post(f"{API_BASE_URL}/query", json=payload)
                            
                            if response.status_code == 200:
                                result = response.json()
                                assistant_response = result.get("response", "")
                                citations = result.get("citations", [])
                                thread_id = result.get("thread_id", None)
                                
                                # Update session state
                                st.session_state["methods_thread_id"] = thread_id
                                st.session_state["methods_response"] = assistant_response
                                st.session_state["methods_citations"] = citations
                                
                                # Restore selections
                                st.session_state["methods_selected_bullet"] = temp_methods_selected_bullet
                                st.session_state["methods_selected_category"] = temp_methods_selected_category
                                
                                st.success("Assistant responded to your query!")
                            else:
                                # Restore selections on error
                                st.session_state["methods_selected_bullet"] = temp_methods_selected_bullet
                                st.session_state["methods_selected_category"] = temp_methods_selected_category
                                st.error(response.json().get("error", "Please upload the file to start your query"))
                        except Exception as e:
                            # Restore selections on exception
                            st.session_state["methods_selected_bullet"] = temp_methods_selected_bullet
                            st.session_state["methods_selected_category"] = temp_methods_selected_category
                            st.error(f"Error: {str(e)}")
                    else:
                        # Restore selections if no query
                        st.session_state["methods_selected_bullet"] = temp_methods_selected_bullet
                        st.session_state["methods_selected_category"] = temp_methods_selected_category
                        st.error("Please enter a query before asking.")
                
                # Display response if available
                if st.session_state.get("methods_response"):
                    st.header("💬 Response")
                    response_text = st.text_area("Response:", st.session_state["methods_response"], height=200, key="methods_response_text")
                    citations = st.session_state.get("methods_citations", [])
                    
                    if st.session_state.get("methods_thread_id"):
                        st.markdown(f"**Thread ID:** {st.session_state.get('methods_thread_id')}")
                    
                    # Save Response Button
                    if st.button("Save Response", key="save_methods_response_button"):
                        # Validate that we have the required data
                        if not st.session_state.get("file_name"):
                            st.error("No file name available. Please upload a file first.")
                        elif not st.session_state.get("methods_user_query"):
                            st.error("No query available. Please select a prompt and run it first.")
                        elif not st.session_state.get("methods_response"):
                            st.error("No response available. Please run a prompt first.")
                        else:
                            payload = {
                                'file_name': st.session_state.file_name,
                                'user_query': st.session_state.methods_user_query,
                                'assistant_response': st.session_state.methods_response,
                                'citations': st.session_state.get("methods_citations", []),
                                'thread_id': st.session_state.get("methods_thread_id"),
                                'selected_bullet': st.session_state.get("methods_selected_bullet"),
                                'selected_category': st.session_state.get("methods_selected_category")
                            }
                            try:
                                # Use the endpoint-specific API
                                save_response = requests.post(f"{API_BASE_URL}/save_endpoint_response", json=payload)
                                if save_response.status_code == 200:
                                    st.success("Endpoint response saved successfully!")
                                else:
                                    error_msg = save_response.json().get("error", "Unknown error")
                                    st.error(f"Error saving response: {error_msg}")
                            except Exception as e:
                                st.error(f"An error occurred: {e}")

            # Display selected endpoints
            if st.session_state["selected_endpoints_for_methods"]:
                st.subheader("Selected Endpoints")  # Use subheader for consistency
                
                # Group selected endpoints by category
                selected_by_category = {}
                for endpoint in st.session_state["selected_endpoints_for_methods"]:
                    # Extract category from the endpoint ID (format: file_name_category_endpoint_name)
                    endpoint_id_parts = endpoint.get("endpoint_id", "").split("_")
                    if len(endpoint_id_parts) > 1:
                        category = endpoint_id_parts[1]  # Category is typically the second part
                    else:
                        category = "Other"
                    
                    # Initialize the category list if it doesn't exist
                    if category not in selected_by_category:
                        selected_by_category[category] = []
                    
                    # Add the endpoint to its category
                    selected_by_category[category].append(endpoint)
                
                # Display selected endpoints grouped by category
                for category, endpoints in selected_by_category.items():
                    st.subheader(category)  # Use subheader for consistency
                    for endpoint in endpoints:
                        st.write(f"• {endpoint.get('endpoint_name')}")  # Use standard bullet
                
                # Button to generate methods from selected endpoints
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("Generate Methods from Selected Endpoints", type="primary"):
                        try:
                            # Prepare payload with filename
                            payload = {
                                'assistant_id': st.session_state.assistant_id,
                                'vector_id': st.session_state.vector_id,
                                'endpoints': st.session_state["selected_endpoints_for_methods"],
                                'file_name': st.session_state.file_name  # Include filename
                            }
                            
                            # Show generation in progress
                            with st.spinner("Generating Methods section..."):
                                # Call the API
                                response = requests.post(f"{API_BASE_URL}/methods/generate_methods_from_endpoints", json=payload)
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    methods_content = result.get("methods_content", "")
                                    citations = result.get("citations", [])
                                    thread_id = result.get("thread_id", None)
                                    
                                    # Store the results in session state
                                    st.session_state["methods"] = methods_content
                                    st.session_state[f"methods_citations"] = citations
                                    st.session_state[f"methods_thread_id"] = thread_id
                                    
                                    # Show the generated content
                                    st.success("✅ Methods section generated successfully!")
                                else:
                                    st.error(f"Error generating methods: {response.json().get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                
                with col2:
                    # Add clear selection button
                    if st.button("Clear Selected Endpoints", key="clear_selected_endpoints"):
                        st.session_state["selected_endpoints_for_methods"] = []
                        st.success("All endpoint selections cleared!")
                        st.experimental_rerun()

        # Display generated Methods content
        if "methods" in st.session_state and st.session_state["methods"]:
            st.subheader("Generated Methods Section")  # Using subheader for consistency
            
            # Create tabs for content and citations
            content_tab, citations_tab = st.tabs(["Content", "Citations"])
            
            with content_tab:
                st.text_area(
                    "Methods Content",
                    st.session_state["methods"],
                    height=400,
                    key="generated_methods_content"
                )
                
                # Add a button to save the generated methods
                if st.button("Save Generated Methods", key="save_generated_methods"):
                    save_payload = {
                        'file_name': st.session_state.file_name,
                        'user_query': "Generated from selected endpoints",
                        'assistant_response': st.session_state["methods"],
                        'citations': st.session_state.get("methods_citations", []),
                        'thread_id': st.session_state.get("methods_thread_id")
                    }
                    
                    save_response = requests.post(f"{API_BASE_URL}/methods/save_methods_response", json=save_payload)
                    
                    if save_response.status_code == 200:
                        st.success("Methods saved successfully!")
                    else:
                        st.error(f"Error saving methods: {save_response.json().get('error', 'Unknown error')}")
            
            with citations_tab:
                if "methods_citations" in st.session_state and st.session_state["methods_citations"]:
                    for i, citation in enumerate(st.session_state["methods_citations"]):
                        st.markdown(f"{i+1}. {citation}")
                else:
                    st.info("No citations found in the generated content.")

    # Chat Functionality
    with st.expander(f"Initialise New chat for {display_name}"):
        user_message = st.text_input(f"Enter your message for the {display_name}:", key=f"user_message_outside_{section_name}")

        if st.button("Run", key=f"send_message_outside_{section_name}"):
            if user_message and st.session_state.assistant_id and st.session_state.vector_id:
                try:
                    # Prepare the payload
                    payload = {
                        'assistant_id': st.session_state.assistant_id,
                        'vector_id': st.session_state.vector_id,
                        'thread_id': st.session_state[f'initialise_new_chat_for_outside_{section_name}_thread_id'], 
                        'message': user_message
                    }

                    # Send the request to the backend
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

            # Save Chat Button
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

# Helper function to manage checkbox state changes
def update_checkbox_state(checkbox_key, endpoint, is_selected, category, endpoint_name):
    """Handle checkbox state changes to ensure proper selection/deselection"""
    
    # Track previous state in session for checkbox
    prev_state_key = f"{checkbox_key}_prev"
    if prev_state_key not in st.session_state:
        st.session_state[prev_state_key] = is_selected
    
    # Get the checkbox value
    checkbox_value = st.checkbox(
        f"{endpoint_name}",
        value=is_selected,
        key=checkbox_key
    )
    
    # Process changes in checkbox state
    if checkbox_value != st.session_state[prev_state_key]:
        # Update the previous state
        st.session_state[prev_state_key] = checkbox_value
        
        if checkbox_value:  # If checked
            # Add to selected endpoints
            if not is_selected:
                st.session_state["selected_endpoints_for_methods"].append(endpoint)
            # Set as current selection for prompt display
            st.session_state["methods_selected_bullet"] = endpoint_name
            st.session_state["methods_selected_category"] = category
        else:  # If unchecked
            # Remove from selected endpoints
            st.session_state["selected_endpoints_for_methods"] = [
                e for e in st.session_state["selected_endpoints_for_methods"] 
                if e.get("endpoint_id") != endpoint.get("endpoint_id")
            ]
            # Clear selection if this was the selected item
            if st.session_state.get("methods_selected_bullet") == endpoint_name:
                st.session_state["methods_selected_bullet"] = None
                st.session_state["methods_selected_category"] = None
    
    return checkbox_value 
