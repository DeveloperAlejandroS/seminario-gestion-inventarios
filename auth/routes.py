from flask import Blueprint, render_template, request, redirect, session
from db import get_db
import bcrypt

auth_bp = Blueprint("auth", __name__)

cache_usuario = {}

# -------------------------------
# LOGIN
# -------------------------------
@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT u.*, r.nombre AS rol
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE u.correo = %s AND u.activo = 1
        """, (correo,))

        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            session["user_id"] = user["id"]
            session["rol"] = user["rol"]
            
            cache_usuario[user["id"]] = {"rol": user["rol"], "nombre": user["nombre"]}

            if user["rol"] == "admin":
                return redirect("/dashboard")
            else:
                return redirect("/operador/dashboard")

        return "Credenciales incorrectas"

    return render_template("login.html")


# -------------------------------
# LOGOUT
# -------------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
