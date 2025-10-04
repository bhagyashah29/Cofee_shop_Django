from flask import Blueprint, render_template
from flask_login import login_required

approvals_bp = Blueprint('approvals', __name__, template_folder='../../templates/approvals')


@approvals_bp.get('/')
@login_required
def approvals_queue():
    return render_template('approvals/queue.html')
