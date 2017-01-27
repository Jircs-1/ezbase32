#!/usr/bin/python3

def bech32_polymod(values):
  GEN = [0x53A0C81, 0x8F09902, 0x11E13204, 0x21526128, 0x12346650]
  chk = 1
  for v in values:
    b = (chk >> 25)
    chk = (chk & 0x1FFFFFF) << 5 ^ v
    for i in range(5):
      chk ^= GEN[i] if ((b >> i) & 1) else 0
  return chk

def bech32_prefix_expand(s):
  return [ord(x) >> 5 for x in s] + [0] + [ord(x) & 31 for x in s] + [0]

def bech32_verify_checksum(prefix, data):
  return bech32_polymod(bech32_prefix_expand(prefix) + data) == 1

def bech32_create_checksum(prefix, data):
  values = bech32_prefix_expand(prefix) + data
  polymod = bech32_polymod(values + [0,0,0,0,0,0]) ^ 1
  return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

CHARSET="0123456789bcdefghijkmnpqrstvwxyz"

def bech32_encode(prefix, data):
  print("checksum: %r" % bech32_create_checksum(prefix, data))
  data += bech32_create_checksum(prefix, data)
  return prefix + '-' + ''.join([CHARSET[d] for d in data])

def bech32_decode(s):
  s = s.lower()
  pos = s.rfind('-')
  if pos < 1 or pos > 40 or pos + 7 > len(s) or pos + 90 < len(s):
    return (None, None)
  if not all(x in CHARSET for x in s[pos+1:]):
    return (None, None)
  prefix = s[:pos]
  data = [CHARSET.find(x) for x in s[pos+1:]]
  if not bech32_verify_checksum(prefix, data):
    return (None, None)
  return (prefix, data[:-6])

def convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    for d in data:
        if d < 0 or (d >> frombits):
            return None
        acc = (acc << frombits) | d
        bits += frombits
        while (bits >= tobits):
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if (pad):
        if (bits):
            ret.append((acc << (tobits - bits)) & maxv)
    elif (acc << (tobits - bits)) & maxv:
        return None
    return ret

def segwit_addr_encode(witver, witprog):
  assert (witver >= 0 and witver <= 16)
  return bech32_encode("bc", [witver] + convertbits(witprog, 8, 5))

def segwit_addr_decode(addr):
  prefix, data = bech32_decode(addr)
  if prefix != "bc":
    return None
  decoded = convertbits(data[1:], 5, 8, False)
  if decoded is None or len(decoded) < 2 or len(decoded) > 40:
    return None
  if (data[0] > 16):
    return None
  if (data[0] == 0 and len(decoded) != 20 and len(decoded) != 32):
    return None
  return (data[0], decoded)

DATA = convertbits([0x7, 0x5, 0x1, 0xe, 0x7, 0x6, 0xe, 0x8, 0x1, 0x9, 0x9, 0x1, 0x9, 0x6, 0xd, 0x4, 0x5, 0x4, 0x9, 0x4, 0x1, 0xc, 0x4, 0x5, 0xd, 0x1, 0xb, 0x3, 0xa, 0x3, 0x2, 0x3, 0xf, 0x1, 0x4, 0x3, 0x3, 0xb, 0xd, 0x6], 4, 8)

ENC = segwit_addr_encode(0, DATA)
DEC = segwit_addr_decode(ENC)

print("DATA: %r" % DATA)
print("ENC: %r" % ENC)
print("DEC: %r" % (DEC,))

#DATA=[10,11,32,0] + 
#
#print bech32_encode(DATA)
#
#for l in range(100):
#  enc = bech32_encode([0 for i in range(l)])
#  dec = bech32_decode(enc)
#  print("enc=%s dec=%r" % (enc, dec))