from db import get_db
import bcrypt

# ==============================================================================
# SECCIÓN 1: MODELO DE USUARIOS - Patrón de Herencia y Polimorfismo
# ==============================================================================
# Esta sección define la jerarquía de usuarios del sistema usando herencia.
# Se aplica el principio de sustitución de Liskov donde Admin y Operador son
# subtipos específicos de Usuario.

class Usuario:
    """
    Clase base abstracta que representa a cualquier usuario del sistema.
    No debe instanciarse directamente debido a que el método 'rol' lanza excepción.
    
    Atributos:
        id (int): Identificador único en la base de datos
        nombre (str): Nombre completo del usuario
        correo (str): Correo electrónico (funciona como username)
        activo (bool): Estado de la cuenta (True=activo, False=inactivo)
    
    Principio SOLID aplicado:
        - Open/Closed: Abierta para extensión (subclases Admin/Operador)
        - Liskov: Las subclases pueden sustituir a la clase base
    """
    def __init__(self, id, nombre, correo, activo=True):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.activo = activo

    @property
    def rol(self):
        """
        Propiedad abstracta que debe implementarse en subclases.
        
        Raises:
            NotImplementedError: Si se intenta acceder desde la clase base
        """
        raise NotImplementedError("Cada subclase define su rol")

    def puede_gestionar(self):
        """
        Determina si el usuario tiene permisos de administración.
        
        Returns:
            bool: False por defecto (solo Admin retorna True)
        """
        return False


class Admin(Usuario):
    """
    Representa un usuario con privilegios administrativos completos.
    Hereda de Usuario y sobreescribe métodos específicos.
    """
    @property
    def rol(self):
        """
        Implementación concreta de la propiedad rol.
        
        Returns:
            str: "admin" - identificador del rol administrativo
        """
        return "admin"

    def puede_gestionar(self):
        """
        Sobreescribe el método para otorgar permisos de administración.
        
        Returns:
            bool: True - indica que este usuario puede gestionar todo
        """
        return True


class Operador(Usuario):
    """
    Representa un usuario con permisos limitados a operaciones básicas.
    Hereda de Usuario con funcionalidad específica para operador.
    """
    @property
    def rol(self):
        """
        Implementación concreta de la propiedad rol.
        
        Returns:
            str: "operador" - identificador del rol operativo
        """
        return "operador"


# ==============================================================================
# SECCIÓN 2: CAPA DE ACCESO A DATOS DE USUARIOS - Patrón Repository
# ==============================================================================
# Esta clase maneja todas las operaciones de base de datos relacionadas con usuarios.
# Separa la lógica de persistencia del modelo de dominio.

