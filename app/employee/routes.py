from __future__ import annotations
import json
from datetime import datetime
from typing import List

from flask import render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user

from ..extensions import db
from ..models import User, Company, Expense, ExpenseLine, ExpenseStatus, ApprovalAssignment, ApprovalDecision, Role, ApprovalStepTemplate
from ..utils.currency import convert_amount
from ..utils.ocr import parse_receipt
from . import employee_bp


@employee_bp.route("/")
@login_required
def dashboard():
    if not current_user.is_employee and not current_user.is_manager and not current_user.is_admin:
        return redirect(url_for("auth.home"))
    expenses = Expense.query.filter_by(employee_id=current_user.id).order_by(Expense.created_at.desc()).all()
    return render_template("employee/dashboard.html", expenses=expenses, ExpenseStatus=ExpenseStatus)


@employee_bp.route("/upload/<path:filename>")
@login_required
def uploaded_file(filename: str):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@employee_bp.route("/expense/new", methods=["GET", "POST"])
@login_required
def new_expense():
    company: Company = current_user.company

    if request.method == "POST":
        category = request.form.get("category", "").strip() or "General"
        description = request.form.get("description", "")
        expense_date_str = request.form.get("expense_date", str(datetime.utcnow().date()))
        try:
            expense_date = datetime.strptime(expense_date_str, "%Y-%m-%d").date()
        except Exception:
            expense_date = datetime.utcnow().date()
        amount_original = float(request.form.get("amount", "0"))
        currency_original = request.form.get("currency", company.currency_code)

        amount_company, rate = convert_amount(amount_original, currency_original, company.currency_code)

        receipt = request.files.get("receipt")
        receipt_filename = None
        ocr_json = None
        if receipt and receipt.filename:
            receipt_filename = f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{receipt.filename}"
            receipt_path = f"{current_app.config['UPLOAD_FOLDER']}/{receipt_filename}"
            receipt.save(receipt_path)

            ocr_result = parse_receipt(open(receipt_path, "rb").read())
            ocr_json = ocr_result.to_json()

        expense = Expense(
            employee_id=current_user.id,
            company_id=company.id,
            category=category,
            description=description,
            expense_date=expense_date,
            amount_original=amount_original,
            currency_original=currency_original,
            amount_company=amount_company,
            currency_company=company.currency_code,
            conversion_rate=rate,
            status=ExpenseStatus.PENDING,
            receipt_filename=receipt_filename,
            ocr_payload_json=ocr_json,
        )
        db.session.add(expense)
        db.session.flush()

        # Add a single line mirroring the total amount for simplicity
        line = ExpenseLine(expense_id=expense.id, description=category, amount_original=amount_original)
        db.session.add(line)
        db.session.flush()

        # Initialize approval assignments for step 1
        _initialize_approval_flow(expense)

        db.session.commit()
        flash("Expense submitted", "success")
        return redirect(url_for("employee.dashboard"))

    return render_template("employee/new_expense.html", company=company)


def _initialize_approval_flow(expense: Expense) -> None:
    company: Company = expense.company
    steps: List[ApprovalStepTemplate] = (
        ApprovalStepTemplate.query.filter_by(company_id=company.id)
        .order_by(ApprovalStepTemplate.sequence)
        .all()
    )
    expense.current_step_sequence = steps[0].sequence if steps else None

    approver_ids: List[int] = []
    # Manager-first rule
    first_step = steps[0] if steps else None
    if (company.manager_approver_enabled or (first_step and first_step.is_manager_step)) and expense.employee.manager_id:
        approver_ids.append(expense.employee.manager_id)

    # Step-specific approvers for first step
    if first_step:
        if first_step.approver_user_id:
            approver_ids.append(first_step.approver_user_id)
        elif first_step.approver_role:
            approver_ids.extend([u.id for u in User.query.filter_by(company_id=company.id, role=first_step.approver_role)])

    if not approver_ids:
        # Fallback to any admin
        approver_ids = [u.id for u in User.query.filter_by(company_id=company.id, role=Role.ADMIN)]

    for uid in sorted(set(approver_ids)):
        db.session.add(
            ApprovalAssignment(
                expense_id=expense.id,
                step_sequence=expense.current_step_sequence or 1,
                approver_user_id=uid,
            )
        )


