import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1
from base64 import b64decode, b64encode
import secrets

#from .crypto import DiffieHellman
#from .helpers import write_bytes, write_int, byte_list_to_int, Credentials, b64_to_int, int_to_bytes

# copied from https://github.com/maraid/zerospot

class ZeroconfCredentials:
    def __init__(self, username: str, password: str):
        self.username: bytes = bytes(username, 'ascii')
        self.password: bytes = bytes(password, 'ascii')
        self.auth_type: int = 0x00
        
        
class ZeroconfBlobBuilder:
    
    def __init__(self, credentials: ZeroconfCredentials, device_id: str, remote_pubkey: str):
        self.credentials: ZeroconfCredentials = credentials
        self.device_id: bytes = bytes(device_id, 'ascii')
        self.remote_pubkey: str = remote_pubkey
        self.dh_keys = DiffieHellman()
        self._blob = b''
        self._encrypted_blob = b''
    
    def build(self):
        self._build()
        self._encrypt()
        return self._encrypted_blob.decode("ascii")

    def _build(self): # -> bytes
        blob = bytearray()
        # 'I'
        write_int(0x49, blob)
        # username
        write_bytes(self.credentials.username, blob)
        # 'P'
        write_int(0x50, blob)
        # auth_type
        write_int(self.credentials.auth_type, blob)
        # 'Q'
        write_int(0x51, blob)
        # password
        write_bytes(self.credentials.password, blob)
        # Padding
        n_zeros = 16 - (len(blob) % 16) - 1
        blob.extend([0] * n_zeros)
        blob.append(n_zeros + 1)

        blen = len(blob)
        for i in range(blen - 0x11, -1, -1):
            blob[blen - i - 1] ^= blob[blen - i - 0x11]
    
        secret = hashlib.sha1(self.device_id).digest()
        
        keys = PBKDF2(secret, self.credentials.username, 20, count=0x100, hmac_hash_module=SHA1)
        key = bytearray(hashlib.sha1(keys).digest()[:20])
        key.extend(bytearray([0x00, 0x00, 0x00, 0x14]))

        encrypted_blob = bytearray()
        cipher = AES.new(key, mode=AES.MODE_ECB)
        block_size = 16
        
        def chunker(seq, size):
            return (seq[pos:pos + size] for pos in range(0, len(seq), size))
        
        for chunk in chunker(blob, block_size):
            encrypted_blob.extend(cipher.encrypt(chunk))

        self._blob = b64encode(encrypted_blob)

    def _encrypt(self):
        remote_device_key = b64_to_int(self.remote_pubkey)
        shared_key = self.dh_keys.shared_secret(remote_device_key)

        b_shared_key = int_to_bytes(shared_key)
        base_key = hashlib.sha1(b_shared_key).digest()[:16]
    
        checksum_key = hmac.new(base_key, b'checksum', 'sha1').digest()
        encryption_key = hmac.new(base_key, b'encryption', 'sha1').digest()

        iv = [253, 81, 222, 19, 70, 203, 45, 89, 141, 68, 210, 240, 93, 20, 76, 30]
        ctr_e = Counter.new(128, initial_value=byte_list_to_int(iv))
        cipher = AES.new(encryption_key[:16], AES.MODE_CTR, counter=ctr_e)
        encrypted_blob = cipher.encrypt(self._blob)
        
        checksum = hmac.new(checksum_key, encrypted_blob, 'sha1').digest()

        encrypted_signed_blob = bytearray(iv)
        encrypted_signed_blob.extend(encrypted_blob)
        encrypted_signed_blob.extend(checksum)
        
        self._encrypted_blob = b64encode(encrypted_signed_blob)


def write_int(i: int, out: bytearray):
    if i < 0x80:
        out.append(i)
    else:
        out.append(0x80 | (i & 0x7f))
        out.append((i >> 7))


def write_bytes(b: bytes, out: bytearray):
    write_int(len(b), out)
    out.extend(b)

def byte_list_to_int(byte_list):
    return int.from_bytes(bytes(byte_list), 'big')

def int_to_bytes(i: int):
    return i.to_bytes((i.bit_length() + 7) // 8, byteorder='big')

def int_to_b64str(i: int):
    return b64encode(int_to_bytes(i)).decode('ascii')

def b64_to_int(b64: str):
    return int.from_bytes(b64decode(b64), 'big')


class DiffieHellman:
    DH_GENERATOR = 2
    DH_PRIME = byte_list_to_int([
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xc9, 0x0f, 0xda, 0xa2, 0x21, 0x68, 0xc2,
        0x34, 0xc4, 0xc6, 0x62, 0x8b, 0x80, 0xdc, 0x1c, 0xd1, 0x29, 0x02, 0x4e, 0x08, 0x8a, 0x67,
        0xcc, 0x74, 0x02, 0x0b, 0xbe, 0xa6, 0x3b, 0x13, 0x9b, 0x22, 0x51, 0x4a, 0x08, 0x79, 0x8e,
        0x34, 0x04, 0xdd, 0xef, 0x95, 0x19, 0xb3, 0xcd, 0x3a, 0x43, 0x1b, 0x30, 0x2b, 0x0a, 0x6d,
        0xf2, 0x5f, 0x14, 0x37, 0x4f, 0xe1, 0x35, 0x6d, 0x6d, 0x51, 0xc2, 0x45, 0xe4, 0x85, 0xb5,
        0x76, 0x62, 0x5e, 0x7e, 0xc6, 0xf4, 0x4c, 0x42, 0xe9, 0xa6, 0x3a, 0x36, 0x20, 0xff, 0xff,
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
    
    def __init__(self):
        self._private_key = secrets.randbits(95 * 8)
        self.public_key = pow(DiffieHellman.DH_GENERATOR, self._private_key, DiffieHellman.DH_PRIME)

    def shared_secret(self, remote_key):
        return pow(remote_key, self._private_key, DiffieHellman.DH_PRIME)
    