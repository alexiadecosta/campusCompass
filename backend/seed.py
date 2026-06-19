from app import create_app, db
from app.models import Student, Resource, Interest
from werkzeug.security import generate_password_hash

app = create_app()


def seed_database():
    with app.app_context():
        print("Resetting database schema...")
        db.drop_all()
        db.create_all()
        print("Creating new records...")

        # Resources (legacy tags kept)
        resource2 = Resource(title="Student Clubs", category="student_orgs", tags="clubs, activities, student life")
        resource5 = Resource(title="Campus Dining", category="food", tags="dining, food, restaurants")
        resource1 = Resource(title="Campus Map", category="events", tags="map, campus, directions")
        resource6 = Resource(title="Career Services", category="career", tags="career, jobs, internships")
        resource3 = Resource(title="Academic Calendar", category="academic", tags="calendar, schedule, academic")
        resource4 = Resource(title="Counseling Services", category="wellness", tags="counseling, mental health, support")

        db.session.add_all([resource1, resource2, resource3, resource4, resource5, resource6])
        db.session.flush()

        # Create interests from resource tags
        tag_set = set()
        for r in [resource1, resource2, resource3, resource4, resource5, resource6]:
            if r.tags:
                for t in r.tags.split(','):
                    tag_set.add(t.strip().lower())

        interests = []
        for t in sorted(tag_set):
            interest = Interest(name=t)
            interests.append(interest)
            db.session.add(interest)

        db.session.commit()

        # Create demo user
        demo = Student(username='demo_student', gmu_email='demo@gmu.edu', password_hash=generate_password_hash('password123'), classification='freshman')
        # associate a couple interests
        if interests:
            demo.interests.append(interests[0])
            if len(interests) > 1:
                demo.interests.append(interests[1])

        db.session.add(demo)
        db.session.commit()
        print("Database seeded successfully!")


# run `python backend/seed.py` to seed the database with initial data
if __name__ == '__main__':
    seed_database()

