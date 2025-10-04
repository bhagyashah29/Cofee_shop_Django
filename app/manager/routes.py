from __future__ import annotations
from datetime import datetime
from typing import List

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..extensions import db
from ..models import (
    User,
    Company,
    Expense,
    ExpenseStatus,
    ApprovalAssignment,
    ApprovalDecision,
    ApprovalStepTemplate,
)
from . import manager_bp


@manager_bp.route("/")
@login_required
def dashboard():
    assignments = (
        ApprovalAssignment.query.filter_by(approver_user_id=current_user.id, decision=ApprovalDecision.PENDING)
        .join(Expense, Expense.id == ApprovalAssignment.expense_id)
        .order_by(Expense.created_at.desc())
        .all()
    )
    return render_template("manager/dashboard.html", assignments=assignments)


@manager_bp.route("/team")
@login_required
def team_expenses():
    # Managers can view their direct reports' expenses
    report_ids = [u.id for u in current_user.reports]
    expenses = (
        Expense.query.filter(Expense.employee_id.in_(report_ids))
        .order_by(Expense.created_at.desc())
        .all()
    )
    return render_template("manager/team.html", expenses=expenses)

@manager_bp.route("/decide/<int:assignment_id>", methods=["POST"])
@login_required
def decide(assignment_id: int):
    assignment = ApprovalAssignment.query.get_or_404(assignment_id)
    if assignment.approver_user_id != current_user.id:
        flash("Not authorized", "danger")
        return redirect(url_for("manager.dashboard"))

    decision = request.form.get("decision", "").upper()
    comment = request.form.get("comment", "")

    if decision not in (ApprovalDecision.APPROVED.value, ApprovalDecision.REJECTED.value):
        flash("Invalid decision", "danger")
        return redirect(url_for("manager.dashboard"))

    assignment.decision = ApprovalDecision(decision)
    assignment.comment = comment
    assignment.decided_at = datetime.utcnow()
    db.session.flush()

    _evaluate_and_advance(assignment.expense)

    db.session.commit()
    flash("Decision recorded", "success")
    return redirect(url_for("manager.dashboard"))


def _evaluate_and_advance(expense: Expense) -> None:
    company: Company = expense.company
    current_sequence = expense.current_step_sequence
    step_assignments: List[ApprovalAssignment] = [a for a in expense.approvals if a.step_sequence == current_sequence]

    approvals = sum(1 for a in step_assignments if a.decision == ApprovalDecision.APPROVED)
    rejections = sum(1 for a in step_assignments if a.decision == ApprovalDecision.REJECTED)
    total = len(step_assignments) if step_assignments else 1

    # Resolve rules: step-level overrides fall back to company-level
    current_step = (
        ApprovalStepTemplate.query.filter(
            ApprovalStepTemplate.company_id == company.id,
            ApprovalStepTemplate.sequence == current_sequence,
        ).first()
    )

    use_percentage = current_step.use_percentage_rule if current_step and current_step.use_percentage_rule else company.use_percentage_rule
    threshold = (
        current_step.percentage_threshold if current_step and current_step.use_percentage_rule else company.percentage_threshold
    )
    use_specific = current_step.use_specific_approver_rule if current_step and current_step.use_specific_approver_rule else company.use_specific_approver_rule
    specific_user_id = (
        current_step.specific_approver_user_id if current_step and current_step.use_specific_approver_rule and current_step.specific_approver_user_id is not None else company.specific_approver_user_id
    )
    operator = (
        current_step.hybrid_operator if current_step and current_step.use_percentage_rule and current_step.use_specific_approver_rule else company.hybrid_operator
    )  # OR/AND

    # Evaluate conditions
    pct_met = (approvals * 100 / total) >= threshold if total > 0 else False
    specific_met = any(a.approver_user_id == specific_user_id and a.decision == ApprovalDecision.APPROVED for a in step_assignments) if specific_user_id else False

    approve_step = False
    reject_step = rejections > 0 and not use_percentage and not use_specific

    if use_percentage and use_specific:
        if operator == "AND":
            approve_step = pct_met and specific_met
        else:
            approve_step = pct_met or specific_met
    elif use_percentage:
        approve_step = pct_met
    elif use_specific:
        approve_step = specific_met
    else:
        approve_step = approvals == total

    if reject_step:
        expense.status = ExpenseStatus.REJECTED
        expense.current_step_sequence = None
        return

    if approve_step:
        # Advance to next step or finalize
        next_step = (
            ApprovalStepTemplate.query.filter(
                ApprovalStepTemplate.company_id == company.id,
                ApprovalStepTemplate.sequence > (current_sequence or 0),
            )
            .order_by(ApprovalStepTemplate.sequence)
            .first()
        )
        if next_step is None:
            expense.status = ExpenseStatus.APPROVED
            expense.current_step_sequence = None
            return

        expense.current_step_sequence = next_step.sequence

        # Create assignments for next step
        approver_ids: List[int] = []
        if next_step.approver_user_id:
            approver_ids.append(next_step.approver_user_id)
        elif next_step.approver_role:
            approver_ids.extend([u.id for u in User.query.filter_by(company_id=company.id, role=next_step.approver_role)])

        if not approver_ids:
            approver_ids = [u.id for u in User.query.filter_by(company_id=company.id, role="ADMIN")]

        for uid in sorted(set(approver_ids)):
            db.session.add(
                ApprovalAssignment(
                    expense_id=expense.id,
                    step_sequence=expense.current_step_sequence,
                    approver_user_id=uid,
                )
            )
