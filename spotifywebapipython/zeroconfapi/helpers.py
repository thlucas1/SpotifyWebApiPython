from base64 import b64decode, b64encode
import binascii


def write_int(i: int, out: bytearray):
    if i < 0x80:
        out.append(i)
    else:
        out.append(0x80 | (i & 0x7f))
        out.append((i >> 7))


def write_bytes(b: bytes, out: bytearray):
    write_int(len(b), out)
    out.extend(b)


def byte_list_to_int(byte_list) -> int:
    """
    Converts a list of bytes to a big integer.
    """
    return int.from_bytes(bytes(byte_list), 'big')


def int_to_bytes(value: int) -> bytes:
    """
    Converts a big integer to bytes.
    """
    return value.to_bytes((value.bit_length() + 7) // 8, byteorder='big') or b'\0'


def int_to_b64str(value: int) -> str:
    """
    Converts a big integer to a base64-encoded string value.
    """
    return b64encode(int_to_bytes(value)).decode('utf-8')


def b64_to_int(value: str):
    """
    Converts a base64-encoded string or byte array to a big integer.
    """
    return int.from_bytes(b64decode(value), 'big')


def b64str_to_bytes(value: str):
    """
    Decodes a base64-encoded string to a byte array.
    """
    return b64decode(value)


def string_to_int(value):
    """
    Converts a string to a big integer.
    """
    return int(binascii.hexlify(value), 16)


def int_of_string(value):
    """
    Converts a string to a big integer.
    """
    return int(binascii.hexlify(value), 16)
