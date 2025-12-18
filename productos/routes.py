from flask import Blueprint, render_template, request, redirect, session, flash
from auth.seguridad import login_required
from models import ProductoDB, Producto, Movimiento
from db import get_db  # ¡IMPORTANTE!
from datetime import datetime

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

# -------------------------------
# FUNCIÓN AUXILIAR: OBTENER CATEGORÍAS
# -------------------------------
def obtener_categorias():
    """Obtiene todas las categorías activas de la base de datos"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, nombre, descripcion 
        FROM categorias 
        WHERE activo = 1 
        ORDER BY nombre ASC
    """)
    
    return cursor.fetchall()

# -------------------------------
# LISTAR PRODUCTOS
# -------------------------------
@productos_bp.route("/")
@login_required()
def listar_productos():
    productos = ProductoDB.obtener_todos()
    return render_template("productos.html", productos=productos)

# -------------------------------
# CREAR PRODUCTO (CON CATEGORÍAS)
# -------------------------------
@productos_bp.route("/crear", methods=["GET", "POST"])
@login_required()
def crear_producto():
    if request.method == "POST":
        try:
            # Validar datos del formulario
            nombre = request.form["nombre"].strip()
            descripcion = request.form.get("descripcion", "").strip()
            
            # Manejar categoría - puede estar vacía
            categoria_id = request.form.get("categoria_id")
            if categoria_id == "" or categoria_id is None:
                categoria_id = None
            else:
                categoria_id = int(categoria_id) if categoria_id else None
            
            stock = int(request.form.get("stock", 0))
            stock_minimo = int(request.form.get("stock_minimo", 0))
            precio = float(request.form.get("precio", 0))
            imagen = request.form.get("imagen", "").strip() or None
            
            # Validaciones básicas
            if not nombre:
                flash("El nombre del producto es obligatorio", "error")
                return redirect("/productos/crear")
            
            if stock < 0:
                flash("El stock no puede ser negativo", "error")
                return redirect("/productos/crear")
            
            if precio < 0:
                flash("El precio no puede ser negativo", "error")
                return redirect("/productos/crear")
            
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
            
            # Registrar movimiento automático
            usuario_id = session.get("user_id")
            if usuario_id:
                mov = Movimiento(
                    producto_id=producto.id, 
                    usuario_id=usuario_id, 
                    tipo="entrada", 
                    fecha=datetime.now()
                )
                mov.registrar()
            
            flash(f"✅ Producto '{nombre}' creado exitosamente", "success")
            return redirect("/productos/")
            
        except ValueError as e:
            flash(f"Error en los datos: {str(e)}", "error")
            return redirect("/productos/crear")
        except Exception as e:
            flash(f"Error al crear producto: {str(e)}", "error")
            return redirect("/productos/crear")
    
    # GET: Mostrar formulario con categorías
    categorias = obtener_categorias()
    return render_template(
        "producto_form.html", 
        producto=None, 
        categorias=categorias
    )

# -------------------------------
# EDITAR PRODUCTO (CON CATEGORÍAS)
# -------------------------------
@productos_bp.route("/editar/<int:producto_id>", methods=["GET", "POST"])
@login_required()
def editar_producto(producto_id):
    producto = ProductoDB.obtener_por_id(producto_id)
    if not producto:
        flash("Producto no encontrado", "error")
        return redirect("/productos/")
    
    if request.method == "POST":
        try:
            # Validar datos del formulario
            producto.nombre = request.form["nombre"].strip()
            producto.descripcion = request.form.get("descripcion", "").strip()
            
            # Manejar categoría - puede estar vacía
            categoria_id = request.form.get("categoria_id")
            if categoria_id == "" or categoria_id is None:
                producto.categoria_id = None
            else:
                producto.categoria_id = int(categoria_id) if categoria_id else None
            
            producto.stock = int(request.form.get("stock", 0))
            producto.stock_minimo = int(request.form.get("stock_minimo", 0))
            producto.precio = float(request.form.get("precio", 0))
            
            imagen = request.form.get("imagen", "").strip()
            producto.imagen = imagen if imagen else None
            
            # Validaciones básicas
            if not producto.nombre:
                flash("El nombre del producto es obligatorio", "error")
                return redirect(f"/productos/editar/{producto_id}")
            
            if producto.stock < 0:
                flash("El stock no puede ser negativo", "error")
                return redirect(f"/productos/editar/{producto_id}")
            
            if producto.precio < 0:
                flash("El precio no puede ser negativo", "error")
                return redirect(f"/productos/editar/{producto_id}")
            
            # Guardar cambios
            producto.actualizar()
            
            # Registrar movimiento automático
            usuario_id = session.get("user_id")
            if usuario_id:
                mov = Movimiento(
                    producto_id=producto.id, 
                    usuario_id=usuario_id, 
                    tipo="entrada", 
                    fecha=datetime.now()
                )
                mov.registrar()
            
            flash(f"✅ Producto '{producto.nombre}' actualizado exitosamente", "success")
            return redirect("/productos/")
            
        except ValueError as e:
            flash(f"Error en los datos: {str(e)}", "error")
            return redirect(f"/productos/editar/{producto_id}")
        except Exception as e:
            flash(f"Error al actualizar producto: {str(e)}", "error")
            return redirect(f"/productos/editar/{producto_id}")
    
    # GET: Mostrar formulario con categorías y producto existente
    categorias = obtener_categorias()
    return render_template(
        "producto_form.html", 
        producto=producto, 
        categorias=categorias
    )

# -------------------------------
# ELIMINAR PRODUCTO
# -------------------------------
@productos_bp.route("/eliminar/<int:producto_id>", methods=["POST"])  # Cambiar a POST para seguridad
@login_required()
def eliminar_producto(producto_id):
    producto = ProductoDB.obtener_por_id(producto_id)
    if not producto:
        flash("Producto no encontrado", "error")
        return redirect("/productos/")
    
    try:
        # Verificar si el producto tiene movimientos asociados
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as count FROM movimientos 
            WHERE producto_id = %s
        """, (producto_id,))
        
        movimientos_count = cursor.fetchone()["count"]
        
        # Eliminar producto
        producto.eliminar()
        
        # Registrar movimiento de eliminación
        usuario_id = session.get("user_id")
        if usuario_id:
            mov = Movimiento(
                producto_id=producto.id, 
                usuario_id=usuario_id, 
                tipo="salida", 
                fecha=datetime.now()
            )
            mov.registrar()
        
        flash(f"✅ Producto '{producto.nombre}' eliminado exitosamente", "success")
        
    except Exception as e:
        flash(f"Error al eliminar producto: {str(e)}", "error")
    
    return redirect("/productos/")