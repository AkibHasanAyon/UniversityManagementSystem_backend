def standard_response_postprocessor(result, generator, request, public):
    """
    Post-processing hook to wrap all successful responses in the standard envelope:
    {
        "status": "success",
        "message": "Operation successful",
        "data": { ... }
    }
    """
    # Iterate over all paths
    paths = result.get('paths', {})
    if not paths:
        return result

    for path, methods in paths.items():
        for method, operation in methods.items():
            if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                continue
            
            responses = operation.get('responses', {})
            
            # Iterate over status codes
            for status, response in responses.items():
                if not status.startswith('2'):
                    continue
                
                # Check for content
                content = response.get('content', {})
                json_content = content.get('application/json', {})
                original_schema = json_content.get('schema')
                
                if original_schema:
                    # Create the wrapper schema
                    wrapped_schema = {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string', 'example': 'success'},
                            'message': {'type': 'string', 'example': 'Operation successful'},
                            'data': original_schema
                        },
                        'required': ['status', 'message', 'data']
                    }
                    
                    # Update the schema in place
                    json_content['schema'] = wrapped_schema

    return result
