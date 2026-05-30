from app import create_app, db
from app.models import Student, Resource

app=create_app()

def seed_database():
    with app.app_context():
        print("Clearing existing data...")
        db.session.query(Student).delete()
        db.session.query(Resource).delete()
        print("Creating new records...")

        #ADD MORE RESOURCES BELOW IN EACH CATEGORY

        #Student Organization
        resource2 = Resource(title="Student Clubs", category="Extracurricular", tags="clubs, activities, student life")
        #Food
        resource5 = Resource(title="Campus Dining", category="Food", tags="dining, food, restaurants")
        #Campus Events
        resource1 = Resource(title="Campus Map", category="Navigation", tags="map, campus, directions")
        #Career Resources
        resource6 = Resource(title="Career Services", category="Career", tags="career, jobs, internships")
        #Academic Resources
        resource3 = Resource(title="Academic Calendar", category="Academics", tags="calendar, schedule, academic")
        #Wellness and Support
        resource4 = Resource(title="Counseling Services", category="Wellness", tags="counseling, mental health, support")

        db.session.add_all([resource1, resource2, resource3, resource4, resource5, resource6])
        db.session.commit() #save changes to the database
        print("Database seeded successfully!")

#run python backend/seed.py to seed the database with initial data
if __name__ == '__main__':
    seed_database()

