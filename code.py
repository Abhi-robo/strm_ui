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
