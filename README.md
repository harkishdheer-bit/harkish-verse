# Harkish Verse

A black-and-white, Spider-Man-inspired developer portfolio built with Python Flask and SQLite.

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
4. Open `http://127.0.0.1:5000`

The contact form saves messages into `harkish_verse.db`.

## Production notes

Before deploying publicly:
- Change `app.secret_key` in `app.py` to a strong secret.
- Turn `debug=False`.
- Use a production WSGI server such as Gunicorn.
- Add spam protection/rate limiting to the contact form.
- Keep the SQLite database private; for larger projects, move to PostgreSQL.

The visual theme is inspired by comic-book web patterns and spider imagery rather than copying Spider-Man artwork or logos.
