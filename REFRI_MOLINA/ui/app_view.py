import flet as ft
from domain.cliente import Cliente
from domain.producto import Producto
from data.cliente_dao import ClienteDAO
from data.producto_repository import ProductoRepository
from data.ventas_repository import VentasRepository
from data.database_manager import DatabaseManager


def _icon(nombre):
    """Obtiene iconos tanto en Flet clásico como en versiones recientes."""
    catalogo = getattr(ft, "Icons", None) or getattr(ft, "icons", None)
    return getattr(catalogo, nombre, None) if catalogo else None


def _option(clave, texto=None):
    """Crea una opción Dropdown compatible con distintas versiones."""
    texto = texto if texto is not None else clave
    opcion_nueva = getattr(ft, "DropdownOption", None)
    if opcion_nueva:
        return opcion_nueva(key=str(clave), text=str(texto))
    dropdown = getattr(ft, "dropdown", None)
    opcion_antigua = getattr(dropdown, "Option", None) if dropdown else None
    if opcion_antigua:
        try:
            return opcion_antigua(key=str(clave), text=str(texto))
        except TypeError:
            return opcion_antigua(str(clave), str(texto))
    return ft.Option(key=str(clave), text=str(texto))


def _boton(texto, on_click, icono=None, outlined=False):
    """Selecciona la clase de botón disponible en la versión instalada."""
    if hasattr(ft, "Button"):
        if outlined and hasattr(ft, "OutlinedButton"):
            return ft.OutlinedButton(content=texto, on_click=on_click)
        kwargs = {"content": texto, "on_click": on_click}
        if icono is not None:
            kwargs["icon"] = icono
        return ft.Button(**kwargs)
    clase = getattr(ft, "OutlinedButton", None) if outlined else getattr(ft, "ElevatedButton", None)
    if clase is None:
        clase = getattr(ft, "TextButton")
    kwargs = {"text": texto, "on_click": on_click}
    if icono is not None:
        kwargs["icon"] = icono
    return clase(**kwargs)


class RefriMolinaApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.clientes = ClienteDAO()
        self.productos = ProductoRepository()
        self.ventas = VentasRepository()
        self.producto_editando = None
        self.cliente_editando = None
        self.crear_tablas()
        self.crear_controles()
        self.mostrar_productos()
        self.mostrar_clientes()
        self.mostrar_ventas()
        self.actualizar_resumen()

    def crear_tablas(self):
        DatabaseManager().inicializar()



    def aviso(self, texto, error=False):
        barra = ft.SnackBar(content=ft.Text(texto), bgcolor="#B42318" if error else "#16803C")
        if hasattr(self.page, "open"):
            self.page.open(barra)
        elif hasattr(self.page, "show_dialog"):
            self.page.show_dialog(barra)
        else:
            self.page.snack_bar = barra
            barra.open = True
            self.page.update()



    def crear_controles(self):
        self.page.title = "REFRI MOLINA | Gestión comercial"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        if hasattr(self.page, "window"):
            self.page.window.width = 1180
            self.page.window.height = 800
        else:
            self.page.window_width = 1180
            self.page.window_height = 800
        self.page.padding = 20
        self.page.bgcolor = "#F3F6FA"

        self.titulo = ft.Text("REFRI MOLINA", size=28, weight=ft.FontWeight.BOLD, color="#123B5D")
        self.subtitulo = ft.Text("Gestión de productos, clientes e inventario", color="#587083")
        self.resumen = ft.Row(wrap=True, spacing=12)


        # Productos
        self.p_nombre = ft.TextField(label="Nombre del producto", width=240)
        self.p_categoria = ft.Dropdown(label="Categoría", width=200, options=[_option(x) for x in ["Refrigerantes", "Compresores", "Tubería y cobre", "Controles y sensores", "Capacitores", "Motores y ventiladores", "Herramientas", "Otros"]])
        self.p_precio = ft.TextField(label="Precio (COP)", width=160, keyboard_type=ft.KeyboardType.NUMBER)
        self.p_stock = ft.TextField(label="Stock", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        self.p_tabla = ft.DataTable(columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Producto")), ft.DataColumn(ft.Text("Categoría")), ft.DataColumn(ft.Text("Precio")), ft.DataColumn(ft.Text("Stock")), ft.DataColumn(ft.Text("Acciones"))], rows=[])
        self.p_tabla_wrap = ft.Column([self.p_tabla], scroll=ft.ScrollMode.AUTO)

        # Clientes
        self.c_nombre = ft.TextField(label="Nombre completo", width=260)
        self.c_documento = ft.TextField(label="Documento/NIT", width=200)
        self.c_telefono = ft.TextField(label="Teléfono", width=180)
        self.c_tabla = ft.DataTable(columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Documento")), ft.DataColumn(ft.Text("Teléfono")), ft.DataColumn(ft.Text("Acciones"))], rows=[])

        # Ventas
        self.v_cliente = ft.Dropdown(label="Cliente", width=260, options=[])
        self.v_producto = ft.Dropdown(label="Producto", width=300, options=[])
        self.v_cantidad = ft.TextField(label="Cantidad", width=120, value="1", keyboard_type=ft.KeyboardType.NUMBER)
        self.v_tabla = ft.DataTable(columns=[ft.DataColumn(ft.Text("Venta")), ft.DataColumn(ft.Text("Cliente")), ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Total"))], rows=[])

        producto_panel = ft.Column([
            ft.Text("Inventario de productos", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([self.p_nombre, self.p_categoria, self.p_precio, self.p_stock], wrap=True),
            ft.Row([_boton("Guardar producto", self.guardar_producto, _icon("SAVE")), _boton("Limpiar", self.limpiar_producto, outlined=True)]),
            ft.Divider(), self.p_tabla_wrap
        ], scroll=ft.ScrollMode.AUTO)

        cliente_panel = ft.Column([
            ft.Text("Gestión de clientes", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([self.c_nombre, self.c_documento, self.c_telefono], wrap=True),
            ft.Row([_boton("Guardar cliente", self.guardar_cliente, _icon("PERSON_ADD")), _boton("Limpiar", self.limpiar_cliente, outlined=True)]),
            ft.Divider(), ft.Column([self.c_tabla], scroll=ft.ScrollMode.AUTO)
        ], scroll=ft.ScrollMode.AUTO)


        ventas_panel = ft.Column([
            ft.Text("Registrar venta", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([self.v_cliente, self.v_producto, self.v_cantidad], wrap=True),
            _boton("Registrar venta y descontar inventario", self.registrar_venta, _icon("SHOPPING_CART")),
            ft.Divider(), ft.Text("Historial de ventas", size=18, weight=ft.FontWeight.BOLD),
            ft.Column([self.v_tabla], scroll=ft.ScrollMode.AUTO)
        ], scroll=ft.ScrollMode.AUTO)

        paneles = [
            ft.Column([self.resumen, ft.Text("Bienvenido al sistema de administración REFRI MOLINA", size=18), ft.Text("Utiliza las pestañas para administrar inventario, clientes y ventas.")], spacing=20),
            producto_panel, cliente_panel, ventas_panel
        ]

        if hasattr(ft, "TabBar") and hasattr(ft, "TabBarView"):
            tabs = ft.Tabs(
                length=4, selected_index=0, expand=True,
                content=ft.Column([
                    ft.TabBar(tabs=[
                        ft.Tab(label="Resumen"), ft.Tab(label="Productos"),
                        ft.Tab(label="Clientes"), ft.Tab(label="Ventas")
                    ]),
                    ft.TabBarView(expand=True, controls=paneles)
                ], expand=True)
            )
        else:
            tabs = ft.Tabs(
                selected_index=0, expand=True,
                tabs=[
                    ft.Tab(text="Resumen", content=paneles[0]),
                    ft.Tab(text="Productos", content=paneles[1]),
                    ft.Tab(text="Clientes", content=paneles[2]),
                    ft.Tab(text="Ventas", content=paneles[3])
                ]
            )
        self.page.add(ft.Column([self.titulo, self.subtitulo, ft.Divider(), tabs], expand=True, spacing=8))



    def limpiar_producto(self, e=None):
        self.producto_editando = None
        self.p_nombre.value = ""
        self.p_categoria.value = None
        self.p_precio.value = ""
        self.p_stock.value = ""
        self.page.update()

    def guardar_producto(self, e=None):
        nombre = (self.p_nombre.value or "").strip()
        categoria = self.p_categoria.value
        try:
            precio = float((self.p_precio.value or "").replace(",", "."))
            stock = int(self.p_stock.value or "")
            if not nombre or not categoria:
                raise ValueError("Completa el nombre y la categoría.")
            if precio < 0 or stock < 0:
                raise ValueError("Precio y stock no pueden ser negativos.")
            obj = Producto(self.producto_editando, nombre, categoria, precio, stock)
            if self.producto_editando is None:
                self.productos.crear(obj)
                self.aviso("Producto registrado correctamente.")
            else:
                self.productos.actualizar(obj)
                self.aviso("Producto actualizado correctamente.")
            self.limpiar_producto()
            self.mostrar_productos(); self.actualizar_resumen()
        except ValueError as ex:
            self.aviso(str(ex) if str(ex) else "Verifica los datos del producto.", True)
        except Exception as ex:
            self.aviso(f"No se pudo guardar: {ex}", True)

    def editar_producto(self, p):
        self.producto_editando = p.id_producto
        self.p_nombre.value = p.nombre
        self.p_categoria.value = p.categoria
        self.p_precio.value = str(p.precio)
        self.p_stock.value = str(p.stock)
        self.page.update()

    def eliminar_producto(self, p):
        try:
            self.productos.eliminar(p.id_producto)
            self.mostrar_productos(); self.actualizar_resumen()
            self.aviso("Producto eliminado.")
        except Exception as ex:
            self.aviso(f"No se puede eliminar (puede tener ventas asociadas): {ex}", True)

    def mostrar_productos(self):
        lista = self.productos.listar()
        rows = []
        for p in lista:
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(p.id_producto))), ft.DataCell(ft.Text(p.nombre)), ft.DataCell(ft.Text(p.categoria)),
                ft.DataCell(ft.Text(f"${p.precio:,.0f}")), ft.DataCell(ft.Text(str(p.stock))),
                ft.DataCell(ft.Row([ft.IconButton(_icon("EDIT"), tooltip="Editar", on_click=lambda e, prod=p: self.editar_producto(prod)), ft.IconButton(_icon("DELETE"), tooltip="Eliminar", icon_color="red", on_click=lambda e, prod=p: self.eliminar_producto(prod))]))
            ]))
        self.p_tabla.rows = rows
        self.v_producto.options = [_option(p.id_producto, f"{p.nombre} | stock {p.stock} | ${p.precio:,.0f}") for p in lista]
        self.page.update()

    def limpiar_cliente(self, e=None):
        self.cliente_editando = None
        self.c_nombre.value = ""; self.c_documento.value = ""; self.c_telefono.value = ""
        self.page.update()

    def guardar_cliente(self, e=None):
        nombre = (self.c_nombre.value or "").strip()
        documento = (self.c_documento.value or "").strip()
        telefono = (self.c_telefono.value or "").strip()
        if not nombre or not documento or not telefono:
            self.aviso("Completa todos los campos del cliente.", True); return
        obj = Cliente(self.cliente_editando, nombre, documento, telefono)
        try:
            if self.cliente_editando is None: self.clientes.crear(obj)
            else: self.clientes.actualizar(obj)
            self.limpiar_cliente(); self.mostrar_clientes(); self.actualizar_resumen()
            self.aviso("Cliente guardado correctamente.")
        except Exception as ex:
            self.aviso(f"No se pudo guardar el cliente: {ex}", True)

    def editar_cliente(self, c):
        self.cliente_editando = c.id_cliente
        self.c_nombre.value = c.nombre; self.c_documento.value = c.documento; self.c_telefono.value = c.telefono
        self.page.update()

    def eliminar_cliente(self, c):
        try:
            self.clientes.eliminar(c.id_cliente)
            self.mostrar_clientes(); self.actualizar_resumen(); self.aviso("Cliente eliminado.")
        except Exception as ex:
            self.aviso(f"No se puede eliminar: el cliente puede tener ventas asociadas. {ex}", True)

    def mostrar_clientes(self):
        lista = self.clientes.listar()
        rows = []
        for c in lista:
            rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(c.id_cliente))), ft.DataCell(ft.Text(c.nombre)), ft.DataCell(ft.Text(c.documento)), ft.DataCell(ft.Text(c.telefono)), ft.DataCell(ft.Row([ft.IconButton(_icon("EDIT"), tooltip="Editar", on_click=lambda e, cli=c: self.editar_cliente(cli)), ft.IconButton(_icon("DELETE"), tooltip="Eliminar", icon_color="red", on_click=lambda e, cli=c: self.eliminar_cliente(cli))]))]))
        self.c_tabla.rows = rows
        self.v_cliente.options = [_option(c.id_cliente, c.nombre) for c in lista]
        self.page.update()

    def registrar_venta(self, e=None):
        try:
            if not self.v_cliente.value or not self.v_producto.value:
                raise ValueError("Selecciona un cliente y un producto.")
            cantidad = int(self.v_cantidad.value or "")
            id_cliente = int(self.v_cliente.value); id_producto = int(self.v_producto.value)
            venta_id = self.ventas.registrar(id_cliente, id_producto, cantidad)
            self.aviso(f"Venta #{venta_id} registrada. Inventario actualizado.")
            self.mostrar_productos(); self.mostrar_ventas(); self.actualizar_resumen()
        except ValueError as ex:
            self.aviso(str(ex), True)
        except Exception as ex:
            self.aviso(f"Error al registrar venta: {ex}", True)

    def mostrar_ventas(self):
        rows = []
        for v in self.ventas.listar():
            rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(v[0]))), ft.DataCell(ft.Text(v[1])), ft.DataCell(ft.Text(v[2])), ft.DataCell(ft.Text(f"${v[3]:,.0f}"))]))
        self.v_tabla.rows = rows
        self.page.update()

    def actualizar_resumen(self):
        with DatabaseManager() as conn:
            nprod = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
            ncli = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
            nventas = conn.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
            stock = conn.execute("SELECT COALESCE(SUM(stock),0) FROM productos").fetchone()[0]
        def tarjeta(titulo, valor, color):
            return ft.Container(content=ft.Column([ft.Text(titulo, color="#607080"), ft.Text(str(valor), size=24, weight=ft.FontWeight.BOLD, color=color)]), padding=18, bgcolor="white", border_radius=12, width=210)
        self.resumen.controls = [tarjeta("Productos registrados", nprod, "#176B87"), tarjeta("Clientes", ncli, "#228B62"), tarjeta("Ventas realizadas", nventas, "#A45B13"), tarjeta("Unidades en stock", stock, "#7554A5")]
        self.page.update()
