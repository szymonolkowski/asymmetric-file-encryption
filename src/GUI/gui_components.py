import flet as ft


class AppGUI:
    def __init__(self):
        self.status_text = ft.Text(weight=ft.FontWeight.BOLD)
        self.progress_ring = ft.ProgressRing(visible=False, width=24, height=24)
        self.file_picker = ft.FilePicker()

        self.public_key_dropdown = ft.Dropdown(width=360, label="Klucz publiczny")
        
        self.decrypt_passwords_panel = ft.Column(spacing=10)

        self.new_key_name = ft.TextField(label="Nazwa nowej pary kluczy", width=320, hint_text="np. wiktor")
        self.new_key_password = ft.TextField(
            label="Hasło nowego klucza prywatnego (opcjonalnie)",
            width=320,
            password=True,
            can_reveal_password=True,
        )

        self.btn_refresh_keys = ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Odśwież klucze")
        self.btn_import_public_key = ft.OutlinedButton("Dodaj klucz publiczny", icon=ft.Icons.UPLOAD_FILE)
        self.btn_import_private_key = ft.OutlinedButton("Dodaj klucz prywatny", icon=ft.Icons.UPLOAD_FILE)
        self.btn_generate_keys = ft.ElevatedButton("Generuj klucze", icon=ft.Icons.VPN_KEY)

        self.public_keys_column = ft.Column(spacing=2)
        self.private_keys_column = ft.Column(spacing=2)

        self.encrypt_advanced = ft.Switch(label="Zaawansowane", value=False)
        self.encrypt_advanced_panel = ft.Column(visible=False, spacing=10)
        self.encrypt_duplicate_policy = self.policy_dropdown("Gdy .safe istnieje")
        self.encrypt_output_dir = ft.TextField(label="Folder zapisu .safe", width=520, read_only=True)
        self.encrypt_pasted_paths = ft.TextField(
            label="Wklej skopiowane ścieżki plików (Ctrl+Shift+C -> Ctrl+V)",
            width=520,
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        self.encrypt_files_column = ft.Column(spacing=6)
        self.encrypt_file_count = ft.Text("0 plików", color=ft.Colors.GREY_400)
        
        # Zmienione etykiety dla metadanych, manifest usunięty
        self.encrypt_metadata_enabled = ft.Checkbox(label="Osadź metadane w pliku .safe", value=True)
        self.encrypt_preserve_tree = ft.Checkbox(label="Zachowaj podfoldery", value=False)
        self.encrypt_include_size = ft.Checkbox(label="Rozmiar i czas w metadanych", value=True)

        self.btn_encrypt_add_files = ft.ElevatedButton("Wybierz pliki", icon=ft.Icons.FILE_OPEN)
        self.btn_encrypt_add_paths = ft.OutlinedButton("Dodaj ścieżki", icon=ft.Icons.ADD)
        self.btn_encrypt_output_dir = ft.OutlinedButton("Folder zapisu", icon=ft.Icons.FOLDER_OPEN)
        self.btn_encrypt_remove_selected = ft.OutlinedButton("Usuń zaznaczone", icon=ft.Icons.DELETE)
        self.btn_encrypt_replace_selected = ft.OutlinedButton("Zamień zaznaczony", icon=ft.Icons.SWAP_HORIZ)
        self.btn_encrypt_clear = ft.OutlinedButton("Wyczyść", icon=ft.Icons.DELETE_SWEEP)
        self.btn_encrypt = ft.ElevatedButton(
            "Zaszyfruj",
            icon=ft.Icons.LOCK,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_700),
        )

        self.decrypt_advanced = ft.Switch(label="Zaawansowane", value=False)
        self.decrypt_advanced_panel = ft.Column(visible=False, spacing=10)
        self.decrypt_duplicate_policy = self.policy_dropdown("Gdy plik istnieje")
        self.decrypt_output_dir = ft.TextField(label="Folder zapisu", width=520, read_only=True)
        self.decrypt_pasted_paths = ft.TextField(
            label="Wklej skopiowane ścieżki plików .safe (Ctrl+Shift+C -> Ctrl+V)",
            width=520,
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        self.decrypt_files_column = ft.Column(spacing=6)
        self.decrypt_file_count = ft.Text("0 plików", color=ft.Colors.GREY_400)
        
        self.btn_decrypt_auto_assign = ft.ElevatedButton(
            "Przydziel automatycznie", 
            icon=ft.Icons.AUTO_FIX_HIGH, 
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.INDIGO_700)
        )
        
        # Zmieniona etykieta, manifesty usunięte z deszyfrowania
        self.decrypt_use_metadata_name = ft.Checkbox(label="Nazwy wyjściowe z wbudowanych metadanych", value=True)

        self.btn_decrypt_add_files = ft.ElevatedButton("Wybierz .safe", icon=ft.Icons.FILE_OPEN)
        self.btn_decrypt_add_paths = ft.OutlinedButton("Dodaj ścieżki", icon=ft.Icons.ADD)
        self.btn_decrypt_output_dir = ft.OutlinedButton("Folder zapisu", icon=ft.Icons.FOLDER_OPEN)
        self.btn_decrypt_remove_selected = ft.OutlinedButton("Usuń zaznaczone", icon=ft.Icons.DELETE)
        self.btn_decrypt_replace_selected = ft.OutlinedButton("Zamień zaznaczony", icon=ft.Icons.SWAP_HORIZ)
        self.btn_decrypt_clear = ft.OutlinedButton("Wyczyść", icon=ft.Icons.DELETE_SWEEP)
        self.btn_decrypt = ft.ElevatedButton(
            "Odszyfruj Wszystko",
            icon=ft.Icons.LOCK_OPEN,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700),
        )

    def policy_dropdown(self, label: str):
        return ft.Dropdown(
            label=label,
            width=220,
            value="copy",
            options=[
                ft.dropdown.Option(key="copy", text="Dodaj kopię"),
                ft.dropdown.Option(key="replace", text="Podmień"),
            ],
        )

    def bordered_panel(self, content: ft.Control, height: int = 500):
        return ft.Container(
            content=content,
            border=ft.Border(
                left=ft.BorderSide(1, ft.Colors.GREY_700),
                top=ft.BorderSide(1, ft.Colors.GREY_700),
                right=ft.BorderSide(1, ft.Colors.GREY_700),
                bottom=ft.BorderSide(1, ft.Colors.GREY_700),
            ),
            border_radius=6,
            padding=10,
            height=height,
        )

    def build_layout(self):
        header = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Asymmetric File Encryptor", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("RSA-OAEP + AES-256-GCM (Z wbudowanymi metadanymi)", size=12, color=ft.Colors.GREY_400),
                ]
            ),
            padding=ft.Padding(bottom=14),
        )

        self.encrypt_advanced_panel.controls = [
            ft.Row([self.encrypt_duplicate_policy, self.btn_encrypt_output_dir], wrap=True),
            self.encrypt_output_dir,
            ft.Row([self.encrypt_pasted_paths, self.btn_encrypt_add_paths], wrap=True),
            ft.Row([self.btn_encrypt_remove_selected, self.btn_encrypt_replace_selected, self.btn_encrypt_clear], wrap=True),
            ft.Row(
                [
                    self.encrypt_metadata_enabled,
                    self.encrypt_preserve_tree,
                    self.encrypt_include_size,
                ],
                wrap=True,
            ),
        ]

        encrypt_tab = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row([self.btn_encrypt_add_files, self.btn_encrypt_clear, self.encrypt_advanced], wrap=True),
                            self.encrypt_pasted_paths,
                            ft.Row([self.public_key_dropdown, self.btn_encrypt], wrap=True),
                            self.encrypt_advanced_panel,
                        ],
                        expand=5,
                        spacing=15,
                    ),
                    ft.VerticalDivider(width=20, color=ft.Colors.GREY_800),
                    ft.Column(
                        [
                            ft.Text("Pliki do szyfrowania", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200),
                            self.bordered_panel(
                                ft.Column([self.encrypt_file_count, self.encrypt_files_column], spacing=8, scroll=ft.ScrollMode.AUTO)
                            ),
                        ],
                        expand=6,
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            ),
            padding=ft.Padding(top=15, bottom=15, left=0, right=0)
        )

        self.decrypt_advanced_panel.controls = [
            ft.Row([self.decrypt_duplicate_policy, self.btn_decrypt_output_dir], wrap=True),
            self.decrypt_output_dir,
            ft.Row([self.decrypt_pasted_paths, self.btn_decrypt_add_paths], wrap=True),
            ft.Row([self.btn_decrypt_remove_selected, self.btn_decrypt_replace_selected, self.btn_decrypt_clear], wrap=True),
            ft.Row(
                [
                    self.decrypt_use_metadata_name,
                ],
                wrap=True,
            ),
        ]

        decrypt_tab = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row([self.btn_decrypt_add_files, self.btn_decrypt_clear, self.decrypt_advanced], wrap=True),
                            self.decrypt_pasted_paths,
                            ft.Row([self.btn_decrypt_auto_assign, self.btn_decrypt], wrap=True),
                            self.decrypt_passwords_panel,
                            self.decrypt_advanced_panel,
                        ],
                        expand=5,
                        spacing=15,
                    ),
                    ft.VerticalDivider(width=20, color=ft.Colors.GREY_800),
                    ft.Column(
                        [
                            ft.Text("Pliki .safe do deszyfrowania (Klucz wybierasz dla każdego pliku)", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_200),
                            self.bordered_panel(
                                ft.Column([self.decrypt_file_count, self.decrypt_files_column], spacing=8, scroll=ft.ScrollMode.AUTO)
                            ),
                        ],
                        expand=6,
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            ),
            padding=ft.Padding(top=15, bottom=15, left=0, right=0)
        )

        keys_tab = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Zarządzanie biblioteką kluczy", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200),
                            self.btn_refresh_keys,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row([self.btn_import_public_key, self.btn_import_private_key], wrap=True),
                    ft.Row([self.new_key_name, self.new_key_password, self.btn_generate_keys], wrap=True),
                    ft.Divider(height=20, color=ft.Colors.GREY_800),
                    ft.Row(
                        [
                            ft.Column([
                                ft.Text("Klucze publiczne", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_100),
                                self.bordered_panel(ft.Column([self.public_keys_column], scroll=ft.ScrollMode.AUTO), height=200)
                            ], expand=1),
                            ft.Column([
                                ft.Text("Klucze prywatne", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_100),
                                self.bordered_panel(ft.Column([self.private_keys_column], scroll=ft.ScrollMode.AUTO), height=200)
                            ], expand=1),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                ],
                spacing=12,
            ),
            padding=ft.Padding(top=15, bottom=0, left=0, right=0)
        )

        tabs = ft.Tabs(
            length=3,
            selected_index=0,
            expand=True,
            content=ft.Column(
                [
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Szyfrowanie", icon=ft.Icons.LOCK),
                            ft.Tab(label="Deszyfrowanie", icon=ft.Icons.LOCK_OPEN),
                            ft.Tab(label="Klucze", icon=ft.Icons.VPN_KEY),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            encrypt_tab,
                            decrypt_tab,
                            keys_tab,
                        ],
                    ),
                ],
                expand=True,
            ),
        )

        actions_menu = ft.Column(
            [
                tabs,
                ft.Row([self.progress_ring, self.status_text], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
        )

        return header, actions_menu