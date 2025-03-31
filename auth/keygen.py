import json
import secrets

def keygen(filename: str, size: int, bytes: int) -> None:
    with open(filename, 'w') as file:
        tokens = [secrets.token_urlsafe(bytes) for _ in range(size)]
        json.dump([str(token) for token in tokens], file)

keygen("tokens.json", 5000, 32)