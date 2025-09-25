# RTPy-Reliable-Transport-in-Python
Academic implementation of a reliable transport protocol at the application layer using Python sockets. Features handshake, sliding window (Go-Back-N and Selective Repeat), ACK/NACK, checksum, and loss/error simulation for client-server communication study.

## How to run (Milestone 1)
```bash
# Git Bash — create/activate venv (optional)
python -m venv .venv
source .venv/Scripts/activat# RTPy – Reliable Transport in Python
### Trabalho Acadêmico – 2025.2

## Português

### Descrição
Este projeto implementa, em Python, um protocolo de transporte confiável em nível de aplicação, inspirado em técnicas utilizadas em protocolos reais como TCP. O trabalho foi desenvolvido como parte da disciplina de Redes de Computadores, com entregas progressivas (**milestones**) que adicionam novas funcionalidades.

### Estrutura das entregas (Milestones)

- **Milestone 1 — Handshake (HELLO / HELLO-OK)**
  Implementação do processo inicial de conexão entre cliente e servidor.
  - Cliente envia mensagem `HELLO` com parâmetros (modo, checksum, timeout, ack mode).
  - Servidor responde com `HELLO-OK`, definindo janela inicial.
  - Logs e documentação inicial.

- **Milestone 2 — Troca de mensagens (sem perdas ou erros)**
  Implementação da fragmentação de mensagens em pacotes (`DATA`) e confirmação por ACKs.
  - Fragmentação em blocos de 4 caracteres.
  - Envio sequencial e recebimento cumulativo.
  - Integridade checada por algoritmos de checksum (CRC16, Adler32, CRC).
  - Implementação opcional de criptografia simétrica (Fernet).

- **Milestone 3 — Simulação de perdas, erros e retransmissão (Go-Back-N)**
  Implementação de mecanismos para lidar com canais não confiáveis.
  - Simulação de perda e corrupção de pacotes com parâmetros configuráveis.
  - Retransmissão de pacotes com base em timeout (Go-Back-N).
  - Logs detalhados para depuração e validação experimental.

### Tecnologias utilizadas
- Python 3.13+
- Sockets TCP
- `cryptography` (Fernet)
- `zlib` (Adler32)
- `crcmod` (CRC16)

### Como executar
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie o servidor:
   ```bash
   python -m server.server
   ```
3. Execute o cliente:
   ```bash
   python -m client.client --msg "Mensagem de teste"
   ```

### Execução com criptografia
1. Gere uma chave Fernet:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
2. Rode o cliente com criptografia ativada:
   ```bash
   python -m client.client --msg "segredo ultra confidencial" --crypto ON --key <sua_chave>
   ```

---

## English

### Description
This project implements, in Python, a reliable transport protocol at the application layer, inspired by mechanisms used in real protocols such as TCP. The work was developed as part of the Computer Networks course, with progressive milestones adding new functionalities.

### Milestones

- **Milestone 1 — Handshake (HELLO / HELLO-OK)**
  Initial connection establishment between client and server.
  - Client sends a `HELLO` message with parameters (mode, checksum, timeout, ack mode).
  - Server replies with `HELLO-OK`, defining the initial window.
  - Logging and initial documentation.

- **Milestone 2 — Message exchange (no errors or losses)**
  Implementation of message fragmentation into `DATA` packets and acknowledgment with ACKs.
  - Messages split into blocks of 4 characters.
  - Sequential sending and cumulative ACK reception.
  - Integrity checking via checksum algorithms (CRC16, Adler32, CRC).
  - Optional symmetric encryption (Fernet).

- **Milestone 3 — Loss, error simulation and retransmission (Go-Back-N)**
  Implementation of mechanisms to handle unreliable channels.
  - Packet loss and corruption simulation with configurable parameters.
  - Packet retransmission based on timeout (Go-Back-N).
  - Detailed logs for debugging and experimental validation.

### Technologies
- Python 3.13+
- TCP sockets
- `cryptography` (Fernet)
- `zlib` (Adler32)
- `crcmod` (CRC16)

### How to run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python -m server.server
   ```
3. Run the client:
   ```bash
   python -m client.client --msg "Test message"
   ```

### Running with encryption
1. Generate a Fernet key:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
2. Run the client with encryption enabled:
   ```bash
   python -m client.client --msg "ultra confidential secret" --crypto ON --key <your_key>
   ```
e

pip install -r requirements.txt

# Terminal 1
 python -m server.server

# Terminal 2
python -m client.client --modo GBN --m 64 --checksum CRC16 --timeout 300 --ack-mode INDIVIDUAL

