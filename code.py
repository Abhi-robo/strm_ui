@app_routes.route('/save_endpoint_response', methods=['POST'])
def save_endpoint_response():
    """
    Save the endpoint data, including the selected endpoint, category, and response to MongoDB.
    """
    try:
        # Parse the data from the request
        data = request.json
        file_name = data.get("file_name")
        user_query = data.get("user_query")
        assistant_response = data.get("assistant_response")
        citations = data.get("citations", [])
        thread_id = data.get("thread_id")
        selected_bullet = data.get("selected_bullet")
        selected_category = data.get("selected_category")

        # Validate required fields
        if not all([file_name, user_query, assistant_response, selected_bullet, selected_category]):
            return jsonify({
                "error": "Missing required fields. Please provide file_name, user_query, assistant_response, selected_bullet, and selected_category."
            }), 400
            
        # Connect to MongoDB
        db = connect_mongo()
        
        # Save the endpoint data using our dedicated function
        doc_id = save_endpoint_data(
            db,
            file_name,
            selected_category,
            selected_bullet,
            user_query,
            assistant_response,
            citations,
            thread_id
        )

        return jsonify({
            "message": "Endpoint response saved successfully!",
            "document_id": doc_id
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500






















import os
import logging
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_endpoint_data(db, file_name, endpoint_category, endpoint_name, user_query, assistant_response, citations, thread_id=None):
    """
    Save endpoint data to a dedicated collection in MongoDB.
    
    Args:
        db: MongoDB database connection
        file_name (str): The name of the file
        endpoint_category (str): The category the endpoint belongs to
        endpoint_name (str): The selected endpoint name/bullet point
        user_query (str): The user's query/prompt
        assistant_response (str): The assistant's response
        citations (list): List of citations
        thread_id (str, optional): The thread ID from OpenAI

    Returns:
        str: The ID of the inserted/updated document
    """
    # Use a collection specifically for endpoints
    collection = db["endpoints"]
    
    # Create a unique identifier for the endpoint + file combination
    entry_id = f"{file_name}_{endpoint_category}_{endpoint_name}"
    
    # Check if the entry already exists
    existing_entry = collection.find_one({"endpoint_id": entry_id})
    
    document = {
        "endpoint_id": entry_id,
        "file_name": file_name,
        "endpoint_category": endpoint_category,
        "endpoint_name": endpoint_name,
        "user_query": user_query,
        "assistant_response": assistant_response,
        "citations": citations,
        "thread_id": thread_id,
        "updated_at": datetime.utcnow()
    }
    
    if existing_entry:
        # Update the existing entry
        result = collection.update_one(
            {"endpoint_id": entry_id},
            {"$set": document}
        )
        logger.info(f"Updated endpoint data for {entry_id}")
        return str(existing_entry.get("_id"))
    else:
        # Add created_at timestamp for new entries
        document["created_at"] = document["updated_at"]
        
        # Insert a new entry
        result = collection.insert_one(document)
        logger.info(f"Saved new endpoint data for {entry_id}")
        return str(result.inserted_id)

def get_endpoints_by_category(db, file_name, category=None):
    """
    Retrieve endpoints from the database, optionally filtered by category.
    
    Args:
        db: MongoDB database connection
        file_name (str): The name of the file
        category (str, optional): The category to filter by
        
    Returns:
        list: List of endpoint documents
    """
    collection = db["endpoints"]
    
    # Build the query filter
    query = {"file_name": file_name}
    if category:
        query["endpoint_category"] = category
    
    # Retrieve and format the results
    endpoints = list(collection.find(query).sort("created_at", -1))
    
    # Convert MongoDB ObjectId to string for JSON serialization
    for endpoint in endpoints:
        if "_id" in endpoint:
            endpoint["_id"] = str(endpoint["_id"])
    
    return endpoints 




























#UI



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









    elif section_name == "methods":
        # Initialize session state for selected endpoints if not already done
        if "selected_endpoints_for_methods" not in st.session_state:
            st.session_state["selected_endpoints_for_methods"] = []
        
        # Add a button to load endpoints
        if st.button("Load Saved Endpoints for Methods", key="load_endpoints_for_methods"):
            try:
                if st.session_state.file_name:
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
                            st.success(f"Loaded endpoints for {len(categorized_endpoints)} categories")
                        else:
                            st.info("No saved endpoints found. Please generate some endpoints first.")
                    else:
                        st.error(f"Error loading endpoints: {response.json().get('error', 'Unknown error')}")
                else:
                    st.error("Please upload a file first")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        
        # If endpoints are loaded, display them as checkboxes
        if "methods_categorized_endpoints" in st.session_state and st.session_state["methods_categorized_endpoints"]:
            st.subheader("Select Endpoints to Include in Methods Section")
            
            # Display endpoints by category
            for category, endpoints in st.session_state["methods_categorized_endpoints"].items():
                with st.expander(f"Category: {category}"):
                    st.write(f"**{category}** - {len(endpoints)} endpoints available")
                    
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
            
            # Display selected endpoints
            if st.session_state["selected_endpoints_for_methods"]:
                st.subheader("Selected Endpoints")
                for idx, endpoint in enumerate(st.session_state["selected_endpoints_for_methods"]):
                    st.write(f"{idx+1}. **{endpoint.get('endpoint_name')}** ({endpoint.get('endpoint_id').split('_')[1]})")
                
                # Button to generate methods from selected endpoints
                if st.button("Generate Methods from Selected Endpoints"):
                    try:
                        # Prepare payload
                        payload = {
                            'assistant_id': st.session_state.assistant_id,
                            'vector_id': st.session_state.vector_id,
                            'endpoints': st.session_state["selected_endpoints_for_methods"]
                        }
                        
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
                            st.success("Methods section generated successfully!")
                            st.subheader("Generated Methods Section")
                            st.text_area(
                                "Methods Content",
                                methods_content,
                                height=400,
                                key="generated_methods_content"
                            )
                            
                            # Display citations if available
                            if citations:
                                st.subheader("Citations")
                                for i, citation in enumerate(citations):
                                    st.markdown(f"{i+1}. {citation}")
                            
                            # Add a button to save the generated methods
                            if st.button("Save Generated Methods"):
                                save_payload = {
                                    'file_name': st.session_state.file_name,
                                    'user_query': "Generated from selected endpoints",
                                    'assistant_response': methods_content,
                                    'citations': citations,
                                    'thread_id': thread_id
                                }
                                
                                save_response = requests.post(f"{API_BASE_URL}/methods/save_methods_response", json=save_payload)
                                
                                if save_response.status_code == 200:
                                    st.success("Methods saved successfully!")
                                else:
                                    st.error(f"Error saving methods: {save_response.json().get('error', 'Unknown error')}")
                        else:
                            st.error(f"Error generating methods: {response.json().get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
























@methods_bp.route('/get_endpoints_for_methods', methods=['GET'])
def get_endpoints_for_methods():
    """
    Retrieve all endpoints from the endpoints collection for display in the Methods section.
    """
    try:
        # Get file_name from query parameters
        file_name = request.args.get('file_name')
        
        if not file_name:
            return jsonify({"error": "file_name parameter is required"}), 400
            
        # Connect to MongoDB
        db = connect_mongo()
        
        # Access the endpoints collection
        collection = db["endpoints"]
        
        # Query all endpoints for this file
        endpoints = list(collection.find({"file_name": file_name}).sort("endpoint_category", 1))
        
        # Process endpoints into a more structured format by category
        categorized_endpoints = {}
        
        for endpoint in endpoints:
            # Convert ObjectId to string for JSON serialization
            if "_id" in endpoint:
                endpoint["_id"] = str(endpoint["_id"])
            
            # Get the category
            category = endpoint.get("endpoint_category")
            
            # Initialize the category list if it doesn't exist
            if category not in categorized_endpoints:
                categorized_endpoints[category] = []
            
            # Add the endpoint to its category
            categorized_endpoints[category].append({
                "endpoint_id": endpoint.get("endpoint_id"),
                "endpoint_name": endpoint.get("endpoint_name"),
                "assistant_response": endpoint.get("assistant_response"),
                "updated_at": endpoint.get("updated_at").isoformat() if endpoint.get("updated_at") else None
            })
        
        return jsonify({
            "endpoints": categorized_endpoints,
            "count": len(endpoints)
        }), 200
    
    except Exception as e:
        logger.error(f"Error in get_endpoints_for_methods: {str(e)}")
        return jsonify({"error": str(e)}), 500




































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
            if "methods_categorized_endpoints" in st.session_state:
                endpoint_count = sum(len(endpoints) for endpoints in st.session_state["methods_categorized_endpoints"].values())
                st.markdown(f"**{endpoint_count}** endpoints loaded from **{len(st.session_state['methods_categorized_endpoints'])}** categories")
        
        if load_button:
            try:
                if st.session_state.file_name:
                    # Show loading message
                    with st.spinner("Loading endpoints..."):
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
                                st.success(f"Loaded {total_endpoints} endpoints from {len(categorized_endpoints)} categories")
                            else:
                                st.info("No saved endpoints found. Please generate endpoints in the Results section first.")
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
        if "methods_categorized_endpoints" in st.session_state and st.session_state["methods_categorized_endpoints"]:
            st.subheader("Select Endpoints to Include in Methods Section")
            
            # Display endpoints by category
            for category, endpoints in st.session_state["methods_categorized_endpoints"].items():
                # Display category as a heading
                st.markdown(f"### {category} ({len(endpoints)} endpoints)")
                
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
                
                # Add some spacing between categories
                st.markdown("---")
            
            # Display selected endpoints
            if st.session_state["selected_endpoints_for_methods"]:
                st.markdown("## Selected Endpoints")
                
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
                    st.markdown(f"### {category}")
                    for endpoint in endpoints:
                        st.markdown(f"- **{endpoint.get('endpoint_name')}**")
                
                # Button to generate methods from selected endpoints
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("Generate Methods from Selected Endpoints", type="primary"):
                        try:
                            # Prepare payload
                            payload = {
                                'assistant_id': st.session_state.assistant_id,
                                'vector_id': st.session_state.vector_id,
                                'endpoints': st.session_state["selected_endpoints_for_methods"]
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
            st.markdown("## Generated Methods Section")
            
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
            if "methods_categorized_endpoints" in st.session_state:
                endpoint_count = sum(len(endpoints) for endpoints in st.session_state["methods_categorized_endpoints"].values())
                st.markdown(f"**{endpoint_count}** endpoints loaded from **{len(st.session_state['methods_categorized_endpoints'])}** categories")
                # Show the file we're working with
                if st.session_state.file_name:
                    st.markdown(f"File: **{st.session_state.file_name}**")
        
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
                
                # Removed spacing between categories

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




















@methods_bp.route('/get_endpoints_for_methods', methods=['GET'])
def get_endpoints_for_methods():
    """
    Retrieve all endpoints from the endpoints collection for display in the Methods section.
    """
    try:
        # Get file_name from query parameters
        file_name = request.args.get('file_name')
        
        if not file_name:
            return jsonify({"error": "file_name parameter is required"}), 400
            
        # Connect to MongoDB
        db = connect_mongo()
        
        # Access the endpoints collection
        collection = db["endpoints"]
        
        # Query all endpoints for this file - make sure we're filtering by the file_name
        file_filter = {"file_name": file_name}
        endpoints = list(collection.find(file_filter).sort("endpoint_category", 1))
        
        # Log the search and results
        logger.info(f"Searching for endpoints with file_name: {file_name}")
        logger.info(f"Found {len(endpoints)} endpoints for file: {file_name}")
        
        # Process endpoints into a more structured format by category
        categorized_endpoints = {}
        
        for endpoint in endpoints:
            # Convert ObjectId to string for JSON serialization
            if "_id" in endpoint:
                endpoint["_id"] = str(endpoint["_id"])
            
            # Get the category
            category = endpoint.get("endpoint_category")
            
            # Initialize the category list if it doesn't exist
            if category not in categorized_endpoints:
                categorized_endpoints[category] = []
            
            # Add the endpoint to its category
            categorized_endpoints[category].append({
                "endpoint_id": endpoint.get("endpoint_id"),
                "endpoint_name": endpoint.get("endpoint_name"),
                "assistant_response": endpoint.get("assistant_response"),
                "updated_at": endpoint.get("updated_at").isoformat() if endpoint.get("updated_at") else None
            })
        
        return jsonify({
            "endpoints": categorized_endpoints,
            "count": len(endpoints),
            "file_name": file_name  # Return file_name for confirmation
        }), 200
    
    except Exception as e:
        logger.error(f"Error in get_endpoints_for_methods: {str(e)}")
        return jsonify({"error": str(e)}), 500


@methods_bp.route('/generate_methods_from_endpoints', methods=['POST'])
def generate_methods_from_endpoints():
    """
    Generate Methods section content based on selected endpoints.
    """
    try:
        data = request.json
        assistant_id = data.get('assistant_id')
        vector_id = data.get('vector_id')
        endpoints = data.get('endpoints', [])
        file_name = data.get('file_name')
        
        if not assistant_id or not vector_id:
            return jsonify({"error": "Missing assistant_id or vector_id"}), 400
            
        if not endpoints:
            return jsonify({"error": "No endpoints provided"}), 400
            
        if not file_name:
            return jsonify({"error": "Missing file_name"}), 400
            
        # Log received data
        logger.info(f"Generating methods for file: {file_name}")
        logger.info(f"Number of endpoints: {len(endpoints)}")
        
        # Initialize OpenAI client
        client = OpenAI()
        
        # Initialize AssistantSession
        assistant_session = AssistantSession(client, assistant_id, vector_id)
        
        # Create a prompt that incorporates the endpoint data
        endpoint_details = []
        for endpoint in endpoints:
            endpoint_name = endpoint.get('endpoint_name')
            endpoint_category = endpoint.get('endpoint_id', '').split('_')[1] if endpoint.get('endpoint_id') else 'Unknown'
            endpoint_response = endpoint.get('assistant_response')
            
            # Add formatted endpoint details to the list
            endpoint_details.append(f"Category: {endpoint_category}\nEndpoint: {endpoint_name}\nDetails: {endpoint_response}\n")
        
        # Combine all endpoint details
        all_endpoint_details = "\n\n".join(endpoint_details)
        
        # Create the main prompt for methods generation, including file name
        methods_prompt = f"""
        Please generate a comprehensive Methods section for the clinical trial manuscript in file: {file_name}
        
        Base your Methods section on the following endpoint information:
        
        {all_endpoint_details}
        
        Please follow these guidelines:
        
        1. Organize the information under clear headings (e.g., 'Study Design,' 'Participants,' 'Interventions,' 'Outcomes,' etc.)
        2. Ensure all the selected endpoints are properly described in the appropriate sections
        3. Use academic language and appropriate terminology
        4. Reference standard guidelines where appropriate (e.g., CONSORT)
        5. Provide enough detail that another researcher could replicate or cite the study
        6. Integrate the information from different endpoints in a coherent and logical manner
        """
        
        # Run the query to generate methods content
        methods_content, citations, thread_id = assistant_session.run_query(methods_prompt, dependent=False)
        
        return jsonify({
            "methods_content": methods_content,
            "citations": citations,
            "thread_id": thread_id,
            "file_name": file_name
        }), 200
        
    except Exception as e:
        logger.error(f"Error in generate_methods_from_endpoints: {str(e)}")
        return jsonify({"error": str(e)}), 500





