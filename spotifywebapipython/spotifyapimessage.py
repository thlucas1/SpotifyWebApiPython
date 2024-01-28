# external package imports.

# our package imports.
from .sautils import export

@export
class SpotifyApiMessage:
    """
    A class representing an exchange object between a client and the Spotify Web API.
    """
    
    def __init__(self, methodName:str, uri:str, urlParameters:dict=None, requestData:dict=None, requestHeaders:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            methodName (str):
                Name of the client method that executed the request.
            uri (str):
                Target uri which should be queried.
            urlParameters (dict):
                Parameter values to be placed into the http request url, if the specified
                uri service requires it; otherwise, None.
            requestData (dict):
                Request data that is to be placed into the http request body, if the specified
                uri service requires it; otherwise, None.
            requestHeaders (dict):
                Request header that is to be placed into the http request headers, if the specified
                uri service requires it; otherwise, None.
        """
        # validation.
        if requestData is None:
            requestData = {}
        if requestHeaders is None:
            requestHeaders = {}
        if urlParameters is None:
            urlParameters = {}

        self._MethodName:str = methodName            
        self._RequestData:dict = requestData
        self._RequestHeaders:dict = requestHeaders
        self._RequestJson:dict = None
        self._ResponseData = {}
        self._IsRequestDataEncoded:bool = False
        self._Uri:str = uri
        self._UrlParameters:dict = urlParameters

      
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def HasRequestData(self) -> bool:
        """ 
        Returns True if request data is present, and should be supplied as part of the 
        http request body; otherwise, False.
        """
        return self._RequestData is not None and len(self._RequestData) != 0


    @property
    def HasRequestHeaders(self) -> bool:
        """ 
        Returns True if request headers are present, and should be supplied as part of the 
        http request headers; otherwise, False.
        """
        return self._RequestHeaders is not None and len(self._RequestHeaders) != 0


    @property
    def HasRequestJson(self) -> bool:
        """ 
        Returns True if request json is present, and should be supplied as part of the 
        http request body; otherwise, False.
        """
        return self._RequestJson is not None and len(self._RequestJson) != 0


    @property
    def HasUrlParameters(self) -> bool:
        """ 
        Returns True if url parameters are present, and should be supplied as part of the 
        http request url; otherwise, False.
        """
        return self._UrlParameters is not None and len(self._UrlParameters) != 0


    @property
    def HasResponseData(self) -> bool:
        """ 
        Returns True if data was returned with the response; otherwise, False. 
        """
        return self._RequestData is not None


    @property
    def IsRequestDataEncoded(self) -> bool:
        """ 
        Indicates if the `RequestData` property is already encoded (True) or not (False).
        """
        return self._IsRequestDataEncoded

    @IsRequestDataEncoded.setter
    def IsRequestDataEncoded(self, value:bool):
        """ 
        Sets the MethodName property value.
        """
        self._IsRequestDataEncoded = value


    @property
    def IsResponseEmpty(self) -> bool:
        """ 
        Returns True if the response contains no data (e.g. a pass / fail response)
        and is not null; otherwise, False.
        """
        return self._ResponseData is not None and len(self._ResponseData) == 0


    @property
    def IsSimpleResponse(self) -> bool:
        """ 
        Returns True if the response contains no data (e.g. a pass / fail response); 
        otherwise, False if the response requires further processing.
        """
        return self._ResponseData is not None and len(self._ResponseData) != 0


    @property
    def MethodName(self) -> str:
        """ 
        The client method that executed the request.
        
        Example: `GetArtist`.
        """
        return self._MethodName

    @MethodName.setter
    def MethodName(self, value:str):
        """ 
        Sets the MethodName property value.
        """
        if value is not None:
            if isinstance(value, str):
                self._MethodName = value


    @property
    def RequestData(self) -> dict: 
        """ 
        Request data that is to be placed into the http request body, if the specified
        uri service requires it.
        """
        return self._RequestData
    
    @RequestData.setter
    def RequestData(self, value:dict):
        """ 
        Sets the RequestData property value.
        """
        if value is not None:
            self._RequestData = value
        

    @property
    def RequestHeaders(self) -> dict: 
        """ 
        Request header data that is to be sent with the http request body, if the specified
        uri service requires it.
        """
        return self._RequestHeaders

    @RequestHeaders.setter
    def RequestHeaders(self, value:dict):
        """ 
        Sets the RequestHeaders property value.
        """
        if value is not None:
            if isinstance(value, dict):
                self._RequestHeaders = value
        

    @property
    def RequestJson(self) -> dict: 
        """ 
        Request data that is to be placed into the http request body, if the specified
        uri service requires it.
        """
        return self._RequestJson
    
    @RequestJson.setter
    def RequestJson(self, value:dict):
        """ 
        Sets the RequestJson property value.
        """
        if value is not None:
            if isinstance(value, dict):
                self._RequestJson = value
        

    @property
    def ResponseData(self) -> dict:
        """ 
        Response data returned from the server, if the specified uri returned
        a response that contains data.
        """
        return self._ResponseData

    @ResponseData.setter
    def ResponseData(self, value:dict):
        """ 
        Sets the ResponseData property value.
        """
        if value is not None:
            # some Spotify responses can contain non-dictionary data!
            #if isinstance(value, dict):
            self._ResponseData = value
        

    @property
    def Uri(self) -> str: 
        """ 
        Target uri which should be queried.
        """
        return self._Uri


    @property
    def UrlParameters(self) -> dict: 
        """ 
        Parameter values to be placed into the http request url, if the specified
        uri service requires it.
        """
        return self._UrlParameters

    @UrlParameters.setter
    def UrlParameters(self, value:dict):
        """ 
        Sets the UrlParameters property value.
        """
        if value is not None:
            if isinstance(value, dict):
                self._UrlParameters = value
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'SpotifyApiMessage:'
        msg = '%s uri="%s"' % (msg, str(self._Uri))
        if self.HasRequestData: msg = '%s RequestData="%s"' % (msg, self._RequestData)
        if self.HasRequestJson: msg = '%s RequestJson="%s"' % (msg, self._RequestJson)
        if self.IsSimpleResponse: msg = '%s response="%s"' % (msg, str(self.IsSimpleResponse).lower())
        return msg 
