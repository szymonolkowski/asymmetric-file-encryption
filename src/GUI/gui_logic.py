import asyncio
import sys
from pathlib import Path

import flet as ft
from gui_components import AppGUI

src_dir = Path(__file__).resolve().parents[1]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from crypto.key_manager import KeyManager
from crypto.pipeline import decrypt_file_hybrid, encrypt_file_hybrid
from crypto.asymmetric import RSAHandler


class AppLogic:
    def __init__(self, page: ft.Page, gui: AppGUI):
        self.page = page
        self.gui = gui
        self.key_manager = KeyManager()

        self.setup_events()
        self.refresh_keys()

    def setup_events(self):
        self.gui.btn_pick_encrypt_input.on_click = self.pick_encrypt_input
        self.gui.btn_pick_encrypt_output.on_click = self.pick_encrypt_output
        self.gui.btn_pick_decrypt_input.on_click = self.pick_decrypt_input
        self.gui.btn_pick_decrypt_output.on_click = self.pick_decrypt_output
        self.gui.btn_refresh_keys.on_click = self.refresh_keys
        self.gui.btn_generate_keys.on_click = self.generate_keys
        self.gui.btn_encrypt.on_click = self.encrypt_file
        self.gui.btn_decrypt.on_click = self.decrypt_file
        self.gui.private_key_dropdown.on_focus = self.refresh_keys
        self.gui.public_key_dropdown.on_focus = self.refresh_keys

    def set_status(self, message: str, is_error: bool = False):
        self.gui.status_text.value = message
        self.gui.status_text.color = ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400
        self.page.update()

    def show_message(self, message: str, is_error: bool = False):
        self.set_status(message, is_error=is_error)
        snack_bar = ft.SnackBar(
            ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_700 if is_error else ft.Colors.GREEN_700,
            show_close_icon=True,
        )
        self.page.show_dialog(snack_bar)

    def refresh_keys(self, _=None):
        self.gui.private_key_dropdown.options = [
            ft.dropdown.Option(key=k, text=k) for k in self.key_manager.list_private_keys()
        ]
        self.gui.public_key_dropdown.options = [
            ft.dropdown.Option(key=k, text=k) for k in self.key_manager.list_public_keys()
        ]
        self.page.update()

    async def generate_keys(self, _):
        key_name = Path(self.gui.new_key_name.value.strip()).stem
        password = self.gui.new_key_password.value or None

        if not key_name:
            return self.show_message("Podaj nazwe nowej pary kluczy.", is_error=True)

        private_key_path = self.key_manager.get_private_key_path(f"{key_name}.pem")
        public_key_path = self.key_manager.get_public_key_path(f"{key_name}.pem")

        if Path(private_key_path).exists() or Path(public_key_path).exists():
            return self.show_message("Klucz o takiej nazwie juz istnieje.", is_error=True)

        self.set_busy(True)
        self.set_status("Generowanie pary kluczy...")

        try:
            await asyncio.to_thread(
                self.write_key_pair,
                str(private_key_path),
                str(public_key_path),
                password,
            )
        except Exception as error:
            self.show_message(f"Blad generowania kluczy: {error}", is_error=True)
            return
        finally:
            self.set_busy(False)

        self.gui.new_key_name.value = ""
        self.gui.new_key_password.value = ""
        self.refresh_keys()
        self.show_message(f"Wygenerowano klucze: {key_name}.pem")

    def write_key_pair(self, private_key_path: str, public_key_path: str, password: str | None):
        rsa_handler = RSAHandler()
        rsa_handler.key_generator()
        rsa_handler.export_private_key(private_key_path, password=password)
        rsa_handler.export_public_key(public_key_path)

    async def pick_encrypt_input(self, _):
        picked_files = await self.gui.file_picker.pick_files(
            dialog_title="Wybierz plik do zaszyfrowania",
            allow_multiple=False,
            file_type=ft.FilePickerFileType.ANY,
        )
        if not picked_files:
            return

        input_path = Path(picked_files[0].path)
        self.gui.encrypt_input_path.value = str(input_path)
        if not self.gui.encrypt_output_path.value:
            self.gui.encrypt_output_path.value = str(input_path.with_name(f"{input_path.name}.safe"))
        self.page.update()

    async def pick_decrypt_input(self, _):
        picked_files = await self.gui.file_picker.pick_files(
            dialog_title="Wybierz plik .safe do odszyfrowania",
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["safe"],
        )
        if not picked_files:
            return

        input_path = Path(picked_files[0].path)
        self.gui.decrypt_input_path.value = str(input_path)
        if not self.gui.decrypt_output_path.value:
            self.gui.decrypt_output_path.value = str(input_path.with_name(self.default_decrypted_name(input_path)))
        self.page.update()

    async def pick_encrypt_output(self, _):
        initial_path = Path(self.gui.encrypt_input_path.value) if self.gui.encrypt_input_path.value else None
        output_path = await self.gui.file_picker.save_file(
            dialog_title="Zapisz zaszyfrowany plik jako",
            file_name=f"{initial_path.name}.safe" if initial_path else "encrypted.safe",
            initial_directory=str(initial_path.parent) if initial_path else None,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["safe"],
        )
        if output_path:
            self.gui.encrypt_output_path.value = output_path
            self.page.update()

    async def pick_decrypt_output(self, _):
        initial_path = Path(self.gui.decrypt_input_path.value) if self.gui.decrypt_input_path.value else None
        output_path = await self.gui.file_picker.save_file(
            dialog_title="Zapisz odszyfrowany plik jako",
            file_name=self.default_decrypted_name(initial_path) if initial_path else "decrypted_file",
            initial_directory=str(initial_path.parent) if initial_path else None,
            file_type=ft.FilePickerFileType.ANY,
        )
        if output_path:
            self.gui.decrypt_output_path.value = output_path
            self.page.update()

    def default_decrypted_name(self, input_path: Path) -> str:
        if input_path.name.endswith(".safe"):
            return input_path.name[:-5]
        return f"{input_path.stem}_decrypted{input_path.suffix}"

    def set_busy(self, is_busy: bool):
        self.gui.progress_ring.visible = is_busy
        self.gui.btn_encrypt.disabled = is_busy
        self.gui.btn_decrypt.disabled = is_busy
        self.gui.btn_pick_encrypt_input.disabled = is_busy
        self.gui.btn_pick_encrypt_output.disabled = is_busy
        self.gui.btn_pick_decrypt_input.disabled = is_busy
        self.gui.btn_pick_decrypt_output.disabled = is_busy
        self.gui.btn_refresh_keys.disabled = is_busy
        self.gui.btn_generate_keys.disabled = is_busy
        self.page.update()

    async def encrypt_file(self, _):
        input_path = self.gui.encrypt_input_path.value
        output_path = self.gui.encrypt_output_path.value
        selected_key = self.gui.public_key_dropdown.value

        if not input_path:
            return self.show_message("Wybierz plik do zaszyfrowania.", is_error=True)
        if not output_path:
            return self.show_message("Wybierz sciezke zapisu pliku .safe.", is_error=True)
        if not selected_key:
            return self.show_message("Wybierz klucz publiczny odbiorcy.", is_error=True)

        public_key_path = self.key_manager.get_public_key_path(selected_key)
        self.set_busy(True)
        self.set_status("Szyfrowanie pliku...")

        try:
            success = await asyncio.to_thread(
                encrypt_file_hybrid,
                input_path,
                public_key_path,
                output_path,
            )
        except Exception as error:
            self.show_message(f"Blad szyfrowania: {error}", is_error=True)
            return
        finally:
            self.set_busy(False)

        if success:
            self.show_message("Plik zaszyfrowany pomyslnie.")
        else:
            self.show_message("Nie udalo sie zaszyfrowac pliku.", is_error=True)

    async def decrypt_file(self, _):
        input_path = self.gui.decrypt_input_path.value
        output_path = self.gui.decrypt_output_path.value
        selected_key = self.gui.private_key_dropdown.value
        password = self.gui.private_key_password.value or None

        if not input_path:
            return self.show_message("Wybierz plik .safe do odszyfrowania.", is_error=True)
        if not output_path:
            return self.show_message("Wybierz sciezke zapisu odszyfrowanego pliku.", is_error=True)
        if not selected_key:
            return self.show_message("Wybierz klucz prywatny.", is_error=True)
        private_key_path = self.key_manager.get_private_key_path(selected_key)
        self.set_busy(True)
        self.set_status("Deszyfrowanie pliku...")

        try:
            success = await asyncio.to_thread(
                decrypt_file_hybrid,
                input_path,
                private_key_path,
                password,
                output_path,
            )
        except Exception as error:
            self.show_message(f"Blad deszyfrowania: {error}", is_error=True)
            return
        finally:
            self.set_busy(False)

        if success:
            self.show_message("Plik odszyfrowany pomyslnie.")
        else:
            self.show_message("Nie udalo sie odszyfrowac pliku. Sprawdz haslo i klucz.", is_error=True)
