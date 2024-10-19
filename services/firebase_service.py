import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("../myauth_copy.json")
firebase_admin.initialize_app(cred)

def create_user(email: str, password: str):
    # Create user logic using Firebase
    pass


