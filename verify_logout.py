
import os
import django
import json

# Setup Django standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_logout():
    # 1. Create User
    email = "testuser@example.com"
    password = "password123"
    try:
        if not User.objects.filter(email=email).exists():
            print("Creating user...")
            user = User.objects.create_user(email=email, password=password, username=email)
        else:
            print("User exists. Resetting password...")
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
    except Exception as e:
        print(f"Error creating user: {e}")
        return

    client = APIClient()

    # 2. Login (Obtain Tokens)
    print("\n--- Login ---")
    response = client.post('/api/auth/login/', {'email': email, 'password': password}, format='json')
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.content.decode('utf-8'))
        return

    # Handle our custom response format
    try:
        data = response.json()
        if 'data' in data: 
            tokens = data['data']
        else:
            tokens = data
        
        refresh_token = tokens.get('refresh')
        access_token = tokens.get('access')

        if not refresh_token or not access_token:
            print(f"Tokens missing in response: {data}")
            return
            
        print("Login successful. Got tokens.")
    except Exception as e:
        print(f"Error parsing login response: {e}")
        print(response.content.decode('utf-8'))
        return

    # 3. Logout
    print("\n--- Logout ---")
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = client.post('/api/auth/logout/', {'refresh': refresh_token}, format='json')
    print(f"Logout Status: {response.status_code}")
    print(f"Logout Response: {response.content.decode('utf-8')}")

    print("\n--- Verify Refresh Token (Post-Logout) ---")
    try:
        from rest_framework_simplejwt.tokens import RefreshToken, TokenError
        try:
            RefreshToken(refresh_token).check_blacklist()
            print("FAILURE: Refresh token is NOT blacklisted (check_blacklist verified).")
        except TokenError:
            print("SUCCESS: Refresh token is blacklisted/invalid.")
    except ImportError:
        print("SimpleJWT not installed? Skipping token check.")
        pass

    # 6. Verify Access Token (Should fail if we demand immediate revocation, but might pass with stateless JWT)
    print("\n--- Verify Access Token (Post-Logout) ---")
    # Try accessing a protected endpoint. 
    # /api/academic/schedules/today/ requires IsAuthenticated
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = client.get('/api/academic/schedules/today/')
    if response.status_code == 200:
        print(f"OBSERVATION: Access token is STILL VALID for protected endpoint (Expected for stateless JWT). Status: {response.status_code}")
    else:
        print(f"SUCCESS: Access token is INVALID. Status: {response.status_code}")


if __name__ == "__main__":
    test_logout()
