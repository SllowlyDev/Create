import base64
import bz2
import gzip
import lzma
import marshal
import zlib
from unittest.mock import patch

import pytest

from utils import (
    assemble_payload,
    decode_base64,
    decode_hex,
    decode_rot13,
    decompress_bz2,
    decompress_gzip,
    decompress_lzma,
    decompress_zlib,
    is_debugger_attached,
    iterated_base64_decode,
    rebuild_payload,
    reverse_bytes,
    xor_data,
)


# ── xor_data ──────────────────────────────────────────────────────────────────

class TestXorData:
    def test_basic_xor(self):
        data = b"\x00\x01\x02\x03"
        key = "A"
        result = xor_data(data, key)
        expected = bytes([0 ^ ord("A"), 1 ^ ord("A"), 2 ^ ord("A"), 3 ^ ord("A")])
        assert result == expected

    def test_roundtrip(self):
        original = b"Hello, World!"
        key = "secret"
        encrypted = xor_data(original, key)
        decrypted = xor_data(encrypted, key)
        assert decrypted == original

    def test_empty_data(self):
        assert xor_data(b"", "key") == b""

    def test_key_cycling(self):
        data = b"\x00\x00\x00\x00\x00\x00"
        key = "AB"
        result = xor_data(data, key)
        assert result == bytes([ord("A"), ord("B")] * 3)

    def test_single_byte_key(self):
        data = b"\xff\xff\xff"
        key = "Z"
        result = xor_data(data, key)
        assert all(b == (0xFF ^ ord("Z")) for b in result)

    def test_long_key(self):
        data = b"AB"
        key = "longkey"
        result = xor_data(data, key)
        assert result == bytes([ord("A") ^ ord("l"), ord("B") ^ ord("o")])

    def test_binary_data(self):
        data = bytes(range(256))
        key = "key"
        encrypted = xor_data(data, key)
        decrypted = xor_data(encrypted, key)
        assert decrypted == data

    def test_identical_data_and_key_byte(self):
        key = "A"
        data = bytes([ord("A")] * 5)
        result = xor_data(data, key)
        assert result == b"\x00\x00\x00\x00\x00"


# ── decode_base64 ────────────────────────────────────────────────────────────

class TestDecodeBase64:
    def test_basic(self):
        encoded = base64.b64encode(b"hello")
        assert decode_base64(encoded) == b"hello"

    def test_empty(self):
        assert decode_base64(b"") == b""

    def test_unicode_string(self):
        encoded = base64.b64encode(b"test data")
        assert decode_base64(encoded.decode()) == b"test data"

    def test_binary_payload(self):
        original = bytes(range(256))
        encoded = base64.b64encode(original)
        assert decode_base64(encoded) == original

    def test_padding(self):
        assert decode_base64(b"YQ==") == b"a"
        assert decode_base64(b"YWI=") == b"ab"
        assert decode_base64(b"YWJj") == b"abc"

    def test_invalid_input(self):
        with pytest.raises(Exception):
            decode_base64(b"not!valid!base64!!!")


# ── decode_rot13 ─────────────────────────────────────────────────────────────

class TestDecodeRot13:
    def test_basic(self):
        assert decode_rot13("Uryyb") == "Hello"

    def test_roundtrip(self):
        original = "The quick brown fox"
        assert decode_rot13(decode_rot13(original)) == original

    def test_non_alpha_unchanged(self):
        assert decode_rot13("123!@#") == "123!@#"

    def test_empty(self):
        assert decode_rot13("") == ""

    def test_all_letters(self):
        plain = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        rot = "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
        assert decode_rot13(rot) == plain

    def test_mixed(self):
        assert decode_rot13("Grfg 123 Qngn") == "Test 123 Data"


# ── decode_hex ────────────────────────────────────────────────────────────────

class TestDecodeHex:
    def test_basic(self):
        assert decode_hex("48656c6c6f") == b"Hello"

    def test_empty(self):
        assert decode_hex("") == b""

    def test_all_bytes(self):
        hex_str = "".join(f"{i:02x}" for i in range(256))
        assert decode_hex(hex_str) == bytes(range(256))

    def test_uppercase(self):
        assert decode_hex("4A4B") == b"JK"

    def test_invalid_hex(self):
        with pytest.raises(ValueError):
            decode_hex("ZZ")

    def test_odd_length(self):
        with pytest.raises(ValueError):
            decode_hex("abc")


