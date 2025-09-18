# RTPy-Reliable-Transport-in-Python
Academic implementation of a reliable transport protocol at the application layer using Python sockets. Features handshake, sliding window (Go-Back-N and Selective Repeat), ACK/NACK, checksum, and loss/error simulation for client-server communication study.

## How to run (Milestone 1)
```bash
# Git Bash — create/activate venv (optional)
python -m venv .venv
source .venv/Scripts/activate

pip install -r requirements.txt

# Terminal 1
 python -m server.server

# Terminal 2
python -m client.client --modo GBN --m 64 --checksum CRC16 --timeout 300 --ack-mode INDIVIDUAL

