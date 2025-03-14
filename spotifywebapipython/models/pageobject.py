# our package imports.
from ..sautils import export

@export
class PageObject:
    """
    Spotify Web API PageObject object.
    
    This allows for multiple pages of objects to be navigated.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._CursorAfter:object = None
        self._CursorBefore:object = None
        self._DateLastRefreshed:float = 0
        self._Href:str = None
        self._IsCursor:bool = False
        self._Items:list[object] = []
        self._Limit:int = 0
        self._Next:str = None
        self._Offset:int = 0
        self._Previous:str = None
        self._Total:int = 0
        
        if (root is None):

            pass
        
        else:

            self._Href = root.get('href', None)
            self._Limit = root.get('limit', 0)
            self._Next = root.get('next', None)
            self._Offset = root.get('offset', 0)
            self._Previous = root.get('previous', None)
            self._Total = root.get('total', 0)
            
            # process all collections and objects.
            item:dict = root.get('cursors',None)
            if item is not None:
                self._IsCursor = True
                self._CursorAfter = item.get('after', None)
                self._CursorBefore = item.get('before', None)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def CursorAfter(self) -> object:
        """ 
        The cursor to use as key to find the next page of items.  
        This value will only be populated when cursor-based paging is used, which is infrrequent.
        The value can be of multiple types: string, integer, etc.
        
        Example: `3jdODvx7rIdq0UGU7BOVR3`
        Example: 1708495520273

        """
        return self._CursorAfter

    @CursorAfter.setter
    def CursorAfter(self, value:object):
        """ 
        Sets the CursorAfter property value.
        """
        self._IsCursor = True
        self._CursorAfter = value


    @property
    def CursorBefore(self) -> object:
        """ 
        The cursor to use as key to find the previous page of items.  
        This value will only be populated when cursor-based paging is used, which is infrrequent.
        The value can be of multiple types: string, integer, etc.
        
        Example: `3jdODvx7rIdq0UGU7BOVR3`
        Example: 1708495520273
        """
        return self._CursorBefore

    @CursorBefore.setter
    def CursorBefore(self, value:object):
        """ 
        Sets the CursorBefore property value.
        """
        self._IsCursor = True
        self._CursorBefore = value


    @property
    def DateLastRefreshed(self) -> float:
        """ 
        Date and time items were was last refreshed, in unix epoch format (e.g. 1669123919.331225).
        A value of zero indicates the date was unknown.
        
        Note that this attribute does not exist in the Spotify Web API; 
        it was added here for convenience.
        """
        return self._DateLastRefreshed
    
    @DateLastRefreshed.setter
    def DateLastRefreshed(self, value:float):
        """ 
        Sets the DateLastRefreshed property value.
        """
        if (value is None):
            self._DateLastRefreshed = 0
        elif isinstance(value, float):
            self._DateLastRefreshed = value
        elif isinstance(value, int):
            self._DateLastRefreshed = float(value)


    @property
    def Href(self) -> str:
        """ 
        A link to the Web API endpoint returning the full result of the request.
        
        Example: `https://api.spotify.com/v1/me/shows?offset=0&limit=20`
        """
        return self._Href


    @property
    def IsCursor(self) -> bool:
        """ 
        True if cursors were returned at some point during the life of this paging object.
        """
        return self._IsCursor
    

    @property
    def Items(self) -> list[object]:
        """ 
        Array of objects.
        
        This property will be overrriden by inheriting classes.
        """
        return self._Items
    

    @property
    def ItemsCount(self) -> int:
        """ 
        Number of objects in the `Items` property array.
        """
        if self._Items is not None:
            return len(self._Items)
        return 0
    

    @property
    def Limit(self) -> int:
        """ 
        The maximum number of items in the response (as set in the query or by default).
        
        This property can be modified in case the paging request needs to be adjusted
        based upon overall request limits.
        """
        return self._Limit

    @Limit.setter
    def Limit(self, value:int):
        """ 
        Sets the Limit property value.
        """
        if value is not None:
            if isinstance(value, int):
                self._Limit = value


    @property
    def Next(self) -> str:
        """ 
        URL to the next page of items; null if none.
        
        Example: `https://api.spotify.com/v1/me/shows?offset=1&limit=1`
        """
        return self._Next


    @property
    def Offset(self) -> int:
        """ 
        The offset of the items returned (as set in the query or by default).
        
        This property can be modified in case the paging request needs to be adjusted
        based upon overall request limits.
        """
        return self._Offset

    @Offset.setter
    def Offset(self, value:int):
        """ 
        Sets the Offset property value.
        """
        if value is not None:
            if isinstance(value, int):
                self._Offset = value


    @property
    def PagingInfo(self) -> str:
        """
        Returns a displayable string of paging parameters.
        
        The return value will vary, based upon if a cursor is used to navigate the results.
        Most methods don't use cursors, but there are a few that do (e.g. `GetArtistsFollowed`).
        
        For a "(items {start} to {end} of {total} total)" message, the `start` value is the
        offset value of the last page of items retrieved.
        """
        endValue:int = (self._Limit + self._Offset)
        if endValue > self._Total:
            endValue = self._Total
        
        # is page using cursor results?
        if self._IsCursor:
            
            msgAfter:str = ''
            msgBefore:str = ''
            msgComma = ''
            
            if self._CursorAfter is not None:
                msgAfter = 'after cursor "%s"' % str(self._CursorAfter)
            if self._CursorBefore is not None:
                msgBefore = 'before cursor "%s"' % str(self._CursorBefore)
                if len(msgAfter) > 0:
                    msgComma = ', '
            if self._CursorAfter is None and self._CursorBefore is None:
                msgComma = 'last page'
                
            msg:str = '(%s%s%s)' % (msgBefore, msgComma, msgAfter)
                        
        # is this the last page of cursor results?
        elif self._Total == 0 and endValue == 0:

            msg:str = '(last page)'
            
        else:
            
            msg:str = '(items {start} to {end} of {total} total)'.format(start=str(self._Offset + 1), 
                                                                         end=str(endValue),
                                                                         total=str(self._Total))

        return msg 
    

    @property
    def Previous(self) -> str:
        """ 
        URL to the previous page of items; null if none.
        
        Example: `https://api.spotify.com/v1/me/shows?offset=1&limit=1`
        """
        return self._Previous


    @property
    def Total(self) -> int:
        """ 
        The total number of items available from the Spotify Web API to return.
        
        Note that sometimes the Spotify Web API returns a larger total than the actual number 
        of items available.  Not sure why this is, but it may not match the `ItemsCount` value.
        """
        return self._Total

    @Total.setter
    def Total(self, value:int):
        """ 
        Sets the Total property value.
        """
        if value is not None:
            if isinstance(value, int):
                self._Total = value


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'date_last_refreshed': self._DateLastRefreshed,
            'href': self._Href,
            'limit': self._Limit,
            'next': self._Next,
            'offset': self._Offset,
            'previous': self._Previous,
            'total': self._Total,
            'items': [ item.ToDictionary() for item in self._Items ],
        }

        # only add cursors if they are populated.
        if self._CursorAfter is not None:
            result['cursor_after'] = self._CursorAfter
        if self._CursorBefore is not None:
            result['cursor_before'] = self._CursorBefore

        return result
        

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        msg:str = '%s' % self.PagingInfo
        msg = '%s\n Href="%s"' % (msg, str(self._Href))
        msg = '%s\n Limit="%s"' % (msg, str(self._Limit))
        msg = '%s\n Next="%s"' % (msg, str(self._Next))
        msg = '%s\n Offset="%s"' % (msg, str(self._Offset))
        msg = '%s\n Previous="%s"' % (msg, str(self._Previous))
        msg = '%s\n Total="%s"' % (msg, str(self._Total))
        msg = '%s\n Items Count="%s"' % (msg, str(self.ItemsCount))
        msg = '%s\n DateLastRefreshed=%s' % (msg, str(self._DateLastRefreshed))
        if self._CursorAfter is not None: msg = '%s\n Cursor After="%s"' % (msg, str(self._CursorAfter))
        if self._CursorBefore is not None: msg = '%s\n Cursor Before="%s"' % (msg, str(self._CursorBefore))
        
        if (includeItems):
            if self.Items is not None: msg = '%s\n\n %s' % (msg, str(self.Items))
            
        return msg 
