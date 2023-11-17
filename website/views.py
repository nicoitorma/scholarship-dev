from flask import Blueprint, session, render_template, redirect, url_for, request, jsonify
from firebase_admin_config import admin_firestore as db
from pyrebase_config import bucket
from firebase_admin import firestore
import json
from .models import Applicant, Student, Beneficiaries

views = Blueprint('views', __name__, static_folder='static',
                  template_folder='templates')

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'pdf']
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


def count_beneficiaries():
    query = db.collection('users').where('status', '==', 'Beneficiary').get()
    count = len(query)
    return count


def count_per_municipality():
    query = db.collection('users').get()
    municipality_count = {'Bagamanoc': 0, 'Panganiban': 0, 'Viga': 0, 'Virac': 0, 'Pandan': 0,
                          'Caramoran': 0, 'Gigmoto': 0, 'Bato': 0, 'Baras': 0, 'San Andres': 0, 'San Miguel': 0}

    for doc in query:
        data = doc.to_dict()
        municipality = data.get('municipality')
        status = data.get('status')

        # Count documents for each address
        if municipality in municipality_count and status == 'Beneficiary':
            municipality_count[municipality] += 1

    return municipality_count


@views.route('/')
def index():
    if 'email' in session:
        email = session['email']
        data = db.collection('users').document(email).get()
        user_details = data.to_dict()
        user_role = user_details.get('role', '')

        if user_role == STUDENT_ROLE:
            session['user_data'] = {
                'name': user_details.get('name'),
                'role': user_role,
                'municipality': user_details.get('municipality', ''),
                'scholarship': user_details.get('scholarship', ''),
                'status': user_details.get('status', ''),
                'allocation': user_details.get('allocation', ''),
                'latest_coe': user_details.get('latest_coe', ''),
                'latest_cog': user_details.get('latest_cog', '')
            }
            return render_template('student/index.html')
        elif user_role == ADMIN_ROLE:
            session['user_data'] = {
                'name': user_details.get('name', ''),
                'role': user_role,
            }
            return admin()

    return redirect(url_for('auth.login'))


def handle_file_upload(file, folder_name):
    """
    Handle file upload to Firebase storage.

    :param file: The file to be uploaded.
    :param folder_name: The folder name in which to store the file.
    :return: The file link in the Firebase storage.
    """
    file_name = f"{folder_name}/{file.filename}"
    file.stream.seek(0)
    bucket.child(file_name).put(file, session['idToken'])
    return bucket.child(file_name).get_url(session['idToken'])


