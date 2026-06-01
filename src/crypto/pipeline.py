import sys
import os

# To pozwala Pythonowi zobaczyć folder 'src' (jeden poziom wyżej niż folder 'crypto')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from asymmetric import RSAHandler
from symmetric import FileEncryptor
from utils.file_handler import FileHandler  # Zakładam, że tu masz ten moduł

def encrypt_file_hybrid(input_path: str, public_key_path: str, output_safe_path: str):
    # Wczytanie całego pliku do pamięci
    with open(input_path, 'rb') as input_file:
        raw_data = input_file.read()

    rsa_handler = RSAHandler()
    file_encryptor = FileEncryptor()

    rsa_handler.load_public_key(public_key_path)
    aes_key = file_encryptor.generate_aes_key()

    ciphertext, nonce = file_encryptor.encrypt_bytes(raw_data, aes_key)
    encrypted_aes_key = rsa_handler.encrypt(aes_key)
    
    if not encrypted_aes_key:
        print("Encryption failed.")
        return False
        
    print("Encryption successful.")
    
    # Krok 1: Generujemy binarne metadane (rozszerzenie)
    ext_data = FileHandler.encode_extension(input_path)
    
    with open(output_safe_path, 'wb') as output_file:
        # Zapisujemy w nowej kolejności: [Rozszerzenie] + [Nonce] + [Klucz AES] + [Dane]
        output_file.write(ext_data)
        output_file.write(nonce)
        output_file.write(encrypted_aes_key)
        output_file.write(ciphertext)
        
    return True

def decrypt_file_hybrid(input_path: str, private_key_path: str, password: str, output_base_path: str):
    file_encryptor = FileEncryptor()
    rsa_handler = RSAHandler()
    
    with open(input_path, 'rb') as input_file:
        # Krok 2: Odczytujemy rozszerzenie bezpośrednio ze strumienia pliku.
        # To automatycznie przesunie kursor (wewnętrzny wskaźnik) pliku za metadane!
        original_ext = FileHandler.decode_extension(input_file)
        
        # Wczytujemy resztę pliku (już bez pierwszych bajtów metadanych)
        encrypted_safe_data = input_file.read()

    # Ponieważ pozbyliśmy się metadanych, Twoje offsety pozostają w 100% niezmienione!
    nonce = encrypted_safe_data[:12]
    encrypted_aes_key = encrypted_safe_data[12:12+256]
    encrypted_data = encrypted_safe_data[12+256:]

    rsa_handler.load_private_key(private_key_path, password)
    aes_key = rsa_handler.decrypt(encrypted_aes_key)
    decrypted_data = file_encryptor.decrypt_bytes(encrypted_data, nonce, aes_key)

    if decrypted_data:
        # Krok 3: Odtwarzamy oryginalną nazwę pliku z odpowiednim rozszerzeniem
        final_output_path = FileHandler.generate_decrypted_path(output_base_path, original_ext)
        
        with open(final_output_path, 'wb') as output_file:
            output_file.write(decrypted_data)
            
        print(f"Decryption successful. Zapisano jako: {final_output_path}")
        return final_output_path # Zwracamy ścieżkę do testów
    else:
        print("Decryption failed.")
        return False


if __name__ == "__main__":
    # Kod testowy z drobnymi modyfikacjami, by przetestować nową logikę
    tekst_testowy = "To jest ściśle tajna wiadomość inżynierska projektu FastSec Hub!".encode('utf-8')

    with open("../../huj.txt", "wb") as f:
        f.write(tekst_testowy)
    print("1. Utworzono plik testowy 'test.txt'.")

    handler = RSAHandler()
    handler.key_generator()
    handler.export_public_key("public.pem")
    handler.export_private_key("private.pem", password="MojeBezpieczneHaslo123")
    print("2. Wygenerowano klucze 'public.pem' oraz 'private.pem'.")

    print("-" * 50)

    print("3. Uruchamiam szyfrowanie z metadanymi...")
    # Wykorzystujemy FileHandler do wygenerowania domyślnej nazwy pliku wyjściowego
    bezpieczna_sciezka = FileHandler.generate_safe_path("test.txt")
    
    encrypt_file_hybrid(
        input_path="test.txt",
        public_key_path="public.pem",
        output_safe_path=bezpieczna_sciezka
    )
    print(f"Sukces! Plik '{bezpieczna_sciezka}' powstał na dysku.")

    print("-" * 50)

    print("4. Uruchamiam deszyfrowanie z przywracaniem rozszerzenia...")
    # Podajemy tylko nazwę bazową, rozszerzenie .txt wczyta się z wnętrza pliku .safe!
    odzyskana_sciezka = decrypt_file_hybrid(
        input_path=bezpieczna_sciezka,
        private_key_path="private.pem",
        password="MojeBezpieczneHaslo123",
        output_base_path="decrypted" # Bez .txt! Program sam to doda.
    )

    print("-" * 50)

    # 5. Weryfikacja wyniku
    if odzyskana_sciezka and os.path.exists(odzyskana_sciezka):
        with open(odzyskana_sciezka, "rb") as f:
            odzyskany_tekst = f.read()

        if odzyskany_tekst == tekst_testowy:
            print("🎉 FINAŁ: Sukces! Plik odzyskany poprawnie, a rozszerzenie zostało przywrócone automatycznie!")
        else:
            print("❌ Coś poszło nie tak. Odzyskany plik różni się od oryginału.")
    else:
        print("❌ Błąd. Nie znaleziono zdeszyfrowanego pliku na dysku.")