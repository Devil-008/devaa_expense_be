from flask import Blueprint, request, jsonify
from app.models import Category
from app.extensions import db
from app.utils.decorators import token_required

bp = Blueprint('categories', __name__, url_prefix='/api/v1/categories')

@bp.route('', methods=['GET'])
@token_required
def get_categories(current_user):
    categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.user_id.is_(None))
    ).all()
    return jsonify({'categories': [c.to_dict() for c in categories]}), 200

@bp.route('', methods=['POST'])
@token_required
def create_category(current_user):
    data = request.get_json()
    if not data or not data.get('name') or not data.get('type'):
        return jsonify({'error': 'Name and type are required'}), 400
        
    new_category = Category(
        user_id=current_user.id,
        name=data['name'],
        type=data['type'],
        color=data.get('color'),
        icon=data.get('icon')
    )
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify({'category': new_category.to_dict()}), 201

@bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_category(current_user, id):
    category = Category.query.get_or_404(id)
    if category.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    category.name = data.get('name', category.name)
    category.type = data.get('type', category.type)
    category.color = data.get('color', category.color)
    category.icon = data.get('icon', category.icon)
    
    db.session.commit()
    return jsonify({'category': category.to_dict()}), 200

@bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_category(current_user, id):
    category = Category.query.get_or_404(id)
    if category.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'}), 200
