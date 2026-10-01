from flask import Blueprint, request, jsonify
from app.models import Transaction, Category
from app.extensions import db
from app.utils.decorators import token_required
from datetime import datetime

bp = Blueprint('transactions', __name__, url_prefix='/api/v1/transactions')

@bp.route('', methods=['GET'])
@token_required
def get_transactions(current_user):
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Simple filtering
    type_filter = request.args.get('type')
    if type_filter:
        query = query.filter_by(type=type_filter)
        
    category_id = request.args.get('category_id')
    if category_id:
        query = query.filter_by(category_id=category_id)
        
    # Date range
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    if from_date:
        query = query.filter(Transaction.transaction_date >= from_date)
    if to_date:
        query = query.filter(Transaction.transaction_date <= to_date)
        
    transactions = query.order_by(Transaction.transaction_date.desc()).all()
    
    return jsonify({'transactions': [t.to_dict() for t in transactions]}), 200

@bp.route('', methods=['POST'])
@token_required
def create_transaction(current_user):
    data = request.get_json()
    
    required_fields = ['category_id', 'type', 'amount', 'transaction_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Validate category ownership
    category = Category.query.get(data['category_id'])
    if not category or (category.user_id is not None and category.user_id != current_user.id):
        return jsonify({'error': 'Invalid category'}), 400
        
    if float(data['amount']) <= 0:
        return jsonify({'error': 'Amount must be greater than zero'}), 400
        
    try:
        tx_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format (YYYY-MM-DD)'}), 400

    new_tx = Transaction(
        user_id=current_user.id,
        category_id=data['category_id'],
        type=data['type'],
        amount=data['amount'],
        transaction_date=tx_date,
        payment_method=data.get('payment_method'),
        note=data.get('note')
    )
    
    db.session.add(new_tx)
    db.session.commit()
    
    return jsonify({'transaction': new_tx.to_dict()}), 201

@bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_transaction(current_user, id):
    tx = Transaction.query.get_or_404(id)
    if tx.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category or (category.user_id is not None and category.user_id != current_user.id):
            return jsonify({'error': 'Invalid category'}), 400
        tx.category_id = data['category_id']
        
    if 'amount' in data:
        if float(data['amount']) <= 0:
            return jsonify({'error': 'Amount must be greater than zero'}), 400
        tx.amount = data['amount']
        
    if 'transaction_date' in data:
        try:
            tx.transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format (YYYY-MM-DD)'}), 400
            
    tx.type = data.get('type', tx.type)
    tx.payment_method = data.get('payment_method', tx.payment_method)
    tx.note = data.get('note', tx.note)
    
    db.session.commit()
    return jsonify({'transaction': tx.to_dict()}), 200

@bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_transaction(current_user, id):
    tx = Transaction.query.get_or_404(id)
    if tx.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    db.session.delete(tx)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted successfully'}), 200
