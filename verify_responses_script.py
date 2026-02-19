
import os
import django
import json

# Setup Django standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

# Import our custom components to ensure they are used (though settings should handle it)
# We will rely on settings configuration mostly, but the test needs to simulate a request through a view that uses these settings.
# By default, APIView uses settings.DEFAULT_RENDERER_CLASSES.

def reproduce():
    factory = APIRequestFactory()
    
    print("--- 1. Success Response (Mock View) ---")
    class MockSuccessView(APIView):
        permission_classes = [AllowAny]
        def get(self, request):
            return Response({'some_data': 'value'})
    
    view = MockSuccessView.as_view()
    request = factory.get('/')
    response = view(request)
    if hasattr(response, 'render'):
        response.render()
    print(response.content.decode('utf-8'))

    print("\n--- 2. Error Response (Mock View - ValidationError) ---")
    class MockErrorView(APIView):
        permission_classes = [AllowAny]
        def get(self, request):
            raise ValidationError({'field': ['Invalid value']})

    view = MockErrorView.as_view()
    request = factory.get('/')
    try:
        response = view(request)
        if hasattr(response, 'render'):
            response.render()
        print(response.content.decode('utf-8'))
    except Exception as e:
        # DRF views handle exceptions internally, but if we call view(request) directly in test without full middleware stack, 
        # exceptions might propagate depending on how test client is used. 
        # APIRequestFactory doesn't process middleware. 
        # APIView.dispatch handles exceptions. So it should return a response.
        # Let's see if our configured exception handler picks it up.
        from rest_framework.views import exception_handler
        # We need to manually call the configured handler if the view doesn't (which it should if using APIView)
        # Wait, APIView.dispatch calls handle_exception which calls settings.EXCEPTION_HANDLER.
        # So if MockErrorView inherits APIView, it should use our handler.
        print(f"Caught exception outside view: {e}")
        # Manually invoke for demonstration if needed, but ideally view handles it.
        # The issue might be that APIView re-raises if it's not a DRF exception OR if we are in DEBUG mode? 
        # APIView catches APIException. ValidationError is APIException.
        pass

if __name__ == "__main__":
    reproduce()
