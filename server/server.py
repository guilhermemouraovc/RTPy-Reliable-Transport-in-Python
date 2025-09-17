import socket
from common.protocol import Hello, HelloOk
from common.logging_utils import setup_logger

HOST = "127.0.0.1"
PORT = 5001

logger = setup_logger("server", logfile="logs/server.log")

def validate_hello(h: Hello) -> tuple[bool, str]:
    if h.modo not in ("GBN", "SR"):
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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        logger.info(f"Servidor escutando em {HOST}:{PORT}")

        conn, addr = s.accept()
        with conn:
            logger.info(f"Conexão de {addr}")
            data = conn.recv(1024)
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

if __name__ == "__main__":
    main()