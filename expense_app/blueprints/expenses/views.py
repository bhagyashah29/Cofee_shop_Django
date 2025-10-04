from flask import Blueprint, render_template
from flask_login import login_required

expenses_bp = Blueprint('expenses', __name__, template_folder='../../templates/expenses')


@expenses_bp.get('/')
@login_required
def my_expenses():
    return render_template('expenses/list.html')


@expenses_bp.get('/new')
@login_required
def new_expense():
    return render_template('expenses/new.html')
