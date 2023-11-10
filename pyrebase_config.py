import pyrebase

config = {
    'apiKey': "AIzaSyDfDh0fBA4OmCDWreHKHPA2DamVlS7jqyw",
    'authDomain': "ako-bicol-a5403.firebaseapp.com",
    'projectId': "ako-bicol-a5403",
    'storageBucket': "ako-bicol-a5403.appspot.com",
    'messagingSenderId': "126824501150",
    'appId': "1:126824501150:web:7130b88bc6e141ff3fd08f",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(config)
user_auth = firebase.auth()
bucket = firebase.storage()
