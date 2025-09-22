import socket
from common.protocol import Hello, HelloOk, Mode
from common.logging_utils import setup_logger

HOST = "127.0.0.1"
PORT = 5001

logger = setup_logger("server", logfile="logs/server.log")

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
    return True, "ok"

def main():
    from common.protocol import parse_data, make_ack  # M2

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        logger.info(f"Servidor escutando em {HOST}:{PORT}")

        conn, addr = s.accept()
        with conn:
            logger.info(f"Conexão de {addr}")

            # ===== Handshake =====
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

            hello_ok = HelloOk(win_init=5, win_min=1, win_max=5).serialize() + "\n"
            logger.info(f"Enviando: {hello_ok.strip()}")
            conn.sendall(hello_ok.encode("utf-8"))

            # ===== Milestone 2: receber DATA e enviar ACK (canal perfeito) =====
            buf = {}
            expected = 0
            total = None

            try:
                while True:
                    raw = conn.recv(4096)
                    if not raw:
                        logger.info("Cliente fechou a conexão.")
                        break

                    for line in raw.decode("utf-8").splitlines():
                        if not line:
                            continue
                        try:
                            pkt = parse_data(line)
                        except Exception:
                            logger.info(f"Ignorando linha não-DATA: {line}")
                            continue

                        seq = pkt["seq"]
                        total = pkt["total"] if total is None else total
                        buf[seq] = pkt["payload"]

                        # calcula próximo esperado (ACK cumulativo)
                        while expected in buf:
                            expected += 1
                        ack = make_ack(expected) + "\n"
                        conn.sendall(ack.encode("utf-8"))
                        logger.info(f"ACK -> {ack.strip()}")

                        if total is not None and expected >= total:
                            msg = "".join(buf[i] for i in range(total))
                            logger.info(f"Mensagem completa ({total} pacotes): {msg}")
                            return
            except Exception as e:
                logger.exception(f"Erro no loop de DATA: {e}")
                try:
                    conn.sendall(f"ERR {e}\n".encode("utf-8"))
                except Exception:
                    pass

if __name__ == "__main__":
    main()
