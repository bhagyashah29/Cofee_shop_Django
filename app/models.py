from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager


class Role(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"


class ApprovalDecision(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ExpenseStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(128), nullable=False)
    currency_code = db.Column(db.String(8), nullable=False)
    manager_approver_enabled = db.Column(db.Boolean, default=True, nullable=False)

    specific_approver_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    use_percentage_rule = db.Column(db.Boolean, default=False, nullable=False)
    percentage_threshold = db.Column(db.Integer, default=100, nullable=False)  # 0-100
    use_specific_approver_rule = db.Column(db.Boolean, default=False, nullable=False)
    hybrid_operator = db.Column(db.String(3), default="OR", nullable=False)  # OR or AND

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    users = db.relationship("User", back_populates="company", lazy=True)
    approval_steps = db.relationship(
        "ApprovalStepTemplate", back_populates="company", order_by="ApprovalStepTemplate.sequence", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Company {self.id} {self.name} {self.currency_code}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(Role), default=Role.EMPLOYEE, nullable=False)

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    company = db.relationship("Company", back_populates="users")

    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    manager = db.relationship("User", remote_side=[id], backref="reports")

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    approval_assignments = db.relationship("ApprovalAssignment", back_populates="approver", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role == Role.MANAGER

    @property
    def is_employee(self) -> bool:
        return self.role == Role.EMPLOYEE

    def get_id(self) -> str:  # flask-login requires str
        return str(self.id)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.id} {self.email} {self.role}>"


@login_manager.user_loader
def load_user(user_id: str) -> Optional["User"]:
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None


class ApprovalStepTemplate(db.Model):
    __tablename__ = "approval_step_templates"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    company = db.relationship("Company", back_populates="approval_steps")

    name = db.Column(db.String(128), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)

    # How to select approver(s) for this step
    is_manager_step = db.Column(db.Boolean, default=False, nullable=False)
    approver_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    approver_role = db.Column(db.Enum(Role), nullable=True)

    # Optional step-level rules (override company defaults if set)
    use_percentage_rule = db.Column(db.Boolean, default=False, nullable=False)
    percentage_threshold = db.Column(db.Integer, default=100, nullable=False)
    use_specific_approver_rule = db.Column(db.Boolean, default=False, nullable=False)
    specific_approver_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    hybrid_operator = db.Column(db.String(3), default="OR", nullable=False)


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    employee = db.relationship("User")

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    company = db.relationship("Company")

    category = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    expense_date = db.Column(db.Date, nullable=False, default=date.today)

    amount_original = db.Column(db.Float, nullable=False)
    currency_original = db.Column(db.String(8), nullable=False)

    amount_company = db.Column(db.Float, nullable=False)
    currency_company = db.Column(db.String(8), nullable=False)
    conversion_rate = db.Column(db.Float, nullable=False)

    status = db.Column(db.Enum(ExpenseStatus), default=ExpenseStatus.PENDING, nullable=False)
    current_step_sequence = db.Column(db.Integer, nullable=True)

    receipt_filename = db.Column(db.String(255), nullable=True)
    ocr_payload_json = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    lines = db.relationship("ExpenseLine", back_populates="expense", cascade="all, delete-orphan")
    approvals = db.relationship("ApprovalAssignment", back_populates="expense", cascade="all, delete-orphan")


class ExpenseLine(db.Model):
    __tablename__ = "expense_lines"

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey("expenses.id"), nullable=False)
    expense = db.relationship("Expense", back_populates="lines")

    description = db.Column(db.String(255), nullable=False)
    amount_original = db.Column(db.Float, nullable=False)


class ApprovalAssignment(db.Model):
    __tablename__ = "approval_assignments"

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey("expenses.id"), nullable=False)
    expense = db.relationship("Expense", back_populates="approvals")

    step_sequence = db.Column(db.Integer, nullable=False)
    approver_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    approver = db.relationship("User", back_populates="approval_assignments")

    decision = db.Column(db.Enum(ApprovalDecision), default=ApprovalDecision.PENDING, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    decided_at = db.Column(db.DateTime, nullable=True)


class ExchangeRateCache(db.Model):
    __tablename__ = "exchange_rate_cache"

    id = db.Column(db.Integer, primary_key=True)
    base_currency = db.Column(db.String(8), nullable=False, unique=True)
    rates_json = db.Column(db.Text, nullable=False)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
