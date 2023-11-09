from flask import Blueprint, session, render_template, redirect, url_for, request, flash
from firebase_admin_config import admin_firestore as db

views = Blueprint('views', __name__, static_folder='static',
                  template_folder='templates')


def get_user_role():
    return 'student'


@views.route('/')
def index():
    if 'email' in session:
        email = session['email']
        user_role = get_user_role()

        data = db.collection('users').document(email).get()
        user_data = data.to_dict()
        name = user_data['name']
        scholarship = user_data['scholarship']

        if user_role == 'student':
            return render_template('student/index.html', name=name,  scholarship=scholarship, user_role=user_role)
        elif user_role == 'admin':
            return render_template('admin/index.html')
    else:
        return redirect(url_for('auth.login'))


@views.route('/apply', methods=['POST', 'GET'])
def apply():
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    if 'email' in session:
        print(request.method)
        if request.method == 'POST':
            if 'file1' not in request.files or 'file2' not in request.files:
                print('No file uploaded')
                return render_template('student/apply.html', error='No file uploaded')
            f_name = request.form['fName']
            l_name = request.form['lName']
            municipality = request.form['municipality']
            school = request.form['school']
            program = request.form['program']
            year_level = request.form['yearlevel']
            file1 = request.files['file1']
            file2 = request.files['file2']

            try:
                # create student details
                user_data = {
                    'name': f_name + ' ' + l_name,
                    'municipality': municipality,
                    'school': school,
                    'program': program,
                    'year_level': year_level
                }

                print(user_data)
                # Store user details in Firestore
                # db.collection('applicants').document(session['email']).set(user_data)
                result = 'Application Submitted'
            except Exception as e:
                result = e
            return render_template('student/apply.html', message=result)
        return render_template('student/apply.html')
    else:
        return redirect(url_for('auth.login'))
