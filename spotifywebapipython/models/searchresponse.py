# external package imports.

# our package imports.
from ..sautils import export
from .albumpagesimplified import AlbumPageSimplified
from .artistpage import ArtistPage
from .audiobookpagesimplified import AudiobookPageSimplified
from .episodepagesimplified import EpisodePageSimplified
from .playlistpagesimplified import PlaylistPageSimplified
from .playlistsimplified import PlaylistSimplified
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
        self._Albums:AlbumPageSimplified = AlbumPageSimplified()
        self._Artists:ArtistPage = ArtistPage()
        self._Audiobooks:AudiobookPageSimplified = AudiobookPageSimplified()
        self._Episodes:EpisodePageSimplified = EpisodePageSimplified()
        self._Playlists:PlaylistPageSimplified = PlaylistPageSimplified()
        self._SearchCriteria:str = searchCriteria
        self._SearchCriteriaType:str = searchCriteriaType
        self._Shows:ShowPageSimplified = ShowPageSimplified()
        self._Tracks:TrackPage = TrackPage()
        
        if (root is None):

            pass
        
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
        The total number of album items returned in the `Tracks.Items` collection
        """
        if self._Albums is not None:
            return self._Albums.ItemsCount
        return 0


    @property
    def Albums(self) -> AlbumPageSimplified:
        """ 
        An `AlbumPageSimplified` object that allows for multiple pages of albums to be navigated.        
        """
        return self._Albums
    
    @Albums.setter
    def Albums(self, value:str):
        """ 
        Sets the Albums property value.
        """
        if value is not None:
            if isinstance(value, AlbumPageSimplified):
                self._Albums = value


    @property
    def ArtistsCount(self) -> int:
        """ 
        The total number of artist items returned in the `Tracks.Items` collection
        """
        if self._Artists is not None:
            return self._Artists.ItemsCount
        return 0


    @property
    def Artists(self) -> ArtistPage:
        """ 
        An `ArtistPage` object that allows for multiple pages of artists to be navigated.        
        """
        return self._Artists
    
    @Artists.setter
    def Artists(self, value:str):
        """ 
        Sets the Artists property value.
        """
        if value is not None:
            if isinstance(value, ArtistPage):
                self._Artists = value


    @property
    def AudiobooksCount(self) -> int:
        """ 
        The total number of audiobook items returned in the `Tracks.Items` collection
        """
        if self._Audiobooks is not None:
            return self._Audiobooks.ItemsCount
        return 0


    @property
    def Audiobooks(self) -> AudiobookPageSimplified:
        """ 
        An `AudiobookPageSimplified` object that allows for multiple pages of audiobooks to be navigated.        
        """
        return self._Audiobooks
    
    @Audiobooks.setter
    def Audiobooks(self, value:str):
        """ 
        Sets the Audiobooks property value.
        """
        if value is not None:
            if isinstance(value, AudiobookPageSimplified):
                self._Audiobooks = value


    @property
    def EpisodesCount(self) -> int:
        """ 
        The total number of episode items returned in the `Tracks.Items` collection
        """
        if self._Episodes is not None:
            return self._Episodes.ItemsCount
        return 0


    @property
    def Episodes(self) -> EpisodePageSimplified:
        """ 
        An `EpisodePageSimplified` object that allows for multiple pages of episodes to be navigated.        
        """
        return self._Episodes
    
    @Episodes.setter
    def Episodes(self, value:str):
        """ 
        Sets the Episodes property value.
        """
        if value is not None:
            if isinstance(value, EpisodePageSimplified):
                self._Episodes = value


    @property
    def PlaylistsCount(self) -> int:
        """ 
        The total number of playlist items returned in the `Tracks.Items` collection
        """
        if self._Playlists is not None:
            return self._Playlists.ItemsCount
        return 0


    @property
    def Playlists(self) -> PlaylistPageSimplified:
        """ 
        An `PlaylistPageSimplified` object that allows for multiple pages of playlists to be navigated.        
        """
        return self._Playlists
    
    @Playlists.setter
    def Playlists(self, value:str):
        """ 
        Sets the Playlists property value.
        """
        if value is not None:
            if isinstance(value, PlaylistPageSimplified):
                self._Playlists = value


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
        The total number of show items returned in the `Tracks.Items` collection
        """
        if self._Shows is not None:
            return self._Shows.ItemsCount
        return 0


    @property
    def Shows(self) -> ShowPageSimplified:
        """ 
        An `ShowPageSimplified` object that allows for multiple pages of shows to be navigated.        
        """
        return self._Shows
    
    @Shows.setter
    def Shows(self, value:str):
        """ 
        Sets the Shows property value.
        """
        if value is not None:
            if isinstance(value, ShowPageSimplified):
                self._Shows = value


    @property
    def TracksCount(self) -> int:
        """ 
        The total number of track items returned in the `Tracks.Items` collection
        """
        if self._Tracks is not None:
            return self._Tracks.ItemsCount
        return 0


    @property
    def Tracks(self) -> TrackPage:
        """ 
        A `TrackPage` object that allows for multiple pages of tracks to be navigated.        
        """
        return self._Tracks
    
    @Tracks.setter
    def Tracks(self, value:str):
        """ 
        Sets the Tracks property value.
        """
        if value is not None:
            if isinstance(value, TrackPage):
                self._Tracks = value


    def GetSpotifyOwnedPlaylists(self) -> list[PlaylistSimplified]:
        """ 
        Gets a list of all playlists contained in the underlying `Playlists` list
        that are owned by `spotify:user:spotify`.
        """
        result:list[PlaylistSimplified] = []
        item:PlaylistSimplified
        for item in self._Playlists.Items:
            if item.Owner is not None:
                if item.Owner.Uri == "spotify:user:spotify":
                    result.append(item)
                    
        # sort items on Name property, ascending order.
        if len(result) > 0:
            result.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

        # return to caller.
        return result
    
        
    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        albums:dict = {}
        if self._Albums is not None:
            albums = self._Albums.ToDictionary()

        artists:dict = {}
        if self._Artists is not None:
            artists = self._Artists.ToDictionary()

        audiobooks:dict = {}
        if self._Audiobooks is not None:
            audiobooks = self._Audiobooks.ToDictionary()

        episodes:dict = {}
        if self._Episodes is not None:
            episodes = self._Episodes.ToDictionary()

        playlists:dict = {}
        if self._Playlists is not None:
            playlists = self._Playlists.ToDictionary()

        shows:dict = {}
        if self._Shows is not None:
            shows = self._Shows.ToDictionary()

        tracks:dict = {}
        if self._Tracks is not None:
            tracks = self._Tracks.ToDictionary()

        result:dict = \
        {
            'search_criteria': self._SearchCriteria,
            'search_criteria_type': self._SearchCriteriaType,
            'albums_count': self.AlbumsCount,
            'albums': albums,
            'artists_count': self.ArtistsCount,
            'artists': artists,
            'audiobooks_count': self.AudiobooksCount,
            'audiobooks': audiobooks,
            'episodes_count': self.EpisodesCount,
            'episodes': episodes,
            'playlists_count': self.PlaylistsCount,
            'playlists': playlists,
            'shows_count': self.ShowsCount,
            'shows': shows,
            'tracks_count': self.TracksCount,
            'tracks': tracks,
        }
        return result
        

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
        msg = '%s\n Audiobooks Count=%s' % (msg, str(self.AudiobooksCount))
        msg = '%s\n Episodes Count=%s' % (msg, str(self.EpisodesCount))
        msg = '%s\n Playlists Count=%s' % (msg, str(self.PlaylistsCount))
        msg = '%s\n Shows Count=%s' % (msg, str(self.ShowsCount))
        msg = '%s\n Tracks Count=%s' % (msg, str(self.TracksCount))
        return msg 