@views.route('/apply', methods=['POST', 'GET'])
def apply():
    if 'email' in session and session['user_data'].get('status', '') == 'None':
        if request.method == 'POST':

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

            if file1 and is_allowed(file1):
                return render_template('student/apply.html', error='Notice of Award file format is not supported')
            if file2 and is_allowed(file2):
                return render_template('student/apply.html', error='Certificate of Enrollment file format is not supported')
            try:
                # db connections
                applicants_ref = db.collection('admin').document('applicants')
                user_ref = db.collection('users').document(email)

                # Storage
                folder_name = f"{municipality}/{email}"
                file1.stream.seek(0)
                file2.stream.seek(0)
                file1_link = handle_file_upload(file1, folder_name)
                file2_link = handle_file_upload(file2, folder_name)

                # Store user details in Firestore
                applicants_ref.update({
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
                user_ref.update({
                    'program': program,
                    'school': school,
                    'year_level': year_level,
                    'municipality': municipality,
                    'status': 'Pending'})

                result = 'Application Submitted'
            except Exception as e:
                result = str(e)
            return render_template('student/apply.html', message=result)
        return render_template('student/apply.html')
    else:
        return redirect(url_for('auth.login'))


@views.route('/certificate-of-grades', methods=['POST', 'GET'])
def cog():
    result = ''
    if 'email' in session:
        if request.method == 'POST':
            semester = request.form.get('semester')
            school_year = request.form.get('school_year')
            course_codes = request.form.getlist('courseCode[]')
            units = request.form.getlist('units[]')
            final_grades = request.form.getlist('finalGrade[]')
            cog_file = request.files.get('cog', None)
            email = session['email']

            if cog_file:
                data = {}

                for code, unit, grade in zip(course_codes, units, final_grades):
                    data[code] = {
                        'units': int(unit),
                        'final_grade': float(grade),
                        'semester': semester,
                        'school_year': school_year
                    }
                try:
                    # Upload data to Firebase
                    doc_ref = db.collection(
                        'beneficiaries_cog').document(email)
                    user_ref = db.collection('users').document(email)

                    municipality = session['user_data'].get('municipality', '')

                    folder_name = f"{municipality}/{email}"
                    cog_file.stream.seek(0)
                    cog_link = handle_file_upload(cog_file, folder_name)

                    # Set the data in the document
                    doc_ref.update(data)
                    user_ref.update({
                        'latest_cog': cog_link
                    })

                    result = 'Certificate of Grade is uploaded'
                except Exception as e:
                    result = e
                return render_template('student/cog.html', message=result)

        gwa = calculate_gwa(session['email'])
        return render_template('student/cog.html', gwa=gwa)
    return redirect(url_for('auth.login'))


@views.route('/certificate-of-enrollment', methods=['POST', 'GET'])
def coe():
    if 'email' in session:
        email = session['email']
        latest_coe = session['user_data'].get('latest_coe', '')

        if request.method == 'POST':
            result = ''
            user_ref = db.collection('users').document(email)
            coe_file = request.files.get('coe_file', None)
            if coe_file and is_allowed(coe_file):
                return render_template('student/coe.html', error='Certificate of Enrollment file format is not supported')

            try:
                # Storage
                folder_name = f"{session['user_data'].get('municipality','')}/{email}"
                coe_file.stream.seek(0)
                coe_link = handle_file_upload(coe_file, folder_name)

                user_ref.update({'latest_coe': coe_link})
                result = 'Certificate of Enrollment updated.'
            except Exception as e:
                result = str(e)
            return render_template('student/coe.html', message=result)

        return render_template('student/coe.html', cog=latest_coe)
    return redirect(url_for('auth.login'))


@views.route('/profile')
def profile():
    if 'email' in session:
        user_ref = db.collection('users').document(session['email']).get()
        user_details = user_ref.to_dict()

        user = Student(name=user_details.get('name', ''), email=user_details.get('email', ''),
                       municipality=user_details.get('municipality', ''), school=user_details.get('school', ''), program=user_details.get('program', ''), year_level=user_details.get('year_level', ''), scholarship=user_details.get('scholarship', ''), status=user_details.get('status', ''))
        return render_template('profile.html', user=user)
    return redirect(url_for('auth.login'))


# FOR ADMIN
@views.route('/admin')
def admin():
    doc2_ref = db.collection('admin').document('grantees')
    doc2_data = doc2_ref.get().to_dict()

    return render_template('admin/index.html', count_beneficiaries=count_beneficiaries(), appli_count=get_applicants_count(), data1=count_per_municipality(), data2=json.dumps(doc2_data))


@views.route('/applicants')
def applicants():
    # This code block is checking if the user is logged in and has the role of an admin. If both
    # conditions are met, it retrieves the documents from the 'applicants' collection in the 'admin'
    # document in Firestore. It then creates a list of Applicant objects using the data from the
    # documents. Finally, it renders the 'admin/applicants.html' template with the list of applicants.
    # If the user is not logged in or does not have the admin role, it redirects them to the login
    # page.
    if 'email' in session and session['user_data'].get('role', '') == ADMIN_ROLE:
        documents = db.collection('admin').document('applicants').get()

        applicants = []
        doc_data = documents.to_dict()
        for key, value in doc_data.items():
            applicants.append(Applicant(
                key, value['email'], value['name'], value['school'], value['program'], value['year_level'], value['noa_link'], value['coe_link'], value['municipality']))

    # This code block is handling the processing of an action (accept or reject) for an applicant in
    # the admin panel.
        return render_template('admin/applicants.html', applicants=applicants)
    return redirect(url_for('auth.login'))


@views.route('/process', methods=['POST'])
def process_action():
    # This code block is handling the processing of an action (accept or reject) for an applicant in
    # the admin panel.
    if request.method == 'POST' and session['user_data'].get('role', '') == ADMIN_ROLE:
        data = request.get_json()
        applicant_id = data['id']
        applicant_email = data['email']
        action = data['action']

        applicants_ref = db.collection('admin').document('applicants')
        user_ref = db.collection('users').document(applicant_email)
        beneficiaries_ref = db.collection(
            'beneficiaries_cog').document(applicant_email)
        beneficiaries_ref.set({})

        if action == 'accept':
            user_ref.update(
                {'scholarship': 'StuFAP', 'status': 'Beneficiary', 'allocation': '7,750'})
        else:
            user_ref.update({'status': 'Rejected'})

        applicants_ref.update({applicant_id: firestore.DELETE_FIELD})

        return redirect(url_for('views.applicants'))
    else:
        return redirect(url_for('auth.login'))


def calculate_gwa(email):
    try:
        # Assuming you're using Firebase Firestore
        documents = db.collection('beneficiaries_cog').document(email).get()

        # Check if the document exists
        if documents.exists:
            doc_data = documents.to_dict()

            # Dictionary to store GWA for each semester and school year
            gwa_by_semester = {}

            for key, value in doc_data.items():
                # Check if the necessary fields exist in the document
                if 'units' in value and 'final_grade' in value and 'school_year' in value and 'semester' in value:
                    units = value['units']
                    final_grade = value['final_grade']
                    school_year = value['school_year']
                    semester = value['semester']

                    weighted_grades = units * final_grade

                    # Initialize the semester's GWA if not present in the dictionary
                    if (school_year, semester) not in gwa_by_semester:
                        gwa_by_semester[(school_year, semester)] = {
                            'total_units': 0, 'total_weighted_grades': 0}

                    # Update the GWA for the semester
                    gwa_by_semester[(school_year, semester)
                                    ]['total_units'] += units
                    gwa_by_semester[(school_year, semester)
                                    ]['total_weighted_grades'] += weighted_grades

            # Prepare data for Jinja template
            gwa_data = []
            for (school_year, semester), data in gwa_by_semester.items():
                total_units = data['total_units']
                total_weighted_grades = data['total_weighted_grades']

                # Check if there are units to avoid division by zero
                if total_units > 0:
                    gwa = total_weighted_grades / total_units
                    gwa_data.append(
                        {'school_year': school_year, 'semester': semester, 'gwa': gwa})
                else:
                    gwa_data.append(
                        {'school_year': school_year, 'semester': semester, 'gwa': 'Error: Total units is zero'})

            return gwa_data

        else:
            return "Error: Document not found for email."

    except Exception as e:
        return "Error:" + str(e)


@views.route('/payout', methods=['POST', 'GET'])
def payout():
    # This code block is checking if the user is logged in and has the role of an admin. If both
    # conditions are met, it allows the admin to access the payout page.
    if 'email' in session and session['user_data'].get('role', '') == ADMIN_ROLE:
        # For scanning QR Code
        if request.method == 'POST':
            data = request.get_json()
            qr_code_data = data.get('qrCodeData')

            documents = db.collection('users').document(qr_code_data).get()
            user_details = documents.to_dict()
            if user_details:
                gwa = calculate_gwa(qr_code_data)

                user_details['gwa'] = gwa
                return jsonify(user_details)
            return jsonify({'message': 'Beneficiary not found'}), 404
        return render_template('admin/payout.html')
    return redirect(url_for('auth.login'))


@views.route('/beneficiaries')
def beneficiaries():
    if 'email' in session and session['user_data'].get('role', '') == ADMIN_ROLE:
        query = db.collection('users').get()

        beneficiaries = []
        for doc in query:
            data = doc.to_dict()
            status = data.get('status')

            # Count documents for each address
            if status == 'Beneficiary':
                beneficiaries.append(Beneficiaries(data.get('email', ''),
                                                   data.get('name', ''), data.get('municipality', ''), data.get('school', ''), data.get('program', ''), data.get('year_level'), data.get('scholarship', ''), data.get('latest_coe', ''), data.get('latest_cog', '')))

        # This code block is handling the processing of an action (accept or reject) for an applicant in
        # the admin panel.
        return render_template('admin/beneficiaries.html', list=beneficiaries)
    return redirect(url_for('auth.login'))


@views.route('/remove', methods=['POST'])
def remove_beneficiary():
    # This code block is handling the processing of an action (accept or reject) for an applicant in
    # the admin panel.
    if request.method == 'POST' and session['user_data'].get('role', '') == ADMIN_ROLE:
        data = request.get_json()
        applicant_email = data['email']
        action = data['action']

        user_ref = db.collection('users').document(applicant_email)
        if action == 'remove':
            user_ref.update(
                {'scholarship': 'None', 'status': 'Removed', 'allocation': '0'})

        return redirect(url_for('views.applicants'))
    else:
        return redirect(url_for('auth.login'))
