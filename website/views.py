from flask import Blueprint, session, render_template, redirect, url_for

views = Blueprint('views', __name__, static_folder='static',
                  template_folder='templates')


def get_user_role():
    return 'student'


@views.route('/')
def index():
    user_role = get_user_role()
    if user_role == 'student':
        print(user_role)
        return render_template('student/index.html', user_role=user_role)
    elif user_role == 'admin':
        return render_template('admin/index.html')
    # return render_template('base.html')
