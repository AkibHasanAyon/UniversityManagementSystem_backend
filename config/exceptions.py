from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'status': 'error',
            'message': 'An error occurred',
            'errors': response.data
        }

        # Try to extract a more specific message if available
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['message'] = response.data.pop('detail')
            elif 'message' in response.data:
                custom_response_data['message'] = response.data.pop('message')
            
            # If after popping message/detail, response.data is empty, we might want to clean up 'errors'
            if not response.data:
                custom_response_data['errors'] = None
            else:
                 custom_response_data['errors'] = response.data
        elif isinstance(response.data, list):
             # If response.data is a list (e.g. implementation errors), keep it as errors
             pass

        response.data = custom_response_data

    return response
