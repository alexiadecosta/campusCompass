from app import db

class Student(db.Model):
    """
    Student account model.

    Fields:
      id: primary key
      username: display name for the student
      email: unique GMU email address used for login
      password: hashed password string
      interests: comma-separated lowercase tags saved by the student
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    interests = db.Column(db.Text)


class Resource(db.Model):
    """
    Campus resource model.

    Fields:
      id: primary key
      title: resource title
      category: high-level category for display
      tags: comma-separated list of interest tags
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))
