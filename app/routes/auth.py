from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db
from app.utils.auth import generate_token
from app.utils.decorators import token_required

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Name, email, and password are required'}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'User already exists with that email'}), 400
        
    new_user = User(
        name=data['name'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    token = generate_token(new_user.id)
    
    return jsonify({
        'message': 'Successfully registered.',
        'token': token,
        'user': new_user.to_dict()
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
        
    token = generate_token(user.id)
    
    return jsonify({
        'message': 'Successfully logged in.',
        'token': token,
        'user': user.to_dict()
    }), 200

@bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    # With stateless JWTs, "logout" is mostly handled client-side by deleting the token.
    # To truly invalidate, we would need a token blacklist, but for now we simply return success.
    return jsonify({'message': 'Successfully logged out.'}), 200

@bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user):
    return jsonify({'user': current_user.to_dict()}), 200

@bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.get_json()
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Old and new passwords are required'}), 400
        
    if not check_password_hash(current_user.password_hash, data['old_password']):
        return jsonify({'error': 'Incorrect old password'}), 401
        
    current_user.password_hash = generate_password_hash(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully.'}), 200
