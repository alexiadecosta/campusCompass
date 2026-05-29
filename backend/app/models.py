from app import db

class Student(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  username=db.Column(db.String(80))
  email=db.Column(db.String(120), unique=True)
  password=db.Column(db.String(200))
  interests=db.Column(db.Text)

class Resource(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  title=db.Column(db.String(200))
  category=db.Column(db.String(50))
  tags=db.Column(db.String(200))
