"""
add_credential.py
Menghasilkan hash password bcrypt yang kompatibel dengan streamlit-authenticator.
Cara paling andal: pakai bcrypt langsung, tanpa bergantung pada API Hasher.
"""

import bcrypt

password = "password"   # ← ganti dengan password asli kamu

hashed = bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

print(hashed)