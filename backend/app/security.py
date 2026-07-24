"""
宠迹 PawTrack — 密码安全工具

使用 PBKDF2-HMAC-SHA256（Python 标准库，无需额外依赖）。
格式：pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
"""
import hashlib
import hmac
import os
import base64

ITERATIONS = 200_000


def hash_password(password: str) -> str:
    """生成密码哈希"""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def verify_password(password: str, stored: str) -> bool:
    """校验密码是否匹配"""
    try:
        algo, iters, salt_b64, hash_b64 = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iters))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False
