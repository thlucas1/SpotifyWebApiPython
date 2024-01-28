# external package imports.

# our package imports.
from ..sautils import export
from .albumpagesimplified import AlbumPageSimplified
from .artistpage import ArtistPage
from .audiobookpagesimplified import AudiobookPageSimplified
from .episodepagesimplified import EpisodePageSimplified
from .playlistpagesimplified import PlaylistPageSimplified
from .showpagesimplified import ShowPageSimplified
from .trackpage import TrackPage

@export
class SearchResponse:
    """
    Spotify Web API SearchResponse object.
    """

    def __init__(self, 
                 searchCriteria:str, 
                 searchCriteriaType:str, 
                 root:dict=None
                 ) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            searchCriteria (str):
                Search query specified for the search.  
            searchCriteriaType (str):
                A comma-separated list of item types that were searched.  
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Albums:AlbumPageSimplified = None
        self._Artists:ArtistPage = None
        self._Audiobooks:AudiobookPageSimplified = None
        self._Episodes:EpisodePageSimplified = None
        self._Playlists:PlaylistPageSimplified = None
        self._SearchCriteria:str = searchCriteria
        self._SearchCriteriaType:str = searchCriteriaType
        self._Shows:ShowPageSimplified = None
        self._Tracks:TrackPage = None
        
        if (root is None):

            self._Albums:AlbumPageSimplified = AlbumPageSimplified()
            self._Artists:ArtistPage = ArtistPage()
            self._Audiobooks:AudiobookPageSimplified = AudiobookPageSimplified()
            self._Episodes:EpisodePageSimplified = EpisodePageSimplified()
            self._Playlists:PlaylistPageSimplified = PlaylistPageSimplified()
            self._Shows:ShowPageSimplified = ShowPageSimplified()
            self._Tracks:TrackPage = TrackPage()
        
        else:

            # process all collections and objects.
            item:dict = root.get('albums',None)
            if item is not None:
                self._Albums = AlbumPageSimplified(root=item)

            item:dict = root.get('artists',None)
            if item is not None:
                self._Artists = ArtistPage(root=item)

            item:dict = root.get('audiobooks',None)
            if item is not None:
                self._Audiobooks = AudiobookPageSimplified(root=item)

            item:dict = root.get('episodes',None)
            if item is not None:
                self._Episodes = EpisodePageSimplified(root=item)

            item:dict = root.get('playlists',None)
            if item is not None:
                self._Playlists = PlaylistPageSimplified(root=item)

            item:dict = root.get('shows',None)
            if item is not None:
                self._Shows = ShowPageSimplified(root=item)

            item:dict = root.get('tracks',None)
            if item is not None:
                self._Tracks = TrackPage(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def AlbumsCount(self) -> int:
        """ 
        The total number of album items found in the search.  
        
        Note that this value could be different than the number of items in the
        underlying `AlbumPageSimplified` object, as paging limits are applied.
        """
        if self._Albums is not None:
            return self._Albums.Total
        return 0


    @property
    def Albums(self) -> AlbumPageSimplified:
        """ 
        An `AlbumPageSimplified` object that allows for multiple pages of albums to be navigated.        
        """
        return self._Albums
    

    @property
    def ArtistsCount(self) -> int:
        """ 
        The total number of artist items found in the search.  
        
        Note that this value could be different than the number of items in the
        underlying `ArtistPage` object, as paging limits are applied.
        """
        if self._Artists is not None:
            return self._Artists.Total
        return 0


    @property
    def Artists(self) -> ArtistPage:
        """ 
        An `ArtistPage` object that allows for multiple pages of artists to be navigated.        
        """
        return self._Artists
    

    @property
    def AudiobooksCount(self) -> int:
        """ 
        The total number of audiobook items found in the search.  
        
        Note that this value could be different than the number of items in the
        underlying `AudiobookPageSimplified` object, as paging limits are applied.
        """
        if self._Audiobooks is not None:
            return self._Audiobooks.Total
        return 0


    @property
    def Audiobooks(self) -> AudiobookPageSimplified:
        """ 
        An `AudiobookPageSimplified` object that allows for multiple pages of audiobooks to be navigated.        
        """
        return self._Audiobooks
    

    @property
    def EpisodesCount(self) -> int:
        """ 
        The total number of episode items found in the search.  
        
        Note that this value could be different than the number of items in the
        underlying `EpisodePageSimplified` object, as paging limits are applied.
        """
        if self._Episodes is not None:
            return self._Episodes.Total
        return 0


    @property
    def Episodes(self) -> EpisodePageSimplified:
        """ 
        An `EpisodePageSimplified` object that allows for multiple pages of episodes to be navigated.        
        """
        return self._Episodes
    

    @property
    def PlaylistsCount(self) -> int:
        """ 
        The total number of playlist items found in the search.  
        
        Note that this value could be different than the number of items in the
        underlying `PlaylistPageSimplified` object, as paging limits are applied.
        """
        if self._Playlists is not None:
            return self._Playlists.Total
        return 0


    @property
    def Playlists(self) -> PlaylistPageSimplified:
        """ 
        An `PlaylistPageSimplified` object that allows for multiple pages of playlists to be navigated.        
        """
        return self._Playlists
    

    @property
    def SearchCriteria(self) -> str:
        """ 
        The search query used to generate the response.
        """
        return self._SearchCriteria
    

    @property
    def SearchCriteriaType(self) -> str:
        """ 
        The comma-separated list of item types that were searched for.  
        
        Search results include hits from all of the specified item types.  
        """
        return self._SearchCriteriaType
    

    @property
    def ShowsCount(self) -> int:
        """ 
        The total number of show items found in the search.  
        
        Note that this value could be different than the number of items in the
        underlying `ShowPageSimplified` object, as paging limits are applied.
        """
        if self._Shows is not None:
            return self._Shows.Total
        return 0


    @property
    def Shows(self) -> ShowPageSimplified:
        """ 
        An `ShowPageSimplified` object that allows for multiple pages of shows to be navigated.        
        """
        return self._Shows
    

    @property
    def TracksCount(self) -> int:
        """ 
        The total number of track items found in the search.  
        
        Note that this value could be different than the number of items in the
        underlying `TrackPage` object, as paging limits are applied.
        """
        if self._Tracks is not None:
            return self._Tracks.Total
        return 0


    @property
    def Tracks(self) -> TrackPage:
        """ 
        A `TrackPage` object that allows for multiple pages of tracks to be navigated.        
        """
        return self._Tracks
    

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        msg:str = 'SearchResponse:'
        msg = '%s\n Search Criteria="%s"' % (msg, str(self._SearchCriteria))
        msg = '%s\n Search Type="%s"' % (msg, str(self._SearchCriteriaType))
        msg = '%s\n Albums Count=%s' % (msg, str(self.AlbumsCount))
        msg = '%s\n Artists Count=%s' % (msg, str(self.ArtistsCount))
        # msg = '%s\n AudioBooks Count=%s' % (msg, str(self.AudioBooksCount))
        msg = '%s\n Episodes Count=%s' % (msg, str(self.EpisodesCount))
        msg = '%s\n Playlists Count=%s' % (msg, str(self.PlaylistsCount))
        msg = '%s\n Shows Count=%s' % (msg, str(self.ShowsCount))
        msg = '%s\n Tracks Count=%s' % (msg, str(self.TracksCount))
        return msg 
