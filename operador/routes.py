from flask import Blueprint, render_template, request, redirect, session
from auth.seguridad import login_required
from db import get_db
from utils.movimientos import registrar_movimiento

operador_bp = Blueprint("operador", __name__)

@operador_bp.route("/operador/dashboard")
@login_required("operador")
def dashboard_operador():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Total productos
    cursor.execute("SELECT COUNT(*) AS total FROM productos WHERE activo = 1")
    total_productos = cursor.fetchone()["total"]

    # Productos con stock bajo
    cursor.execute("""
        SELECT nombre, stock, stock_minimo
        FROM productos
        WHERE activo = 1 AND stock <= stock_minimo
    """)
    stock_bajo = cursor.fetchall()

    # Últimos movimientos
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
    ultimos_movimientos = cursor.fetchall()

    return render_template(
        "dashboard.html",
        rol="operador",
        total_productos=total_productos,
        stock_bajo=stock_bajo,
        ultimos_movimientos=ultimos_movimientos
    )

# -------------------------------
# FORMULARIO MOVIMIENTO
# -------------------------------
@operador_bp.route("/operador/movimiento", methods=["GET", "POST"])
@login_required("operador")
def movimiento():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, nombre, stock FROM productos WHERE activo = 1")
    productos = cursor.fetchall()

    error = None

    if request.method == "POST":
        try:
            producto_id = int(request.form["producto_id"])
            tipo = request.form["tipo"]
            cantidad = int(request.form["cantidad"])
            usuario_id = session["user_id"]

            registrar_movimiento(producto_id, usuario_id, tipo, cantidad)
            return redirect("/operador/dashboard")

        except Exception as e:
            error = str(e)

    return render_template(
        "movimiento_form.html",
        productos=productos,
        error=error
    )


# -------------------------------
# HISTORIAL DE MOVIMIENTOS
# -------------------------------
@operador_bp.route("/operador/movimientos")
@login_required("operador")
def movimientos_operador():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            m.fecha,
            p.nombre AS producto,
            u.nombre AS usuario,
            m.tipo,
            m.cantidad
        FROM movimientos m
        JOIN productos p ON m.producto_id = p.id
        JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.fecha DESC
    """)

    movimientos = cursor.fetchall()
    return render_template("movimientos.html", movimientos=movimientos)