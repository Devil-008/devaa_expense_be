from functools import wraps
from flask import request, jsonify, current_app
from .auth import decode_token
from app.models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Format: "Bearer <token>"
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
                
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
            
        try:
            user_id = decode_token(token)
            if isinstance(user_id, str) and not user_id.isdigit(): # Check if it returned an error message
                return jsonify({'error': user_id}), 401
                
            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({'error': 'User not found!'}), 401
        except Exception as e:
            return jsonify({'error': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
        
    return decorated
