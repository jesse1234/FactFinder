from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from .models import User
from . import db

users = Blueprint('user', __name__)

@users.route('/users', methods=['GET'])
@login_required
def get_all_users():
    """Get all users from the database"""
    try:
        users = User.query.all()
        users_list = []

        for user in users:
            users_list.append({
                'id': user.id,
                'email': user.email,
                'username': user.username
            })

        return jsonify({
            'success': True,
            'users': users_list
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@users.route('/users/<int:user_id>', methods = ['PUT'])
@login_required
def update_user(user_id):
    """Update user information"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()

        if 'email' in data:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({
                    'success': False,
                    'error': 'Email already exists'
                }), 400
            user.email = data['email']

        if 'username' in data:
            user.username = data['username']
        
        if 'password' in data:
            user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'User updated successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.session.close()

@users.route('/users/<int:user_id>', methods = ["DELETE"])
@login_required
def delete_user(user_id):
    """Delete user from database"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'error': 'Cannot delete account'
            }), 400
        
        if hasattr(user, 'rag_query'):
            for query in user.rag_query:
                db.session.delete(query)

        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.session.close()

@users.route('/users/search', methods = ['GET'])
def search_users():
    """Search users by email or username"""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return get_all_users()
        
        users = User.query.filter(
            (User.email.ilike(f'%{search_term}%')) |
            (User.username.ilike(f'%{search_term}%'))
        ).all()

        users_list = [{
            'id': user.id,
            'email': user.email,
            'username': user.username
        }  for user in users]

        return jsonify({
            'success': True,
            'users': users_list
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@users.route('/users/stats', methods = ['GET'])
@login_required
def get_user_stats():
    """Get user statistics"""
    try: 
        total_users = User.query.count()
        total_queries = 0

        if hasattr(User, 'rag_query'):
            for user in User.query.all():
                total_queries += len(user.rag_query)

        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_queries': total_queries
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@users.route('/users/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user's details"""
    try:
        user = User.query.get(current_user.id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
