from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Resource, Student
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify("Campus Compass backend is running!")

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

    return jsonify({
        'message': 'Account created successfully',
        'id': new_student.id,
        'email': new_student.email,
        'username': new_student.username,
    })


@main.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400

    user = Student.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Authentication successful — return a simple success message.
    # In production you would return a token or set a secure session.
    return jsonify({'message': 'Login successful', 'username': user.username})


@main.route('/tags')
def tags():
    resources = Resource.query.all()
    tags_set = set()
    for r in resources:
        if r.tags:
            for t in r.tags.split(','):
                t = t.strip().lower()
                if t:
                    tags_set.add(t)
    return jsonify(sorted(list(tags_set)))


@main.route('/set_interests', methods=['POST'])
def set_interests():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    interests = data.get('interests', [])

    if not email:
        return jsonify({'error': 'email is required'}), 400

    user = Student.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'user not found'}), 404

    user.interests = ','.join([i.strip().lower() for i in interests if i and i.strip()])
    db.session.commit()
    return jsonify({'message': 'Interests updated'})


@main.route('/recommendations')
def recommendations():
    # If an email query param is provided, filter resources by the user's interests
    email = request.args.get('email')
    resources = Resource.query.all()

    if email:
        user = Student.query.filter_by(email=email.strip().lower()).first()
        if user and user.interests:
            user_tags = set([t.strip().lower() for t in user.interests.split(',') if t.strip()])
            matched = []
            for r in resources:
                r_tags = set([t.strip().lower() for t in (r.tags or '').split(',') if t.strip()])
                if user_tags & r_tags:
                    matched.append(r)
            resources = matched

    return jsonify([
        {"title": r.title, "category": r.category}
        for r in resources
    ])

