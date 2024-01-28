# external package imports.

# our package imports.
from ..sautils import export
from .chaptersimplified import ChapterSimplified
from .audiobooksimplified import AudiobookSimplified

@export
class Chapter(ChapterSimplified):
    """
    Spotify Web API Chapter object.
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
        super().__init__(root=root)
        
        self._Audiobook:AudiobookSimplified = None
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            item:dict = root.get('audiobook',None)
            if item is not None:
                self._Audiobook = AudiobookSimplified(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Audiobook(self) -> AudiobookSimplified:
        """ 
        The audiobook for which the chapter belongs.
        
        This is a `AudiobookSimplified` object.
        """
        return self._Audiobook


    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Chapter: %s' % super().ToString(False)
        if self._Audiobook is not None: msg = '%s\n Audiobook Name="%s"' % (msg, str(self._Audiobook.Name))
        return msg

