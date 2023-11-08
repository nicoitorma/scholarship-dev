from flask import Blueprint, render_template, url_for, redirect, request, session
import pyrebase

firebaseConfig = {
    'apiKey': 'AIzaSyB-x4jXcDvyug5Z4c5Zosjum24UavUKWeQ',
    'authDomain': 'qr-attendance-32c1b.firebaseapp.com',
    'databaseURL': 'https://qr-attendance-32c1b-default-rtdb.asia-southeast1.firebasedatabase.app',
    'projectId': 'qr-attendance-32c1b',
    'storageBucket': 'qr-attendance-32c1b.appspot.com',
    'messagingSenderId': '870415657488',
    'appId': '1:870415657488:web:0cfc89d7b6d6e5a09c7895',
    'measurementId': 'G-Z7Z6MPVR9S'
}
cred = pyrebase.initialize_app(firebaseConfig)
firebase = cred.auth()

auth = Blueprint('auth', __name__, static_folder='static',
                 template_folder='templates',)


@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['em']
        password = request.form['pass']
        error = ''
        try:
            user = firebase.sign_in_with_email_and_password(email, password)
            if user:
                session['email'] = email
                session['username'] = user['displayName']
                session['dp'] = user['profilePicture']

                return redirect(url_for('views.dashboard'))
        except:
            error = 'Invalid email or password.'
            return render_template('login.html', error=error)
    else:
        if 'email' in session:
            return redirect(url_for('views.dashboard'))
        return render_template('login.html')
