import flet as ft
from ui.app_view import RefriMolinaApp


def main(page: ft.Page):
    RefriMolinaApp(page)


if hasattr(ft, "run"):
    ft.run(main)
else:
    ft.app(target=main)
