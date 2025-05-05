import secrets

secret_key = secrets.token_hex(32)  # 32-byte hex token (64 characters)
print(secret_key)
