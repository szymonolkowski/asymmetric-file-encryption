from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class FileEncryptor:
    def __init__(self):
        pass

    def generate_aes_key(self):
        return os.urandom(32)

    def encrypt_bytes(self, data, key):
        nonce = os.urandom(12)
        cipher = AESGCM(key)
        return cipher.encrypt(nonce, data, None), nonce

    def decrypt_bytes(self, data, nonce, key):
        try:
            cipher = AESGCM(key)
            return cipher.decrypt(nonce, data, None)
        except ValueError:
            # TODO: Invalid authentication notification
            return None
