# external package imports.
from typing import List, Tuple

# our package imports.
from ..vibrant import Swatch
from ..sautils import export

@export
class ImagePaletteColors:
    """
    Image Palette Colors object.

    This is a helper class, and is not part of the Spotify Web API specification.
    """

    def __init__(self, root:list[Tuple[int, int, int]]=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (list[Tuple[int, int, int]]):
                A list of color palette Tuple in the form (r, g, b) that contains extracted 
                color palette information; otherwise, None.
        """
        # initialize storage.
        self._ImageSource:str = None
        self._Items:list[Swatch] = []

        if (not isinstance(root, list)):

            pass
        
        else:

            # store color palette information.
            if root is not None:
                for item in root:
                    if item is not None:
                        self._Items.append(Swatch(rgb=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def ImageSource(self) -> str:
        """ 
        Image that was processed to obtain the palette.
        """
        return self._ImageSource

    @ImageSource.setter
    def ImageSource(self, value:str):
        """ 
        Sets the ImageSource property value.
        """
        self._ImageSource = value


    @property
    def Items(self) -> list[Swatch]:
        """ 
        Array of `Swatch` objects.
        """
        return self._Items
    

    @property
    def ItemsCount(self) -> int:
        """ 
        Length of `Items` array.
        """
        return len(self._Items)
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'image_source': self._ImageSource,
            'items_count': self.ItemsCount,
            'items': [ item.ToDictionary() for item in self._Items ],
        }

        return result
        

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        msg:str = 'Swatch:'
        msg = '%s\n ImageSource="%s"' % (msg, str(self._ImageSource))
        msg = '%s\n Items Count="%s"' % (msg, str(self.ItemsCount))
        
        if (includeItems):
            if self.Items is not None: msg = '%s\n\n %s' % (msg, str(self.Items))
            
        return msg 
