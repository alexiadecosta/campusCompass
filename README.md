# Campus Compass

## Overview

Campus Compass is a campus resource recommendation app with:
- A Flask backend serving API endpoints and storing users/resources in PostgreSQL
- A React frontend that allows users to sign up, log in, select interests, and view personalized recommendations

## Repository Structure

- `backend/`
  - `run.py`: app startup script
  - `app/__init__.py`: Flask app factory and database initialization
  - `app/routes.py`: API endpoints for signup, login, tags, interests, and recommendations
  - `app/models.py`: SQLAlchemy models for `Student` and `Resource`
  - `seed.py`: database seeding script for sample resources
- `frontend/`
  - `package.json`: frontend package configuration
  - `src/`: React application files
  - `src/pages/`: `Landing`, `Signup`, `Login`, `Interests`, and `Dashboard` pages
  - `src/api.js`: frontend API helper for talking to backend

## Prerequisites

Team members need:
- GitHub access to this repository
- Node.js and npm installed
- Python 3.11+ installed
- PostgreSQL installed and running locally

## Backend Setup

1. Open a terminal and navigate to the repo root.

2. Create a Python virtual environment and activate it:

```powershell
cd c:\Users\<username>\campusCompass
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install backend dependencies:

```powershell
pip install -r backend/requirements.txt
```

4. Create the PostgreSQL database

Use a PostgreSQL client or `psql` and create the database used in the app config:

```sql
CREATE DATABASE campusCompass;
```

5. Confirm the backend database URL in `backend/app/__init__.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/campusCompass'
```

If your local database user or password differs, update that URI accordingly.

6. Run the backend:

```powershell
python backend/run.py
```

You should see the backend running. Verify by opening:

```text
http://localhost:5000/
```

It should return a simple JSON message.

## Frontend Setup

1. Open a new terminal and navigate to the frontend folder:

```powershell
cd c:\Users\<username>\campusCompass\frontend
```

2. Install frontend dependencies:

```powershell
npm install
```

3. Start the React app:

```powershell
npm start
```

4. Open the website in a browser:

```text
http://localhost:3000/
```

## Using the App

1. Visit `http://localhost:3000/`
2. Click **Sign Up** to create a new account.
   - Accounts must use a `@gmu.edu` email address.
3. After signup, you are redirected to the **Interests** page.
4. Select interests (tags) and save them.
5. View personalized recommendations on the **Dashboard**.
6. Use **Log In** to return later and view your recommendations again.

## API Endpoints

- `GET /` — health check
- `POST /signup` — create a new user
- `POST /login` — authenticate user
- `GET /tags` — retrieve available interest tags from resources
- `POST /set_interests` — save user interest tags
- `GET /recommendations?email=<email>` — retrieve recommendations filtered by user interests

## Database Notes

- `Student` model fields:
  - `id`, `username`, `email`, `password`, and `interests`
  - `interests` is stored as a comma-separated string
- `Resource` model fields:
  - `id`, `title`, `category`, `tags`
  - `tags` is a comma-separated string of resource tags

## Seeding Sample Data

To add initial sample resources, run:

```powershell
python backend/seed.py
```

## Common Commands

```powershell
# Start backend
python backend/run.py

# Start frontend
cd frontend
npm start

# Seed the database
python backend/seed.py
```

## Notes for Team Members

- If the app does not start, check that PostgreSQL is running and the database URI matches your local credentials.
- If `npm start` fails, run `npm install` again and ensure Node.js is installed.
- For GitHub collaboration, create feature branches and submit pull requests for changes.
- This repository currently uses local `localStorage` to track the logged-in user's email for personalization.
