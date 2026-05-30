from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.models import Resource, Student
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify("Campus Compass backend is running!")

@main.route('/recommendations')
def recommendations():
    resources = Resource.query.all()
    return jsonify([
        {"title": r.title, "category": r.category}
        for r in resources
    ])

@main.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'username, email, and password are required'}), 400

    if not email.endswith('@gmu.edu'):
        return jsonify({'error': 'Please use a GMU email address'}), 400

    if Student.query.filter_by(email=email).first():
        return jsonify({'error': 'A user with that email already exists'}), 409

    hashed_password = generate_password_hash(password)
    new_student = Student(username=username, email=email, password=hashed_password)
    db.session.add(new_student)
    db.session.commit()

    return jsonify({'message': 'Account created successfully'})

