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
    
    # New session states for endpoint response management
    if "endpoint_responses" not in st.session_state:
        st.session_state["endpoint_responses"] = {}  # Dictionary to store responses by endpoint
    
    if "current_prompt_is_subgroup" not in st.session_state:
        st.session_state["current_prompt_is_subgroup"] = False
        
    if "methods_categorized_endpoints" not in st.session_state:
        st.session_state["methods_categorized_endpoints"] = {}
    
    # Session states for subgroup analysis selection
    if "selected_subgroup_analyses" not in st.session_state:
        st.session_state["selected_subgroup_analyses"] = {}
        
    if "selected_endpoints_for_methods" not in st.session_state:
        st.session_state["selected_endpoints_for_methods"] = []
    
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
            
    # Clear endpoint response management data
    st.session_state["endpoint_responses"] = {}
    st.session_state["current_prompt_is_subgroup"] = False
    st.session_state["methods_categorized_endpoints"] = {}
    
    # Clear subgroup related session state
    st.session_state["selected_subgroup_analyses"] = {}
    st.session_state["selected_endpoints_for_methods"] = []
    
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
                
                # Check if the selected prompt is a subgroup prompt
                st.session_state["current_prompt_is_subgroup"] = is_subgroup_prompt(prompt_selection)
                
                st.write("Selected Prompt:")
                st.markdown(prompt_selection)
                
                # Show subgroup detection status
                if st.session_state["current_prompt_is_subgroup"]:
                    st.markdown("**📊 Subgroup Analysis Detected**")
                
                # Set user_query as the selected prompt
                st.session_state['user_query'] = prompt_selection  # Save the selected prompt as user_query

                checkbox_dependent = st.checkbox("Dependent on threads", value=True)
                st.session_state["checkbox_dependent"] = checkbox_dependent

                get_checkbox_dependent_status = lambda: "ON" if st.session_state['checkbox_dependent'] else "OFF"

                # Display the conversation status
                st.write(f"Conversation: {get_checkbox_dependent_status()}")

                # Show "Run for selected prompts for checkbox" button
                if st.button("Run for selected prompt"):
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
                    # Show a view of existing responses for this endpoint
                    endpoint_key = st.session_state["selected_bullet"]
                    
                    # Create a list to store responses for this endpoint if it doesn't exist
                    if endpoint_key in st.session_state["endpoint_responses"]:
                        with st.expander(f"View saved responses for this endpoint ({len(st.session_state['endpoint_responses'][endpoint_key])} responses)"):
                            for i, resp in enumerate(st.session_state["endpoint_responses"][endpoint_key]):
                                st.markdown(f"**Prompt {i+1}:** {resp['prompt_text'][:100]}...")
                                is_subgroup = "Yes" if resp["is_subgroup"] else "No"
                                st.markdown(f"**Subgroup Analysis:** {is_subgroup}")
                                st.markdown("**Response Preview:**")
                                st.markdown(resp["response"][:200] + "..." if len(resp["response"]) > 200 else resp["response"])
                                st.markdown("---")

                    if st.button("Save Response", key="save_checkbox_response_button"): 
                        # Create a response object with metadata
                        response_obj = {
                            "prompt_text": st.session_state.user_query,
                            "response": response_text,
                            "is_subgroup": st.session_state["current_prompt_is_subgroup"],
                            "citations": citations,
                            "thread_id": st.session_state.current_checkbox_thread_id
                        }
                        
                        # Add to endpoint responses in session state
                        if endpoint_key not in st.session_state["endpoint_responses"]:
                            st.session_state["endpoint_responses"][endpoint_key] = []
                        
                        # Add the new response to the list
                        st.session_state["endpoint_responses"][endpoint_key].append(response_obj)
                        
                        # Prepare payload for backend
                        payload = {
                            'file_name': st.session_state.file_name,
                            'user_query': st.session_state.user_query,
                            'assistant_response': response_text,
                            'citations': citations,
                            'thread_id': st.session_state.current_checkbox_thread_id,
                            'selected_bullet': st.session_state.selected_bullet,
                            'selected_category': st.session_state.selected_category,
                            'is_subgroup': st.session_state["current_prompt_is_subgroup"]
                        }
                        try:
                            # Use the endpoint-specific API
                            save_response = requests.post(f"{API_BASE_URL}/save_endpoint_response", json=payload)
                            if save_response.status_code == 200:
                                st.success("Endpoint response saved successfully!")
                            else:
                                st.error(f"Error saving response: {save_response.json().get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"An error occurred: {e}")



    # Update the Methods section to display available subgroup analyses
    elif section_name == "methods":
        # Initialize session state for selected endpoints if not already done
        if "selected_endpoints_for_methods" not in st.session_state:
            st.session_state["selected_endpoints_for_methods"] = []
        
        # Initialize session state for selected subgroup analyses
        if "selected_subgroup_analyses" not in st.session_state:
            st.session_state["selected_subgroup_analyses"] = {}
        
        # Add a button to load endpoints
        col1, col2 = st.columns([1, 3])
        with col1:
            load_button = st.button("Load Saved Endpoints", key="load_endpoints_for_methods", type="primary")
        with col2:
            if "methods_categorized_endpoints" in st.session_state and st.session_state.get("methods_categorized_endpoints"):
                endpoint_count = sum(len(endpoints) for endpoints in st.session_state["methods_categorized_endpoints"].values())
                st.markdown(f"**{endpoint_count}** endpoints loaded from **{len(st.session_state['methods_categorized_endpoints'])}** categories")
                # Show the file we're working with
                if st.session_state.file_name:
                    st.markdown(f"File: **{st.session_state.file_name}**")
            else:
                st.markdown("No endpoints loaded yet. Click to load endpoints.")
        
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
            3. For endpoints with available subgroup analyses, you can select those as well
            4. Click "Generate Methods from Selected Endpoints" to create your Methods section
            """)
            
            # Display "Available Subgroup Analyses" section if we have any in session_state
            if st.session_state.get("endpoint_responses"):
                with st.expander("Available Subgroup Analyses from Results", expanded=True):
                    st.markdown("### Subgroup Analyses")
                    st.markdown("Check the box next to any subgroup analysis you want to include in your Methods section:")
                    
                    # Display subgroup analyses from endpoint_responses
                    has_subgroups = False
                    
                    for endpoint, responses in st.session_state["endpoint_responses"].items():
                        # Filter only subgroup responses
                        subgroup_responses = [r for r in responses if r.get("is_subgroup")]
                        
                        if subgroup_responses:
                            has_subgroups = True
                            st.markdown(f"#### {endpoint}")
                            
                            for i, resp in enumerate(subgroup_responses):
                                checkbox_key = f"subgroup_{endpoint}_{i}"
                                
                                # Check if already selected
                                is_selected = endpoint in st.session_state["selected_subgroup_analyses"] and i in st.session_state["selected_subgroup_analyses"][endpoint]
                                
                                if st.checkbox(
                                    f"Subgroup Analysis {i+1}: {resp['prompt_text'][:100]}...",
                                    value=is_selected,
                                    key=checkbox_key
                                ):
                                    # Add to selected subgroups
                                    if endpoint not in st.session_state["selected_subgroup_analyses"]:
                                        st.session_state["selected_subgroup_analyses"][endpoint] = []
                                    
                                    if i not in st.session_state["selected_subgroup_analyses"][endpoint]:
                                        st.session_state["selected_subgroup_analyses"][endpoint].append(i)
                                else:
                                    # Remove from selected subgroups if unchecked
                                    if endpoint in st.session_state["selected_subgroup_analyses"] and i in st.session_state["selected_subgroup_analyses"][endpoint]:
                                        st.session_state["selected_subgroup_analyses"][endpoint].remove(i)
                                
                                # Show a preview of the response
                                with st.expander(f"Preview Response {i+1}"):
                                    st.markdown(resp["response"])
                    
                    if not has_subgroups:
                        st.markdown("No subgroup analyses available yet. Generate subgroup analyses in the Results section first.")

        # Display selected endpoints
        selected_endpoint = None
        selected_category = None

        # If endpoints are loaded, display them as checkboxes
        if "methods_categorized_endpoints" in st.session_state and st.session_state["methods_categorized_endpoints"]:
            st.subheader("Select Endpoints to Include in Methods Section")
            
            # Display endpoints by category
            for category, endpoints in st.session_state["methods_categorized_endpoints"].items():
                # Display category as a heading
                st.subheader(category)  # Use subheader instead of markdown for consistency with display_endpoints
                
                # Display all endpoints in this category as checkboxes
                for endpoint in endpoints:
                    endpoint_id = endpoint.get("endpoint_id")
                    endpoint_name = endpoint.get("endpoint_name")
                    
                    # Create a unique key for this checkbox
                    checkbox_key = f"methods_endpoint_{endpoint_id}"
                    
                    # Check if this endpoint is already selected
                    is_selected = endpoint_id in [e.get("endpoint_id") for e in st.session_state["selected_endpoints_for_methods"]]
                    
                    # Display checkbox
                    if st.checkbox(
                        f"{endpoint_name}",
                        value=is_selected,
                        key=checkbox_key
                    ):
                        # Set selected endpoint
                        selected_endpoint = endpoint_name
                        selected_category = category

                        # Store in session state
                        st.session_state["selected_bullet"] = endpoint_name
                        st.session_state["selected_category"] = category
                        
                        # If checked and not already in the list, add it
                        if not is_selected:
                            st.session_state["selected_endpoints_for_methods"].append(endpoint)
                    else:
                        # If unchecked and in the list, remove it
                        if is_selected:
                            st.session_state["selected_endpoints_for_methods"] = [
                                e for e in st.session_state["selected_endpoints_for_methods"] 
                                if e.get("endpoint_id") != endpoint_id
                            ]
            
            # If an endpoint is selected, show the prompt selection
            if selected_endpoint or st.session_state.get("selected_bullet"):
                # Use session state if not set directly
                if not selected_endpoint:
                    selected_endpoint = st.session_state.get("selected_bullet")
                if not selected_category:
                    selected_category = st.session_state.get("selected_category")
                
                st.markdown("---")
                st.header("Prompt Selection")
                st.write(f"You selected: {selected_endpoint}")
                
                # Methods section specific prompts
                methods_prompts = [
                    f"1. Summarise study design: Based upon the methods sections of the report please can you provide details of the trial design, including the number of centres it was conducted in and also the countries it was conducted in. Please can you provide this information as a bulleted list",

                    f"2. Inclusion criteria: Please can you summarise the inclusion criteria for patients in the study. Please can you provide this information as a bulleted list {selected_endpoint}",

                    f"3. Exclusion criteria: Please can you summarise {selected_endpoint} the exclusion criteria for patients in the study. Please can you provide this information as a bulleted list",

                    f"4. Ethics criteria: Please can you provide details of ethical approval for this trial, and also funding. Please can you provide this information as a bulleted list",

                    f"5. Randomisation: Please can you provide details of how people were randomised in the study, including the tool used for randomisation and any stratification. Please can you provide this information as a bulleted list",

                    f"6. Study structure: Please can you provide details of how the study was structured, including details of each different study period. Please can you provide this information as a bulleted list",

                    f"7. Treatment: Please can you provide details of how patients received the treatment. Please can you provide this information as a bulleted list",

                    f"8. Endpoints: Please can you provide details of the outcome {selected_endpoint}. Please can you provide details, including how and when they are evaluated. For when they were evaluated please can you provide exact timepoints (i.e. which days or weeks). Please can you provide this information as a bulleted list.",

                    f"9. Endpoints: Please can you provide details of the outcome {selected_endpoint}. Please can you provide details for any subgroups evaluated, if any, including how and when they are evaluated. For when they were evaluated please can you provide exact timepoints (i.e. which days or weeks). Please can you provide this information as a bulleted list",

                    f"10. Trial amendments: Please can you provide this information as a bulleted list"
                ]
                
                # Show a section for selected subgroup analyses if available
                endpoint_key = selected_endpoint
                if endpoint_key in st.session_state.get("selected_subgroup_analyses", {}) and st.session_state["selected_subgroup_analyses"][endpoint_key]:
                    st.markdown("### Selected Subgroup Analyses for this Endpoint")
                    selected_indices = st.session_state["selected_subgroup_analyses"][endpoint_key]
                    
                    if endpoint_key in st.session_state.get("endpoint_responses", {}):
                        responses = st.session_state["endpoint_responses"][endpoint_key]
                        subgroup_responses = [r for i, r in enumerate(responses) if r.get("is_subgroup") and i in selected_indices]
                        
                        for i, resp in enumerate(subgroup_responses):
                            st.markdown(f"**Subgroup Analysis {i+1}**: {resp['prompt_text'][:100]}...")
                            with st.expander(f"View Response"):
                                st.markdown(resp["response"])
                
                prompt_selection = st.selectbox(
                    "Select a Prompt for Methods Section",
                    methods_prompts,
                    key="methods_prompt_selector"
                )
                
                st.write("Selected Prompt:")
                st.markdown(prompt_selection)
                
                # Set user_query as the selected prompt
                st.session_state['user_query'] = prompt_selection  # Save the selected prompt as user_query

                # Add dependent/independent thread option
                col1, col2 = st.columns([1, 2])
                with col1:
                    checkbox_dependent = st.checkbox("Dependent on threads", value=True, key=f"methods_dependent_checkbox")
                    st.session_state["checkbox_dependent"] = checkbox_dependent
                
                with col2:
                    get_checkbox_dependent_status = lambda: "ON" if st.session_state['checkbox_dependent'] else "OFF"
                    st.write(f"Thread Dependency: {get_checkbox_dependent_status()}")
                
                # Show "Run prompt" button
                if st.button("Run Selected Prompt", key=f"methods_run_prompt"):
                    # Store the current selection to restore later
                    temp_selected_bullet = st.session_state["selected_bullet"]
                    temp_selected_category = st.session_state["selected_category"]
                    
                    checkbox_user_query = st.session_state.get('user_query', '')
                    
                    if checkbox_user_query:
                        try:
                            # Clear previous response and citations from the session state
                            st.session_state["checkbox_response"] = ""
                            st.session_state["checkbox_citations"] = []

                            # Append any selected subgroup information to the query if this is a subgroup-related prompt
                            if "subgroup" in checkbox_user_query.lower() and endpoint_key in st.session_state.get("selected_subgroup_analyses", {}):
                                subgroup_info = "\n\nInclude the following subgroup analyses:\n"
                                
                                if endpoint_key in st.session_state.get("endpoint_responses", {}):
                                    responses = st.session_state["endpoint_responses"][endpoint_key]
                                    selected_indices = st.session_state["selected_subgroup_analyses"].get(endpoint_key, [])
                                    
                                    for i, resp in enumerate(responses):
                                        if resp.get("is_subgroup") and i in selected_indices:
                                            subgroup_info += f"- {resp['prompt_text']}\n"
                                
                                checkbox_user_query += subgroup_info

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
                    response_text = st.text_area("Response:", st.session_state["checkbox_response"], height=200, key="methods_response_text")
                    citations = st.session_state["checkbox_citations"]

                    if st.session_state.current_checkbox_thread_id:
                        st.markdown(f"**Thread ID:** {st.session_state.current_checkbox_thread_id}")

                    if "user_query" in st.session_state and st.session_state["checkbox_response"]:
                        # Save Response Button
                        if st.button("Save Response", key="save_methods_response_button"): 
                            payload = {
                                'file_name': st.session_state.file_name,
                                'user_query': st.session_state.user_query,
                                'assistant_response': response_text,
                                'citations': citations,
                                'thread_id': st.session_state.current_checkbox_thread_id,
                                'selected_bullet': st.session_state.selected_bullet,
                                'selected_category': st.session_state.selected_category,
                                'selected_subgroups': st.session_state.get("selected_subgroup_analyses", {}).get(endpoint_key, [])
                            }
                            try:
                                # Use the methods-specific API
                                save_response = requests.post(f"{API_BASE_URL}/methods/save_methods_response", json=payload)
                                if save_response.status_code == 200:
                                    st.success("Methods response saved successfully!")
                                else:
                                    st.error(f"Error saving response: {save_response.json().get('error', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"An error occurred: {e}")




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

# Regex-Based Subgroup Prompt Detection
def is_subgroup_prompt(prompt_text: str) -> bool:
    """
    Check if a prompt is related to subgroup analysis using regex.
    
    Args:
        prompt_text: The text of the prompt to check
        
    Returns:
        bool: True if the prompt is related to subgroup analysis, False otherwise
    """
    pattern = r"\b(subgroup[s]?|sub-group[s]?|sub group[s]?)\b"
    return bool(re.search(pattern, prompt_text, flags=re.IGNORECASE))


