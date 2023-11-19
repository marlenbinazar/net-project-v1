import logging

import pyrebase

config = {
    "apiKey": "AIzaSyAw6ZMNTM2S11i5fNuMKdVfI6s978wjR48",
    "authDomain": "netshards-app.firebaseapp.com",
    "databaseURL": "https://netshards-app-default-rtdb.firebaseio.com",
    "projectId": "netshards-app",
    "storageBucket": "netshards-app.appspot.com",
    "messagingSenderId": "156715781087",
    "appId": "1:156715781087:web:e877ce7c0e8fc55ab6126a",
    "measurementId": "G-719L3Z33G7",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
logger = logging.getLogger(__name__)


def login_and_get_user_data(email, password):
    try:
        # Login and get the user's authentication token
        user = auth.sign_in_with_email_and_password(email, password)
        user_token = user["idToken"]

        # Decode the token to get the user's UID
        decoded_token = auth.verify_id_token(user_token)
        uid = decoded_token["uid"]

        # Fetch user data from the Firebase database
        user_data = db.child("users").child(uid).get().val()

        return user_data, user_token
    except auth.AuthError as e:
        logger.error(f"Firebase Auth Error: {str(e)}")
        return None, None
    except Exception as e:
        logger.error(f"Error fetching user data: {str(e)}")
        return None, None


def register_user(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        print(f"Error creating user: {e}")
        return None
