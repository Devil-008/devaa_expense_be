from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app.models import Transaction, Category
from app.extensions import db
from app.utils.decorators import token_required
from datetime import datetime, date, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/api/v1/dashboard')

@bp.route('/summary', methods=['GET'])
@token_required
def get_summary(current_user):
    # Default to current month if no dates provided
    today = date.today()
    from_date_str = request.args.get('from', today.replace(day=1).isoformat())
    to_date_str = request.args.get('to', today.isoformat())
    
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= from_date,
        Transaction.transaction_date <= to_date
    ).all()
    
    income = sum(float(tx.amount) for tx in transactions if tx.type == 'income')
    expenses = sum(float(tx.amount) for tx in transactions if tx.type == 'expense')
    balance = income - expenses
    
    return jsonify({
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'period': f"{from_date_str} to {to_date_str}"
    }), 200

@bp.route('/category-breakdown', methods=['GET'])
@token_required
def get_category_breakdown(current_user):
    today = date.today()
    from_date_str = request.args.get('from', today.replace(day=1).isoformat())
    to_date_str = request.args.get('to', today.isoformat())
    
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    
    # Only break down expenses
    breakdown = db.session.query(
        Category.name, Category.color, func.sum(Transaction.amount).label('total')
    ).join(Transaction, Transaction.category_id == Category.id)\
     .filter(
         Transaction.user_id == current_user.id,
         Transaction.type == 'expense',
         Transaction.transaction_date >= from_date,
         Transaction.transaction_date <= to_date
     )\
     .group_by(Category.id).all()
     
    data = [{'name': b[0], 'color': b[1], 'value': float(b[2])} for b in breakdown]
    
    return jsonify({'breakdown': data}), 200

@bp.route('/recent-transactions', methods=['GET'])
@token_required
def get_recent_transactions(current_user):
    limit = request.args.get('limit', 5, type=int)
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.transaction_date.desc())\
        .limit(limit).all()
        
    return jsonify({'transactions': [t.to_dict() for t in transactions]}), 200
