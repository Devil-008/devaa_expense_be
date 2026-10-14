from flask import Blueprint, request, jsonify
from app.models import Transaction
from app.extensions import db
from app.utils.decorators import token_required
from sqlalchemy import func, case

bp = Blueprint('reports', __name__, url_prefix='/api/v1/reports')

@bp.route('/monthly-trends', methods=['GET'])
@token_required
def get_monthly_trends(current_user):
    months = request.args.get('months', 6, type=int)
    query = db.session.query(
        func.date_format(Transaction.transaction_date, '%Y-%m').label('month'),
        func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('income'),
        func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('expense')
    ).filter(Transaction.user_id == current_user.id)\
     .group_by('month')\
     .order_by(func.max(Transaction.transaction_date).desc())\
     .limit(months)
    
    results = query.all()
    data = [{"month": r.month, "income": float(r.income), "expense": float(r.expense)} for r in reversed(results)]
    return jsonify({"data": data})