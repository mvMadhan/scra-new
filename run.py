from app import create_app
from atexit import register

# Only create the app — don't add jobs here
app = create_app()

# Make sure scheduler inside scan.py handles everything dynamically
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
