from pathlib import Path

class KeyManager:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent.parent

        self.public_dir = self.project_root / "keys" / "public"
        self.private_dir = self.project_root / "keys" / "private"

        self.public_dir.mkdir(parents=True, exist_ok=True)
        self.private_dir.mkdir(parents=True, exist_ok=True)

    def list_public_keys(self) -> list:
        """Zwraca listę nazw plików kluczy publicznych (.pem) dostępnych w systemie"""
        return [f.name for f in self.public_dir.glob("*.pem")]

    def list_private_keys(self) -> list:
        """Zwraca listę nazw plików kluczy prywatnych (.pem) dostępnych w systemie"""
        return [f.name for f in self.private_dir.glob("*.pem")]

    def get_public_key_path(self, filename: str) -> str:
        """Zwraca pełną ścieżkę jako tekst do wybranego klucza publicznego"""
        return str(self.public_dir / filename)

    def get_private_key_path(self, filename: str) -> str:
        """Zwraca pełną ścieżkę jako tekst do wybranego klucza prywatnego"""
        return str(self.private_dir / filename)


if __name__ == "__main__":
    # Szybki test na sucho w terminalu
    km = KeyManager()
    print("Folder kluczy publicznych:", km.public_dir)
    print("Dostępne klucze publiczne:", km.list_public_keys())
    print("Dostępne klucze prywatne:", km.list_private_keys())