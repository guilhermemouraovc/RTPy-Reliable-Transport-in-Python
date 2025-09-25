import argparse
import socket
from cryptography.fernet import Fernet
from common.protocol import Hello, HelloOk, Mode
from common.protocol import parse_data, make_ack
from common.logging_utils import setup_logger

HOST = "127.0.0.1"
PORT = 5001

logger = setup_logger("server", logfile="logs/server.log")

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default=HOST)
    p.add_argument("--port", type=int, default=PORT)
    p.add_argument("--key", help="chave Fernet base64 (necessária se cliente usar crypto=ON)")
    p.add_argument("--key-file", help="arquivo contendo a chave Fernet base64")
    return p.parse_args()

def load_key(args) -> bytes | None:
    if args.key_file:
        with open(args.key_file, "rb") as f:
            return f.read().strip()
    if args.key:
        return args.key.encode()
    return None

def validate_hello(h: Hello) -> tuple[bool, str]:
    if h.modo not in (Mode.GBN, Mode.SR):
        return False, "modo inválido"
    if h.max_msg_len < 30:
        return False, "max_msg_len deve ser >= 30"
    if h.checksum not in ("CRC16", "Adler32", "CRC"):
        return False, "checksum inválido"
    if h.timeout_ms <= 0:
        return False, "timeout_ms deve ser > 0"
    if h.ack_mode not in ("INDIVIDUAL", "GROUP"):
        return False, "ack_mode inválido"
    if h.crypto not in ("ON", "OFF"):
        return False, "crypto inválido"
    return True, "ok"

def main():
    args = parse_args()
    key = load_key(args)
    cipher = Fernet(key) if key else None

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((args.host, args.port))
        s.listen(1)
        logger.info(f"Servidor escutando em {args.host}:{args.port}")

        conn, addr = s.accept()
        with conn:
            logger.info(f"Conexão de {addr}")

            # HELLO
            data = conn.recv(1024)
            if not data:
                return
            line = data.decode("utf-8").strip()
            logger.info(f"Recebido: {line}")

            try:
                h = Hello.parse(line)
                ok, msg = validate_hello(h)
                if not ok:
                    logger.info(f"HELLO inválido: {msg}")
                    conn.sendall(f"ERR {msg}\n".encode("utf-8"))
                    return
            except Exception as e:
                logger.exception("Falha ao parsear HELLO")
                conn.sendall(f"ERR parse HELLO: {e}\n".encode("utf-8"))
                return

            # exige chave se crypto=ON
            if h.crypto == "ON" and not cipher:
                logger.error("Cliente pediu crypto=ON, mas o servidor não recebeu --key/--key-file")
                conn.sendall(b"ERR crypto on but no key\n")
                return

            hello_ok = HelloOk(win_init=5, win_min=1, win_max=5).serialize() + "\n"
            logger.info(f"Enviando: {hello_ok.strip()}")
            conn.sendall(hello_ok.encode("utf-8"))

            # Loop DATA/ACK
            buf = {}
            expected = 0
            total = None

            try:
                while True:
                    raw = conn.recv(4096)
                    if not raw:
                        logger.info("Cliente fechou a conexão.")
                        break

                    for l in raw.decode("utf-8").splitlines():
                        if not l:
                            continue
                        try:
                            pkt = parse_data(l)  # já valida checksum
                        except Exception as e:
                            logger.info(f"Ignorando/Erro DATA: {e} linha={l}")
                            continue

                        seq = pkt["seq"]
                        total = pkt["total"] if total is None else total
                        buf[seq] = pkt["payload"]

                        while expected in buf:
                            expected += 1
                        ack = make_ack(expected) + "\n"
                        conn.sendall(ack.encode("utf-8"))
                        logger.info(f"ACK -> {ack.strip()}")

                        if total is not None and expected >= total:
                            joined = "".join(buf[i] for i in range(total))
                            if h.crypto == "ON":
                                # joined é o ciphertext base64
                                plain = cipher.decrypt(joined.encode("utf-8")).decode("utf-8")
                                logger.info(f"Mensagem completa (decifrada): {plain}")
                            else:
                                logger.info(f"Mensagem completa ({total} pacotes): {joined}")
                            return
            except Exception as e:
                logger.exception(f"Erro no loop de DATA: {e}")
                try:
                    conn.sendall(f"ERR {e}\n".encode("utf-8"))
                except Exception:
                    pass

if __name__ == "__main__":
    main()
