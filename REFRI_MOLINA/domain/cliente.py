from dataclasses import dataclass

@dataclass
class Cliente:
    id_cliente: int | None
    nombre: str
    documento: str
    telefono: str

    @classmethod
    def desde_tupla(cls, fila):
        return cls(*fila)

    def __str__(self):
        return f"{self.nombre} ({self.documento})"

    def __repr__(self):
        return f"Cliente(id={self.id_cliente}, nombre={self.nombre!r})"

    def __len__(self):
        return len(self.nombre)
