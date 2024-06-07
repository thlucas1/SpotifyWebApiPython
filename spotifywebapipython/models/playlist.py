# external package imports.

# our package imports.
from ..sautils import export
from .followers import Followers
from .playlistpage import PlaylistPage
from .playlistsimplified import PlaylistSimplified
from .track import Track

@export
class Playlist(PlaylistSimplified):
    """
    Spotify Web API Playlist object.
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
        self._Tracks:PlaylistPage = None

        if (root is None):

            # if not building the class from json response, then initialize various properties as 
            # the playlist is probably being built manually.
            self._Followers = Followers()
            self._Tracks = PlaylistPage()
        
        else:

            # process all collections and objects.
            item:dict = root.get('followers',None)
            if item is not None:
                self._Followers = Followers(root=item)
        
            item:dict = root.get('tracks',None)
            if item is not None:
                self._Tracks = PlaylistPage(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Followers(self) -> Followers:
        """ 
        Information about the followers of the playlist.
        """
        return self._Followers


    @property
    def Tracks(self) -> PlaylistPage:
        """ 
        The tracks of the playlist.
        
        This is a `PlaylistPage` object, meaning only 50 tracks max are listed per request.
        """
        return self._Tracks


    def GetTracks(self) -> list[Track]:
        """ 
        Gets a list of all tracks contained in the underlying `Items` list.
        
        This is a convenience method so one does not have to loop through the `Items`
        array of PlaylistPage objects to get the list of tracks.
        """
        result:list[Track] = []
        if self._Tracks is not None:
            result = self._Tracks.GetTracks()
        return result
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        # get base class result.
        resultBase:dict = super().ToDictionary()

        followers:dict = {}
        if self._Followers is not None:
            followers = self._Followers.ToDictionary()

        tracks:dict = {}
        if self._Tracks is not None:
            tracks = self._Tracks.ToDictionary()

        result:dict = \
        {
            'tracks': tracks,
            'followers': followers
        }
        
        # combine base class results with these results.
        resultBase.update(result)
        
        # return an unsorted dictionary.
        return resultBase
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Playlist: %s' % super().ToString(False)
        #if self._Followers is not None: msg = '%s\n %s' % (msg, str(self._Followers))
        if self._Tracks is not None: msg = '%s\n Tracks Count=%s' % (msg, str(self._Tracks.Total))
        return msg 
