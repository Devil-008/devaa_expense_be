from flask import Blueprint, request, Response
from app.utils.auth import token_required
from app.models import Transaction
from app import db
from sqlalchemy import func
import csv
import io
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/api/v1/reports/monthly-trends', methods=['GET'])
@token_required
def get_monthly_trends(current_user):
    months = int(request.args.get('months', 6))
    # Simplified aggregation logic for demonstration
    results = db.session.query(
        func.date_format(Transaction.date, '%Y-%m').label('month'),
        func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('income'),
        func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('expense')
    ).filter(Transaction.user_id == current_user.id).group_by('month').limit(months).all()
    return {'data': [{'month': r.month, 'income': float(r.income or 0), 'expense': float(r.expense or 0)} for r in results]}

@reports_bp.route('/api/v1/transactions/export', methods=['GET'])
@token_required
def export_transactions(current_user):
    transactions = Transaction.query.filter(Transaction.user_id == current_user.id).all()
    si = io.StringIO()
    cw = csv.writer(si, quoting=csv.QUOTE_ALL)
    cw.writerow(['Date', 'Type', 'Category', 'Amount', 'Payment Method', 'Note'])
    for t in transactions:
        cw.writerow([t.date, t.type, t.category, t.amount, t.payment_method, t.note])
    return Response(si.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=transactions.csv'})