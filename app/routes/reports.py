from flask import Blueprint, request, jsonify
from sqlalchemy import func, case
from app.models import Transaction
from app.extensions import db
from app.utils.decorators import token_required

reports_bp = Blueprint('reports', __name__, url_prefix='/api/v1/reports')

@reports_bp.route('/monthly-trends', methods=['GET'])
@token_required
def get_monthly_trends(current_user):
    months = request.args.get('months', 6, type=int)
    trends = db.session.query(
        func.date_format(Transaction.transaction_date, '%Y-%m').label('month'),
        func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('income'),
        func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('expense')
    ).filter(Transaction.user_id == current_user.id)
    .group_by('month')
    .order_by(func.max(Transaction.transaction_date).desc())
    .limit(months).all()
    
    data = [{'month': t[0], 'income': float(t[1] or 0), 'expense': float(t[2] or 0)} for t in reversed(trends)]
    
    return jsonify({'status_code': 200, 'is_success': True, 'message': 'Trends fetched successfully', 'data': data}), 200