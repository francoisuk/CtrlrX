# Encodage base64 propre à JUCE (MemoryBlock::toBase64Encoding / fromBase64Encoding)
CH = ".ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+"
def encode(data: bytes) -> str:
    nbits = len(data) * 8
    n = int.from_bytes(data, 'little')
    out = [CH[(n >> b) & 63] for b in range(0, nbits, 6)]
    return "%d.%s" % (len(data), "".join(out))
def decode(s: str) -> bytes:
    size, body = s.split('.', 1)
    size = int(size); n = 0
    for i, c in enumerate(body):
        n |= CH.index(c) << (6 * i)
    return (n & ((1 << (size * 8)) - 1)).to_bytes(size, 'little')
