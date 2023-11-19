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


def get_user_data_from_firebase(user_token):
    try:
        # Decode the token to get the user's UID
        uid = auth.verify_id_token(user_token)["uid"]

        # Fetch user data from the Firebase database
        user_data = db.child("users").child(uid).get().val()

        return user_data
    except Exception as e:
        print(f"Error fetching user data: {str(e)}")
        return None


def register_user(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        print(f"Error logging in: {e}")
        return None


def get_user_token(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user["idToken"]
    except Exception as e:
        print(f"Error getting user token: {e}")
        return None
