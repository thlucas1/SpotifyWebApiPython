# external package imports.

# our package imports.
from ..sautils import export
from .audiobooksimplified import AudiobookSimplified
from .chapterpagesimplified import ChapterPageSimplified

@export
class Audiobook(AudiobookSimplified):
    """
    Spotify Web API Audiobook object.
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
        
        self._Chapters:ChapterPageSimplified = None
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            item:dict = root.get('chapters',None)
            if item is not None:
                self._Chapters = ChapterPageSimplified(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Chapters(self) -> ChapterPageSimplified:
        """ 
        The chapters of the audiobook.
        
        This is a `ChapterPageSimplified` object.
        """
        return self._Chapters


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        # get base class result.
        resultBase:dict = super().ToDictionary()

        chapters:dict = {}
        if self._Chapters is not None:
            chapters = self._Chapters.ToDictionary()

        result:dict = \
        {
            'chapters': chapters
        }
        
        # combine base class results with these results.
        resultBase.update(result)
        
        # return a sorted dictionary.
        return resultBase
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Audiobook: %s' % super().ToString(False)
        if self._Chapters is not None: msg = '%s\n Chapter Count=%s' % (msg, str(self._Chapters.Total))
        return msg 
