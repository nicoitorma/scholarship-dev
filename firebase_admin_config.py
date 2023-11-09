import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('./ako-bicol.json')
firebase_admin.initialize_app(cred)
admin_firestore = firestore.client()
