import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Base URL
BASE_URL = 'http://127.0.0.1:8000/api/auth'

def test_auth_flow():
    # 1. Create Test User
    email = "test@uni.edu"
    password = "password123"
    try:
        user = User.objects.get(email=email)
        user.delete()
        print("Previous test user deleted.")
    except User.DoesNotExist:
        pass

    user = User.objects.create_user(username="test_user", email=email, password=password, role='student')
    print(f"Test user created: {email} / {password}")

    # 2. Login
    print("\n--- Testing Login ---")
    response = requests.post(f"{BASE_URL}/login/", data={'email': email, 'password': password})
    if response.status_code == 200:
        print("Login Successful!")
        data = response.json()
        access = data.get('access')
        refresh = data.get('refresh')
        user_info = data.get('user')
        print(f"User Info: {user_info}")
        if not access or not refresh:
            print("FAILED: Missing tokens")
            return
    else:
        print(f"Login Failed: {response.content}")
        return

    # 3. Refresh Token
    print("\n--- Testing Token Refresh ---")
    response = requests.post(f"{BASE_URL}/refresh/", data={'refresh': refresh})
    if response.status_code == 200:
        print("Token Refresh Successful!")
        new_access = response.json().get('access')
        print(f"New Access Token: {new_access[:10]}...")
    else:
        print(f"Refresh Failed: {response.content}")

    # 4. Password Reset Request
    print("\n--- Testing Password Reset Request ---")
    response = requests.post(f"{BASE_URL}/forgot-password/", data={'email': email})
    if response.status_code == 200:
        print("Reset Request Successful! (Check console for email)")
    else:
        print(f"Reset Request Failed: {response.content}")

    # 5. Logout
    print("\n--- Testing Logout ---")
    headers = {'Authorization': f'Bearer {access}'}
    response = requests.post(f"{BASE_URL}/logout/", data={'refresh': refresh}, headers=headers)
    if response.status_code == 204:
        print("Logout Successful!")
    else:
        print(f"Logout Failed: {response.content}")

if __name__ == "__main__":
    test_auth_flow()
