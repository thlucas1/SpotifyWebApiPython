# external package imports.

# our package imports.
from ..sautils import export
from .imageobject import ImageObject

@export
class Category:
    """
    Spotify Web API Category object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Href:str = None
        self._Id:str = None
        self._Icons:list[ImageObject] = []
        self._Name:str = None
        

        if (root is None):

            pass
        
        else:

            self._Href = root.get('href', None)
            self._Id = root.get('id', None)
            self._Name = root.get('name', None)

            # process all collections and objects.
            items:list = root.get('icons',[])
            for item in items:
                self._Icons.append(ImageObject(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception as ex:
            if (isinstance(self, Category )) and (isinstance(other, Category )):
                return self.Name == other.Name
            return False

    def __lt__(self, other):
        try:
            return self.Name < other.Name
        except Exception as ex:
            if (isinstance(self, Category )) and (isinstance(other, Category )):
                return self.Name < other.Name
            return False


    @property
    def Href(self) -> str:
        """ 
        A link to the Web API endpoint returning full details of the category.
        """
        return self._Href


    @property
    def Id(self) -> str:
        """ 
        The Spotify category ID of the category.  
        Some ID's are read-able text, while most are a unique id format.
        
        Example: `toplists`  
        Example: `0JQ5DAqbMKFDXXwE9BDJAr`  (e.g. unique id for `Rock`)
        """
        return self._Id


    @property
    def Icons(self) -> list[ImageObject]:
        """ 
        The category icon in various sizes, widest first.
        """
        return self._Icons


    @property
    def Name(self) -> str:
        """ 
        The name of the category.
        """
        return self._Name


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'href': self._Href,
            'icons': [ item.ToDictionary() for item in self._Icons ],
            'id': self._Id,
            'name': self._Name,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Category:'
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._Icons is not None: msg = '%s\n Icons Count=%s' % (msg, str(len(self._Icons)))
        return msg
