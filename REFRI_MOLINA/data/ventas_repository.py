from datetime import datetime
from data.database_manager import DatabaseManager

class VentasRepository:
    def listar(self):
        with DatabaseManager() as conn:
            filas = conn.execute("""
                SELECT v.id_venta, c.nombre, v.fecha, v.total
                FROM ventas v JOIN clientes c ON c.id_cliente=v.id_cliente
                ORDER BY v.id_venta DESC
            """).fetchall()
            return [tuple(f) for f in filas]

    def registrar(self, id_cliente, id_producto, cantidad):
        with DatabaseManager() as conn:
            producto = conn.execute("SELECT precio, stock FROM productos WHERE id_producto=?", (id_producto,)).fetchone()
            if not producto:
                raise ValueError("El producto no existe.")
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a cero.")
            if producto["stock"] < cantidad:
                raise ValueError("No hay suficiente inventario para esa venta.")
            subtotal = float(producto["precio"]) * cantidad
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = conn.execute("INSERT INTO ventas(id_cliente,fecha,total) VALUES(?,?,?)", (id_cliente, fecha, subtotal))
            id_venta = cur.lastrowid
            conn.execute("INSERT INTO detalle_venta(id_venta,id_producto,cantidad,precio_unitario,subtotal) VALUES(?,?,?,?,?)",
                         (id_venta, id_producto, cantidad, float(producto["precio"]), subtotal))
            conn.execute("UPDATE productos SET stock=stock-? WHERE id_producto=?", (cantidad, id_producto))
            return id_venta
