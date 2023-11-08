from flask import Blueprint, render_template, url_for, redirect, request, session
import pyrebase

firebaseConfig = {
    'apiKey': "AIzaSyDfDh0fBA4OmCDWreHKHPA2DamVlS7jqyw",
    'authDomain': "ako-bicol-a5403.firebaseapp.com",
    'projectId': "ako-bicol-a5403",
    'storageBucket': "ako-bicol-a5403.appspot.com",
    'messagingSenderId': "126824501150",
    'appId': "1:126824501150:web:7130b88bc6e141ff3fd08f",
    "databaseURL": ""
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

                return redirect(url_for('views.index'))
        except:
            error = 'Invalid email or password.'
            return render_template('login.html', error=error)
    else:
        if 'email' in session:
            return redirect(url_for('views.index'))
        return render_template('login.html')


@auth.route('/register', methods=['POST', 'GET'])
def register():
    return render_template('register.html')


@auth.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    return redirect(url_for('auth.login'))


@auth.route('/forgot-password')
def forgot_pass():
    return render_template('forgot-password.html')
