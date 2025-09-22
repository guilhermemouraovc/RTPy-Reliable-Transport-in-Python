import argparse
import socket
from common.protocol import Hello, HelloOk, Mode
from common.protocol import make_data, parse_ack

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5001)
    p.add_argument("--modo", choices=["GBN", "SR"], default="GBN")
    p.add_argument("--m", type=int, default=64, help="max_msg_len")
    p.add_argument("--checksum", choices=["CRC16", "Adler32", "CRC"], default="CRC16")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--ack-mode", choices=["INDIVIDUAL", "GROUP"], default="INDIVIDUAL")
    p.add_argument("--msg", default="HelloWorldFromRTPy!", help="mensagem a enviar")
    return p.parse_args()

def chunk4(s: str) -> list[str]:
    return [s[i:i+4] for i in range(0, len(s), 4)]

def main():
    args = parse_args()

    # Handshake
    hello = Hello(
        modo=Mode(args.modo),
        max_msg_len=args.m,
        checksum=args.checksum,
        timeout_ms=args.timeout,
        ack_mode=args.ack_mode,
    ).serialize() + "\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))
        s.sendall(hello.encode("utf-8"))
        resp = s.recv(1024).decode("utf-8").strip()
        print(f"[CLIENT] enviado: {hello.strip()}")
        print(f"[CLIENT] recebido: {resp}")

        # Janela inicial vinda do servidor
        hok = HelloOk.parse(resp)
        win = hok.win_init

        # ===== Milestone 2: enviar DATA com janela, canal perfeito =====
        chunks = chunk4(args.msg)
        total = len(chunks)
        next_to_send = 0
        ack_base = 0

        file_r = s.makefile("r", encoding="utf-8")  # ler ACK por linha

        while ack_base < total:
            # enche a janela [ack_base, ack_base+win)
            while next_to_send < min(ack_base + win, total):
                pkt = make_data(seq=next_to_send, total=total, payload=chunks[next_to_send])
                s.sendall((pkt + "\n").encode("utf-8"))
                print(f"[CLIENT] DATA -> {pkt}")
                next_to_send += 1

            # lê ACK cumulativo
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
