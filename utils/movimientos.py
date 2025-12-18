from db import get_db

def registrar_movimiento(producto_id, usuario_id, tipo, cantidad, proveedor_id=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Obtener stock actual
    cursor.execute(
        "SELECT stock FROM productos WHERE id = %s",
        (producto_id,)
    )
    producto = cursor.fetchone()

    if not producto:
        raise Exception("Producto no existe")

    stock_actual = producto["stock"]

    # Validar stock negativo
    if tipo == "salida" and cantidad > stock_actual:
        raise Exception("Stock insuficiente")

    # Registrar movimiento
    cursor.execute("""
        INSERT INTO movimientos
        (producto_id, usuario_id, tipo, cantidad, proveedor_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (producto_id, usuario_id, tipo, cantidad, proveedor_id))

    # Actualizar stock
    if tipo == "entrada":
        nuevo_stock = stock_actual + cantidad
    else:
        nuevo_stock = stock_actual - cantidad

    cursor.execute(
        "UPDATE productos SET stock = %s WHERE id = %s",
        (nuevo_stock, producto_id)
    )

    db.commit()
