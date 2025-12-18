from flask import Flask
from auth.routes import auth_bp
from admin.routes import admin_bp
from operador.routes import operador_bp
from productos.routes import productos_bp


app = Flask(__name__)
app.secret_key = "clave_super_secreta"

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(operador_bp)
app.register_blueprint(productos_bp)

if __name__ == "__main__":
    app.run(debug=True)
