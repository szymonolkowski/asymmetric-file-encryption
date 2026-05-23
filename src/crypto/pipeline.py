from .asymmetric import RSAHandler
from .symmetric import FileEncryptor


def encrypt_file_hybrid(input_path: str, public_key_path: str, output_safe_path: str):
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
    with open(output_safe_path, 'wb') as output_file:
        output_file.write(nonce)
        output_file.write(encrypted_aes_key)
        output_file.write(ciphertext)
    return True

def decrypt_file_hybrid(input_path: str, private_key_path: str, password : str, output_path: str):
    file_encryptor = FileEncryptor()
    rsa_handler = RSAHandler()
    with open(input_path, 'rb') as input_file:
        encrypted_safe_data = input_file.read()

    nonce = encrypted_safe_data[:12]
    encrypted_aes_key = encrypted_safe_data[12:12+256]
    encrypted_data = encrypted_safe_data[12+256:]

    rsa_handler.load_private_key(private_key_path, password)

    aes_key = rsa_handler.decrypt(encrypted_aes_key)

    decrypted_data = file_encryptor.decrypt_bytes(encrypted_data,nonce,aes_key)

    if decrypted_data:
        with open(output_path, 'wb') as output_file:
            output_file.write(decrypted_data)
        print("Decryption successful.")
        return True
    else:
        print("Decryption failed.")
        return False


if __name__ == "__main__":
    tekst_testowy = "To jest ściśle tajna wiadomość inżynierska projektu FastSec Hub!".encode('utf-8')

    with open("test.txt", "wb") as f:
        f.write(tekst_testowy)
    print("1. Utworzono plik testowy 'test.txt'.")

    # 2. Generujemy parę kluczy RSA na potrzeby testu
    handler = RSAHandler()
    handler.key_generator()

    # Eksportujemy klucze do plików (używamy hasła do klucza prywatnego)
    handler.export_public_key("public.pem")
    handler.export_private_key("private.pem", password="MojeBezpieczneHaslo123")
    print("2. Wygenerowano i zapisano klucze 'public.pem' oraz 'private.pem'.")

    print("-" * 50)

    # 3. TEST SZYFROWANIA HYBRYDOWEGO
    print("3. Uruchamiam szyfrowanie...")
    encrypt_file_hybrid(
        input_path="test.txt",
        public_key_path="public.pem",
        output_safe_path="encrypted.safe"  # Zmień rozszerzenie na Wasze projektowe .safe
    )
    print("Sukces! Plik 'encrypted.safe' powstał na dysku.")

    print("-" * 50)

    # 4. TEST DESZYFROWANIA HYBRYDOWEGO
    print("4. Uruchamiam deszyfrowanie...")
    decrypt_file_hybrid(
        input_path="encrypted.safe",
        private_key_path="private.pem",
        password="MojeBezpieczneHaslo123",
        output_path="decrypted.txt"
    )

    print("-" * 50)

    # 5. Weryfikacja wyniku
    with open("decrypted.txt", "rb") as f:
        odzyskany_tekst = f.read()

    if odzyskany_tekst == tekst_testowy:
        print("🎉 FINAŁ: Sukces! Plik odzyskany w 100% poprawnie. Logika krypto działa!")
    else:
        print("❌ Coś poszło nie tak. Odzyskany plik różni się od oryginału.")