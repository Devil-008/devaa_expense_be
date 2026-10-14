from flask import Blueprint, request, Response
from app.models import Transaction
from app.extensions import db
from app.utils.decorators import token_required
import csv
import io
from datetime import datetime

bp = Blueprint('transactions', __name__, url_prefix='/api/v1/transactions')

@bp.route('/export', methods=['GET'])
@token_required
def export_transactions(current_user):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Payment Method', 'Note'])
    
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    transactions = query.all()
    for t in transactions:
        writer.writerow([t.transaction_date, t.type, t.category.name if t.category else 'N/A', t.amount, t.payment_method, t.note])
    
    output.seek(0)
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename="transactions_{datetime.now().strftime("%Y_%m_%d")}.csv"'
    return response