import flet as ft


class AppGUI:
    def __init__(self):
        self.status_text = ft.Text(weight=ft.FontWeight.BOLD)
        self.progress_ring = ft.ProgressRing(visible=False, width=24, height=24)

        self.encrypt_input_path = ft.TextField(
            label="Plik do zaszyfrowania", width=520, read_only=True
        )
        self.encrypt_output_path = ft.TextField(
            label="Zapisz jako .safe", width=520, read_only=True
        )
        self.decrypt_input_path = ft.TextField(
            label="Plik .safe do odszyfrowania", width=520, read_only=True
        )
        self.decrypt_output_path = ft.TextField(
            label="Zapisz odszyfrowany plik jako", width=520, read_only=True
        )
        self.new_key_name = ft.TextField(
            label="Nazwa nowej pary kluczy", width=360, hint_text="np. wiktor"
        )
        self.new_key_password = ft.TextField(
            label="Haslo nowego klucza prywatnego",
            width=360,
            password=True,
            can_reveal_password=True,
        )

        self.private_key_dropdown = ft.Dropdown(
            width=360, label="Klucz prywatny do deszyfrowania"
        )
        self.public_key_dropdown = ft.Dropdown(
            width=360, label="Klucz publiczny odbiorcy"
        )
        self.private_key_password = ft.TextField(
            label="Haslo klucza prywatnego",
            width=360,
            password=True,
            can_reveal_password=True,
        )

        self.file_picker = ft.FilePicker()

        self.btn_pick_encrypt_input = ft.OutlinedButton(
            "Wybierz plik", icon=ft.Icons.FILE_OPEN
        )
        self.btn_pick_encrypt_output = ft.OutlinedButton(
            "Wybierz zapis", icon=ft.Icons.SAVE
        )
        self.btn_pick_decrypt_input = ft.OutlinedButton(
            "Wybierz .safe", icon=ft.Icons.FILE_OPEN
        )
        self.btn_pick_decrypt_output = ft.OutlinedButton(
            "Wybierz zapis", icon=ft.Icons.SAVE
        )
        self.btn_refresh_keys = ft.IconButton(
            icon=ft.Icons.REFRESH, tooltip="Odswiez liste kluczy"
        )
        self.btn_generate_keys = ft.ElevatedButton(
            "Generuj klucze", icon=ft.Icons.VPN_KEY
        )
        self.btn_encrypt = ft.ElevatedButton(
            "Zaszyfruj",
            icon=ft.Icons.LOCK,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_700),
        )
        self.btn_decrypt = ft.ElevatedButton(
            "Odszyfruj",
            icon=ft.Icons.LOCK_OPEN,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700),
        )

    def build_layout(self):
        header = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Asymmetric File Encryptor", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "RSA-OAEP + AES-256-GCM",
                        size=12,
                        color=ft.Colors.GREY_400,
                    ),
                ]
            ),
            padding=ft.Padding(bottom=20),
        )

        encrypt_menu = ft.Column(
            controls=[
                ft.Text("1. Szyfrowanie", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200),
                ft.Row([self.encrypt_input_path, self.btn_pick_encrypt_input], wrap=True),
                ft.Row([self.encrypt_output_path, self.btn_pick_encrypt_output], wrap=True),
                self.public_key_dropdown,
                self.btn_encrypt,
            ],
            spacing=12,
        )

        decrypt_menu = ft.Column(
            controls=[
                ft.Text("2. Deszyfrowanie", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200),
                ft.Row([self.decrypt_input_path, self.btn_pick_decrypt_input], wrap=True),
                ft.Row([self.decrypt_output_path, self.btn_pick_decrypt_output], wrap=True),
                self.private_key_dropdown,
                self.private_key_password,
                self.btn_decrypt,
            ],
            spacing=12,
        )

        actions_menu = ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Text("Klucze RSA", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200),
                        self.btn_refresh_keys,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row([self.new_key_name, self.new_key_password, self.btn_generate_keys], wrap=True),
                ft.Divider(height=20, color=ft.Colors.GREY_700),
                encrypt_menu,
                ft.Divider(height=20, color=ft.Colors.GREY_700),
                decrypt_menu,
                ft.Row(
                    [
                        ft.Container(content=self.status_text, padding=ft.Padding(top=10), expand=True),
                        self.progress_ring,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            expand=True,
            spacing=12,
        )

        return header, actions_menu
