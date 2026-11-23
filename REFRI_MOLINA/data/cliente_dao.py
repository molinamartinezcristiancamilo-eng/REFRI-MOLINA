from domain.cliente import Cliente
from data.database_manager import DatabaseManager


class ClienteDAO:
    def listar(self):
        with DatabaseManager() as conn:
            filas = conn.execute("SELECT id_cliente, nombre, documento, telefono FROM clientes ORDER BY nombre").fetchall()
            return [Cliente.desde_tupla(tuple(f)) for f in filas]

    def crear(self, cliente):
        with DatabaseManager() as conn:
            conn.execute("INSERT INTO clientes(nombre, documento, telefono) VALUES (?, ?, ?)",
                        (cliente.nombre, cliente.documento, cliente.telefono))

    def actualizar(self, cliente):
        with DatabaseManager() as conn:
            conn.execute("UPDATE clientes SET nombre=?, documento=?, telefono=? WHERE id_cliente=?",
                        (cliente.nombre, cliente.documento, cliente.telefono, cliente.id_cliente))

    def eliminar(self, id_cliente):
        with DatabaseManager() as conn:
            conn.execute("DELETE FROM clientes WHERE id_cliente=?", (id_cliente,))
