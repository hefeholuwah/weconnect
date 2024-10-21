import firebase_admin
from firebase_admin import credentials, auth
import asyncio
import os

# Initialize the Firebase Admin SDK with your service account key
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "../myauth_copy.json"))
firebase_admin.initialize_app(cred)

async def verify_firebase_token(token: str):
    """Verify the Firebase ID token asynchronously."""
    try:
        # Since verify_id_token is blocking, we run it in a separate thread
        decoded_token = await asyncio.to_thread(auth.verify_id_token, token)
        return decoded_token  # This will contain user's info (like uid)
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

async def create_user(email: str, password: str):
    """Creates a new user in Firebase."""
    try:
        # Create a user with the specified email and password
        user = await asyncio.to_thread(auth.create_user, email=email, password=password)
        return user
    except Exception as e:
        print(f"Error creating user: {e}")
        raise
