# external package imports.
from datetime import datetime, timedelta, timezone
import sys

"""
Utility module of helper functions.
"""

SONOS_NOT_IMPLEMENTED:str = 'NOT_IMPLEMENTED'


def GetUnixTimestampMSFromUtcNow(days:int=0,
                                 hours:int=0,
                                 minutes:int=0,
                                 seconds:int=0,
                                 ) -> int:
    """
    Returns a Unix millisecond timestamp value from the current utc datetime for the
    difference specified by input arguments.
    
    """
    # get current utc datetime (in a timezone aware datetime instance).
    dtUtc:datetime = datetime.now(timezone.utc)
    
    # get offset timedelta.
    dtUtcOffset = (dtUtc + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds))
    
    # convert to unix timestamp (# of seconds since epoch date of 1970/01/01).
    dtUtcUnixTS:float = dtUtcOffset.timestamp()

    # convert to milliseconds.
    dtUtcUnixTSMS:int = int(dtUtcUnixTS * 1000)
    
    # return unix milliseconds timestamp value.
    return dtUtcUnixTSMS


def passwordMaskString(inputObj:str) -> str:
    """
    Checks a string for a password value and masks the value so that the password is not displayed 
    in a trace file.

    Args:
        inputObj (str):
            String object to check.
    
    Returns:
        A copy of the `inputObj` value with password masked.
    """
    # if input is null then don't bother.
    if (inputObj is None):
        return inputObj
    
    # create a new value.
    result:str = ''.ljust(len(inputObj), '*')
                
    return result


def mediaPositionHMS_fromSeconds(
    position:int, 
    ) -> float:
    """
    Converts an integer media position value from seconds to a string value in H:MM:SS format.
        
    Args:
        position (int):
            The position value (as specified in seconds) to convert.
    """
    result:str = '0:00:00'
    
    # validations.
    if (isinstance(position, float)):
        position = int(position)
    if (position is None) or (position < 1):
        return result            

    # convert seconds to H:MM:SS string format.
    nSeconds = int(position)
    mm, ss = divmod(nSeconds, 60)            # get minutes and seconds first
    hh, mm= divmod(mm, 60)                   # get hours next
    result = "%d:%02d:%02d" % (hh, mm, ss)   # format to hh:mm:ss
    
    # return result to caller.
    return result


def mediaPositionHMS_toSeconds(
    timestr:str
    ) -> int:
    """
    Convert an "HH:MM:SS" string value to total number of seconds.
        
    Args:
        timestr (int):
            The position value (as specified in H:MM:SS) to convert.
    """
    if (timestr is None) or (timestr == '') or (timestr == SONOS_NOT_IMPLEMENTED): 
        return 0
        
    seconds= 0
    for part in timestr.split(':'):
        seconds= seconds*60 + int(part, 10)
    return seconds


def static_init(cls):
    """
    Define the decorator used to call an initializer for a class with all static methods.
    This allows static variables to be initialized one time for the class.
    """
    if getattr(cls, "static_init", None):
        cls.static_init()
    return cls


def export(fn):
    """
    Define the decorator used to modify a module's "__all__" variable.
    This avoids us having to manually modify a module's "__all__" variable when adding new classes.
    """
    mod = sys.modules[fn.__module__]
    if hasattr(mod, '__all__'):
        mod.__all__.append(fn.__name__)
    else:
        mod.__all__ = [fn.__name__]

    return fn
    

def validateDelay(
        delay:float, 
        default:float=0.5, 
        maxDelay:float=10
        ) -> float:
    """
    Validates a delay value.
        
    Args:
        delay (int):
            The delay value to validate.
        default (int):
            The default delay value to set if the user-input delay is not valid.
        maxDelay (int):
            The maximum delay value allowed.  
            Default is 10.
    """
    if (isinstance(delay,int)): 
        delay = float(delay)
            
    if (not isinstance(delay,float)) or (delay < 0): 
        result = default
    elif (delay > maxDelay): 
        result = maxDelay
    else:
        result = delay
            
    return result


def _xmlGetInnerText(elmNode, default:str=None) -> str:
    """
    Finds the specified xml node inner text from the root Element object and returns its value
    as a string.  The default argument is returned if the xml node name is not found.
    
    Args:
        root (xml.etree.ElementTree.Element)
            The Element object to search.
        default (str):
            A default value to assign if the xml node does not contain innerText.
            
    Returns:
        The string value if innerText was found; 
        otherwise, the default value.
    """
    if elmNode is None:
        return default
    
    # get text of all child nodes.
    innertext:str = (elmNode.text or '') + ''.join(_xmlGetInnerText(e) for e in elmNode) + (elmNode.tail or '')
    
    # did we find anything?  if not, then return default.
    if innertext is None:
        return default
    
    # return found inner text.
    return innertext


class Event:
    """
    C# like event processing in Python3.

    <details>
        <summary>View Sample Code</summary>
    ```python
    # Define the class that will be raising events:
    class MyFileWatcher:
        def __init__(self):
            self.fileChanged = Event()      # define event

        def watchFiles(self):
            source_path = "foo"
            self.fileChanged(source_path)   # fire event

    def log_file_change(source_path):       # event handler 1
        print "%r changed." % (source_path,)

    def log_file_change2(source_path):      # event handler 2
        print "%r changed!" % (source_path,)

    # Define the code that will be handling raised events.
    watcher              = MyFileWatcher()
    watcher.fileChanged += log_file_change2
    watcher.fileChanged += log_file_change
    watcher.fileChanged -= log_file_change2
    watcher.watchFiles()
    ```
    </details>
    """

    def __init__(self, *args) -> None:
        """
        Initializes a new instance of the class.
        """
        self.handlers = set()

    def fire(self, *args, **kargs):
        """
        Calls (i.e. "fires") all method handlers defined for this event.

        Exceptions will be ignored for individual handlers.
        """
        for handler in self.handlers:
            try:
                handler(*args, **kargs)
            except:
                pass

    def getHandlerCount(self):
        """
        Returns the number of method handlers defined for this event.
        """
        return len(self.handlers)

    def handle(self, handler):
        """
        Adds a method handler for this event.
        """
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        """
        Removes the specified method handler for this event.

        Args:
            handler (object):
                The method handler to remove.

        This method will not throw an exception.
        """
        try:
            self.handlers.remove(handler)
        except:
            pass   # ignore exceptions.
        return self

    def unhandle_all(self):
        """
        Removes all method handlers (if any) for this event.

        This method will not throw an exception.
        """
        try:
            self.handlers.clear()
        except:
            pass   # ignore exceptions.
        return self

    # alias method definitions.
    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount
