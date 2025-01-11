from flask import Blueprint, request, flash, redirect, url_for, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Admin
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            # Return a session cookie or token
            return jsonify({
                'message': 'Login successful',
                'session_token': request.cookies.get('session')
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':

            data = request.get_json()
            email = data.get('email')
            username = data.get('username')
            password1 = data.get('password1')
            password2 = data.get('password2')

            # Validate data
            if not all([email, username, password1, password2]):
                return jsonify({'error': 'Missing required fields'}), 400

            user = User.query.filter_by(email=email).first()
            if user:
                return jsonify({'error': 'Email already exists'}), 400

            if password1 != password2:
                return jsonify({'error': 'Passwords do not match'}), 400

            # Create new user
            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(password1, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()

            return jsonify({
                'message': 'Account created successfully',
                'email': email
            }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        db.session.close()

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    
    # Check if request is from Chainlit
    is_chainlit = request.headers.get('X-Chainlit-Request')
    
    if is_chainlit:
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        }), 200
    else:
        flash('Logged out successfully!', category='success')
        return redirect(url_for('auth.login'))
    
# Admin auth routes

@auth.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            # Return a session cookie or token
            return jsonify({
                'message': 'Login successful',
                'session_token': request.cookies.get('session')
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/admin/sign-up', methods=['GET', 'POST'])
def admin_signup():
    try:
        if request.method == 'POST':
            # Get data from JSON request
            data = request.get_json()
            email = data.get('email')
            username = data.get('username')
            password1 = data.get('password1')
            password2 = data.get('password2')

            # Validate data
            if not all([email, username, password1, password2]):
                return jsonify({'error': 'Missing required fields'}), 400

            admin = Admin.query.filter_by(email=email).first()
            if admin:
                return jsonify({'error': 'Email already exists'}), 400

            if password1 != password2:
                return jsonify({'error': 'Passwords do not match'}), 400

            # Create new user
            new_user = Admin(
                email=email,
                username=username,
                password=generate_password_hash(password1, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()

            return jsonify({
                'message': 'Account created successfully',
                'email': email
            }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        db.session.close()

@auth.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    
    # Check if request is from Chainlit
    is_chainlit = request.headers.get('X-Chainlit-Request')
    
    if is_chainlit:
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        }), 200
    else:
        flash('Logged out successfully!', category='success')
        return redirect(url_for('auth.login'))
    
@auth.route('/verify-session')
@login_required
def verify_session():
    return jsonify({'status': 'valid'}), 200