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

