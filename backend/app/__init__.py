from flask import Flask
from flask_cors import CORS #cross-origin resource sharing, frontend (React) is hosted on diff domain than backend
from flask_sqlalchemy import SQLAlchemy #object-relational mapper

db=SQLAlchemy() #database
def create_app():
  app=Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI']=\'postgresql://postgres:password@localhost/campusCompass'
  CORS(app)
  db.init_app(app)
  from app.routes import main
  app.register_blueprint(main)
  return app
