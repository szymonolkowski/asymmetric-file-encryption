from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

class RSAHandler:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def key_generator(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()

    def export_private_key(self, filename: str = None, password: str = None):
        if password:
            encryption = serialization.BestAvailableEncryption(password.encode('utf-8'))
        else:
            encryption = serialization.NoEncryption()

        key_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=encryption
        )

        if filename:
            with open(filename, "wb") as f:
                f.write(key_bytes)
            return None

        return key_bytes

    def export_public_key(self, filename: str = None):
        key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        if filename:
            with open(filename, "wb") as f:
                f.write(key_bytes)
                return None

        return key_bytes

    def load_private_key(self, filename: str, password: str = None):
        with open(filename, "rb") as f:
            password_bytes = password.encode('utf-8') if password else None
            self.private_key = serialization.load_pem_private_key(f.read(), password_bytes)
            self.public_key = self.private_key.public_key()
            return None

    def load_public_key(self, filename: str):
        with open(filename, "rb") as f:
            self.public_key = serialization.load_pem_public_key(f.read())
            return None

    def encrypt(self, data: bytes):
        return self.public_key.encrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

    def decrypt(self, data: bytes):
        return self.private_key.decrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))