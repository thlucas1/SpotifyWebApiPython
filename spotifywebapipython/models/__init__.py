# import all classes from the namespace.
from .album import Album, AlbumSimplified
from .albumpagesaved import AlbumPageSaved, AlbumSaved
from .albumpagesimplified import AlbumPageSimplified
from .artist import Artist, ArtistSimplified
from .artistinfo import ArtistInfo, ArtistInfoTourEvent
from .artistpage import ArtistPage
from .audiobook import Audiobook, AudiobookSimplified
from .audiobookpagesimplified import AudiobookPageSimplified
from .audiofeatures import AudioFeatures
from .author import Author
from .category import Category
from .categorypage import CategoryPage
from .chapter import Chapter, ChapterSimplified
from .chapterpagesimplified import ChapterPageSimplified
from .context import Context
from .copyright import Copyright
from .device import Device
from .episode import Episode, EpisodeSimplified
from .episodepagesaved import EpisodePageSaved, EpisodeSaved
from .episodepagesimplified import EpisodePageSimplified
from .explicitcontent import ExplicitContent
from .externalids import ExternalIds
from .externalurls import ExternalUrls
from .followers import Followers
from .imageobject import ImageObject
from .imagevibrantcolors import ImageVibrantColors
from .narrator import Narrator
from .owner import Owner
from .pageobject import PageObject
from .playeractions import PlayerActions
from .playerplaystate import PlayerPlayState
from .playerqueueinfo import PlayerQueueInfo
from .playhistory import PlayHistory
from .playhistorypage import PlayHistoryPage
from .playlist import Playlist, PlaylistSimplified
from .playlistpage import PlaylistPage
from .playlistpagesimplified import PlaylistPageSimplified
from .playlisttrack import PlaylistTrack
from .playlisttracksummary import PlaylistTrackSummary
from .recommendationseed import RecommendationSeed
from .restrictions import Restrictions
from .resumepoint import ResumePoint
from .searchresponse import SearchResponse
from .show import Show, ShowSimplified
from .showpagesaved import ShowPageSaved, ShowSaved
from .showpagesimplified import ShowPageSimplified
from .spotifyconnectdevices import SpotifyConnectDevices, SpotifyConnectDevice
from .track import Track, TrackSimplified
from .trackpage import TrackPage
from .trackpagesaved import TrackPageSaved, TrackSaved
from .trackpagesimplified import TrackPageSimplified
from .trackrecommendations import TrackRecommendations
from .userprofile import UserProfile, UserProfileSimplified
from .zeroconfdiscoveryresult import ZeroconfDiscoveryResult
from .zeroconfproperty import ZeroconfProperty

# all classes to import when "import *" is specified.
__all__ = [
    'Album','AlbumSimplified',
    'AlbumPageSaved','AlbumSaved',
    'AlbumPageSimplified',
    'Artist','ArtistSimplified',
    'ArtistInfo', 'ArtistInfoTourEvent',
    'ArtistPage',
    'Audiobook','AudiobookSimplified',
    'AudiobookPageSimplified',
    'AudioFeatures',
    'Author',
    'Category',
    'CategoryPage',
    'Chapter','ChapterSimplified',
    'ChapterPageSimplified',
    'Context',
    'Copyright',
    'Device',
    'Episode','EpisodeSimplified',
    'EpisodePageSaved','EpisodeSaved',
    'EpisodePageSimplified',
    'ExplicitContent',
    'ExternalIds',
    'ExternalUrls',
    'Followers',
    'ImageObject',
    'ImageVibrantColors',
    'Narrator',
    'Owner',
    'PageObject',
    'PlayerActions',
    'PlayerPlayState',
    'PlayerQueueInfo',
    'PlayHistory',
    'PlayHistoryPage',
    'Playlist','PlaylistSimplified',
    'PlaylistPage',
    'PlaylistPageSimplified',
    'PlaylistTrack',
    'PlaylistTrackSummary',
    'RecommendationSeed',
    'Restrictions',
    'ResumePoint',
    'SearchResponse',
    'Show','ShowSimplified',
    'ShowPageSaved','ShowSaved',
    'ShowPageSimplified',
    'SpotifyConnectDevices', 'SpotifyConnectDevice',
    'Track','TrackSimplified',
    'TrackPage',
    'TrackPageSaved','TrackSaved',
    'TrackPageSimplified',
    'TrackRecommendations',
    'UserProfile','UserProfileSimplified',
    'ZeroconfDiscoveryResult',
    'ZeroconfProperty',
]
