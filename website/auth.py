from flask import Blueprint, render_template, url_for, redirect, request, session
from pyrebase_config import user_auth
from firebase_admin_config import admin_firestore as db
from requests.exceptions import RequestException

auth = Blueprint('auth', __name__, static_folder='static',
                 template_folder='templates',)


@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['em']
        password = request.form['password']
        error = ''
        try:
            user = user_auth.sign_in_with_email_and_password(email, password)
            if user:
                session['email'] = email
                session['username'] = user['displayName']
                session['idToken'] = user['idToken']

            return redirect(url_for('views.index'))

        except Exception:
            error = 'Incorrect email or password.'
        return render_template('login.html', error=error)
    else:
        if 'email' in session:
            return redirect(url_for('views.index'))
        return render_template('login.html')


@auth.route('/register', methods=['POST', 'GET'])
def register():
    result = ''
    if request.method == 'POST':
        f_name = request.form['fName']
        l_name = request.form['lName']
        email = request.form['em']
        password = request.form['repeatPassword']

        try:
            # create student authentication
            user = user_auth.create_user_with_email_and_password(
                email=email, password=password)

            # create student details
            user_data = {
                'name': f_name + ' ' + l_name,
                'role': 'student',
                'scholarship': 'None',
                'status': 'None',
                'email': email
            }

            # Store user details in Firestore
            db.collection('users').document(
                user['email']).set(user_data)
            result = 'Account successfully created'
        except Exception as e:
            return render_template('register.html', error=e)
        return render_template('register.html', message=result)
    else:
        return render_template('register.html')


@auth.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    session.pop('user_data', None)
    return redirect(url_for('auth.login'))


@auth.route('/forgot-password')
def forgot_pass():
    return render_template('forgot-password.html')
