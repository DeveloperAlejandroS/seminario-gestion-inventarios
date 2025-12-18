from flask import Blueprint, render_template, redirect, request
from auth.seguridad import login_required
from db import get_db
from models import UsuarioDB
import bcrypt

admin_bp = Blueprint("admin", __name__)

# -------------------------------
# DASHBOARD ADMIN
# -------------------------------
@admin_bp.route("/dashboard")
@login_required("admin")
def dashboard_admin():
    """
    Muestra el dashboard del administrador con estadísticas clave.
    Estadísticas incluidas:
    - Total de productos
    - Productos con stock bajo
    - Últimos movimientos de inventario
    - Total de usuarios
    
    Returns:
    - Renderiza la plantilla 'dashboard.html' con las estadísticas.
    
    """
    
    # Conexión a la base de datos y cursor para consultas
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Total productos activos en inventario
    cursor.execute("SELECT COUNT(*) AS total FROM productos WHERE activo = 1")
    total_productos = cursor.fetchone()["total"]

    # Productos con stock bajo (<= stock_minimo)
    cursor.execute("""
        SELECT nombre, stock, stock_minimo
        FROM productos
        WHERE activo = 1 AND stock <= stock_minimo
    """)
    stock_bajo = cursor.fetchall()

    # Últimos movimientos de inventario (5 más recientes) 
    cursor.execute("""
    SELECT 
        m.fecha_movimiento AS fecha,
        p.nombre AS producto,
        u.nombre AS usuario,
        m.tipo
    FROM movimientos m
    JOIN productos p ON m.producto_id = p.id
    JOIN usuarios u ON m.usuario_id = u.id
    ORDER BY m.fecha_movimiento DESC
    LIMIT 5
""")
    # Obtener los resultados de la consulta 
    ultimos_movimientos = cursor.fetchall()
    
    # Total de usuarios activos en el sistema 
    cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE activo = 1")
    total_usuarios = cursor.fetchone()["total"]

    return render_template(
        "dashboard.html",
        rol="admin",
        total_productos=total_productos,
        stock_bajo=stock_bajo,
        ultimos_movimientos=ultimos_movimientos,
        total_usuarios=total_usuarios
    )


# -------------------------------
# LISTAR USUARIOS
# -------------------------------
@admin_bp.route("/usuarios")
@login_required("admin")
def listar_usuarios():
    """
    Lista todos los usuarios del sistema.
    

    Returns:
    - Renderiza la plantilla 'usuarios.html' con la lista de usuarios.
    """
    usuarios = UsuarioDB.obtener_todos()
    return render_template("usuarios.html", usuarios=usuarios)


# -------------------------------
# ACTIVAR / DESACTIVAR
# -------------------------------
@admin_bp.route("/usuarios/estado/<int:usuario_id>")
@login_required("admin")
def cambiar_estado_usuario(usuario_id):
    """
    Cambia el estado (activo/inactivo) de un usuario.
    Args:
    - usuario_id (int): ID del usuario cuyo estado se va a cambiar.
    Returns:
    - Redirige a la página de lista de usuarios.
    """
    UsuarioDB.cambiar_estado(usuario_id)
    return redirect("/usuarios")

@admin_bp.route("/usuarios/crear", methods=["GET", "POST"])
@login_required("admin")
def crear_usuario():
    """
    Crea un nuevo usuario en el sistema.
    Returns:
    - GET: Renderiza el formulario de creación de usuario.
    - POST: Procesa el formulario y crea el usuario, luego redirige a la lista de usuarios.
    
    """
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]
        rol_id = request.form["rol_id"]

        # Hash de la contraseña
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Guardar en DB
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, password, rol_id)
            VALUES (%s, %s, %s, %s)
        """, (nombre, correo, password_hash, rol_id))
        db.commit()

        return redirect("/usuarios")

    # GET: mostrar formulario de creación
    return render_template("usuarios_crear.html")
