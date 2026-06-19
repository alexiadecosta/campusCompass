from flask import Flask
from flask_cors import CORS #cross-origin resource sharing, frontend (React) is hosted on diff domain than backend
from flask_sqlalchemy import SQLAlchemy #object-relational mapper

db = SQLAlchemy() #database

def create_app():
    app = Flask(__name__)
    import os
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'postgresql://postgres:password@localhost/campusCompass'
    )
    # Secret key for token generation; set via env in production
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    # Session lifetime (seconds) default 1 day
    app.config['TOKEN_EXPIRES'] = int(os.environ.get('TOKEN_EXPIRES', 86400))
    CORS(app)
    db.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
