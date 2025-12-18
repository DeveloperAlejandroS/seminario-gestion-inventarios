from db import get_db
import bcrypt

# =========================
# USUARIOS
# =========================

class Usuario:
    def __init__(self, id, nombre, correo, activo=True):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.activo = activo

    @property
    def rol(self):
        raise NotImplementedError("Cada subclase define su rol")

    def puede_gestionar(self):
        return False


class Admin(Usuario):
    @property
    def rol(self):
        return "admin"

    def puede_gestionar(self):
        return True


class Operador(Usuario):
    @property
    def rol(self):
        return "operador"


# =========================
# USUARIOS DB
# =========================

class UsuarioDB:

    @staticmethod
    def obtener_todos():
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                u.id, u.nombre, u.correo, r.nombre AS rol, u.activo
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
        """)

        usuarios = []
        for u in cursor.fetchall():
            if u["rol"] == "admin":
                usuarios.append(Admin(u["id"], u["nombre"], u["correo"], u["activo"]))
            else:
                usuarios.append(Operador(u["id"], u["nombre"], u["correo"], u["activo"]))

        return usuarios

    @staticmethod
    def cambiar_estado(usuario_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE usuarios
            SET activo = IF(activo = 1, 0, 1)
            WHERE id = %s
        """, (usuario_id,))

        db.commit()
        
    @staticmethod
    def crear_usuario(nombre, correo, contrasena, rol_id):
        db = get_db()
        cursor = db.cursor()

        hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contrasena, rol_id, activo)
            VALUES (%s, %s, %s, %s, 1)
        """, (nombre, correo, hashed_password, rol_id))

        db.commit()
    
    


# =========================
# PRODUCTOS
# =========================

class Producto:
    def __init__(self, id, nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen, activo=True, creado_en=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria_id = categoria_id
        self.stock = stock
        self.stock_minimo = stock_minimo
        self.precio = precio
        self.imagen = imagen
        self.activo = activo
        self.creado_en = creado_en

    # Propiedad para saber si el stock está bajo
    def stock_bajo(self):
        return self.stock <= self.stock_minimo
    
    @classmethod
    def crear(cls, nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen, activo, creado_en)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1, NOW())
        """, (nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen))
        db.commit()
        producto_id = cursor.lastrowid
        return cls(producto_id, nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen)
    
    def actualizar(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE productos
            SET nombre=%s, descripcion=%s, categoria_id=%s, stock=%s, stock_minimo=%s, precio=%s, imagen=%s
            WHERE id=%s
        """, (self.nombre, self.descripcion, self.categoria_id, self.stock, self.stock_minimo, self.precio, self.imagen, self.id))
        db.commit()

    def eliminar(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE productos SET activo=0 WHERE id=%s", (self.id,))
        db.commit()

# =========================
# PRODUCTOS DB
# =========================

class ProductoDB:

    @staticmethod
    def obtener_todos():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen, activo, creado_en
            FROM productos
            WHERE activo = 1
        """)
        productos = []
        for p in cursor.fetchall():
            productos.append(Producto(**p))
        return productos

    @staticmethod
    def obtener_por_id(producto_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen, activo, creado_en
            FROM productos
            WHERE id = %s
        """, (producto_id,))
        data = cursor.fetchone()
        if data:
            return Producto(**data)
        return None

    @staticmethod
    def crear(nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen))
        db.commit()

    def actualizar(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE productos
            SET nombre=%s, descripcion=%s, categoria_id=%s, stock=%s, stock_minimo=%s, precio=%s, imagen=%s
            WHERE id=%s
        """, (self.nombre, self.descripcion, self.categoria_id, self.stock, self.stock_minimo, self.precio, self.imagen, self.id))
        db.commit()

    def eliminar(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE productos SET activo=0 WHERE id=%s",
            (self.id,)
        )
        db.commit()


class Movimiento:
    def __init__(self, producto_id, usuario_id, tipo, fecha=None):
        self.producto_id = producto_id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.fecha = fecha

    def registrar(self):
        """Guarda el movimiento en la base de datos"""
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO movimientos (producto_id, usuario_id, tipo, fecha_movimiento)
            VALUES (%s, %s, %s, NOW())
        """, (self.producto_id, self.usuario_id, self.tipo))

        db.commit()

    @staticmethod
    def obtener_todos():
        """
        Obtiene todos los movimientos con los nombres del usuario y del producto
        """
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                m.id,
                p.nombre AS producto,
                u.nombre AS usuario,
                m.tipo,
                m.fecha
            FROM movimientos m
            JOIN productos p ON m.producto_id = p.id
            JOIN usuarios u ON m.usuario_id = u.id
            ORDER BY m.fecha DESC
        """)

        return cursor.fetchall()


