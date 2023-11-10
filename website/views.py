from flask import Blueprint, session, render_template, redirect, url_for, request, g
from firebase_admin_config import admin_firestore as db
from pyrebase_config import bucket
import os
import json

views = Blueprint('views', __name__, static_folder='static',
                  template_folder='templates')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


@views.route('/')
def index():
    if 'email' in session:
        email = session['email']
        data = db.collection('users').document(email).get()
        user = data.to_dict()
        user_role = user['role']

        if user_role == 'student':
            session['user_data'] = {
                'name': user['name'],
                'role': user_role,
                'scholarship': user['scholarship']
            }

            return render_template('student/index.html')
        elif user_role == 'admin':

            session['user_data'] = {
                'name': user['name'],
                'role': user_role,
            }
            doc1_ref = db.collection('admin').document('municipality')
            doc2_ref = db.collection('admin').document('grantees')

            doc1_data = doc1_ref.get().to_dict()
            doc2_data = doc2_ref.get().to_dict()

            return render_template('admin/index.html', data1=json.dumps(doc1_data), data2=json.dumps(doc2_data))
    else:
        return redirect(url_for('auth.login'))


def is_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/apply', methods=['POST', 'GET'])
def apply():
    if 'email' in session:
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

            # create student details
            form_field = {
                'name': f_name + ' ' + l_name,
                'municipality': municipality,
                'school': school,
                'program': program,
                'year_level': year_level
            }

            try:
                # Store user details in Firestore
                db.collection('applicants').document(
                    session['email']).set(form_field)

                # Store NOA and COE pic in fbase storage
                folder_name = '/'.join([str(municipality),
                                       str(session['email'])])
                file1_name = str(folder_name) + '/' + str(file1.filename)
                file2_name = str(folder_name) + '/' + str(file2.filename)

                bucket.child(file1_name).put(file1)
                bucket.child(file2_name).put(file2)

                result = 'Application Submitted'
            except Exception as e:
                result = e
            return render_template('student/apply.html', message=result)
        return render_template('student/apply.html')
    else:
        return redirect(url_for('auth.login'))


# FOR ADMIN

@views.route('/applicants')
def fetch():
    return "<h2>APPLICANTS</h2>"
