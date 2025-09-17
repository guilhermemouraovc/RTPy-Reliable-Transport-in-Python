from dataclasses import dataclass
from enum import Enum
from typing import Dict

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

    def serialize(self) -> str:
        return (
            "HELLO "
            f"modo={self.modo} "
            f"max_msg_len={self.max_msg_len} "
            f"checksum={self.checksum} "
            f"timeout_ms={self.timeout_ms} "
            f"ack_mode={self.ack_mode}"
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