# our package imports.
from spotifywebapipython.models import SpotifyConnectDevice


class SpotifyConnectDeviceEventArgs:
    """
    Class used by various methods that inform interested parties that a Spotify
    Connect device update has occured.

    Threadsafety:
        This class is fully thread-safe.
    """
    def __init__(self, device:SpotifyConnectDevice) -> None:
        """
        Initializes a new instance of the class.

        Args:
            device (SpotifyConnectDevice):
                Spotify Connect device object that was affected.
        """

        # initialize instance.
        self._DeviceObject:SpotifyConnectDevice = device


    @property
    def DeviceObject(self) -> SpotifyConnectDevice:
        """
        Spotify Connect device object that was affected.
        """
        return self._DeviceObject

    @DeviceObject.setter
    def DeviceObject(self, value:str) -> None:
        """ 
        Sets the DeviceObject property value.
        """
        if (isinstance(value, SpotifyConnectDevice)):
            self._DeviceObject = value


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "SpotifyConnectDeviceEventArgs: {status}".
        """
        return str.format("SpotifyConnectDeviceEventArgs: {0}", self._DeviceObject or "")


class SpotifyConnectDeviceEventHandler:
    """
    Event handler type definition for an event.
    """

    def __init__(self, sender:object, e:SpotifyConnectDeviceEventArgs) -> None:
        """
        Initializes a new instance of the class.

        Args:
            sender (object):
                The object which fired the event.
            e (SpotifyConnectDeviceEventArgs):
                Arguments that contain detailed information related to the event,
                and canceling of its processing.
        """
