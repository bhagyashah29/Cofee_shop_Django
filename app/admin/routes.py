from __future__ import annotations
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..extensions import db
from ..models import User, Company, Role, ApprovalStepTemplate
from ..utils.currency import fetch_countries_and_currencies
from . import admin_bp


def require_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))


@admin_bp.route("/")
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for("auth.home"))
    company: Company = current_user.company
    users = User.query.filter_by(company_id=company.id).all()
    steps = ApprovalStepTemplate.query.filter_by(company_id=company.id).order_by(ApprovalStepTemplate.sequence).all()
    return render_template("admin/dashboard.html", company=company, users=users, steps=steps, Role=Role)


@admin_bp.route("/users", methods=["POST"])  # create or update
@login_required
def create_user():
    if not current_user.is_admin:
        return redirect(url_for("auth.home"))
    email = request.form.get("email", "").lower()
    name = request.form.get("name", "")
    password = request.form.get("password", "")
    role = request.form.get("role", Role.EMPLOYEE.value)
    manager_id = request.form.get("manager_id")

    if not email or not name or not password:
        flash("Missing required fields", "danger")
        return redirect(url_for("admin.dashboard"))

    if User.query.filter_by(email=email).first():
        flash("Email already exists", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User(email=email, name=name, role=Role(role), company_id=current_user.company_id)
    user.set_password(password)
    if manager_id:
        try:
            user.manager_id = int(manager_id)
        except Exception:
            pass

    db.session.add(user)
    db.session.commit()
    flash("User created", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/expenses")
@login_required
def expenses():
    if not current_user.is_admin:
        return redirect(url_for("auth.home"))
    company: Company = current_user.company
    from ..models import Expense, ExpenseStatus
    expenses = Expense.query.filter_by(company_id=company.id).order_by(Expense.created_at.desc()).all()
    return render_template("admin/expenses.html", expenses=expenses, ExpenseStatus=ExpenseStatus)


@admin_bp.route("/expenses/<int:expense_id>/override", methods=["POST"])
@login_required
def override_expense(expense_id: int):
    if not current_user.is_admin:
        return redirect(url_for("auth.home"))
    from ..models import Expense, ExpenseStatus
    expense = Expense.query.get_or_404(expense_id)
    action = request.form.get("action", "")
    if action == "approve":
        expense.status = ExpenseStatus.APPROVED
        expense.current_step_sequence = None
    elif action == "reject":
        expense.status = ExpenseStatus.REJECTED
        expense.current_step_sequence = None
    db.session.commit()
    flash("Expense overridden", "info")
    return redirect(url_for("admin.expenses"))


@admin_bp.route("/company", methods=["POST"])  # update settings
@login_required
def update_company():
    if not current_user.is_admin:
        return redirect(url_for("auth.home"))
    company: Company = current_user.company
    company.name = request.form.get("name", company.name)
    company.manager_approver_enabled = bool(request.form.get("manager_approver_enabled"))

    company.use_percentage_rule = bool(request.form.get("use_percentage_rule"))
    try:
        company.percentage_threshold = int(request.form.get("percentage_threshold", company.percentage_threshold))
    except Exception:
        pass
    company.use_specific_approver_rule = bool(request.form.get("use_specific_approver_rule"))
    try:
        company.specific_approver_user_id = int(request.form.get("specific_approver_user_id")) if request.form.get("specific_approver_user_id") else None
    except Exception:
        pass
    company.hybrid_operator = request.form.get("hybrid_operator", company.hybrid_operator)

    db.session.commit()
    flash("Company settings updated", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/steps", methods=["POST"])  # create step
@login_required
def create_step():
    if not current_user.is_admin:
        return redirect(url_for("auth.home"))
    company: Company = current_user.company
    name = request.form.get("name", "").strip() or "Step"
    sequence = int(request.form.get("sequence", "1"))
    is_manager_step = bool(request.form.get("is_manager_step"))
    approver_user_id = request.form.get("approver_user_id")
    approver_role = request.form.get("approver_role")

    step = ApprovalStepTemplate(
        company_id=company.id,
        name=name,
        sequence=sequence,
        is_manager_step=is_manager_step,
        approver_user_id=int(approver_user_id) if approver_user_id else None,
        approver_role=Role(approver_role) if approver_role else None,
    )
    db.session.add(step)
    db.session.commit()
    flash("Approval step added", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/steps/<int:step_id>/delete", methods=["POST"])  # delete step
@login_required
def delete_step(step_id: int):
    if not current_user.is_admin:
        return redirect(url_for("auth.home"))
    step = ApprovalStepTemplate.query.get_or_404(step_id)
    db.session.delete(step)
    db.session.commit()
    flash("Step deleted", "info")
    return redirect(url_for("admin.dashboard"))
