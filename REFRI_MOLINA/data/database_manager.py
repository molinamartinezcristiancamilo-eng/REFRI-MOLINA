import sqlite3
from pathlib import Path


class DatabaseManager:
    def __init__(self, nombre_db="refri_molina.db"):
        self.ruta = Path(__file__).resolve().parent.parent / nombre_db



    def __enter__(self):
        self.conexion = sqlite3.connect(self.ruta)
        self.conexion.execute("PRAGMA foreign_keys = ON;")
        self.conexion.row_factory = sqlite3.Row
        return self.conexion



    def __exit__(self, tipo_error, error, traceback):
        if tipo_error is None:
            self.conexion.commit()
        else:
            self.conexion.rollback()
        self.conexion.close()
        return False



    def inicializar(self):
        with self as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    documento TEXT NOT NULL UNIQUE,
                    telefono TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS productos (
                    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    precio REAL NOT NULL CHECK(precio >= 0),
                    stock INTEGER NOT NULL CHECK(stock >= 0)
                );
                CREATE TABLE IF NOT EXISTS ventas (
                    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cliente INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    total REAL NOT NULL DEFAULT 0,
                    FOREIGN KEY(id_cliente) REFERENCES clientes(id_cliente)
                );
                CREATE TABLE IF NOT EXISTS detalle_venta (
                    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_venta INTEGER NOT NULL,
                    id_producto INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY(id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
                    FOREIGN KEY(id_producto) REFERENCES productos(id_producto)
                );
            """)
            cantidad = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
            if cantidad == 0:
                conn.executemany(
                    "INSERT INTO productos(nombre,categoria,precio,stock) VALUES(?,?,?,?)",
                    [
                        ("Refrigerante R134a 1 kg", "Refrigerantes", 85000, 12),
                        ("Refrigerante R410A 1 kg", "Refrigerantes", 110000, 8),
                        ("Capacitor 35 uF", "Capacitores", 28000, 15),
                        ("Termostato digital", "Controles y sensores", 65000, 6),
                        ("Tubo cobre 1/4 (metro)", "Tubería y cobre", 18000, 30),
                        ("Motor ventilador universal", "Motores y ventiladores", 95000, 5),
                    ],
                )
