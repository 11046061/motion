from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from . import admin_bp
from database import get_db_connection

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT password, is_admin FROM members WHERE email = %s', (email,))
                account = cursor.fetchone()
        if account and check_password_hash(account[0], password):
            if account[1]:  # 如果是管理員
                session['admin_logged_in'] = True
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Unauthorized access', 'error')
        else:
            flash('Invalid email or password', 'error')
    return render_template('admin_login.html')

@admin_bp.route('/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please log in as admin to view this page.', 'error')
        return redirect(url_for('admin.admin_login'))
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT id, username, email, birthday FROM members')
            members = cursor.fetchall()
    return render_template('admin_dashboard.html', members=members)

@admin_bp.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('admin.admin_login'))
