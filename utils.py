import base64
import bz2
import codecs
import gzip
import lzma
import marshal
import zlib


def xor_data(data, key):
    key = key.encode()
    return bytes([
        b ^ key[i % len(key)]
        for i, b in enumerate(data)
    ])


def decode_base64(data):
    return base64.b64decode(data)


def decode_rot13(text):
    return codecs.decode(text, "rot_13")


def decode_hex(hex_string):
    return bytes.fromhex(hex_string)


def decompress_lzma(data):
    return lzma.decompress(data)


def decompress_gzip(data):
    return gzip.decompress(data)


def decompress_bz2(data):
    return bz2.decompress(data)


def decompress_zlib(data):
    return zlib.decompress(data)


def iterated_base64_decode(data, iterations=5):
    result = data
    for _ in range(iterations):
        result = base64.b64decode(result)
    return result


def reverse_bytes(data):
    return data[::-1]


def assemble_payload(*parts):
    return "".join(parts)


def is_debugger_attached():
    import sys
    if hasattr(sys, "gettrace"):
        return sys.gettrace() is not None
    return False


def rebuild_payload(payload_str, xor_key):
    data = decode_base64(payload_str)
    data = decode_rot13(data.decode()).encode()
    data = decode_hex(data.decode())
    data = xor_data(data, xor_key)
    data = reverse_bytes(data)
    data = iterated_base64_decode(data, iterations=5)
    data = decompress_lzma(data)
    data = decompress_gzip(data)
    data = decompress_bz2(data)
    data = decompress_zlib(data)
    return marshal.loads(data)