# ── decompress_lzma ──────────────────────────────────────────────────────────

class TestDecompressLzma:
    def test_basic(self):
        original = b"decompress me with lzma"
        compressed = lzma.compress(original)
        assert decompress_lzma(compressed) == original

    def test_empty(self):
        compressed = lzma.compress(b"")
        assert decompress_lzma(compressed) == b""

    def test_large_data(self):
        original = b"x" * 100_000
        compressed = lzma.compress(original)
        assert decompress_lzma(compressed) == original

    def test_invalid_data(self):
        with pytest.raises(Exception):
            decompress_lzma(b"not lzma data")


# ── decompress_gzip ──────────────────────────────────────────────────────────

class TestDecompressGzip:
    def test_basic(self):
        original = b"decompress me with gzip"
        compressed = gzip.compress(original)
        assert decompress_gzip(compressed) == original

    def test_empty(self):
        compressed = gzip.compress(b"")
        assert decompress_gzip(compressed) == b""

    def test_large_data(self):
        original = b"y" * 100_000
        compressed = gzip.compress(original)
        assert decompress_gzip(compressed) == original

    def test_invalid_data(self):
        with pytest.raises(Exception):
            decompress_gzip(b"not gzip data")


# ── decompress_bz2 ──────────────────────────────────────────────────────────

class TestDecompressBz2:
    def test_basic(self):
        original = b"decompress me with bz2"
        compressed = bz2.compress(original)
        assert decompress_bz2(compressed) == original

    def test_empty(self):
        compressed = bz2.compress(b"")
        assert decompress_bz2(compressed) == b""

    def test_large_data(self):
        original = b"z" * 100_000
        compressed = bz2.compress(original)
        assert decompress_bz2(compressed) == original

    def test_invalid_data(self):
        with pytest.raises(Exception):
            decompress_bz2(b"not bz2 data")


# ── decompress_zlib ──────────────────────────────────────────────────────────

class TestDecompressZlib:
    def test_basic(self):
        original = b"decompress me with zlib"
        compressed = zlib.compress(original)
        assert decompress_zlib(compressed) == original

    def test_empty(self):
        compressed = zlib.compress(b"")
        assert decompress_zlib(compressed) == b""

    def test_large_data(self):
        original = b"w" * 100_000
        compressed = zlib.compress(original)
        assert decompress_zlib(compressed) == original

    def test_invalid_data(self):
        with pytest.raises(Exception):
            decompress_zlib(b"not zlib data")


# ── iterated_base64_decode ───────────────────────────────────────────────────

class TestIteratedBase64Decode:
    def test_single_iteration(self):
        original = b"test"
        encoded = base64.b64encode(original)
        assert iterated_base64_decode(encoded, iterations=1) == original

    def test_five_iterations(self):
        data = b"payload"
        encoded = data
        for _ in range(5):
            encoded = base64.b64encode(encoded)
        assert iterated_base64_decode(encoded, iterations=5) == data

    def test_zero_iterations(self):
        data = b"unchanged"
        assert iterated_base64_decode(data, iterations=0) == data

    def test_three_iterations(self):
        data = b"three layers"
        encoded = data
        for _ in range(3):
            encoded = base64.b64encode(encoded)
        assert iterated_base64_decode(encoded, iterations=3) == data


# ── reverse_bytes ────────────────────────────────────────────────────────────

class TestReverseBytes:
    def test_basic(self):
        assert reverse_bytes(b"abcd") == b"dcba"

    def test_empty(self):
        assert reverse_bytes(b"") == b""

    def test_single_byte(self):
        assert reverse_bytes(b"x") == b"x"

    def test_palindrome(self):
        data = b"racecar"
        assert reverse_bytes(data) == data

    def test_binary(self):
        data = bytes([0, 1, 2, 3])
        assert reverse_bytes(data) == bytes([3, 2, 1, 0])


# ── assemble_payload ─────────────────────────────────────────────────────────

