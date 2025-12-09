import flet as ft


def main(page: ft.Page):
    page.title = "NTMND · Hola Flet"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    texto = ft.Text("Tu libertad en 0s y 1s (NTMND)", size=24, weight="bold")
    subtitulo = ft.Text("App local. Sin rastreo. Sin Hermano Mayor.", size=16)

    def on_click(e):
        page.snack_bar = ft.SnackBar(
            ft.Text("Esto está corriendo SOLO en tu máquina 😏")
        )
        page.snack_bar.open = True
        page.update()

    boton = ft.ElevatedButton("Probar mi libertad digital", on_click=on_click)

    page.add(
        ft.Column(
            controls=[texto, subtitulo, boton],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


ft.app(target=main)