class UsuarioDB:
    """
    Clase Repository para operaciones CRUD de usuarios en la base de datos.
    Utiliza métodos estáticos para no requerir instanciación.
    
    Responsabilidades:
        - Transformar filas de BD en objetos de dominio (Usuario/Admin/Operador)
        - Ejecutar consultas SQL parametrizadas
        - Gestionar transacciones de base de datos
    """

    @staticmethod
    def obtener_todos():
        """
        Obtiene todos los usuarios del sistema con sus roles.
        
        Proceso:
            1. Conecta a la base de datos
            2. Ejecuta JOIN entre usuarios y roles
            3. Transforma cada fila en objeto Admin u Operador según el rol
            4. Retorna lista de objetos de dominio
        
        Returns:
            list[Usuario]: Lista de instancias de Admin u Operador
        
        SQL Nota: El JOIN con la tabla roles es necesario para obtener el nombre del rol
        """
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
            # Factory Pattern implícito: Decide qué tipo de usuario crear
            if u["rol"] == "admin":
                usuarios.append(Admin(u["id"], u["nombre"], u["correo"], u["activo"]))
            else:
                usuarios.append(Operador(u["id"], u["nombre"], u["correo"], u["activo"]))

        return usuarios

    @staticmethod
    def cambiar_estado(usuario_id):
        """
        Alterna el estado activo/inactivo de un usuario.
        
        Args:
            usuario_id (int): ID del usuario a modificar
        
        SQL Nota: 
            - IF(activo = 1, 0, 1) es un toggle que cambia 1→0 y 0→1
            - Esto evita necesidad de primero consultar el estado actual
        """
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
        """
        Crea un nuevo usuario en el sistema con contraseña hasheada.
        
        Args:
            nombre (str): Nombre completo
            correo (str): Correo electrónico (único)
            contrasena (str): Contraseña en texto plano
            rol_id (int): ID del rol en la tabla roles
        
        Seguridad:
            - Usa bcrypt para hashing de contraseñas
            - bcrypt.gensalt() genera un salt único
            - Hash incluye salt automáticamente
        
        Nota: Falta validación de correo único y manejo de excepciones
        """
        db = get_db()
        cursor = db.cursor()

        # HASHING DE CONTRASEÑA - CRÍTICO PARA SEGURIDAD
        hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contrasena, rol_id, activo)
            VALUES (%s, %s, %s, %s, 1)
        """, (nombre, correo, hashed_password, rol_id))

        db.commit()
    
    


# ==============================================================================
# SECCIÓN 3: MODELO DE PRODUCTOS - Patrón Active Record
# ==============================================================================
# El modelo Producto combina datos y comportamiento de persistencia.
# Sigue el patrón Active Record donde cada objeto sabe guardarse a sí mismo.

class Producto:
    """
    Modelo que representa un producto en el inventario.
    Implementa el patrón Active Record: los objetos gestionan su propia persistencia.
    
    Atributos:
        id (int): Identificador único (None para productos nuevos)
        nombre (str): Nombre del producto
        descripcion (str): Descripción detallada
        categoria_id (int): FK a la tabla categorías
        stock (int): Cantidad actual en inventario
        stock_minimo (int): Número mínimo antes de alertar
        precio (float): Precio de venta
        imagen (str): Ruta o URL de la imagen
        activo (bool): Estado (True=disponible, False=eliminado lógico)
        creado_en (str): Fecha de creación (formato DATETIME de MySQL)
    """
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

    # --------------------------------------------------------------------------
    # MÉTODOS DE DOMINIO (Lógica de negocio)
    # --------------------------------------------------------------------------
    
    def stock_bajo(self):
        """
        Determina si el producto tiene stock por debajo del mínimo.
        
        Returns:
            bool: True si stock <= stock_minimo, False en caso contrario
        
        Ejemplo de uso:
            if producto.stock_bajo():
                enviar_alerta_reabastecimiento(producto)
        """
        return self.stock <= self.stock_minimo
    
    # --------------------------------------------------------------------------
    # MÉTODOS DE PERSISTENCIA (Active Record Pattern)
    # --------------------------------------------------------------------------
    
    @classmethod
    def crear(cls, nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen):
        """
        Método de clase para crear y persistir un nuevo producto.
        
        Args:
            cls (class): La clase Producto
            nombre, descripcion, etc.: Atributos del producto
        
        Proceso:
            1. Inserta en BD con valores por defecto (activo=1, creado_en=NOW())
            2. Obtiene el ID autogenerado
            3. Retorna instancia de Producto con el ID asignado
        
        Returns:
            Producto: Instancia del producto recién creado
        
        SQL Nota: NOW() es función de MySQL que retorna fecha/hora actual
        """
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
        """
        Persiste los cambios del producto en la base de datos.
        
        Precondición: El producto debe tener un ID válido (no None)
        
        SQL Nota: Actualiza todos los campos excepto 'activo' y 'creado_en'
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE productos
            SET nombre=%s, descripcion=%s, categoria_id=%s, stock=%s, stock_minimo=%s, precio=%s, imagen=%s
            WHERE id=%s
        """, (self.nombre, self.descripcion, self.categoria_id, self.stock, self.stock_minimo, self.precio, self.imagen, self.id))
        db.commit()

    def eliminar(self):
        """
        Eliminación lógica del producto (soft delete).
        
        No borra físicamente el registro, solo cambia 'activo' a 0.
        Ventajas:
            - Mantiene integridad referencial
            - Permite recuperación
            - Conserva historial
        
        SQL Nota: UPDATE en lugar de DELETE para soft delete
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE productos SET activo=0 WHERE id=%s", (self.id,))
        db.commit()

