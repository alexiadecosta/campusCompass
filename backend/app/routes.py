from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime
from app.models import Resource, Student, Interest, SavedResource
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
    if Student.query.filter_by(gmu_email=email).first():
      return jsonify({'error': 'A user with that email already exists'}), 409

    hashed_password = generate_password_hash(password)
    new_student = Student(username=username, gmu_email=email, password_hash=hashed_password)
    db.session.add(new_student)
    db.session.commit()
    # generate auth token
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps({'id': new_student.id})

    return jsonify({
      'message': 'Account created successfully',
      'id': new_student.id,
      'email': new_student.gmu_email,
      'username': new_student.username,
      'token': token
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

    user = Student.query.filter_by(gmu_email=email).first()
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    if not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401
    # Authentication successful — generate token
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps({'id': user.id})
    return jsonify({'message': 'Login successful', 'username': user.username, 'token': token})


@main.route('/tags')
def tags():
    """
    Return a sorted list of unique resource tags.

    Output:
      ["tag1", "tag2", ...]

    This endpoint is used by the frontend interest selection page.
    """
    # Combine Interest table values with legacy resource tag strings
    tags = set()
    for i in Interest.query.all():
      tags.add(i.name)
    resources = Resource.query.all()
    for r in resources:
      if getattr(r, 'tags', None):
        for t in r.tags.split(','):
          t = t.strip().lower()
          if t:
            tags.add(t)
    return jsonify(sorted(list(tags)))


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
    # Prefer authorization header with token; fall back to email param
    auth = request.headers.get('Authorization', '')
    user = None
    if auth.startswith('Bearer '):
      token = auth.split(' ', 1)[1].strip()
      s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
      try:
        data_token = s.loads(token, max_age=current_app.config.get('TOKEN_EXPIRES', 86400))
        user = Student.query.get(data_token.get('id'))
      except SignatureExpired:
        return jsonify({'error': 'token expired'}), 401
      except BadSignature:
        return jsonify({'error': 'invalid token'}), 401

    if not user:
      email = data.get('email', '').strip().lower()
      if not email:
        return jsonify({'error': 'email or Authorization token is required'}), 400
      user = Student.query.filter_by(gmu_email=email).first()
      if not user:
        return jsonify({'error': 'user not found'}), 404

    interests = data.get('interests', [])
    # Clear existing interests
    user.interests = []
    for i in interests:
      name = i.strip().lower()
      if not name:
        continue
      interest = Interest.query.filter_by(name=name).first()
      if not interest:
        interest = Interest(name=name)
        db.session.add(interest)
        db.session.flush()
      if interest not in user.interests:
        user.interests.append(interest)

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
    # Accept token via Authorization header or email query param
    auth = request.headers.get('Authorization', '')
    user = None
    if auth.startswith('Bearer '):
      token = auth.split(' ', 1)[1].strip()
      s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
      try:
        data_token = s.loads(token, max_age=current_app.config.get('TOKEN_EXPIRES', 86400))
        user = Student.query.get(data_token.get('id'))
      except Exception:
        user = None

    if not user:
      email = request.args.get('email')
      if email:
        user = Student.query.filter_by(gmu_email=email.strip().lower()).first()

    resources = Resource.query.all()

    # If we have a user, compute a relevance score per resource.
    results = []
    now = datetime.utcnow()

    # gather popularity counts for normalization
    save_counts = {}
    max_count = 0
    for r in resources:
      cnt = db.session.query(SavedResource).filter_by(resource_id=r.id).count()
      save_counts[r.id] = cnt
      if cnt > max_count:
        max_count = cnt

    for r in resources:
      # compute tag overlap
      r_tags = set([i.name for i in r.interests]) if getattr(r, 'interests', None) else set()
      if not r_tags and getattr(r, 'tags', None):
        r_tags = set([t.strip().lower() for t in (r.tags or '').split(',') if t.strip()])

      tag_overlap = 0
      if user and user.interests:
        user_tags = set([i.name for i in user.interests])
        tag_overlap = len(user_tags & r_tags)

      # classification match boost
      class_score = 0
      if not r.classification_target or r.classification_target in ('all', None):
        class_score = 1
      elif user and user.classification and r.classification_target == user.classification:
        class_score = 1

      # popularity normalized
      pop = save_counts.get(r.id, 0)
      pop_score = (pop / max_count) if max_count > 0 else 0

      # recency score: more recent => closer to 1 (within 365 days)
      days = (now - (r.updated_at or r.created_at)).days if (r.updated_at or r.created_at) else 365
      recency_score = max(0.0, 1.0 - (days / 365.0))

      # combine scores with weights
      score = 0.0
      # tag relevance weight: prefer exact overlap — normalized by max possible overlap
      score += 0.6 * (tag_overlap / (len(user.interests) if user and user.interests else 1)) if user and user.interests else 0
      score += 0.2 * class_score
      score += 0.1 * pop_score
      score += 0.1 * recency_score

      results.append((score, r))

    # if user exists, sort by score descending, otherwise sort by popularity+recency
    if user:
      results.sort(key=lambda x: x[0], reverse=True)
    else:
      results.sort(key=lambda x: (save_counts.get(x[1].id, 0), (now - (x[1].updated_at or x[1].created_at)).days), reverse=True)

    return jsonify([
      {
        "id": r.id,
        "title": r.title,
        "category": r.category,
        "description": r.description,
        "link": r.link,
        "classification_target": r.classification_target,
        "tags": getattr(r, 'tags', None),
        "score": float(score)
      }
      for score, r in results
    ])


@main.route('/resources')
def resources():
    """
    Return resources filtered by category.

    Query parameters:
      category (optional): filter results by category (e.g., 'student_orgs', 'food', 'events', 'career', 'academic', 'wellness')

    Behavior:
      - without category: returns all resources
      - with category: returns only resources matching that category

    Output:
      [
        {"id": <id>, "title": "resource title", "category": "category", "tags": "tag1, tag2"},
        ...
      ]
    """
    category = request.args.get('category')
    
    if category:
      resources_q = Resource.query.filter_by(category=category.strip())
    else:
      resources_q = Resource.query

    resources = resources_q.all()

    return jsonify([
      {
        "id": r.id,
        "title": r.title,
        "category": r.category,
        "description": r.description,
        "link": r.link,
        "classification_target": r.classification_target,
        "tags": getattr(r, 'tags', None)
      }
      for r in resources
    ])


def _get_user_from_token():
  auth = request.headers.get('Authorization', '')
  if not auth.startswith('Bearer '):
    return None
  token = auth.split(' ', 1)[1].strip()
  s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
  try:
    data_token = s.loads(token, max_age=current_app.config.get('TOKEN_EXPIRES', 86400))
    return Student.query.get(data_token.get('id'))
  except Exception:
    return None


def _require_admin():
  user = _get_user_from_token()
  if not user:
    return None, (jsonify({'error': 'invalid or missing token'}), 401)
  if not getattr(user, 'is_admin', False):
    return None, (jsonify({'error': 'admin privileges required'}), 403)
  return user, None


@main.route('/admin/resource', methods=['POST'])
def admin_create_resource():
  """Admin: create a new resource. Expects JSON with fields:
    title (required), description, category (required), classification_target, link, tags (array or comma string)
  """
  user, err = _require_admin()
  if err:
    return err

  data = request.get_json() or {}
  title = data.get('title', '').strip()
  category = data.get('category', '').strip()
  description = data.get('description')
  classification_target = data.get('classification_target')
  link = data.get('link')
  tags_in = data.get('tags', [])

  if not title or not category:
    return jsonify({'error': 'title and category are required'}), 400

  # normalize tags into list of lowercase strings
  if isinstance(tags_in, str):
    tags_list = [t.strip().lower() for t in tags_in.split(',') if t.strip()]
  elif isinstance(tags_in, list):
    tags_list = [str(t).strip().lower() for t in tags_in if str(t).strip()]
  else:
    tags_list = []

  resource = Resource(title=title, description=description, category=category, classification_target=classification_target, link=link, tags=(', '.join(tags_list) if tags_list else None))
  db.session.add(resource)
  db.session.flush()

  # attach interests
  for name in tags_list:
    interest = Interest.query.filter_by(name=name).first()
    if not interest:
      interest = Interest(name=name)
      db.session.add(interest)
      db.session.flush()
    if interest not in resource.interests:
      resource.interests.append(interest)

  db.session.commit()
  return jsonify({'message': 'resource created', 'id': resource.id}), 201


@main.route('/admin/resource/<int:resource_id>', methods=['PUT', 'PATCH'])
def admin_update_resource(resource_id):
  user, err = _require_admin()
  if err:
    return err

  resource = Resource.query.get(resource_id)
  if not resource:
    return jsonify({'error': 'resource not found'}), 404

  data = request.get_json() or {}
  title = data.get('title')
  category = data.get('category')
  description = data.get('description')
  classification_target = data.get('classification_target')
  link = data.get('link')
  tags_in = data.get('tags')

  if title is not None:
    resource.title = title.strip()
  if category is not None:
    resource.category = category.strip()
  if description is not None:
    resource.description = description
  if classification_target is not None:
    resource.classification_target = classification_target
  if link is not None:
    resource.link = link

  # update tags if provided
  if tags_in is not None:
    if isinstance(tags_in, str):
      tags_list = [t.strip().lower() for t in tags_in.split(',') if t.strip()]
    elif isinstance(tags_in, list):
      tags_list = [str(t).strip().lower() for t in tags_in if str(t).strip()]
    else:
      tags_list = []

    resource.tags = (', '.join(tags_list) if tags_list else None)
    # clear existing interests and reattach
    resource.interests = []
    for name in tags_list:
      interest = Interest.query.filter_by(name=name).first()
      if not interest:
        interest = Interest(name=name)
        db.session.add(interest)
        db.session.flush()
      if interest not in resource.interests:
        resource.interests.append(interest)

  db.session.commit()
  return jsonify({'message': 'resource updated'})


@main.route('/admin/resource/<int:resource_id>', methods=['DELETE'])
def admin_delete_resource(resource_id):
  user, err = _require_admin()
  if err:
    return err

  resource = Resource.query.get(resource_id)
  if not resource:
    return jsonify({'error': 'resource not found'}), 404

  db.session.delete(resource)
  db.session.commit()
  return jsonify({'message': 'resource deleted'})


@main.route('/resource/<int:resource_id>/save', methods=['POST'])
def save_resource(resource_id):
  """Save a resource for the authenticated user."""
  user = _get_user_from_token()
  if not user:
    return jsonify({'error': 'invalid or missing token'}), 401

  resource = Resource.query.get(resource_id)
  if not resource:
    return jsonify({'error': 'resource not found'}), 404

  existing = SavedResource.query.filter_by(user_id=user.id, resource_id=resource_id).first()
  if existing:
    return jsonify({'message': 'already saved'}), 200

  sr = SavedResource(user_id=user.id, resource_id=resource_id)
  db.session.add(sr)
  db.session.commit()
  return jsonify({'message': 'resource saved'})


@main.route('/resource/<int:resource_id>/save', methods=['DELETE'])
def unsave_resource(resource_id):
  """Remove a saved resource for the authenticated user."""
  user = _get_user_from_token()
  if not user:
    return jsonify({'error': 'invalid or missing token'}), 401

  saved = SavedResource.query.filter_by(user_id=user.id, resource_id=resource_id).first()
  if not saved:
    return jsonify({'message': 'not saved'}), 200

  db.session.delete(saved)
  db.session.commit()
  return jsonify({'message': 'resource unsaved'})


@main.route('/saved')
def list_saved():
  """Return saved resources for the authenticated user."""
  user = _get_user_from_token()
  if not user:
    return jsonify({'error': 'invalid or missing token'}), 401

  saved_rows = SavedResource.query.filter_by(user_id=user.id).order_by(SavedResource.saved_at.desc()).all()
  resources = [Resource.query.get(s.resource_id) for s in saved_rows]
  return jsonify([
    { 'id': r.id, 'title': r.title, 'category': r.category, 'link': r.link, 'tags': getattr(r, 'tags', None) }
    for r in resources if r
  ])

