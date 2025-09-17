import argparse
import socket
from common.protocol import Hello, Mode

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5001)
    p.add_argument("--modo", choices=["GBN", "SR"], default="GBN")
    p.add_argument("--m", type=int, default=64, help="max_msg_len")
    p.add_argument("--checksum", choices=["CRC16","Adler32","CRC"], default="CRC16")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--ack-mode", choices=["INDIVIDUAL","GROUP"], default="INDIVIDUAL")
    return p.parse_args()

def main():
    args = parse_args()
    hello = Hello(
        modo=Mode(args.modo),
        max_msg_len=args.m,
        checksum=args.checksum,
        timeout_ms=args.timeout,
        ack_mode=args.ack_mode
    ).serialize() + "\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))
        s.sendall(hello.encode("utf-8"))
        resp = s.recv(1024).decode("utf-8").strip()
        print(f"[CLIENT] enviado: {hello.strip()}")
        print(f"[CLIENT] recebido: {resp}")

if __name__ == "__main__":
    main()
