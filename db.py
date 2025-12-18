import mysql.connector

def get_db():
    return mysql.connector.connect(
        # host="localhost",
        host="dpg-d522h03e5dus73akfcog-a",
        database="inventario_pymes",
        user="root",
        password="LfVEm3H3d4E999WvdEAME1WrTJla5PZS",
        port=5432
    )
