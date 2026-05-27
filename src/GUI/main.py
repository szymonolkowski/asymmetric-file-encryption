import flet as ft
from gui_components import AppGUI
from gui_logic import AppLogic

def main(page: ft.Page):
    # Konfiguracja okna
    page.title = "Asymmetric File Encryptor - Projekt"
    page.padding = 24
    page.theme_mode = ft.ThemeMode.DARK

    # Inicjalizacja klas
    gui = AppGUI()
    page.services.append(gui.file_picker) # File picker jest serwisem w nowszych wersjach Flet
    
    # Przekazujemy GUI do logiki, aby mogła obsługiwać przyciski
    logic = AppLogic(page, gui)

    # Zbudowanie widoku na podstawie danych z GUI
    header, actions_menu = gui.build_layout()

    # Dodanie elementów na ekran
    page.add(
        header,
        actions_menu,
    )

if __name__ == "__main__":
    ft.run(main)