# ==============================================================================
# SECCIÓN 4: REPOSITORIO DE PRODUCTOS - DUPLICACIÓN PROBLEMÁTICA
# ==============================================================================

class ProductoDB:
    """
    ⚠️ CLASE CON PROBLEMAS DE DISEÑO ⚠️
    
    Duplica completamente la funcionalidad de los métodos de clase/instancia de Producto.
    Esto crea dos formas de hacer lo mismo, causando:
        1. Inconsistencia
        2. Confusión para desarrolladores
    
    Posibles soluciones:
        - Eliminar esta clase y usar solo Producto (Active Record)
    """

    @staticmethod
    def obtener_todos():
        """
        Obtiene todos los productos activos.
        
        Duplicado de: Podría ser método de clase de Producto
        
        SQL Nota: WHERE activo = 1 filtra productos eliminados lógicamente
        """
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nombre, descripcion, categoria_id, stock, stock_minimo, precio, imagen, activo, creado_en
            FROM productos
            WHERE activo = 1
        """)
        productos = []
        for p in cursor.fetchall():
            # Producto(**p) usa unpacking de diccionario para crear instancia
            productos.append(Producto(**p))
        return productos

    @staticmethod
    def obtener_por_id(producto_id):
        """
        Obtiene un producto específico por ID.
        
        Args:
            producto_id (int): ID del producto a buscar
        
        Returns:
            Producto or None: Instancia del producto o None si no existe
        """
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


# ==============================================================================
# SECCIÓN 5: MODELO DE MOVIMIENTOS - Registro de Auditoría
# ==============================================================================
# Clase para rastrear cambios en el inventario (entradas, salidas, ajustes).

class Movimiento:
    """
    Representa un movimiento de inventario (entrada/salida de stock).
    Patrón: Registro de Auditoría / Event Sourcing básico.
    
    Cada movimiento es inmutable una vez registrado y proporciona:
        - Trazabilidad completa de cambios
        - Responsabilidad (qué usuario hizo qué)
        - Historial para reportes
    
    Atributos:
        producto_id (int): FK al producto afectado
        usuario_id (int): FK al usuario que realizó el movimiento
        tipo (str): Tipo de movimiento ('entrada', 'salida', 'ajuste')
        fecha (datetime): Fecha y hora del movimiento (None=usar fecha actual)
    """
    def __init__(self, producto_id, usuario_id, tipo, fecha=None):
        self.producto_id = producto_id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.fecha = fecha

    def registrar(self):
        """
        Persiste el movimiento en la base de datos.
        
        SQL Nota:
            - NOW() usa la fecha/hora del servidor de BD
            - Esto es más confiable que datetime.now() del servidor app
        
        Mejora sugerida: Transacción que actualice producto.stock y registre movimiento
        """
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
        Obtiene el historial completo de movimientos con información relacionada.
        
        SQL Nota:
            - JOIN con productos para obtener nombre del producto
            - JOIN con usuarios para obtener nombre del usuario
            - ORDER BY fecha DESC: Más reciente primero
        
        Returns:
            list[dict]: Lista de diccionarios con datos de movimientos
        
        Inconsistencia: Retorna diccionarios, no objetos Movimiento
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
    
# En tu models.py, añade:
class Categoria:
    def __init__(self, id, nombre, descripcion=None, activa=True):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.activa = activa


class CategoriaDB:
    @staticmethod
    def obtener_todas(activas_only=True):
        """Obtiene todas las categorías"""
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        sql = "SELECT id, nombre, descripcion, activa FROM categorias"
        if activas_only:
            sql += " WHERE activa = 1"
        
        sql += " ORDER BY nombre ASC"
        
        cursor.execute(sql)
        return [Categoria(**cat) for cat in cursor.fetchall()]
    
    @staticmethod
    def obtener_por_id(categoria_id):
        """Obtiene una categoría por su ID"""
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre, descripcion, activa 
            FROM categorias 
            WHERE id = %s
        """, (categoria_id,))
        
        data = cursor.fetchone()
        return Categoria(**data) if data else None