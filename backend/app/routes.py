from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Resource, Student
from app import db

# Backend API blueprint for Campus Compass.
# Provides user signup, login, interest selection, and recommendation endpoints.
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify("Campus Compass backend is running!")

@main.route('/signup', methods=['POST'])
def signup():
    """
    Create a new student account.

    Expected request JSON:
      {
        "username": "string",
        "email": "string",
        "password": "string"
      }

    Validation:
      - username, email, and password are required
      - email must end with '@gmu.edu'
      - email must be unique

    Returns JSON on success:
      {
        "message": "Account created successfully",
        "id": <integer>,
        "email": "string",
        "username": "string"
      }

    Returns JSON error responses with HTTP status codes 400 or 409.
    """
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
    """
    Authenticate an existing student.

    Expected request JSON:
      {
        "email": "string",
        "password": "string"
      }

    Output on success:
      {
        "message": "Login successful",
        "username": "string"
      }

    Returns 400 for missing credentials and 401 for invalid login.
    """
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
    """
    Return a sorted list of unique resource tags.

    Output:
      ["tag1", "tag2", ...]

    This endpoint is used by the frontend interest selection page.
    """
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
    """
    Save a user's selected interests.

    Expected request JSON:
      {
        "email": "string",
        "interests": ["tag1", "tag2", ...]
      }

    Behavior:
      - finds the student by email
      - stores interests as a lowercase comma-separated string

    Returns:
      {"message": "Interests updated"}

    Returns 400 for missing email and 404 if user is not found.
    """
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
    """
    Return resource recommendations.

    Query parameters:
      email (optional): filter results by the user's saved interests.

    Behavior:
      - without email: returns all resources
      - with email: returns only resources that share at least one tag with user interests

    Output:
      [
        {"title": "resource title", "category": "category"},
        ...
      ]
    """
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

