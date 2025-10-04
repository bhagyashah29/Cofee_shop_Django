from __future__ import annotations
from typing import Optional

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db
from ..models import User, Company, Role
from ..utils.currency import fetch_countries_and_currencies
from . import auth_bp


@auth_bp.route("/")
def home():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        if current_user.is_manager:
            return redirect(url_for("manager.dashboard"))
        return redirect(url_for("employee.dashboard"))
    return render_template("auth/home.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        admin_name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        country = request.form.get("country", "").strip()

        if not company_name or not admin_name or not email or not password or not country:
            flash("All fields are required", "danger")
            return redirect(url_for("auth.signup"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return redirect(url_for("auth.signup"))

        countries = fetch_countries_and_currencies()
        currency_code = countries.get(country)
        if not currency_code:
            flash("Invalid country selected", "danger")
            return redirect(url_for("auth.signup"))

        company = Company(name=company_name, country=country, currency_code=currency_code)
        db.session.add(company)
        db.session.flush()

        admin = User(email=email, name=admin_name, role=Role.ADMIN, company_id=company.id)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        login_user(admin)
        flash("Company and admin created", "success")
        return redirect(url_for("admin.dashboard"))

    countries = fetch_countries_and_currencies()
    return render_template("auth/signup.html", countries=countries)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").lower()
        password = request.form.get("password", "")
        user: Optional[User] = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash("Welcome back!", "success")
            return redirect(url_for("auth.home"))
        flash("Invalid credentials", "danger")
        return redirect(url_for("auth.login"))
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("auth.home"))
