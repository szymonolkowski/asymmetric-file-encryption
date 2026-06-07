import asyncio
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import flet as ft
from gui_components import AppGUI

src_dir = Path(__file__).resolve().parents[1]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from crypto.asymmetric import RSAHandler
from crypto.key_manager import KeyManager
from crypto.pipeline import decrypt_file_hybrid, encrypt_file_hybrid


class AppLogic:
    def __init__(self, page: ft.Page, gui: AppGUI):
        self.page = page
        self.gui = gui
        self.key_manager = KeyManager()
        self.files = {"encrypt": [], "decrypt": []}

        self.setup_events()
        self.refresh_keys()
        self.toggle_advanced_panels()
        self.refresh_file_list("encrypt")
        self.refresh_file_list("decrypt")

    def setup_events(self):
        self.gui.btn_encrypt_add_files.on_click = self.pick_encrypt_files
        self.gui.btn_encrypt_add_paths.on_click = self.add_encrypt_pasted_paths
        self.gui.btn_encrypt_output_dir.on_click = self.pick_encrypt_output_dir
        self.gui.btn_encrypt_remove_selected.on_click = self.remove_encrypt_selected_files
        self.gui.btn_encrypt_replace_selected.on_click = self.replace_encrypt_selected_file
        self.gui.btn_encrypt_clear.on_click = self.clear_encrypt_files
        self.gui.btn_encrypt.on_click = self.encrypt_files
        self.gui.encrypt_advanced.on_change = self.toggle_advanced_panels
        self.gui.encrypt_pasted_paths.on_change = lambda _: self.add_pasted_paths("encrypt")

        self.gui.btn_decrypt_add_files.on_click = self.pick_decrypt_files
        self.gui.btn_decrypt_add_paths.on_click = self.add_decrypt_pasted_paths
        self.gui.btn_decrypt_output_dir.on_click = self.pick_decrypt_output_dir
        self.gui.btn_decrypt_remove_selected.on_click = self.remove_decrypt_selected_files
        self.gui.btn_decrypt_replace_selected.on_click = self.replace_decrypt_selected_file
        self.gui.btn_decrypt_clear.on_click = self.clear_decrypt_files
        self.gui.btn_decrypt.on_click = self.decrypt_files
        self.gui.btn_decrypt_auto_assign.on_click = self.auto_assign_keys
        self.gui.decrypt_advanced.on_change = self.toggle_advanced_panels
        self.gui.decrypt_pasted_paths.on_change = lambda _: self.add_pasted_paths("decrypt")

        self.gui.btn_refresh_keys.on_click = self.refresh_keys
        self.gui.btn_import_public_key.on_click = self.import_public_key
        self.gui.btn_import_private_key.on_click = self.import_private_key
        self.gui.btn_generate_keys.on_click = self.generate_keys
        self.gui.public_key_dropdown.on_focus = self.refresh_keys

    # ==========================================
    # BLACHY I EVENTY
    # ==========================================
    async def pick_encrypt_files(self, _):
        await self.pick_files("encrypt")

    async def pick_decrypt_files(self, _):
        await self.pick_files("decrypt")

    def add_encrypt_pasted_paths(self, _):
        self.add_pasted_paths("encrypt")

    def add_decrypt_pasted_paths(self, _):
        self.add_pasted_paths("decrypt")

    async def pick_encrypt_output_dir(self, _):
        await self.pick_output_dir("encrypt")

    async def pick_decrypt_output_dir(self, _):
        await self.pick_output_dir("decrypt")

    def remove_encrypt_selected_files(self, _):
        self.remove_selected_files("encrypt")

    def remove_decrypt_selected_files(self, _):
        self.remove_selected_files("decrypt")

    async def replace_encrypt_selected_file(self, _):
        await self.replace_selected_file("encrypt")

    async def replace_decrypt_selected_file(self, _):
        await self.replace_selected_file("decrypt")

    def clear_encrypt_files(self, _):
        self.files["encrypt"].clear()
        self.refresh_file_list("encrypt")

    def clear_decrypt_files(self, _):
        self.files["decrypt"].clear()
        self.refresh_file_list("decrypt")
        self.update_decrypt_passwords_panel()

    def toggle_advanced_panels(self, _=None):
        self.gui.encrypt_advanced_panel.visible = bool(self.gui.encrypt_advanced.value)
        self.gui.decrypt_advanced_panel.visible = bool(self.gui.decrypt_advanced.value)
        self.refresh_file_list("encrypt")
        self.refresh_file_list("decrypt")
        self.page.update()

    def controls_for(self, group: str) -> dict:
        if group == "encrypt":
            return {
                "advanced": self.gui.encrypt_advanced,
                "policy": self.gui.encrypt_duplicate_policy,
                "output_dir": self.gui.encrypt_output_dir,
                "pasted_paths": self.gui.encrypt_pasted_paths,
                "column": self.gui.encrypt_files_column,
                "count": self.gui.encrypt_file_count,
            }
        return {
            "advanced": self.gui.decrypt_advanced,
            "policy": self.gui.decrypt_duplicate_policy,
            "output_dir": self.gui.decrypt_output_dir,
            "pasted_paths": self.gui.decrypt_pasted_paths,
            "column": self.gui.decrypt_files_column,
            "count": self.gui.decrypt_file_count,
        }

    def is_advanced(self, group: str) -> bool:
        return bool(self.controls_for(group)["advanced"].value)

    def mode_name(self, group: str) -> str:
        return f"{group}_advanced" if self.is_advanced(group) else group

    def set_status(self, message: str, is_error: bool = False):
        self.gui.status_text.value = message
        self.gui.status_text.color = ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400
        self.page.update()

    def show_message(self, message: str, is_error: bool = False):
        self.set_status(message, is_error=is_error)
        self.page.show_dialog(
            ft.SnackBar(
                ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700 if is_error else ft.Colors.GREEN_700,
                show_close_icon=True,
            )
        )

    # ==========================================
    # ZARZĄDZANIE KLUCZAMI
    # ==========================================
    def refresh_keys(self, _=None):
        private_keys = self.key_manager.list_private_keys()
        public_keys = self.key_manager.list_public_keys()
        
        if self.gui.public_key_dropdown.value not in public_keys:
            self.gui.public_key_dropdown.value = None

        self.gui.public_key_dropdown.options = [ft.dropdown.Option(key=k, text=k) for k in public_keys]

        self.gui.public_keys_column.controls.clear()
        for key in public_keys:
            self.gui.public_keys_column.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.VPN_KEY_OUTLINED, color=ft.Colors.BLUE_400),
                    ft.Text(key, expand=True),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, tooltip="Usuń z bazy", data=("public", key), on_click=self.delete_key)
                ])
            )

        self.gui.private_keys_column.controls.clear()
        for key in private_keys:
            self.gui.private_keys_column.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.KEY, color=ft.Colors.GREEN_400),
                    ft.Text(key, expand=True),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, tooltip="Usuń z bazy", data=("private", key), on_click=self.delete_key)
                ])
            )

        if not self.gui.public_key_dropdown.value and len(public_keys) == 1:
            self.gui.public_key_dropdown.value = public_keys[0]
            
        self.update_decrypt_passwords_panel()
        self.page.update()

    def delete_key(self, event):
        key_type, key_name = event.control.data
        if key_type == "public":
            path = Path(self.key_manager.get_public_key_path(key_name))
        else:
            path = Path(self.key_manager.get_private_key_path(key_name))

        try:
            if path.exists():
                path.unlink()
            self.show_message(f"Usunięto klucz: {key_name}")
            if key_type == "private":
                for item in self.files["decrypt"]:
                    if item.get("key_name") == key_name:
                        item["key_name"] = None
                self.refresh_file_list("decrypt")
                self.update_decrypt_passwords_panel()
            self.refresh_keys()
        except Exception as e:
            self.show_message(f"Błąd usuwania klucza: {e}", is_error=True)

    def key_needs_password(self, key_name: str) -> bool:
        try:
            path = self.key_manager.get_private_key_path(key_name)
            with open(path, "rb") as f:
                return b"ENCRYPTED" in f.read()
        except Exception:
            return False

    def update_decrypt_passwords_panel(self):
        required_keys = set()
        for item in self.files["decrypt"]:
            if item.get("key_name"):
                required_keys.add(item["key_name"])
                
        keys_needing_passwords = {k for k in required_keys if self.key_needs_password(k)}
            
        current_passwords = {c.data: c.value for c in self.gui.decrypt_passwords_panel.controls}
        self.gui.decrypt_passwords_panel.controls.clear()
        
        for key in sorted(keys_needing_passwords):
            self.gui.decrypt_passwords_panel.controls.append(
                ft.TextField(
                    label=f"Wpisz hasło odblokowujące klucz: {key}",
                    width=360,
                    password=True,
                    can_reveal_password=True,
                    value=current_passwords.get(key, ""),
                    data=key
                )
            )
        self.page.update()

    def auto_assign_keys(self, _=None):
        assigned = 0
        private_keys = self.key_manager.list_private_keys()
        for item in self.files["decrypt"]:
            metadata = self.read_metadata(Path(item["path"]))
            if metadata and "key_name" in metadata and metadata["key_name"] in private_keys:
                if item.get("key_name") != metadata["key_name"]:
                    item["key_name"] = metadata["key_name"]
                    assigned += 1
        
        self.refresh_file_list("decrypt")
        self.update_decrypt_passwords_panel()
        if _ is not None:
            self.show_message(f"Przydzielono {assigned} kluczy na podstawie metadanych.")

    # ==========================================
    # LOGIKA RENDEROWANIA LISTY PLIKÓW
    # ==========================================
    def create_dropdown_change_handler(self, idx):
        def handler(e):
            self.files["decrypt"][idx]["key_name"] = e.control.value
            self.update_decrypt_passwords_panel()
        return handler

    def refresh_file_list(self, group: str):
        controls = self.controls_for(group)
        column = controls["column"]
        column.controls.clear()
        files = self.files[group]
        selected_count = sum(1 for item in files if item.get("selected", False))
        controls["count"].value = f"{len(files)} plików, zaznaczone: {selected_count}"
        
        private_keys = self.key_manager.list_private_keys()

        for index, item in enumerate(files):
            path = Path(item["path"])
            error_msg = item.get("error")
            icon_color = ft.Colors.RED_400 if error_msg else ft.Colors.BLUE_400
            icon_type = ft.Icons.ERROR if error_msg else ft.Icons.INSERT_DRIVE_FILE

            text_col = ft.Column([
                ft.Text(path.name, tooltip=str(path), size=13, color=ft.Colors.RED_200 if error_msg else None)
            ], spacing=0)

            row_controls = []
            
            if self.is_advanced(group):
                checkbox = ft.Checkbox(value=item.get("selected", False), data=(group, index))
                checkbox.on_change = self.toggle_file_selection
                row_controls.append(checkbox)

            row_controls.extend([
                ft.Icon(icon_type, color=icon_color, tooltip=error_msg),
                ft.Container(content=text_col, expand=True),
            ])

            if group == "decrypt":
                valid_value = item.get("key_name") if item.get("key_name") in private_keys else None
                
                key_dropdown = ft.Dropdown(
                    options=[ft.dropdown.Option(k) for k in private_keys],
                    value=valid_value,
                    width=150,
                    height=35,
                    text_size=12,
                    content_padding=5,
                    hint_text="Wybierz klucz..."
                )
                key_dropdown.on_change = self.create_dropdown_change_handler(index)
                row_controls.append(key_dropdown)

                row_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.LOCK_OPEN,
                        icon_color=ft.Colors.GREEN_400,
                        tooltip="Odszyfruj natychmiast",
                        data=(group, index),
                        on_click=self.decrypt_single_file,
                    )
                )

            if self.is_advanced(group):
                row_controls.append(ft.IconButton(icon=ft.Icons.SWAP_HORIZ, tooltip="Zamień plik", data=(group, index), on_click=self.replace_file_at_index))

            row_controls.append(ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400, tooltip="Usuń z listy", data=(group, index), on_click=self.remove_file_at_index))

            column.controls.append(
                ft.Row(row_controls, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            )
        self.page.update()

    def toggle_file_selection(self, event):
        group, index = event.control.data
        if 0 <= index < len(self.files[group]):
            self.files[group][index]["selected"] = bool(event.control.value)
        self.refresh_file_list(group)

    async def pick_files(self, group: str):
        decrypt_mode = group == "decrypt"
        picked_files = await self.gui.file_picker.pick_files(
            dialog_title="Wybierz pliki .safe" if decrypt_mode else "Wybierz pliki do szyfrowania",
            allow_multiple=True,
            file_type=ft.FilePickerFileType.CUSTOM if decrypt_mode else ft.FilePickerFileType.ANY,
            allowed_extensions=["safe"] if decrypt_mode else None,
        )
        if picked_files:
            self.add_paths(group, [file.path for file in picked_files if file.path])

    def add_pasted_paths(self, group: str):
        field = self.controls_for(group)["pasted_paths"]
        if not field.value:
            return
        paths = [path.strip().strip('"').strip("'") for path in field.value.splitlines() if path.strip()]
        if paths:
            self.add_paths(group, paths)
        field.value = ""
        self.page.update()

    def add_paths(self, group: str, paths: list[str]):
        files = self.files[group]
        policy = self.controls_for(group)["policy"].value
        added = 0

        for raw_path in paths:
            path = Path(raw_path)
            if not path.is_file():
                continue

            file_data = {"path": str(path), "selected": False, "key_name": None}
            existing_index = next((i for i, item in enumerate(files) if item["path"] == str(path)), None)
            
            if existing_index is not None and policy == "replace":
                files[existing_index] = file_data
            else:
                files.append(file_data)
            added += 1

        if group == "decrypt":
            self.auto_assign_keys()
        self.refresh_file_list(group)
            
        if added > 0:
            self.show_message(f"Dodano pliki: {added}")
        elif paths:
            self.show_message("Nie dodano poprawnych plików.", is_error=True)

    async def pick_output_dir(self, group: str):
        directory = await self.gui.file_picker.get_directory_path(dialog_title="Wybierz folder zapisu")
        if directory:
            self.controls_for(group)["output_dir"].value = directory
            self.page.update()

    def remove_selected_files(self, group: str):
        before = len(self.files[group])
        self.files[group] = [item for item in self.files[group] if not item.get("selected", False)]
        removed = before - len(self.files[group])
        self.refresh_file_list(group)
        self.show_message(f"Usunięto pliki: {removed}" if removed else "Nie zaznaczono plików.", is_error=removed == 0)

    def remove_file_at_index(self, event):
        group, index = event.control.data
        if 0 <= index < len(self.files[group]):
            self.files[group].pop(index)
        self.refresh_file_list(group)
        if group == "decrypt":
            self.update_decrypt_passwords_panel()

    async def replace_selected_file(self, group: str):
        selected_indexes = [i for i, item in enumerate(self.files[group]) if item.get("selected", False)]
        if len(selected_indexes) != 1:
            return self.show_message("Zaznacz dokładnie jeden plik do zamiany.", is_error=True)
        await self.replace_index(group, selected_indexes[0])

    async def replace_file_at_index(self, event):
        group, index = event.control.data
        await self.replace_index(group, index)

    async def replace_index(self, group: str, index: int):
        picked_files = await self.gui.file_picker.pick_files(
            dialog_title="Wybierz plik zamienny",
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM if group == "decrypt" else ft.FilePickerFileType.ANY,
            allowed_extensions=["safe"] if group == "decrypt" else None,
        )
        if picked_files and picked_files[0].path:
            path = Path(picked_files[0].path)
            file_data = {"path": str(path), "selected": False, "key_name": None}
                    
            self.files[group][index] = file_data
            
            if group == "decrypt":
                self.auto_assign_keys()
            self.refresh_file_list(group)

    async def import_public_key(self, _):
        await self.import_keys(self.key_manager.public_dir, "publiczny")

    async def import_private_key(self, _):
        await self.import_keys(self.key_manager.private_dir, "prywatny")

    async def import_keys(self, target_dir: Path, label: str):
        picked_files = await self.gui.file_picker.pick_files(
            dialog_title=f"Dodaj klucz {label}",
            allow_multiple=True,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pem"],
        )
        if not picked_files:
            return

        imported = 0
        for picked_file in picked_files:
            source = Path(picked_file.path)
            target = self.resolve_conflict("encrypt", target_dir / source.name)
            if source.resolve() == target.resolve():
                continue
            shutil.copy2(source, target)
            imported += 1

        self.refresh_keys()
        self.show_message(f"Dodano klucze: {imported}")

    async def generate_keys(self, _):
        key_name = Path(self.gui.new_key_name.value.strip()).stem
        password = self.gui.new_key_password.value or None
        if not key_name:
            return self.show_message("Podaj nazwę nowej pary kluczy.", is_error=True)

        private_key_path = self.resolve_conflict("encrypt", Path(self.key_manager.get_private_key_path(f"{key_name}.pem")))
        public_key_path = self.resolve_conflict("encrypt", Path(self.key_manager.get_public_key_path(f"{key_name}.pem")))

        self.set_busy(True)
        self.set_status("Generowanie pary kluczy...")
        try:
            await asyncio.to_thread(self.write_key_pair, str(private_key_path), str(public_key_path), password)
        except Exception as error:
            self.show_message(f"Błąd generowania kluczy: {error}", is_error=True)
            return
        finally:
            self.set_busy(False)

        self.gui.new_key_name.value = ""
        self.gui.new_key_password.value = ""
        self.refresh_keys()
        self.show_message(f"Wygenerowano klucze: {private_key_path.name}")

    def write_key_pair(self, private_key_path: str, public_key_path: str, password: str | None):
        rsa_handler = RSAHandler()
        rsa_handler.key_generator()
        rsa_handler.export_private_key(private_key_path, password=password)
        rsa_handler.export_public_key(public_key_path)

    def resolve_conflict(self, group: str, path: Path) -> Path:
        policy = self.controls_for(group)["policy"].value
        if policy == "replace" or not path.exists():
            return path

        counter = 1
        while True:
            candidate = path.with_name(f"{path.stem}_copy_{counter}{path.suffix}")
            if not candidate.exists():
                return candidate
            counter += 1

    def default_output_dir(self, group: str, input_path: Path) -> Path:
        output_value = self.controls_for(group)["output_dir"].value
        return Path(output_value) if output_value else input_path.parent

    def encrypted_output_path(self, input_path: Path) -> Path:
        output_dir = self.default_output_dir("encrypt", input_path)
        if self.is_advanced("encrypt") and self.gui.encrypt_preserve_tree.value:
            output_dir = output_dir / input_path.parent.name
            output_dir.mkdir(parents=True, exist_ok=True)
        return self.resolve_conflict("encrypt", output_dir / f"{input_path.name}.safe")

    def decrypted_output_path(self, input_path: Path) -> Path:
        metadata = self.read_metadata(input_path)
        if self.is_advanced("decrypt") and self.gui.decrypt_use_metadata_name.value and metadata and metadata.get("suggested_decrypt_output"):
            output_name = metadata["suggested_decrypt_output"]
        elif input_path.name.endswith(".safe"):
            output_name = input_path.name[:-5]
        else:
            output_name = f"{input_path.stem}_decrypted{input_path.suffix}"
        return self.resolve_conflict("decrypt", self.default_output_dir("decrypt", input_path) / output_name)

    # ==========================================
    # LOGIKA OSADZANYCH METADANYCH (FOOTERS)
    # ==========================================
    def append_metadata(self, safe_path: Path, metadata: dict):
        try:
            meta_bytes = json.dumps(metadata).encode('utf-8')
            with open(safe_path, 'ab') as f:
                f.write(meta_bytes)
                f.write(len(meta_bytes).to_bytes(4, byteorder='big'))
                f.write(b"<META>") # Znacznik pozwalający zidentyfikować, czy plik posiada metadane
        except Exception as e:
            print(f"Błąd podczas osadzania metadanych: {e}")

    def strip_metadata(self, safe_path: Path) -> dict | None:
        try:
            with open(safe_path, 'r+b') as f:
                f.seek(0, 2)
                file_size = f.tell()
                if file_size < 10:
                    return None
                    
                f.seek(-6, 2)
                if f.read(6) == b"<META>":
                    f.seek(-10, 2)
                    meta_len = int.from_bytes(f.read(4), byteorder='big')
                    total_meta_size = meta_len + 10
                    
                    if file_size < total_meta_size:
                        return None
                        
                    f.seek(file_size - total_meta_size)
                    meta_bytes = f.read(meta_len)
                    meta_dict = json.loads(meta_bytes.decode('utf-8'))
                    
                    # Obcinamy stopkę z metadanymi, aby czysty GCM przeszedł weryfikację
                    f.truncate(file_size - total_meta_size)
                    return meta_dict
        except Exception:
            pass
        return None

    def read_metadata(self, safe_path: Path) -> dict | None:
        if not safe_path.is_file():
            return None
            
        # 1. Próba odczytania wbudowanych metadanych ze stopki
        try:
            with open(safe_path, 'rb') as f:
                f.seek(0, 2)
                file_size = f.tell()
                if file_size >= 10:
                    f.seek(-6, 2)
                    if f.read(6) == b"<META>":
                        f.seek(-10, 2)
                        meta_len = int.from_bytes(f.read(4), byteorder='big')
                        if file_size >= meta_len + 10:
                            f.seek(-10 - meta_len, 2)
                            meta_bytes = f.read(meta_len)
                            return json.loads(meta_bytes.decode('utf-8'))
        except Exception:
            pass
            
        # 2. Wsteczna kompatybilność - jeśli wbudowane nie istnieją, szuka starego pliku .meta.json
        external_meta_path = Path(f"{safe_path}.meta.json")
        if external_meta_path.is_file():
            try:
                return json.loads(external_meta_path.read_text(encoding="utf-8"))
            except Exception:
                pass
                
        return None

    def set_busy(self, is_busy: bool):
        controls = [
            self.gui.btn_encrypt_add_files,
            self.gui.btn_encrypt_add_paths,
            self.gui.btn_encrypt_output_dir,
            self.gui.btn_encrypt_remove_selected,
            self.gui.btn_encrypt_replace_selected,
            self.gui.btn_encrypt_clear,
            self.gui.btn_decrypt_add_files,
            self.gui.btn_decrypt_add_paths,
            self.gui.btn_decrypt_output_dir,
            self.gui.btn_decrypt_remove_selected,
            self.gui.btn_decrypt_replace_selected,
            self.gui.btn_decrypt_clear,
            self.gui.encrypt_advanced,
            self.gui.decrypt_advanced,
            self.gui.btn_refresh_keys,
            self.gui.btn_import_public_key,
            self.gui.btn_import_private_key,
            self.gui.btn_generate_keys,
            self.gui.btn_encrypt,
            self.gui.btn_decrypt,
            self.gui.btn_decrypt_auto_assign,
            self.gui.encrypt_pasted_paths,
            self.gui.decrypt_pasted_paths
        ]
        self.gui.progress_ring.visible = is_busy
        for control in controls:
            control.disabled = is_busy
        self.page.update()
# ... (początek klasy bez zmian aż do encrypt_files) ...

    async def encrypt_files(self, _):
        files = list(self.files["encrypt"])
        selected_key = self.gui.public_key_dropdown.value
        if not files:
            return self.show_message("Dodaj pliki do szyfrowania.", is_error=True)
        if not selected_key:
            return self.show_message("Wybierz klucz publiczny.", is_error=True)

        self.set_busy(True)
        self.set_status("Szyfrowanie plików...")
        public_key_path = self.key_manager.get_public_key_path(selected_key)
        results = []

        try:
            for item in files:
                input_path = Path(item["path"])
                output_path = self.encrypted_output_path(input_path)
                success = await asyncio.to_thread(encrypt_file_hybrid, str(input_path), public_key_path, str(output_path))
                
                # ZMIANA: Zawsze osadzamy metadane, bez sprawdzania checkboxa
                if success:
                    metadata = {
                        "operation": "encrypt",
                        "key_name": selected_key,
                        "suggested_decrypt_output": input_path.name,
                        "created_at": datetime.now().isoformat(timespec="seconds"),
                        "source_size": input_path.stat().st_size if self.gui.encrypt_include_size.value else None
                    }
                    self.append_metadata(output_path, metadata)
                    results.append({"input": str(input_path), "output": str(output_path), "success": True})
        except Exception as error:
            self.show_message(f"Błąd szyfrowania: {error}", is_error=True)
            return
        finally:
            self.set_busy(False)

        self.files["encrypt"].clear()
        self.refresh_file_list("encrypt")
        self.show_message(f"Zaszyfrowano pomyślnie.")

    async def decrypt_files(self, _):
        files = list(self.files["decrypt"])
        if not files:
            return self.show_message("Dodaj pliki .safe do deszyfrowania.", is_error=True)

        self.set_busy(True)
        self.set_status("Deszyfrowanie plików...")
        
        passwords = {c.data: c.value for c in self.gui.decrypt_passwords_panel.controls}
        failed_files = []
        success_count = 0

        try:
            for item in files:
                input_path = Path(item["path"])
                file_key = item.get("key_name")
                
                if not file_key:
                    item["error"] = "Brak klucza"
                    failed_files.append(item)
                    continue
                    
                password = passwords.get(file_key) or None
                private_key_path = self.key_manager.get_private_key_path(file_key)
                output_path = self.decrypted_output_path(input_path)
                
                # Zawsze próbujemy odczytać metadane z pliku
                embedded_meta = self.strip_metadata(input_path)
                
                try:
                    success = await asyncio.to_thread(decrypt_file_hybrid, str(input_path), private_key_path, password, str(output_path))
                    item["error"] = None
                    success_count += 1
                except Exception as e:
                    item["error"] = str(e)
                    # Jeśli się nie udało, doklejamy metadane z powrotem
                    if embedded_meta:
                        self.append_metadata(input_path, embedded_meta)
                    failed_files.append(item)

        finally:
            self.set_busy(False)
            for c in self.gui.decrypt_passwords_panel.controls:
                c.value = ""

        self.files["decrypt"] = failed_files
        self.refresh_file_list("decrypt")
        self.show_message(f"Odszyfrowano: {success_count}/{len(files)}")

    async def decrypt_single_file(self, event):
        group, index = event.control.data
        item = self.files["decrypt"][index]
        input_path = Path(item["path"])
        file_key = item.get("key_name")

        if not file_key:
            return self.show_message("Wybierz klucz!", is_error=True)

        passwords = {c.data: c.value for c in self.gui.decrypt_passwords_panel.controls}
        password = passwords.get(file_key) or None
        
        self.set_busy(True)
        # Zawsze czytamy metadane z pliku
        embedded_meta = self.strip_metadata(input_path)
        
        private_key_path = self.key_manager.get_private_key_path(file_key)
        output_path = self.decrypted_output_path(input_path)

        try:
            success = await asyncio.to_thread(decrypt_file_hybrid, str(input_path), private_key_path, password, str(output_path))
            if success:
                self.files["decrypt"].pop(index)
                self.show_message("Odszyfrowano.")
            else:
                if embedded_meta: self.append_metadata(input_path, embedded_meta)
                self.show_message("Błąd!", is_error=True)
        finally:
            self.set_busy(False)
            self.refresh_file_list("decrypt")