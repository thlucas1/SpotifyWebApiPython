class Credentials:
    """
    Credentials used by the Spotify SpConnectionLoginBlob method.
    """

    def __init__(self, username: str, password: str):
        """
        Initializes a new instance of the class.
        
        Args:
            username (str):
                Spotify Connect user name to login with.  
            password (str):
                Spotify Connect user password to login with.  
        """
        self.username: bytes = bytes(username, 'ascii')
        self.password: bytes = bytes(password, 'ascii')
        self.auth_type: int = 0x00