from flask import Blueprint, session, render_template, redirect, url_for, request, jsonify
from firebase_admin_config import admin_firestore as db
from pyrebase_config import bucket
from firebase_admin import firestore
import json
from .models import Applicant

views = Blueprint('views', __name__, static_folder='static',
                  template_folder='templates')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
STUDENT_ROLE = 'student'
ADMIN_ROLE = 'admin'


def get_applicants_count():
    """
    Retrieve the number of applicants from the 'applicants' document in the 'admin' collection.
    :return: The count of applicants.
    """
    documents = db.collection('admin').document('applicants').get()
    doc_data = documents.to_dict()
    return len(doc_data)


def is_allowed(filename):
    """
    Check if a filename has an allowed extension.

    :param filename: The name of a file.
    :return: A boolean indicating whether the filename has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/')
def index():
    if 'email' in session:
        email = session['email']
        data = db.collection('users').document(email).get()
        user = data.to_dict()
        user_role = user.get('role', '')

        if user_role == STUDENT_ROLE:
            session['user_data'] = {
                'name': user.get('name', ''),
                'role': user_role,
                'scholarship': user.get('scholarship', ''),
                'status': user.get('status', '')
            }
            return render_template('student/index.html')
        elif user_role == ADMIN_ROLE:
            return admin(user=user)
    else:
        return redirect(url_for('auth.login'))


def handle_file_upload(file, folder_name):
    """
    Handle file upload to Firebase storage.

    :param file: The file to be uploaded.
    :param folder_name: The folder name in which to store the file.
    :return: The file link in the Firebase storage.
    """
    file_name = f"{folder_name}/{file.filename}"
    bucket.child(file_name).put(file, session['idToken'])
    return bucket.child(file_name).get_url(session['idToken'])


@views.route('/apply', methods=['POST', 'GET'])
def apply():
    if 'email' in session and session['user_data'].get('status', '') == 'None':
        if request.method == 'POST':
            if 'file1' not in request.files or 'file2' not in request.files:
                print('No file uploaded')
                return render_template('student/apply.html', error='No file uploaded')

            f_name = request.form.get('fName', '')
            l_name = request.form.get('lName', '')
            municipality = request.form.get('municipality', '')
            school = request.form.get('school', '')
            program = request.form.get('program', '')
            year_level = request.form.get('yearlevel', '')
            file1 = request.files.get('file1', None)
            file2 = request.files.get('file2', None)
            email = session.get('email', '')
            key = get_applicants_count()

            try:
                # db connections
                doc_ref = db.collection('admin').document('applicants')
                user_ref = db.collection('users').document(email)

                # Storage
                folder_name = f"{municipality}/{email}"
                file1_link = handle_file_upload(file1, folder_name)
                file2_link = handle_file_upload(file2, folder_name)

                # Store user details in Firestore
                doc_ref.update({
                    str(key): {
                        'name': f"{f_name} {l_name}",
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
                result = str(e)

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
    if 'email' in session and session['user_data'].get('role', '') == ADMIN_ROLE:
        documents = db.collection('admin').document('applicants').get()
        print('HERE IN ACTION')

        applicants = []
        doc_data = documents.to_dict()
        for key, value in doc_data.items():
            applicants.append(Applicant(
                key, value['email'], value['name'], value['municipality'], value['school'], value['program'], value['year_level'], value['noa_link'], value['coe_link']))

        print(len(applicants))
        return render_template('admin/applicants.html', applicants=applicants)
    return redirect(url_for('auth.login'))


@views.route('/process', methods=['POST'])
def process_action():
    if request.method == 'POST' and session['user_data'].get('role', '') == ADMIN_ROLE:
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
    else:
        return redirect(url_for('auth.login'))


@views.route('/payout')
def payout():
    # return '<h2>PAYOUTTTT NAAAA</h2>'
    if 'email' in session and session['user_data'].get('role', '') == ADMIN_ROLE:
        documents = db.collection('admin').document('applicants').get()
        print('HERE IN ACTION')

        applicants = []
        doc_data = documents.to_dict()
        for key, value in doc_data.items():
            applicants.append(Applicant(
                key, value['email'], value['name'], value['municipality'], value['school'], value['program'], value['year_level'], value['noa_link'], value['coe_link']))

        print(len(applicants))
        return render_template('admin/payout.html')
    return redirect(url_for('auth.login'))


@views.route('qr_result', methods=['POST'])
def qr_result():
    data = request.get_json()
    qr_code_data = data.get('qrCodeData')

    print(qr_code_data)

    # Send a response back to the client
    return jsonify({'user': {
        'name': 'Very long name',
        'email': 'email.1@gmail.com'

    }})
