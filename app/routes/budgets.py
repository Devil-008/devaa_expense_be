from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.utils.auth import token_required
from sqlalchemy import func
from datetime import datetime

bp = Blueprint('budgets', __name__, url_prefix='/api/v1/budgets')

@bp.route('', methods=['GET'])
@token_required
def get_budgets(current_user):
    month = request.args.get('month', datetime.utcnow().month, type=int)
    year = request.args.get('year', datetime.utcnow().year, type=int)
    budgets = Budget.query.filter_by(user_id=current_user.id, month=month, year=year).all()
    return jsonify([b.to_dict() for b in budgets]), 200

@bp.route('', methods=['POST'])
@token_required
def create_budget(current_user):
    data = request.get_json()
    existing = Budget.query.filter_by(user_id=current_user.id, category_id=data['category_id'], month=data['month'], year=data['year']).first()
    if existing:
        return jsonify({'message': 'Budget for this category already exists'}), 409
    new_budget = Budget(user_id=current_user.id, **data)
    db.session.add(new_budget)
    db.session.commit()
    return jsonify(new_budget.to_dict()), 201

@bp.route('/status', methods=['GET'])
@token_required
def get_status(current_user):
    month = request.args.get('month', datetime.utcnow().month, type=int)
    year = request.args.get('year', datetime.utcnow().year, type=int)
    budgets = Budget.query.filter_by(user_id=current_user.id, month=month, year=year).all()
    results = []
    for b in budgets:
        spent = db.session.query(func.sum(Transaction.amount)).filter_by(category_id=b.category_id, user_id=current_user.id).filter(func.extract('month', Transaction.date) == month, func.extract('year', Transaction.date) == year).scalar() or 0.0
        percentage = (spent / b.amount) * 100 if b.amount > 0 else 0
        results.append({
            'category_id': b.category_id,
            'budget_amount': float(b.amount),
            'spent_amount': float(spent),
            'remaining_amount': float(b.amount - spent),
            'percentage_used': float(percentage),
            'is_over_budget': spent > b.amount
        })
    return jsonify(results), 200