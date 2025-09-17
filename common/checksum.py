import crcmod

# CRC-16/Modbus: simples e suficiente
_crc16 = crcmod.predefined.Crc('modbus')

def crc16(data: bytes) -> str:
    c = _crc16.new()
    c.update(data)
    return f"{c.crcValue:04X}"