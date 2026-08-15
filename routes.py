from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Post
from app import app
from db import db
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

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
        return jsonify({"error": "Invalid email or password"}), 401

    hashed_pw_db = user_db.password

    if not check_password_hash(hashed_pw_db, log_password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user_db.id))

    return jsonify({"message": "Login successful", "access_token": access_token}), 200


@app.route("/post", methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()

    new_title = data.get('title')
    new_content = data.get('content')

    if not new_title or not new_content:
        return jsonify({"error": "Missing required fields"}), 400

    current_user_id = get_jwt_identity()

    new_post = Post(title=new_title, content=new_content, user_id=current_user_id)

    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "Post added successfully"}), 201

@app.route("/posts", methods=['GET'])
@jwt_required()
def get_posts():
    all_posts = Post.query.all()
    results = []

    for post in all_posts:
        post_data = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id
        }

        results.append(post_data)

    return jsonify({
        "total_posts": len(results),
        "posts": results}), 200

@app.route("/post/<int:id>", methods=['GET'])
@jwt_required()
def get_post_detail(id):
    post = Post.query.get(id)

    if not post:
        return jsonify({"message": "No post with this id"}), 404

    post_data = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at,
        "updated_at": post.updated_at
    }

    return jsonify({"post_detail": post_data}), 200

@app.route("/post/<int:id>", methods = ['PUT'])
@jwt_required()
def update_post(id):
    current_user_id = str(get_jwt_identity())

    post = Post.query.get(id)
    if not post:
        return jsonify({"error": "404 Not Found"}), 404

    if str(post.user_id) != current_user_id:
        return jsonify({"error": "You don't have permission to modify this post"}), 403

    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Missing update data"}), 400

    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)

    db.session.commit()

    return jsonify({"message": "Post updated successfully!"}), 200

@app.route("/post/<int:id>", methods = ['DELETE'])
@jwt_required()
def delete_post(id):
    current_user_id = str(get_jwt_identity())

    post = Post.query.get(id)
    if not post:
        return jsonify({"error": "404 Not Found"}), 404

    if str(post.user_id) != current_user_id:
        return jsonify({"error": "You don't have permission to delete this post"}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "Post deleted successfully!"}), 200