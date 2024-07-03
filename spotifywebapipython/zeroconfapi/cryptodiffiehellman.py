import secrets

from .helpers import byte_list_to_int, int_to_bytes, b64_to_int, int_to_b64str

class CryptoDiffieHellman:
    """
    Diffie Hellman cryptography helper class.
    
    The following link does a pretty good job of explaining this process:
    https://www.comparitech.com/blog/information-security/diffie-hellman-key-exchange/
    """
    
    DH_GENERATOR = 2
    DH_PRIME_MODULUS = byte_list_to_int([
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xc9, 0x0f, 0xda, 0xa2, 0x21, 0x68, 0xc2,
        0x34, 0xc4, 0xc6, 0x62, 0x8b, 0x80, 0xdc, 0x1c, 0xd1, 0x29, 0x02, 0x4e, 0x08, 0x8a, 0x67,
        0xcc, 0x74, 0x02, 0x0b, 0xbe, 0xa6, 0x3b, 0x13, 0x9b, 0x22, 0x51, 0x4a, 0x08, 0x79, 0x8e,
        0x34, 0x04, 0xdd, 0xef, 0x95, 0x19, 0xb3, 0xcd, 0x3a, 0x43, 0x1b, 0x30, 0x2b, 0x0a, 0x6d,
        0xf2, 0x5f, 0x14, 0x37, 0x4f, 0xe1, 0x35, 0x6d, 0x6d, 0x51, 0xc2, 0x45, 0xe4, 0x85, 0xb5,
        0x76, 0x62, 0x5e, 0x7e, 0xc6, 0xf4, 0x4c, 0x42, 0xe9, 0xa6, 0x3a, 0x36, 0x20, 0xff, 0xff,
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
    

    def __init__(self):
        """
        Initializes a new instance of the class.
        """
        # generate our private key value.
        self._PrivateKey = secrets.randbits(95 * 8)
        
        # generate a public key that we can share with a partner.
        self._PublicKey:int = pow(CryptoDiffieHellman.DH_GENERATOR, self._PrivateKey, CryptoDiffieHellman.DH_PRIME_MODULUS)


    @property
    def PublicKey(self) -> int:
        """ 
        Returns our public key in an integer format.
        """
        return self._PublicKey
    
    @PublicKey.setter
    def PublicKey(self, value:int):
        """ 
        Sets the PublicKey property value.
        """
        if isinstance(value, int):
            self._PublicKey = value


    @property
    def PublicKeyBase64String(self) -> str:
        """ 
        Returns our public key in a base64 encoded string format.
        """
        return int_to_b64str(self._PublicKey)
    

    def SharedSecret(self, remotePublicKey:int):
        """
        Returns a shared secret value that is calculated based upon the specified `remotePublicKey`
        value, our private key value, and a shared Modulus value.
        
        Args:
            remotePublicKey (int):
                The Remote clients PublicKey value.
        
        The shared secret value can be calculated as:
        SharedSecret = remotePublicKey(base,g) ** PrivateKey(secret,a) % DH_PRIME(modulus,p)
        SharedSecret = g**a mod p
        SharedSecret = base ** secret % modulus
        
        - base = remotePublicKey
        - secret = PrivateKey
        - modulus = DH_PRIME
        """
        # calculate the shared secret value based upon the remote's PublicKey, our PrivateKey, and the shared Modulus.
        
        # another way to express this formula is:
        # SharedSecret = g**a mod p
        
        # another way to express this formula is:
        # SharedSecret = base ** secret % modulus
        
        # - base or `g`     = remotePublicKey
        # - secret or `a`   = PrivateKey
        # - modulus or `p`  = DH_PRIME
        return pow(remotePublicKey, self._PrivateKey, CryptoDiffieHellman.DH_PRIME_MODULUS)
    