from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from .models import RAGQuery, Admin, ChatHistory, User
from . import db

rag_api = Blueprint('api_rag', __name__)

@rag_api.route('/queries', methods = ['GET'])
# @login_required
def get_all_queries():
    """Get all queries from the database"""
    try:
        queries = RAGQuery.query.all()
        queries_list = []

        for query in queries:
            queries_list.append({
                'id': query.id,
                'question': query.question,
                'context': query.context,
                'output': query.output,
                'date': query.date,
                'user_id': query.user_id,
                'admin_id': query.admin_id
            })

        return jsonify({
            'success': True,
            'queries': queries_list 
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@rag_api.route('/queries/<int:query_id>', methods = ['DELETE'])
@login_required
def delete_query(query_id):
    """Delete query from database"""
    try:
        query = RAGQuery.query.get(query_id)
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query not found'
            }), 404
        
        if query.user_id == current_user.id or query.admin_id == current_user.id:
            db.session.delete(query)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Query deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Unauthorized to delete this query'
            }), 403
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.session.close()

@rag_api.route('/queries/search', methods = ['GET'])
@login_required
def search_queries():
    """Search queries"""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return get_all_queries()
        
        queries = RAGQuery.query.filter(
            (RAGQuery.question.ilike(f'%{search_term}%')) |
            (RAGQuery.context.ilike(f'%{search_term}%')) |
            (RAGQuery.output.ilike(f'%{search_term}%'))
        ).all()

        queries_list = []
        for query in queries:
            queries_list.append({
                'id': query.id,
                'question': query.question,
                'context': query.context,
                'output': query.output,
                'date': query.date,
                'user_id': query.user_id,
                'admin_id': query.admin_id
            })

        return jsonify({
            'success': True,
            'queries': queries_list
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rag_api.route('/users/chat/history', methods=['GET'])
@login_required
def get_user_chat_history():
    try:
        if not current_user or not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Get user from the database
        user = User.query.get(current_user.id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        histories = ChatHistory.query.filter_by(user_id=user.id).order_by(ChatHistory.date.desc()).all()

        return jsonify({
            'success': True,
            'histories': [{
                'id': h.id,
                'title': h.title,
                'date': h.date.isoformat(),
                'messages': h.messages
            } for h in histories]
        }), 200
    
    except Exception as e:
        print(f"Error in get_user_chat_history: {str(e)}")  # Debug print
        return jsonify({'success': False, 'error': str(e)}), 500

@rag_api.route('/users/chat/history', methods=['POST'])
@login_required
def save_user_chat_history():
    try:
        if not current_user or not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401

        # Get user from the database
        user = User.query.get(current_user.id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        messages = data.get('messages', [])
        session_id = data.get('session_id')
        title = data.get('title', 'New Chat')

        if session_id:
            history = ChatHistory.query.get(session_id)
            if not history:
                return jsonify({
                    'success': False,
                    'error': 'Chat history not found'
                }), 404
            if history.user_id != user.id:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized access'
                }), 403
        else:
            # Create new chat history
            history = ChatHistory(
                title=title,
                messages=messages,  # Save messages directly
                user_id=user.id,
                admin_id=None
            )
            db.session.add(history)

        # If updating existing history
        if session_id:
            history.messages = messages

        db.session.commit()

        return jsonify({
            'success': True,
            'history_id': history.id
        }), 200
    
    except Exception as e:
        print(f"Error in save_user_chat_history: {str(e)}")  # Debug print
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    

# Admin chat history endpoints
@rag_api.route('/admin/chat/history', methods=['GET'])
@login_required
def get_admin_chat_history():
    try:
        if not Admin.query.filter_by(email=current_user.email).first():
            return jsonify({
                'success': False,
                'error': 'Unauthorized access'
            }), 403

        histories = ChatHistory.query.filter_by(admin_id=current_user.id).order_by(ChatHistory.date.desc()).all()

        return jsonify({
            'success': True,
            'histories': [{
                'id': h.id,
                'title': h.title,
                'date': h.date.isoformat(),
                'messages': h.messages
            } for h in histories]
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@rag_api.route('/admin/chat/history', methods=['POST'])
@login_required
def save_admin_chat_history():
    try:
        if not Admin.query.filter_by(email=current_user.email).first():
            return jsonify({
                'success': False,
                'error': 'Unauthorized access'
            }), 403

        data = request.get_json()
        messages = data.get('messages', [])
        session_id = data.get('session_id')

        if session_id:
            history = ChatHistory.query.get(session_id)
            if history.admin_id != current_user.id:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized access'
                }), 403
        else:
            title = messages[0]['content'][:50] if messages else "New Chat"
            history = ChatHistory(
                title=title,
                messages=[],
                user_id=None,
                admin_id=current_user.id
            )
            db.session.add(history)
            db.session.flush()

        history.messages = messages
        db.session.commit()

        return jsonify({
            'success': True,
            'history_id': history.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500