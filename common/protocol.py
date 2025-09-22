from dataclasses import dataclass
from enum import Enum
from typing import Dict
from common.checksum import adler16

class Mode(str, Enum):
    GBN = "GBN"
    SR = "SR"

@dataclass
class Hello:
    modo: Mode
    max_msg_len: int
    checksum: str
    timeout_ms: int
    ack_mode: str  # INDIVIDUAL | GROUP
    crypto: str = "OFF"  # ON | OFF

    def serialize(self) -> str:
        return (
            "HELLO "
            f"modo={self.modo.value} "
            f"max_msg_len={self.max_msg_len} "
            f"checksum={self.checksum} "
            f"timeout_ms={self.timeout_ms} "
            f"ack_mode={self.ack_mode}"
            f" ack_mode={self.ack_mode} "
            f"crypto={self.crypto}"
        )

    @staticmethod
    def parse(line: str) -> "Hello":
        if not line.startswith("HELLO "):
            raise ValueError("Mensagem não é HELLO")
        parts = line[len("HELLO "):].strip().split()
        kv: Dict[str, str] = {}
        for p in parts:
            k, v = p.split("=", 1)
            kv[k] = v
        return Hello(
            modo=Mode(kv["modo"]),
            max_msg_len=int(kv["max_msg_len"]),
            checksum=kv["checksum"],
            timeout_ms=int(kv["timeout_ms"]),
            ack_mode=kv["ack_mode"],
            crypto=kv.get("crypto", "OFF"),
        )

@dataclass
class HelloOk:
    win_init: int
    win_min: int
    win_max: int

    def serialize(self) -> str:
        return (
            "HELLO-OK "
            f"win_init={self.win_init} "
            f"win_min={self.win_min} "
            f"win_max={self.win_max}"
        )

    @staticmethod
    def parse(line: str) -> "HelloOk":
        if not line.startswith("HELLO-OK "):
            raise ValueError("Mensagem não é HELLO-OK")
        parts = line[len("HELLO-OK "):].strip().split()
        kv: Dict[str, str] = {}
        for p in parts:
            k, v = p.split("=", 1)
            kv[k] = v
        return HelloOk(
            win_init=int(kv["win_init"]),
            win_min=int(kv["win_min"]),
            win_max=int(kv["win_max"]),
        )
# --- Milestone 2: DATA / ACK ---

def make_data(seq: int, total: int, payload: str) -> str:
    # payload máximo de 4 chars
    assert 0 <= len(payload) <= 4
    csum = adler16(payload.encode("utf-8"))      # checksum do payload (hex 4 dígitos)
    return f"DATA|{seq}|{len(payload)}|{total}|{payload}|{csum}"

def parse_data(line: str) -> dict:
    if not line.startswith("DATA|"):
        raise ValueError("not DATA")
    parts = line.split("|")
    if len(parts) != 6:
        raise ValueError("bad DATA format")
    _, s_seq, s_len, s_total, payload, s_csum = parts
    seq = int(s_seq)
    ln = int(s_len)
    total = int(s_total)

    if ln != len(payload):
        raise ValueError("len mismatch")

    # valida integridade
    if adler16(payload.encode("utf-8")) != s_csum.upper():
        raise ValueError("checksum error")

    return {"seq": seq, "len": ln, "total": total, "payload": payload}

def make_ack(next_seq: int) -> str:
    return f"ACK|{next_seq}"

def parse_ack(line: str) -> int:
    if not line.startswith("ACK|"):
        raise ValueError("not ACK")
    return int(line.split("|", 1)[1])