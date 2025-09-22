import crcmod
import zlib

# CRC-16/Modbus: simples e suficiente
_crc16 = crcmod.predefined.Crc('modbus')

def crc16(data: bytes) -> str:
    c = _crc16.new()
    c.update(data)
    return f"{c.crcValue:04X}"

def adler16(data: bytes) -> str:
    """Adler32 reduzido a 16 bits, em hex 4 dígitos"""
    return f"{zlib.adler32(data) & 0xFFFF:04X}"