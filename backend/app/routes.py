from flask import Blueprint, jsonify
from app.models import Resource
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify({"message": "Campus Compass backend is running!"})

@main.route('/recommendations')
def recommendations():
  resources=Resource.query.all()
  return jsonify([{"title":r.title, 
                   "category":r.category
                  } for r in resources])
  