class TestAssemblePayload:
    def test_basic(self):
        assert assemble_payload("abc", "def") == "abcdef"

    def test_empty_parts(self):
        assert assemble_payload() == ""

    def test_single_part(self):
        assert assemble_payload("only") == "only"

    def test_ten_parts(self):
        parts = [f"p{i}" for i in range(10)]
        assert assemble_payload(*parts) == "p0p1p2p3p4p5p6p7p8p9"

    def test_preserves_order(self):
        assert assemble_payload("z", "a", "m") == "zam"


# ── is_debugger_attached ─────────────────────────────────────────────────────

class TestIsDebuggerAttached:
    def test_no_debugger(self):
        with patch("sys.gettrace", return_value=None):
            assert is_debugger_attached() is False

    def test_debugger_active(self):
        mock_trace = lambda *args: None
        with patch("sys.gettrace", return_value=mock_trace):
            assert is_debugger_attached() is True

    def test_no_gettrace(self):
        with patch("sys.gettrace", side_effect=AttributeError):
            with patch.object(__import__("sys"), "gettrace", create=False):
                pass
        # Fallback: if gettrace doesn't exist, should return False
        import sys
        original = getattr(sys, "gettrace", None)
        try:
            if hasattr(sys, "gettrace"):
                delattr(sys, "gettrace")
            from utils import is_debugger_attached as ida
            assert ida() is False
        finally:
            if original is not None:
                sys.gettrace = original


# ── rebuild_payload (integration) ────────────────────────────────────────────

class TestRebuildPayload:
    def _make_payload(self, code_obj, xor_key):
        """Build an obfuscated payload string that rebuild_payload can decode."""
        data = marshal.dumps(code_obj)
        data = zlib.compress(data)
        data = bz2.compress(data)
        data = gzip.compress(data)
        data = lzma.compress(data)
        for _ in range(5):
            data = base64.b64encode(data)
        data = data[::-1]
        data = xor_data(data, xor_key)
        hex_str = data.hex()
        rot13_hex = decode_rot13(hex_str)
        payload_str = base64.b64encode(rot13_hex.encode()).decode()
        return payload_str

    def test_roundtrip_simple_code(self):
        code = compile("x = 42", "<test>", "exec")
        xor_key = "testkey"
        payload = self._make_payload(code, xor_key)
        result = rebuild_payload(payload, xor_key)
        namespace = {}
        exec(result, namespace)
        assert namespace["x"] == 42

    def test_roundtrip_with_function(self):
        source = "def add(a, b): return a + b"
        code = compile(source, "<test>", "exec")
        xor_key = "EcEDploAhnayhIGXuLwACxbO"
        payload = self._make_payload(code, xor_key)
        result = rebuild_payload(payload, xor_key)
        namespace = {}
        exec(result, namespace)
        assert namespace["add"](2, 3) == 5

    def test_different_keys_fail(self):
        code = compile("y = 1", "<test>", "exec")
        payload = self._make_payload(code, "rightkey")
        with pytest.raises(Exception):
            rebuild_payload(payload, "wrongkey")


# ── Pipeline step composition ────────────────────────────────────────────────

class TestPipelineComposition:
    def test_base64_then_rot13_roundtrip(self):
        original = "test data"
        encoded = base64.b64encode(original.encode()).decode()
        rot = decode_rot13(encoded)
        back = decode_rot13(rot)
        assert base64.b64decode(back.encode()) == original.encode()

    def test_hex_encode_decode_roundtrip(self):
        original = b"\xde\xad\xbe\xef"
        hex_str = original.hex()
        assert decode_hex(hex_str) == original

    def test_compression_chain(self):
        original = b"compress me through all the layers!"
        compressed = zlib.compress(original)
        compressed = bz2.compress(compressed)
        compressed = gzip.compress(compressed)
        compressed = lzma.compress(compressed)

        result = decompress_lzma(compressed)
        result = decompress_gzip(result)
        result = decompress_bz2(result)
        result = decompress_zlib(result)
        assert result == original

    def test_xor_reverse_roundtrip(self):
        data = b"symmetric operations"
        key = "mykey"
        encrypted = xor_data(data, key)
        reversed_data = reverse_bytes(encrypted)
        unreversed = reverse_bytes(reversed_data)
        decrypted = xor_data(unreversed, key)
        assert decrypted == data
