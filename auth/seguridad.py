from flask import session, redirect
from functools import wraps

def login_required(rol=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect("/")
            if rol and session["rol"] != rol:
                return "Acceso denegado"
            return f(*args, **kwargs)
        return wrapper
    return decorator
