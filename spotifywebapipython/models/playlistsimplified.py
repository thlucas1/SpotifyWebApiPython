# external package imports.

# our package imports.
from ..sautils import export
from .externalurls import ExternalUrls
from .imageobject import ImageObject
from .playlisttracksummary import PlaylistTrackSummary
from .owner import Owner

@export
class PlaylistSimplified:
    """
    Spotify Web API PlaylistSimplified object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Collaborative:bool = None
        self._Description:str = None
        self._ExternalUrls:ExternalUrls = None
        self._Href:str = None
        self._Id:str = None
        self._Images:list[ImageObject] = []
        self._Name:str = None
        self._Owner:Owner = None
        self._Public:bool = None
        self._SnapshotId:str = None
        self._Tracks:PlaylistTrackSummary = None
        self._Type:str = None
        self._Uri:str = None

        if (root is None):

            # if not building the class from json response, then initialize various properties as 
            # the playlist is probably being built manually.
            self._ExternalUrls = ExternalUrls()
            self._Tracks = PlaylistTrackSummary()
        
        else:

            self._Collaborative = root.get('collaborative', None)
            self._Description = root.get('description', None)
            self._Href = root.get('href', None)
            self._Id = root.get('id', None)
            self._Name = root.get('name', None)
            self._Public = root.get('public', None)
            self._SnapshotId = root.get('snapshot_id', None)
            self._Type = root.get('type', None)
            self._Uri = root.get('uri', None)

            # process all collections and objects.
            item:dict = root.get('external_urls',None)
            if item is not None:
                self._ExternalUrls = ExternalUrls(root=item)

            items:list = root.get('images',None)
            if items is not None:
                for item in items:
                    self._Images.append(ImageObject(root=item))
        
            item:dict = root.get('owner',None)
            if item is not None:
                self._Owner = Owner(root=item)
                
            # Tracks could be one of the following objects:
            # - PlaylistTrackSummary (default) if used for playlist summary methods.
            # - PlaylistPage if used for playlist detail methods.
            item:dict = root.get('tracks',None)
            if item is not None:
                self._Tracks = PlaylistTrackSummary(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception:
            if (isinstance(self, PlaylistSimplified )) and (isinstance(other, PlaylistSimplified )):
                return self.Name == other.Name
            return False

    def __lt__(self, other):
        try:
            return self.Name < other.Name
        except Exception:
            if (isinstance(self, PlaylistSimplified )) and (isinstance(other, PlaylistSimplified )):
                return self.Name < other.Name
            return False


    @property
    def Collaborative(self) -> bool:
        """ 
        True if the owner allows other users to modify the playlist.
        """
        return self._Collaborative
    

    @property
    def Description(self) -> str:
        """ 
        The playlist description.  
        
        Only returned for modified, verified playlists; otherwise null.
        """
        return self._Description

    @Description.setter
    def Description(self, value:str):
        """ 
        Sets the Description property value.
        """
        if isinstance(value, str):
            self._Description = value
    

    @property
    def ExternalUrls(self) -> ExternalUrls:
        """ 
        Known external URLs for this playlist.
        """
        return self._ExternalUrls
    

    @property
    def Href(self) -> str:
        """ 
        A link to the Web API endpoint providing full details of the playlist.
        """
        return self._Href


    @property
    def Id(self) -> str:
        """ 
        The Spotify ID for the playlist.
        
        Example: `5v5ETK9WFXAnGQ3MRubKuE`
        """
        return self._Id

    @Id.setter
    def Id(self, value:str):
        """ 
        Sets the Id property value.
        """
        if isinstance(value, str):
            self._Id = value
    

    @property
    def Images(self) -> list[ImageObject]:
        """ 
        Images for the playlist.  
        
        The array may be empty or contain up to three images.  
        The images are returned by size in descending order.  
        Note: If returned, the source URL for the image (url) is temporary and will expire in less than a day.
        """
        return self._Images


    @property
    def ImageUrl(self) -> str:
        """
        Returns the highest resolution order image from the `Images` list, if images 
        are defined; otherwise, null.
        """
        return ImageObject.GetImageHighestResolution(self._Images)
            
        
    @property
    def Name(self) -> str:
        """ 
        The name of the playlist.
        """
        return self._Name
    
    @Name.setter
    def Name(self, value:str):
        """ 
        Sets the Name property value.
        """
        if isinstance(value, str):
            self._Name = value
    

    @property
    def Owner(self) -> Owner:
        """ 
        The user who owns the playlist.
        """
        return self._Owner
    

    @property
    def Public(self) -> bool:
        """ 
        The playlist's public/private status:  
        - true: the playlist is public.  
        - false: the playlist is private.  
        - null: the playlist status is not relevant.  
        """
        return self._Public
    

    @property
    def SnapshotId(self) -> str:
        """ 
        The version identifier for the current playlist.  
        
        Can be supplied in other requests to target a specific playlist version.
        """
        return self._SnapshotId
    

    @property
    def Tracks(self) -> PlaylistTrackSummary:  # [PlaylistTrackSummary | PlaylistPage]
        """ 
        The tracks summary of the playlist.
        """
        return self._Tracks


    @property
    def Type(self) -> str:
        """ 
        The object type: `playlist`.
        """
        return self._Type

    @Type.setter
    def Type(self, value:str):
        """ 
        Sets the Type property value.
        """
        if isinstance(value, str):
            self._Type = value
    

    @property
    def Uri(self) -> str:
        """ 
        The Spotify URI for the playlist.
        
        Example: `spotify:playlist:5v5ETK9WFXAnGQ3MRubKuE`
        """
        return self._Uri
    
    @Uri.setter
    def Uri(self, value:str):
        """ 
        Sets the Uri property value.
        """
        if isinstance(value, str):
            self._Uri = value
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        externalUrls:dict = {}
        if self._ExternalUrls is not None:
            externalUrls = self._ExternalUrls.ToDictionary()

        owner:dict = {}
        if self._Owner is not None:
            owner = self._Owner.ToDictionary()

        tracks:dict = {}
        if self._Tracks is not None:
            tracks = self._Tracks.ToDictionary()

        result:dict = \
        {
            'collaborative': self._Collaborative,
            'description': self._Description,
            'external_urls': externalUrls,
            'href': self._Href,
            'id': self._Id,
            'image_url': self.ImageUrl,
            'images': [ item.ToDictionary() for item in self._Images ],
            'name': self._Name,
            'owner': owner,
            'public': self._Public,
            'snapshotId': self._SnapshotId,
            'tracks': tracks,
            'type': self._Type,
            'uri': self._Uri,
        }
        return result
        

    def ToString(self, includeTitle:bool=True) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeTitle (str):
                True to include the class name title prefix.
        """
        msg:str = ''
        if includeTitle: 
            msg = 'PlaylistSimplified:'
        
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        if self._Collaborative is not None: msg = '%s\n Collaborative="%s"' % (msg, str(self._Collaborative))
        if self._Description is not None: msg = '%s\n Description="%s"' % (msg, str(self._Description))
        #if self._ExternalUrls is not None: msg = '%s\n %s' % (msg, str(self._ExternalUrls))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._Images is not None: msg = '%s\n Images Count=%s' % (msg, str(len(self._Images)))
        if self._Owner is not None: msg = '%s\n Owner="%s"' % (msg, str(self._Owner.Uri))
        if self._Public is not None: msg = '%s\n Public="%s"' % (msg, str(self._Public))
        if self._SnapshotId is not None: msg = '%s\n SnapshotId="%s"' % (msg, str(self._SnapshotId))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg 
