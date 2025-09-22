import argparse
import socket
from cryptography.fernet import Fernet
from common.protocol import Hello, HelloOk, Mode
from common.protocol import make_data, parse_ack

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5001)
    p.add_argument("--modo", choices=["GBN", "SR"], default="GBN")
    p.add_argument("--m", type=int, default=64, help="max_msg_len")
    p.add_argument("--checksum", choices=["CRC16","Adler32","CRC"], default="CRC16")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--ack-mode", choices=["INDIVIDUAL","GROUP"], default="INDIVIDUAL")
    p.add_argument("--msg", default="HelloWorldFromRTPy!", help="mensagem a enviar")
    p.add_argument("--crypto", choices=["OFF","ON"], default="OFF")
    p.add_argument("--key", help="chave Fernet base64 (mesma do servidor)")
    p.add_argument("--key-file", help="arquivo contendo a chave Fernet base64")
    return p.parse_args()

def chunk4(s: str) -> list[str]:
    return [s[i:i+4] for i in range(0, len(s), 4)]

def load_key(args) -> bytes | None:
    if args.crypto == "OFF":
        return None
    if args.key_file:
        with open(args.key_file, "rb") as f:
            return f.read().strip()
    if args.key:
        return args.key.encode()
    raise SystemExit("ERR: --crypto ON requer --key ou --key-file")

def main():
    args = parse_args()
    key = load_key(args)
    cipher = Fernet(key) if key else None

    # mensagem em claro
    plain = args.msg

    # se crypto ON: cifrar a mensagem inteira, vira base64 (str)
    if cipher:
        ciphertext = cipher.encrypt(plain.encode("utf-8")).decode("utf-8")
        to_send = ciphertext
    else:
        to_send = plain

    # Handshake com flag de crypto
    hello = Hello(
        modo=Mode(args.modo),
        max_msg_len=args.m,
        checksum=args.checksum,
        timeout_ms=args.timeout,
        ack_mode=args.ack_mode,
        crypto=args.crypto,
    ).serialize() + "\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))
        s.sendall(hello.encode("utf-8"))
        resp = s.recv(1024).decode("utf-8").strip()
        print(f"[CLIENT] enviado: {hello.strip()}")
        print(f"[CLIENT] recebido: {resp}")
        hok = HelloOk.parse(resp)
        win = hok.win_init

        # fragmentar a string a transmitir (plain ou ciphertext) em blocos de 4
        chunks = chunk4(to_send)
        total = len(chunks)
        next_to_send = 0
        ack_base = 0

        file_r = s.makefile("r", encoding="utf-8")

        while ack_base < total:
            while next_to_send < min(ack_base + win, total):
                pkt = make_data(seq=next_to_send, total=total, payload=chunks[next_to_send])
                s.sendall((pkt + "\n").encode("utf-8"))
                print(f"[CLIENT] DATA -> {pkt}")
                next_to_send += 1

            line = file_r.readline()
            if not line:
                break
            nxt = parse_ack(line.strip())
            print(f"[CLIENT] ACK <- {nxt}")
            if nxt > ack_base:
                ack_base = nxt

        print(f"[CLIENT] done. total={total}, win={win}")

if __name__ == "__main__":
    main()
