from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__, template_folder='../../templates/auth')


@auth_bp.get('/login')
def login():
    return render_template('auth/login.html')


@auth_bp.post('/login')
def login_post():
    # Placeholder; real implementation after models
    email = request.form.get('email')
    password = request.form.get('password')
    flash('Auth not yet implemented', 'warning')
    return redirect(url_for('auth.login'))


@auth_bp.get('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.get('/signup')
def signup():
    return render_template('auth/signup.html')


@auth_bp.post('/signup')
def signup_post():
    flash('Signup not yet implemented', 'warning')
    return redirect(url_for('auth.signup'))
