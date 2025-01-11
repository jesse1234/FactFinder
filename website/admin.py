from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from .models import Admin
from . import db

admin = Blueprint('admin', __name__)

@admin.route('/admin/<int:admin_id>', methods=['PUT'])
@login_required
def update_admin(admin_id):
    """Update admin information"""
    try:
        # Check if current user is an admin
        current_admin = Admin.query.get(current_user.id)
        if not current_admin:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access'
            }), 403

        # Get the admin to update (should be the same as current_admin)
        admin_to_update = Admin.query.get(admin_id)
        if not admin_to_update:
            return jsonify({
                'success': False,
                'error': 'Admin not found'
            }), 404

        # Check if admin is updating their own profile
        if current_admin.id != admin_id:
            return jsonify({
                'success': False,
                'error': 'Cannot update other admin profiles'
            }), 403
        
        data = request.get_json()
        print(f"Received data: {data}")  # Debug print

        updated = False  # Track if any changes were made

        if 'email' in data and data['email'] != current_admin.email:
            existing_admin = Admin.query.filter_by(email=data['email']).first()
            if existing_admin and existing_admin.id != admin_id:
                return jsonify({
                    'success': False,
                    'error': 'Email already exists'
                }), 400
            admin_to_update.email = data['email']
            updated = True

        if 'username' in data and data['username'] != current_admin.username:
            admin_to_update.username = data['username']
            updated = True
        
        if 'password' in data and data['password']:
            admin_to_update.password = generate_password_hash(data['password'], method='pbkdf2:sha256')
            updated = True

        if updated:
            db.session.commit()

            if 'password' in data and data['password']:
                return jsonify({
                    'success': True,
                    'message': 'Admin updated successfully. Please login again with new credentials',
                    'require_relogin': True
                }), 200
            
            return jsonify({
                'success': True,
                'message': 'Admin updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No changes were made'
            }), 400
    
    except Exception as e:
        print(f"Error in update_admin: {str(e)}")  # Debug print
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.session.close()


@admin.route('/admin/me', methods=['GET'])
@login_required
def get_current_admin():
    """Get current admin's details"""
    try:
        admin = Admin.query.get(current_user.id)
        if not admin:
            return jsonify({
                'success': False,
                'error': 'Admin not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': admin.id,
                'email': admin.email,
                'username': admin.username
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
