from flask import Blueprint, request, jsonify, Response
from sqlalchemy import func, case
from app.extensions import db
from app.models import Transaction
from app.utils.decorators import token_required
import csv
import io
from datetime import datetime

bp = Blueprint('reports', __name__, url_prefix='/api/v1/reports')

@bp.route('/monthly-trends', methods=['GET'])
@token_required
def get_monthly_trends(current_user):
    months = request.args.get('months', 6, type=int)
    results = db.session.query(
        func.strftime('%Y-%m', Transaction.transaction_date).label('month'),
        func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('income'),
        func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('expense')
    ).filter(Transaction.user_id == current_user.id).group_by('month').order_by('month desc').limit(months).all()
    data = [{'month': r[0], 'income': float(r[1] or 0), 'expense': float(r[2] or 0)} for r in results]
    return jsonify({'status_code': 200, 'is_success': True, 'data': data}), 200

@bp.route('/transactions/export', methods=['GET'])
@token_required
def export_transactions(current_user):
    start_date = request.args.get('from')
    end_date = request.args.get('to')
    query = Transaction.query.filter(Transaction.user_id == current_user.id)
    if start_date: query = query.filter(Transaction.transaction_date >= start_date)
    if end_date: query = query.filter(Transaction.transaction_date <= end_date)
    
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Payment Method', 'Note'])
    for t in query.all():
        writer.writerow([t.transaction_date, t.type, t.category, t.amount, t.payment_method, t.note])
    
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename="transactions_{datetime.now().strftime("%Y_%m_%d")}.csv"'
    return response