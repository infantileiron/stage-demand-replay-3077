import base64
import hashlib
import hmac
import json
import os
import time
from src.config.settings import settings

def password_hash(password, salt=None):
    salt = salt or os.urandom(16).hex()
    value = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
    return salt + ":" + value

def password_matches(password, digest):
    return hmac.compare_digest(password_hash(password, digest.split(":")[0]), digest)

def b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

def token_for(user):
    header = b64(b'{"alg":"HS256","typ":"JWT"}')
    payload = b64(json.dumps({"sub": str(user["id"]), "exp": int(time.time())+3600}).encode())
    unsigned = header + "." + payload
    return unsigned + "." + b64(hmac.new(settings.jwt_secret.encode(), unsigned.encode(), hashlib.sha256).digest())

def decode_token(token):
    header, payload, signature = token.split(".")
    unsigned = header + "." + payload
    expected = b64(hmac.new(settings.jwt_secret.encode(), unsigned.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(signature, expected): raise ValueError("无效签名")
    meta = json.loads(base64.urlsafe_b64decode(header + "="*(-len(header)%4)))
    data = json.loads(base64.urlsafe_b64decode(payload + "="*(-len(payload)%4)))
    if meta.get("alg") != "HS256" or data["exp"] <= time.time(): raise ValueError("凭证已过期")
    return int(data["sub"])
