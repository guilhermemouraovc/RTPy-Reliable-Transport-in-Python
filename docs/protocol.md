# Protocolo — Handshake (Marco 1)

**Cliente → Servidor**
HELLO modo=GBN|SR max_msg_len=M checksum=CRC16|Adler32|CRC timeout_ms=NNN ack_mode=INDIVIDUAL|GROUP
**Servidor → Cliente**
HELLO-OK win_init=5 win_min=1 win_max=5
Validações:
- `max_msg_len ≥ 30`
- `timeout_ms > 0`
- campos com valores válidos