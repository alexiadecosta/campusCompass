from app import db
from datetime import datetime

# Association table: users <-> interests
user_interests = db.Table(
    'user_interests',
    db.Column('user_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'), primary_key=True)
)

# Association table: resources <-> interests (tags)
resource_tags = db.Table(
    'resource_tags',
    db.Column('resource_id', db.Integer, db.ForeignKey('resource.id'), primary_key=True),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'), primary_key=True)
)


class Student(db.Model):
    """Student account model (users table).

    Columns:
      id (PK)
      username
      gmu_email (unique)
      password_hash
      classification (freshman/transfer/other)
      created_at
    Relationships:
      interests: many-to-many with Interest
      saved_resources: one-to-many with SavedResource
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    gmu_email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    classification = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    interests = db.relationship('Interest', secondary=user_interests, backref=db.backref('students', lazy='dynamic'))
    saved_resources = db.relationship('SavedResource', back_populates='user', cascade='all, delete-orphan')


class Interest(db.Model):
    """Interest / tag table.

    Columns:
      id (PK)
      name (unique)
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class Resource(db.Model):
    """Campus resource model.

    Columns:
      id (PK)
      title
      description
      category (events, academic, career, wellness, food, transportation)
      classification_target (nullable: freshman/transfer/other/all)
      link
      tags (legacy comma-separated string for backward compatibility)
      created_at
      updated_at
    Relationships:
      interests: many-to-many with Interest via resource_tags
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    classification_target = db.Column(db.String(20), nullable=True)
    link = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)  # legacy field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    interests = db.relationship('Interest', secondary=resource_tags, backref=db.backref('resources', lazy='dynamic'))


class SavedResource(db.Model):
    """Saved resources join table.

    Columns:
      id (PK)
      user_id (FK -> student.id)
      resource_id (FK -> resource.id)
      saved_at
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('Student', back_populates='saved_resources')
    resource = db.relationship('Resource')
