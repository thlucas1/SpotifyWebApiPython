import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1
from base64 import b64decode, b64encode

from .credentials import Credentials
from .cryptodiffiehellman import CryptoDiffieHellman
from .helpers import write_bytes, write_int, byte_list_to_int, b64_to_int, int_to_bytes, string_to_int

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext, SISourceId
import logging
_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
#_logsi.SystemLogger = logging.getLogger(__name__)


class BlobBuilder:
    """
    Builds a Spotify Connect Zeroconf Blob object.
    
    Maximum length of the zeroconf blob (SP_MAX_ZEROCONF_BLOB_LENGTH)
    is 2047 characters (not counting terminating NULL).
    """
    
    AES_KEY_SIZE:int = 16               # 16 byte / 128 bit key size for AES encryption
    AES_BLOCK_SIZE:int = 16             # 16 byte / 128 bit block size for AES encryption

    def __init__(self, 
                 credentials:Credentials, 
                 device_id:str, 
                 remotePublicKeyBase64String:str,
                 originDeviceName:str=None,
                 ) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            credentials (Credentials):
            deviceId (str):
            remotePublicKeyBase64String (str):
                Remote public key value in a base64-encoded string format.
            originDeviceName (str):
        """
        # validation.
        if (originDeviceName is None) or (not isinstance(originDeviceName,str)):
            originDeviceName:str = 'ha-spotifyplus'
            
        # initialize storage.
        self._EncryptedBlob:bytes = b''
        self._EncryptedBlobSigned:bytes = b''
        self._EncryptedBlobSignedBase64String:str = ''
        self._RemotePublicKeyBase64String:str = remotePublicKeyBase64String
        self._RemotePublicKey:int = b64_to_int(remotePublicKeyBase64String)

        # formulate origin device information.
        self._OriginDeviceName:str = originDeviceName
        self._OriginDeviceId:str = hashlib.sha1(bytes(self._OriginDeviceName, 'ascii')).digest().hex()

        self.credentials:Credentials = credentials
        self.device_id:bytes = bytes(device_id, 'ascii')
        self.dh_keys = CryptoDiffieHellman()
        self._blob:bytes = b''
        self._decrypted_blob:bytes = b''
    

    @property
    def EncryptedBlob(self) -> bytes:
        """ 
        Returns the unsigned encrypted blob as a bytes object.
        """
        return self._EncryptedBlob
    

    @property
    def EncryptedBlobSigned(self) -> bytes:
        """ 
        Returns the signed encrypted blob as a bytes object.
        """
        return self._EncryptedBlobSigned
    

    @property
    def EncryptedBlobSignedBase64String(self) -> str:
        """ 
        Returns the signed encrypted blob as a base64 encoded string.
        """
        return self._EncryptedBlobSignedBase64String
    

    @property
    def RemotePublicKeyBase64String(self) -> str:
        """ 
        Returns the remote public key value in a base64 encoded string format.
        """
        return self._RemotePublicKeyBase64String
    

    @property
    def RemotePublicKey(self) -> int:
        """ 
        Returns the remote public key key value in an integer format.
        """
        return self._RemotePublicKey
    

    def build(self):
        """
        Builds the blob, encrypts it, and returns the signed encrypted blob as a base64 encoded string.
        """
        self._BuildBlob()
        self._Encrypt()
        return self._EncryptedBlobSignedBase64String


    def _BuildBlob(self): # -> bytes
        
        apiMethodName:str = 'BlobBuilder._BuildBlob'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("device_id", self.device_id)
            _logsi.LogMethodParmList(SILevel.Verbose, "Building Spotify Connect ZeroConf addUser Blob", apiMethodParms)

            # create the blob data that will be sent to the device.
            blob = bytearray()
            write_int(0x49, blob)                           # 'I' (eye-catcher)
            write_bytes(self.credentials.username, blob)    # username data (length + value)
            write_int(0x50, blob)                           # 'P' (eye-catcher)
            write_int(self.credentials.auth_type, blob)     # auth_type
            write_int(0x51, blob)                           # 'Q' (eye-catcher)
            write_bytes(self.credentials.password, blob)    # password data (length + value)
            _logsi.LogBinary(SILevel.Verbose, "Blob Data, Unencrypted Bytes", blob)
            
            # padding
            n_zeros = BlobBuilder.AES_BLOCK_SIZE - (len(blob) % BlobBuilder.AES_BLOCK_SIZE) - 1
            blob.extend([0] * n_zeros)
            blob.append(n_zeros + 1)
            _logsi.LogBinary(SILevel.Verbose, "Blob Data, Unencrypted Bytes (with padding)", blob)

            # not sure what the following is really trying to accomplish.
            # it leaves the first 16 bytes as-is, then starts performing a Bitwise XOR on 
            # on each byte remaining in the buffer (starting at offset 0x11 / byte 17).
            blen = len(blob)
            for i in range(blen - 0x11, -1, -1):
                blob[blen - i - 1] ^= blob[blen - i - 0x11]
            _logsi.LogBinary(SILevel.Verbose, "Blob Data, Unencrypted Bytes after XOR of bytes 16 thru %d" % (blen), blob)
    
            # secret is the deviceId value.
            secret = hashlib.sha1(self.device_id).digest()
            _logsi.LogBinary(SILevel.Verbose, "Blob Data Secret, SHA1 Digest", secret)
        
            # create a unique, strong hash for the given secret.
            keys = PBKDF2(secret, self.credentials.username, 20, count=0x100, hmac_hash_module=SHA1)
            key = bytearray(hashlib.sha1(keys).digest()[:20])
            key.extend(bytearray([0x00, 0x00, 0x00, 0x14]))
            _logsi.LogBinary(SILevel.Verbose, "Blob Data Encryption Key", key)

            # create a new AES cipher that will be used to encrypt the data.
            # use the hashed secret as the encryption key.
            # data will be encrypted in 16-byte blocks (or chunks).
            encrypted_blob = bytearray()
            cipher = AES.new(key, mode=AES.MODE_ECB)
        
            def chunker(seq, size):
                return (seq[pos:pos + size] for pos in range(0, len(seq), size))
        
            # encrypt the data.
            for chunk in chunker(blob, BlobBuilder.AES_BLOCK_SIZE):
                encrypted_blob.extend(cipher.encrypt(chunk))

            # trace.
            _logsi.LogBinary(SILevel.Verbose, "Blob Data, Encrypted Bytes", encrypted_blob)

            # convert encrypted bytes to a base64-encoded string so we can 
            # send it to the device via an http request.
            self._blob = b64encode(encrypted_blob)
            _logsi.LogBinary(SILevel.Verbose, "Blob Data, Encrypted base64-encoded bytes", self._blob)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def _GetIVectorAES128(self) -> bytes:
        """
        Returns a new initialization vector for AES (128-bit) cryptographic functions.

        Returns:
            A new initialization vector of 16 bytes (128-bits).</returns>
        """
        iv_data:list = [253, 81, 222, 19, 70, 203, 45, 89, 141, 68, 210, 240, 93, 20, 76, 30]
        return int.from_bytes(bytes(iv_data), 'big')


    def _Encrypt(self):
        """
        Encrypts the `_blob` argument and 
        """
        
        apiMethodName:str = 'BlobBuilder.Encrypt'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("RemotePublicKeyBase64String", self.RemotePublicKeyBase64String)
            apiMethodParms.AppendKeyValue("RemotePublicKey", self.RemotePublicKey)
            _logsi.LogMethodParmList(SILevel.Verbose, "Encrypt Spotify Connect ZeroConf addUser Blob", apiMethodParms)

            # trace.
            _logsi.LogInt(SILevel.Verbose, "Remote Public Key: %s" % self.RemotePublicKey, self.RemotePublicKey)
            
            # create shared key.
            shared_key:int = self.dh_keys.SharedSecret(self.RemotePublicKey)
            _logsi.LogInt(SILevel.Verbose, "Shared Key: %s" % shared_key, shared_key)

            b_shared_key:bytes = int_to_bytes(shared_key)
            _logsi.LogBinary(SILevel.Verbose, "Shared Key bytes", b_shared_key)
            base_key:bytes = hashlib.sha1(b_shared_key).digest()[:16]
            _logsi.LogBinary(SILevel.Verbose, "Base Key bytes", base_key)
    
            # create encryption key (16 byte / 128 bit key size for AES encryption).
            encryption_key:bytes = hmac.new(base_key, b'encryption', 'sha1').digest()
            encryption_key = encryption_key[:BlobBuilder.AES_KEY_SIZE]
            _logsi.LogBinary(SILevel.Verbose, "Encryption Key (AES128-bit) bytes", encryption_key)

            # create new AES encryption cipher, and encrypt the data.
            iv:list[int] = [253, 81, 222, 19, 70, 203, 45, 89, 141, 68, 210, 240, 93, 20, 76, 30]
            ctr_e:dict = Counter.new(128, initial_value=self._GetIVectorAES128())
            cipher = AES.new(encryption_key, AES.MODE_CTR, counter=ctr_e)
            encrypted_blob:bytes = cipher.encrypt(self._blob)
            _logsi.LogBinary(SILevel.Verbose, "Encrypted Blob (unsigned, bytes)", encrypted_blob)
        
            # create checksum key and checksum value of encrypted data.
            checksum_key:bytes = hmac.new(base_key, b'checksum', 'sha1').digest()
            _logsi.LogBinary(SILevel.Verbose, "Checksum Key: %s" % checksum_key.hex(), checksum_key)
            checksum:bytes = hmac.new(checksum_key, encrypted_blob, 'sha1').digest()
            _logsi.LogBinary(SILevel.Verbose, "Checksum Value (bytes)", checksum)

            # create signed encrypted data buffer that contains the encrypted data and checksum.
            self._EncryptedBlobSigned:bytearray = bytearray(iv)
            self._EncryptedBlobSigned.extend(encrypted_blob)
            self._EncryptedBlobSigned.extend(checksum)
            _logsi.LogBinary(SILevel.Verbose, "Encrypted Blob (signed with checksum, bytes)", self._EncryptedBlobSigned)
        
            # convert encrypted bytes to a base64-encoded string.
            b64result_bytes:bytes = b64encode(self._EncryptedBlobSigned)
            self._EncryptedBlobSignedBase64String:str = b64result_bytes.decode('ascii')
            _logsi.LogText(SILevel.Verbose, "Encrypted Blob (signed with checksum, base64-encoded string)", self._EncryptedBlobSignedBase64String)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)
    

 #    def _Decrypt(
 #            self,
 #            encrypted_blob_signed:str,
 #            ) -> None:
 #        """
 #        Decreypts the specified blob that was previously encrypted and signed by the
 #        `Encrypt` method.
        
 #        Args:
 #            encrypted_blob_signed (str):
 #                A base64 encoded string that represents a signed and encrypted data blob; the
 #                packet consists of the IV, data, and checksum blocks.
 #        """
        
 #        apiMethodName:str = 'BlobBuilder.Decrypt'
 #        apiMethodParms:SIMethodParmListContext = None
        
 #        try:
            
 #            # trace.
 #            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
 #            apiMethodParms.AppendKeyValue("encrypted_blob_signed", encrypted_blob_signed)
 #            apiMethodParms.AppendKeyValue("RemotePublicKeyBase64String", self.RemotePublicKeyBase64String)
 #            _logsi.LogMethodParmList(SILevel.Verbose, "Decrypt Spotify Connect ZeroConf addUser Blob", apiMethodParms)

 #            if encrypted_blob_signed is not None:
 #                self._EncryptedBlobSignedBase64String = encrypted_blob_signed

 #            # convert base64-encoded string to bytes.
 #            _logsi.LogText(SILevel.Verbose, "Encrypted Blob (signed with checksum, base64-encoded string)", self._EncryptedBlobSignedBase64String)
 #            self._EncryptedBlobSigned:bytes = b64decode(self._EncryptedBlobSignedBase64String)
 #            _logsi.LogBinary(SILevel.Verbose, "Encrypted Blob (signed with checksum, bytes)", self._EncryptedBlobSigned)

 #            # get the individual components of the signed blob packet.
 #            iv = self._EncryptedBlobSigned[:16]
 #            self._EncryptedBlob = self._EncryptedBlobSigned[16:len(self._EncryptedBlobSigned)-20]
 #            checksum = self._EncryptedBlobSigned[len(self._EncryptedBlobSigned)-20:]
 #            _logsi.LogBinary(SILevel.Verbose, "Checksum Value (bytes)", checksum)
 #            _logsi.LogBinary(SILevel.Verbose, "Encrypted Blob (unsigned, bytes)", self._EncryptedBlob)

 #            clientKey:str = "7efznlz1HspR5tQftOUdz7cv/L6V5EuXWI596GyiQMist7piBWxfbdAjcpP9/o7WnCl5HdwgI7nY6cQ7ktz3Tsbs4kSG5mbi1QwnYi8IbJ9sdYdd8YxI3Vl6dfuG3JWP"
 #            result_b64decode = b64decode(clientKey)
 #            result_b64_to_int = b64_to_int(clientKey) # 114863 ...
 #            # result_string_to_int = string_to_int(clientKey) # 114863 ...
 #            # result_byte_list_to_int = byte_list_to_int(clientKey) # 114863 ...
 #            # result_dh_keys_Exchange = self.dh_keys.Exchange(clientKey) # 6243 ...
 #            #resultInt = self.dh_keys.Exchange(clientKey) # exception
 #            #resultInt = self.dh_keys.shared_secret(b64_to_int(resultBytes)) # exception
 #            #result_dh_keys_shared_secret = self.dh_keys.shared_secret(string_to_int(resultBytes)) # 438506 ...
 #            #resultInt = self.dh_keys.shared_secret(string_to_int(clientKey)) # exception ...

 #            remote_device_key:int = b64_to_int(clientKey)
 #            shared_key:int = 478549389067009439856765960469867849375843534534536997108028584308833390603433510828238916782187762759272369310194601566745030716193055009703822032238289108648174583850368649722797922715533666774901465941959787614689524297840942749
 #            shared_key_int_to_bytes = int_to_bytes(shared_key)
 #            #shared_key_b64encode = b64encode(shared_key)
 #            shared_key_b64encode_int_to_bytes = b64encode(int_to_bytes(shared_key))
 #            shared_key_b64encode_utf8 = b64encode(int_to_bytes(shared_key)).decode('utf-8') 

            
 #            #shared_key:int = self.dh_keys.shared_secret(remote_device_key)
 #            b_shared_key:bytes = int_to_bytes(shared_key)
 #            base_key:bytes = hashlib.sha1(b_shared_key).digest()[:16]
 #            #tmpbytes = b64decode(clientKey)
 #            #shared_key:int = byte_list_to_int(tmpbytes)
 #            #shared_key:int = b64_to_int(clientKey)
 #            #shared_key = self.dh_keys.Exchange(clientKey)
 #            _logsi.LogValue(SILevel.Verbose, "Shared Key: %s" % shared_key, shared_key)
	#         #baseKey := func() []byte { sum := sha1.Sum(sharedSecret); return sum[:16] }()
 #            #b_shared_key:bytes = int_to_bytes(shared_key)
 #            #base_key:bytes = hashlib.sha1(b_shared_key).digest()[:16]
 #        	#encryptionKey := func() []byte { sum := mac.Sum(nil); return sum[:16] }()
 #            encryption_key:bytes = hmac.new(base_key, b'encryption', 'sha1').digest()
 #            _logsi.LogBinary(SILevel.Verbose, "Encryption Key", encryption_key)
            
 #            # # create remote device key.
 #            # remote_device_key:int = b64_to_int(self.RemotePublicKeyBase64String)
 #            # _logsi.LogValue(SILevel.Verbose, "Remote Device Key", remote_device_key)
            
 #            # # create shared key.
 #            # shared_key:int = self.dh_keys.shared_secret(remote_device_key)
 #            # _logsi.LogValue(SILevel.Verbose, "Shared Key: %s" % shared_key, shared_key)

 #            # b_shared_key:bytes = int_to_bytes(shared_key)
 #            # base_key:bytes = hashlib.sha1(b_shared_key).digest()[:16]
            
 #            # # create encryption key.
 #            # encryption_key:bytes = hmac.new(base_key, b'encryption', 'sha1').digest()
 #            # _logsi.LogBinary(SILevel.Verbose, "Encryption Key", encryption_key)

 #            # create new AES cipher, and decrypt the data.
 #            ctr_e:dict = Counter.new(128, initial_value=byte_list_to_int(iv))
 #            cipher = AES.new(encryption_key[:16], AES.MODE_CTR, counter=ctr_e)
 #            self._decrypted_blob = cipher.decrypt(self._EncryptedBlob)
 #            _logsi.LogBinary(SILevel.Verbose, "Blob Data, Encrypted base64-encoded bytes", self._decrypted_blob)
 #            self._blob = b64decode(self._decrypted_blob)
 #            _logsi.LogBinary(SILevel.Verbose, "Blob Data, Encrypted Bytes", self._blob)


	# # cipher.NewCTR(bc, iv).XORKeyStream(decrypted, encrypted)

 #        finally:
        
 #            # trace.
 #            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)
