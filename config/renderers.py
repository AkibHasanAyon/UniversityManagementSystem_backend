from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code if renderer_context else 200

        # Check if already formatted (e.g. by exception handler)
        # We look for the standard keys we expect in our envelope.
        if isinstance(data, dict) and 'status' in data and 'message' in data and ('data' in data or 'errors' in data):
             return super().render(data, accepted_media_type, renderer_context)

        if renderer_context:
            # If status is 204 No Content, change to 200 OK so we can return a body
            if renderer_context['response'].status_code == 204:
                renderer_context['response'].status_code = 200
                status_code = 200
                if data is None:
                    data = {}

        response_data = {
            'status': 'success',
            'message': 'Operation successful',
            'data': data
        }

        # Customize message for DELETE requests
        if renderer_context and renderer_context['request'].method == 'DELETE' and status_code < 400:
            response_data['message'] = 'Delete successful'
        
        # Adjust for error status codes if not already handled/formatted
        if status_code >= 400:
            response_data['status'] = 'error'
            response_data['message'] = 'An error occurred'
            response_data['errors'] = data
            if 'data' in response_data:
                del response_data['data']
        
        # Helper to extract message and handle pagination from the original data
        if isinstance(data, dict):
            # We extract message if present
            if 'message' in data:
                response_data['message'] = data.pop('message')
            
            # Handle pagination logic for success responses
            if status_code < 400 and 'results' in data and 'count' in data:
                 response_data['data'] = data['results']
                 response_data['pagination'] = {k: v for k, v in data.items() if k != 'results'}

        return super().render(response_data, accepted_media_type, renderer_context)
