import os

def generate_aes_256_key():
  """Generiert einen zufälligen 256-Bit (32 Bytes) Schlüssel für AES."""
  return os.urandom(256)

# Generiere den Schlüssel
secret_key = generate_aes_256_key()

# Gib den Schlüssel als Hex-String aus (optional, zur Anzeige)
print(f"Dein geheimer AES-256 Schlüssel (Hex): {secret_key.hex()}")
print(f"Länge des Schlüssels in Bytes: {len(secret_key)}")
print(f"Länge des Schlüssels in Bits: {len(secret_key) * 8}")

# Wichtig: Behandle diesen Schlüssel streng vertraulich!
# Speichere ihn sicher und teile ihn nicht.