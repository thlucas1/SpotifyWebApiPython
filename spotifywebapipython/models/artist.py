# external package imports.

# our package imports.
from ..sautils import export
from .artistsimplified import ArtistSimplified
from .followers import Followers
from .imageobject import ImageObject

@export
class Artist(ArtistSimplified):
    """
    Spotify Web API Artist object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        # initialize base class.
        super().__init__(root)

        # initialize storage.
        self._Followers:Followers = None
        self._Genres:list[str] = []
        self._Images:list[ImageObject] = []
        self._Popularity:int = None
        
        if (root is None):

            pass
        
        else:

            self._Popularity = root.get('popularity', None)

            # process all collections and objects.
            item:dict = root.get('followers',None)
            if item is not None:
                self._Followers = Followers(root=item)

            items:list[str] = root.get('genres',None)
            if items is not None:
                for item in items:
                    self._Genres.append(item)
        
            items:list = root.get('images',None)
            if items is not None:
                for item in items:
                    self._Images.append(ImageObject(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Followers(self) -> Followers:
        """ 
        Information about the followers of the artist.
        """
        return self._Followers


    @property
    def Genres(self) -> list[str]:
        """ 
        A list of the genres the artist is associated with; if not yet classified, the array is empty.
        
        Example: `["Prog rock","Grunge"]`
        """
        return self._Genres


    @property
    def Images(self) -> list[ImageObject]:
        """ 
        Images of the artist in various sizes, widest first.
        """
        return self._Images


    @property
    def ImageUrl(self) -> str:
        """
        Gets the first image url in the `Images` list, if images are defined;
        otherwise, null.
        """
        if len(self._Images) > 0:
            return self._Images[0].Url
        return None
            
        
    @property
    def Popularity(self) -> int:
        """ 
        The popularity of the artist.  
        The value will be between 0 and 100, with 100 being the most popular.  
        The artist's popularity is calculated from the popularity of all the artist's tracks.
        """
        return self._Popularity


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        # get base class result.
        resultBase:dict = super().ToDictionary()

        followers:dict = {}
        if self._Followers is not None:
            followers = self._Followers.ToDictionary()

        result:dict = \
        {
            'followers': followers,
            'genres': [ item for item in self._Genres ],
            'image_url': self.ImageUrl,
            'images': [ item.ToDictionary() for item in self._Images ],
            'popularity': self._Popularity
        }
        
        # combine base class results with these results.
        resultBase.update(result)
        
        # return a sorted dictionary.
        return dict(sorted(resultBase.items()))
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Artist: %s' % super().ToString(False)
        #if self._Followers is not None: msg = '%s\n %s' % (msg, str(self._Followers))
        if self._Genres is not None: msg = '%s\n Genres Count=%s' % (msg, str(len(self._Genres)))
        if self._Images is not None: msg = '%s\n Images Count=%s' % (msg, str(len(self._Images)))
        if self._Popularity is not None: msg = '%s\n Popularity="%s"' % (msg, str(self._Popularity))
        return msg 
