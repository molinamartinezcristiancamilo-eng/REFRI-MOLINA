from dataclasses import dataclass


@dataclass
class Producto:
    id_producto: int | None
    nombre: str
    categoria: str
    precio: float
    stock: int

    @classmethod
    def desde_tupla(cls, fila):
        return cls(*fila)

    def __str__(self):
        return f"{self.nombre} - ${self.precio:,.0f}"

    def __repr__(self):
        return f"Producto(id={self.id_producto}, nombre={self.nombre!r})"

    def __len__(self):
        return self.stock
