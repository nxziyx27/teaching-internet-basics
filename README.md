# Teaching Internet Basics — Web Version

This is a Flask web conversion of the original Tkinter Teaching Internet Basics project.

## Run locally

```bash
py -m pip install -r requirements.txt
py app.py
```

Open `http://127.0.0.1:5000`.

## Admin

Default credentials:
- Username: `admin`
- Password: `admin123`

Change these in Render environment variables before sharing publicly.

## Deploy to Render

1. Create a GitHub repository and upload this entire folder.
2. In Render, create a **New Web Service** from the GitHub repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Render automatically provides an HTTPS address such as `https://your-service.onrender.com`.

Important: this version uses SQLite, so it is best for a college/demo project. For permanent production data, move the database to PostgreSQL later.
