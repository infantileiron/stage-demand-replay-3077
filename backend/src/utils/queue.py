"""Redis RESP2 queue, no in-process substitute in production."""
import socket
from src.config.settings import settings

def _read(stream):
    line = stream.readline()
    if not line: raise ConnectionError("Redis connection closed")
    kind, value = line[:1], line[1:-2]
    if kind == b"-": raise RuntimeError(value.decode())
    if kind == b"+": return value.decode()
    if kind == b":": return int(value)
    if kind == b"$":
        size = int(value)
        if size < 0: return None
        raw = stream.read(size); stream.read(2)
        return raw.decode()
    if kind == b"*":
        size = int(value)
        return None if size < 0 else [_read(stream) for _ in range(size)]
    raise RuntimeError("Invalid Redis response")

def command(*parts):
    raw = [str(p).encode() for p in parts]
    request = b"*"+str(len(raw)).encode()+b"\r\n"+b"".join(b"$"+str(len(x)).encode()+b"\r\n"+x+b"\r\n" for x in raw)
    with socket.create_connection((settings.redis_host, settings.redis_port), timeout=5) as sock:
        sock.sendall(request)
        return _read(sock.makefile("rb"))

def enqueue(run_id): return command("LPUSH", "stage-demand:runs", run_id)
def dequeue():
    result = command("BRPOP", "stage-demand:runs", 2)
    return int(result[1]) if result else None

def ping(): return command("PING") == "PONG"
