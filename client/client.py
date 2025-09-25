import argparse
import socket
import time
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
    # M3: simulação + RTO
    p.add_argument("--loss-every", type=int, help="dropa DATA quando seq % N == offset")
    p.add_argument("--loss-offset", type=int, default=0)
    p.add_argument("--corrupt-every", type=int, help="corrompe payload quando seq % N == offset")
    p.add_argument("--corrupt-offset", type=int, default=0)
    p.add_argument("--rto", type=int, default=300, help="timeout (ms) do retransmissor (GBN)")
    return p.parse_args()

# ==== M3 helpers ====
def should_drop(seq: int, every: int | None, offset: int) -> bool:
    return every is not None and (seq % every) == offset

def should_corrupt(seq: int, every: int | None, offset: int) -> bool:
    return every is not None and (seq % every) == offset

def now_ms() -> int:
    return int(time.time() * 1000)
# ==== end helpers ====

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

    plain = args.msg
    to_send = cipher.encrypt(plain.encode()).decode() if cipher else plain

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

        chunks = chunk4(to_send)
        total = len(chunks)
        next_to_send = 0
        ack_base = 0

        # M3: estado do GBN
        rto = args.rto
        send_time = None
        inflight: set[int] = set()

        # timeout de leitura no socket (segundos)
        s.settimeout(rto / 1000.0)
        recv_buf = ""  # buffer de texto para montar linhas

        while ack_base < total:
            # Enche a janela [ack_base, ack_base+win)
            while next_to_send < min(ack_base + win, total):
                payload = chunks[next_to_send]

                # Simulação determinística
                if should_drop(next_to_send, args.loss_every, args.loss_offset):
                    print(f"[SIM] DROP seq={next_to_send}")
                else:
                    if should_corrupt(next_to_send, args.corrupt_every, args.corrupt_offset):
                        payload_to_send = ("X" + payload[1:]) if payload else "X"
                        print(f"[SIM] CORRUPT seq={next_to_send} '{payload}' -> '{payload_to_send}'")
                    else:
                        payload_to_send = payload

                    pkt = make_data(seq=next_to_send, total=total, payload=payload_to_send)
                    s.sendall((pkt + "\n").encode("utf-8"))
                    print(f"[CLIENT] DATA -> {pkt}")

                inflight.add(next_to_send)
                if send_time is None:
                    send_time = now_ms()
                next_to_send += 1

            # Tenta ler 1+ ACKs; se não vier nada até o RTO, RETX
            try:
                data = s.recv(1024)   # levanta socket.timeout se não chegar nada no período
                if not data:
                    break  # conexão fechada
                recv_buf += data.decode("utf-8")

                # processa todas as linhas completas recebidas
                while "\n" in recv_buf:
                    line, recv_buf = recv_buf.split("\n", 1)
                    if not line:
                        continue
                    nxt = parse_ack(line.strip())  # ACK|next_seq (cumulativo)
                    print(f"[CLIENT] ACK <- {nxt}")
                    if nxt > ack_base:
                        inflight = {q for q in inflight if q >= nxt}
                        ack_base = nxt
                        send_time = now_ms() if ack_base < next_to_send else None

            except socket.timeout:
                # RTO atingido: RETX de toda a janela [ack_base .. next_to_send-1]
                if send_time is not None:
                    print(f"[TIMEOUT] GBN base={ack_base} -> RETX {ack_base}..{next_to_send-1}")
                    send_time = now_ms()
                    for q in range(ack_base, next_to_send):
                        if q in inflight:
                            payload = chunks[q]
                            pkt = make_data(seq=q, total=total, payload=payload)
                            s.sendall((pkt + "\n").encode("utf-8"))
                            print(f"[RETX] DATA -> {pkt}")

        print(f"[CLIENT] done. total={total}, win={win}")

if __name__ == "__main__":
    main()
