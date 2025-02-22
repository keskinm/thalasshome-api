from flask import request, session, flash, redirect, Blueprint
from dashboard.db.client import supabase_cli

from werkzeug.security import check_password_hash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['POST'])
def do_admin_login1():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    response = (
        supabase_cli.table("users")
        .select("*")
        .eq("username", POST_USERNAME)
        .maybe_single()
        .execute()
    ).data

    if response and check_password_hash(response["password"], POST_PASSWORD):
        session['logged_in'] = True
        return redirect('/')
    else:
        flash('wrong password!')
        print("wrong password")
        return redirect('/login')
