def bit_to_byte(bits):
  return bits/8.


def bytes_to_kb(bytes):
  return bytes/1024.

 
def kb_to_mb(kb):
  return kb/1024.

 
def mb_to_gb(mb):
   return mb/1024.


def bytes_to_mb(bytes):
  return kb_to_mb(bytes_to_kb(bytes))


def bits_to_mb(bits):
   return kb_to_mb(bytes_to_kb(bit_to_byte(bits)))


def bits_to_gb(bits):
    return mb_to_gb(bits_to_mb(bits))