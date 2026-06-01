import os
import shutil
import secrets

class FileHandler:
    """
    Moduł pomocniczy do zarządzania plikami, metadanymi oraz bezpiecznym usuwaniem danych.
    """

    # ==========================================
    # ZADANIE 1: Obsługa metadanych (Opcja Binarna)
    # ==========================================
    @staticmethod
    def encode_extension(filepath: str) -> bytes:
        """
        Pobiera rozszerzenie z oryginalnego pliku i pakuje je w format binarny:
        [4 bajty określające długość] + [rozszerzenie w UTF-8]
        """
        _, ext = os.path.splitext(filepath)
        ext_bytes = ext.encode('utf-8')
        # Zapisujemy długość rozszerzenia jako 4-bajtową liczbę całkowitą (big-endian)
        ext_length = len(ext_bytes).to_bytes(4, byteorder='big')
        return ext_length + ext_bytes

    @staticmethod
    def decode_extension(file_stream) -> str:
        """
        Odczytuje rozszerzenie z początku strumienia pliku .safe.
        Przesuwa kursor pliku o odczytaną liczbę bajtów.
        """
        ext_length_bytes = file_stream.read(4)
        if not ext_length_bytes:
            raise EOFError("Nieoczekiwany koniec pliku podczas odczytu metadanych.")
        
        ext_length = int.from_bytes(ext_length_bytes, byteorder='big')
        
        # Jeśli plik nie miał rozszerzenia (ext_length == 0)
        if ext_length == 0:
            return ""
            
        ext_bytes = file_stream.read(ext_length)
        return ext_bytes.decode('utf-8')

    # ==========================================
    # ZADANIE 2: Bezpieczny odczyt i zapis (I/O)
    # ==========================================
    @staticmethod
    def validate_for_encryption(input_path: str, output_dir: str = None) -> None:
        """
        Sprawdza stabilność systemu przed szyfrowaniem (uprawnienia, miejsce na dysku).
        Rzuca odpowiednie wyjątki z czytelnym komunikatem dla warstwy GUI.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Plik wejściowy nie istnieje: {input_path}")
        
        if not os.access(input_path, os.R_OK):
            raise PermissionError(f"Brak uprawnień do odczytu pliku: {input_path}")
        
        # Domyślnie sprawdzamy miejsce na dysku tam, gdzie znajduje się plik wejściowy
        if output_dir is None:
            output_dir = os.path.dirname(os.path.abspath(input_path))
            
        # Obliczanie wymaganego miejsca: rozmiar pliku + ~268 bajtów (RSA + Nonce) + bufor 50 bajtów
        file_size = os.path.getsize(input_path)
        required_space = file_size + 318 
        
        try:
            total, used, free = shutil.disk_usage(output_dir)
            if free < required_space:
                raise OSError(f"Brak miejsca na dysku docelowym. Wymagane: {required_space} B, dostępne: {free} B.")
        except FileNotFoundError:
            raise FileNotFoundError(f"Katalog docelowy nie istnieje: {output_dir}")

    # ==========================================
    # ZADANIE 3: Niszczenie danych (Data Shredding)
    # ==========================================
    @staticmethod
    def shred_and_remove_file(filepath: str, passes: int = 1) -> None:
        """
        Nadpisuje fizyczne miejsce pliku na dysku kryptograficznie bezpiecznymi
        losowymi bajtami przed jego usunięciem (zapobiega odzyskiwaniu danych).
        """
        if not os.path.exists(filepath):
            return

        try:
            file_size = os.path.getsize(filepath)
            # Otwieramy plik w trybie binarnym zapisu, bez buforowania
            with open(filepath, "ba+", buffering=0) as f:
                for _ in range(passes):
                    f.seek(0)
                    # Nadpisanie losowymi bajtami (bezpieczniejsze niż same zera)
                    f.write(secrets.token_bytes(file_size))
            
            # Po nadpisaniu możemy bezpiecznie usunąć wskaźnik pliku
            os.remove(filepath)
        except Exception as e:
            raise OSError(f"Błąd podczas niszczenia pliku {filepath}: {str(e)}")

    # ==========================================
    # ZADANIE 4: Kontrakt z GUI (Dla Wicia)
    # ==========================================
    @staticmethod
    def generate_safe_path(original_filepath: str) -> str:
        """
        Generuje domyślną ścieżkę do zapisu dla zaszyfrowanego pliku.
        Przykład: 'C:/Dokumenty/raport.pdf' -> 'C:/Dokumenty/raport.pdf.safe'
        """
        return f"{original_filepath}.safe"

    @staticmethod
    def generate_decrypted_path(safe_filepath: str, original_ext: str) -> str:
        """
        Generuje ścieżkę do pliku po deszyfracji z uwzględnieniem oryginalnego rozszerzenia.
        Przykład: 'raport.pdf.safe' -> 'raport.pdf'
        Jeżeli ktoś zmienił nazwę na 'tajne.safe' -> 'tajne.pdf'
        """
        # Użycie funkcji wbudowanej z Pythona 3.9+
        base_name = safe_filepath.removesuffix('.safe')
        
        # Zapobiega podwójnemu rozszerzeniu jeśli base_name już je ma (np. raport.pdf)
        if original_ext and not base_name.endswith(original_ext):
            return f"{base_name}{original_ext}"
            
        return base_name