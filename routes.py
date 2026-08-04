from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import app
from db import db
from flask_jwt_extended import JWTManager

@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()

    reg_username = data.get('username')
    reg_email = data.get('email')
    reg_password = data.get('password')

    if not reg_email or not reg_username or not reg_password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(username=reg_username).first():
        return jsonify({"error": "username already exists"}), 400
    if User.query.filter_by(email=reg_email).first():
        return jsonify({"error": "email already exists"}), 400

    hashed_pw = generate_password_hash(reg_password)

    new_user = User(username=reg_username, email=reg_email, password=hashed_pw)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registered successfully"}), 201

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()

    log_email = data.get('email')
    log_password = data.get('password')

    if not log_email or not log_password:
        return jsonify({"error": "Missing required fields"}), 400

    user_db = User.query.filter_by(email=log_email).first()
    if not user_db:
        return jsonify({"error": "Invalid email or password"}), 400

    hashed_pw_db = user_db.password

    if not check_password_hash(hashed_pw_db, log_password):
        return jsonify({"error": "Invalid email or password"}), 400

    return jsonify({"message": "Login successful"}), 200
