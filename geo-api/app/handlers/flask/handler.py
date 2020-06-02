from app import app
from app.handlers.flask import (
    response,
)
@app.route('/health')
def health():
    return response(200, "healthy!")
