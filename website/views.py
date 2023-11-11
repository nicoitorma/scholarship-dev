from flask import Blueprint, session, render_template, redirect, url_for, request, jsonify
from firebase_admin_config import admin_firestore as db
from pyrebase_config import bucket
from firebase_admin import firestore
import json
from .models import Applicant

views = Blueprint('views', __name__, static_folder='static',
                  template_folder='templates')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def get_applicants_count():
    """
    The function `get_applicants_count` retrieves the number of applicants from a database collection.
    :return: the count of applicants stored in the 'applicants' document in the 'admin' collection in
    the database.
    """
    documents = db.collection('admin').document('applicants').get()
    doc_data = documents.to_dict()
    return len(doc_data)


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
                'scholarship': user['scholarship'],
                'status': user['status']
            }

            return render_template('student/index.html')
        elif user_role == 'admin':
            return admin(user=user)
    else:
        return redirect(url_for('auth.login'))


def is_allowed(filename):
    """
    The function checks if a filename has an allowed extension.

    :param filename: The `filename` parameter is a string that represents the name of a file
    :return: a boolean value. It checks if the given filename has a dot (.) in it and if the file
    extension (the part after the last dot) is in the list of allowed extensions.
    """
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
            email = session['email']
            key = get_applicants_count()

            try:
                # db connections
                doc_ref = db.collection('admin').document('applicants')
                user_ref = db.collection('users').document(email)

                # Storage
                folder_name = '/'.join([str(municipality),
                                       email])
                file1_name = str(folder_name) + '/' + str(file1.filename)
                file2_name = str(folder_name) + '/' + str(file2.filename)

                # Store NOA and COE pic in fbase storage
                bucket.child(file1_name).put(file1, session['idToken'])
                bucket.child(file2_name).put(file2, session['idToken'])

                file1_link = bucket.child(
                    file1_name).get_url(session['idToken'])
                file2_link = bucket.child(
                    file2_name).get_url(session['idToken'])

                # Store user details in Firestore
                doc_ref.update({
                    str(key): {
                        'name': f_name + ' ' + l_name,
                        'municipality': municipality,
                        'school': school,
                        'program': program,
                        'year_level': year_level,
                        'noa_link': file1_link,
                        'coe_link': file2_link,
                        'email': email
                    }
                })

                # Update status of user for scholarship
                user_ref.update({'status': 'Pending'})

                result = 'Application Submitted'
            except Exception as e:
                result = e
            return render_template('student/apply.html', message=result)
        return render_template('student/apply.html')
    else:
        return redirect(url_for('auth.login'))


@views.route('/profile')
def profile():
    return '<h2>TODO: PROFILEEEEEEE</h2>'

# FOR ADMIN


@views.route('/admin')
def admin(user):
    session['user_data'] = {
        'name': user['name'],
        'role': user['role']
    }
    doc1_ref = db.collection('admin').document('municipality')
    doc2_ref = db.collection('admin').document('grantees')
    grantees = db.collection('users').where(
        'scholarship', '!=', 'none')

    doc1_data = doc1_ref.get().to_dict()
    doc2_data = doc2_ref.get().to_dict()

    return render_template('admin/index.html', appli_count=get_applicants_count(), data1=json.dumps(doc1_data), data2=json.dumps(doc2_data))


@views.route('/applicants')
def applicants():
    if 'email' in session:
        documents = db.collection('admin').document('applicants').get()

        applicants = []
        doc_data = documents.to_dict()
        for key, value in doc_data.items():
            applicants.append(Applicant(
                key, value['email'], value['name'], value['municipality'], value['school'], value['program'], value['year_level'], value['noa_link'], value['coe_link']))

        return render_template('admin/applicants.html', applicants=applicants)
    return redirect(url_for('auth.login'))


@views.route('/process_action', methods=['POST'])
def process_action():
    data = request.get_json()
    applicant_id = data['id']
    applicant_email = data['email']
    action = data['action']

    doc_ref = db.collection('admin').document('applicants')
    user_ref = db.collection('users').document(applicant_email)

    if action == 'accept':
        user_ref.update({'status': 'Beneficiary'})
    else:
        user_ref.update({'status': 'Rejected'})

    doc_ref.update({applicant_id: firestore.DELETE_FIELD})

    return redirect(url_for('views.applicants'))


@views.route('/payout')
def payout():
    return '<h2>PAYOUTTTT NAAAA</h2>'
