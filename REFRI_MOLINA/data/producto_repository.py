from domain.producto import Producto
from data.database_manager import DatabaseManager


class ProductoRepository:
    def listar(self):
        with DatabaseManager() as conn:
            filas = conn.execute("SELECT id_producto, nombre, categoria, precio, stock FROM productos ORDER BY nombre").fetchall()
            return [Producto.desde_tupla(tuple(f)) for f in filas]

    def crear(self, producto):
        with DatabaseManager() as conn:
            conn.execute("INSERT INTO productos(nombre,categoria,precio,stock) VALUES(?,?,?,?)",
                        (producto.nombre, producto.categoria, producto.precio, producto.stock))

    def actualizar(self, producto):
        with DatabaseManager() as conn:
            conn.execute("UPDATE productos SET nombre=?, categoria=?, precio=?, stock=? WHERE id_producto=?",
                        (producto.nombre, producto.categoria, producto.precio, producto.stock, producto.id_producto))

    def eliminar(self, id_producto):
        with DatabaseManager() as conn:
            conn.execute("DELETE FROM productos WHERE id_producto=?", (id_producto,))

    def buscar(self, id_producto):
        with DatabaseManager() as conn:
            fila = conn.execute("SELECT id_producto,nombre,categoria,precio,stock FROM productos WHERE id_producto=?",
                              (id_producto,)).fetchone()
            return Producto.desde_tupla(tuple(fila)) if fila else None
