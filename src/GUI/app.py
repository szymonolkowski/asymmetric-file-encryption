import flet as ft
from crypto import encrypt_file_hybrid, decrypt_file_hybrid
from crypto import KeyManager as KM

def main(page: ft.Page):
    txt_nazwa = ft.Text("Nie wybrano pliku")
    lista_plikow_ui = ft.Column()
    pliki = []
    
    async def otworz_okno(e):
        nonlocal pliki

        wyb_pliki = await ft.FilePicker().pick_files(
            dialog_title="Wybierz pliki",
            allow_multiple=True,
            allowed_extensions=["txt", "pdf", "png", "jpg"]
        )
        
        if wyb_pliki:
            for nowy_plik in wyb_pliki:
                if nowy_plik.path not in [p.path for p in pliki]:
                    pliki.append(nowy_plik)

            nazwy_plikow = [plik.name for plik in pliki]
            txt_nazwa.value = f"Wybrano {len(pliki)} plików:"
            lista_plikow_ui.controls = [ft.Text(nazwa) for nazwa in nazwy_plikow]

            odswiez(e)
    def clear_list(e):
        pliki.clear()
        lista_plikow_ui.controls = []
        odswiez(e)
    def odswiez(e):
        txt_nazwa.value = f"Wybrano {len(pliki)} plików:" if pliki else "Nie wybrano pliku"
        lista_plikow_ui.controls.clear()
        for plik in pliki:
            wiersz = ft.Row([
                ft.Text(plik.name, expand=True),
                ft.ElevatedButton(
                    "delete", 
                    on_click=usun_plik, 
                    icon_color="red", 
                    data=plik,
                    tooltip="Usuń plik"
                )
            ])
            lista_plikow_ui.controls.append(wiersz)
        page.update()

    def usun_plik(e):
        plik_do_usuniecia = e.control.data
        pliki.remove(plik_do_usuniecia)
        odswiez(e)
    
    def szyfruj(e):
        return
    def deszyfruj(e):
        return 
    menu_plikow=ft.Column([
        ft.Row([
            ft.ElevatedButton("Wybierz plik z dysku", on_click=otworz_okno),
            ft.ElevatedButton("Wyczyść listę", on_click=clear_list),
        ]),
        txt_nazwa,
        lista_plikow_ui
    ], width=400)
    funkje_przyciskow= ft.Column([
        ft.ElevatedButton("szyfruj", on_click=szyfruj),
        ft.ElevatedButton("deszyfruj", on_click=deszyfruj),
    ], expand=True)
    page.add(ft.Row([menu_plikow, funkje_przyciskow], expand=True))
if __name__ == "__main__":
    ft.app(target=main)