from flask import Blueprint, render_template, request, redirect, session
from auth.seguridad import login_required
from models import ProductoDB, Producto, Admin, Operador, Movimiento
from datetime import datetime

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

# -------------------------------
# LISTAR PRODUCTOS
# -------------------------------
@productos_bp.route("/")
@login_required()
def listar_productos():
    productos = ProductoDB.obtener_todos()
    return render_template("productos.html", productos=productos)

# -------------------------------
# CREAR PRODUCTO
# -------------------------------
@productos_bp.route("/crear", methods=["GET", "POST"])
@login_required()
def crear_producto():
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form.get("descripcion", "")
        categoria_id = request.form.get("categoria_id") or None
        stock = int(request.form.get("stock", 0))
        stock_minimo = int(request.form.get("stock_minimo", 0))
        precio = float(request.form.get("precio", 0))
        imagen = request.form.get("imagen") or None

        # Crear producto con POO
        producto = Producto.crear(
            nombre=nombre,
            descripcion=descripcion,
            categoria_id=categoria_id,
            stock=stock,
            stock_minimo=stock_minimo,
            precio=precio,
            imagen=imagen
        )
        
        usuario_id = session.get("user_id")
        if usuario_id:
            mov = Movimiento(producto_id=producto.id, usuario_id=usuario_id, tipo="entrada", fecha=datetime.now())
            mov.registrar()

        return redirect("/productos/")

    return render_template("producto_form.html", producto=None)

# -------------------------------
# EDITAR PRODUCTO
# -------------------------------
@productos_bp.route("/editar/<int:producto_id>", methods=["GET", "POST"])
@login_required()
def editar_producto(producto_id):
    producto = ProductoDB.obtener_por_id(producto_id)
    if not producto:
        return "Producto no encontrado", 404

    if request.method == "POST":
        producto.nombre = request.form["nombre"]
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form["stock"])
        producto.stock_minimo = int(request.form["stock_minimo"])

        producto.actualizar()
        
        usuario_id = session.get("user_id")
        if usuario_id:
            mov = Movimiento(producto_id=producto.id, usuario_id=usuario_id, tipo="entrada", fecha=datetime.now())
            mov.registrar()
            
        return redirect("/productos/")

    return render_template("productos_editar.html", producto=producto)

# -------------------------------
# ELIMINAR PRODUCTO
# -------------------------------
@productos_bp.route("/eliminar/<int:producto_id>")
@login_required()
def eliminar_producto(producto_id):
    producto = ProductoDB.obtener_por_id(producto_id)
    if not producto:
        return "Producto no encontrado", 404

    producto.eliminar()
    
    usuario_id = session.get("user_id")
    if usuario_id:
        mov = Movimiento(producto_id=producto.id, usuario_id=usuario_id, tipo="salida", fecha=datetime.now())
        mov.registrar()
    return redirect("/productos/")

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
        rol="admin",
        total_productos=total_productos,
        stock_bajo=stock_bajo,
        ultimos_movimientos=ultimos_movimientos
    )


# -------------------------------
# LISTAR USUARIOS
# -------------------------------
@admin_bp.route("/usuarios")
@login_required("admin")
def listar_usuarios():
    usuarios = UsuarioDB.obtener_todos()
    return render_template("usuarios.html", usuarios=usuarios)


# -------------------------------
# ACTIVAR / DESACTIVAR
# -------------------------------
@admin_bp.route("/usuarios/estado/<int:usuario_id>")
@login_required("admin")
def cambiar_estado_usuario(usuario_id):
    UsuarioDB.cambiar_estado(usuario_id)
    return redirect("/usuarios")

@admin_bp.route("/usuarios/crear", methods=["GET", "POST"])
@login_required("admin")
def crear_usuario():
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
                return redirect("/dashboard")

        return "Credenciales incorrectas"

    return render_template("login.html")


# -------------------------------
# LOGOUT
# -------------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")