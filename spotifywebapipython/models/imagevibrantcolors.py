# external package imports.
from ..vibrant import Palette

# our package imports.
from ..sautils import export

@export
class ImageVibrantColors:
    """
    Image Vibrant Colors object.
    """

    def __init__(self, root:Palette=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (Palette):
                Vibrant Palette object that contains extracted color information used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._DarkMuted:str = None
        self._DarkVibrant:str = None
        self._LightMuted:str = None
        self._LightVibrant:str = None
        self._Muted:str = None
        self._Vibrant:str = None
        
        if (not isinstance(root, Palette)):

            pass
        
        else:

            # add vibrant color palette RGB information to results.
            self._DarkMuted = f"#{root.dark_muted.rgb[0]:02x}{root.dark_muted.rgb[1]:02x}{root.dark_muted.rgb[2]:02x}"
            self._DarkVibrant = f"#{root.dark_vibrant.rgb[0]:02x}{root.dark_vibrant.rgb[1]:02x}{root.dark_vibrant.rgb[2]:02x}"
            self._LightMuted = f"#{root.light_muted.rgb[0]:02x}{root.light_muted.rgb[1]:02x}{root.light_muted.rgb[2]:02x}"
            self._LightVibrant = f"#{root.light_vibrant.rgb[0]:02x}{root.light_vibrant.rgb[1]:02x}{root.light_vibrant.rgb[2]:02x}"
            self._Muted = f"#{root.muted.rgb[0]:02x}{root.muted.rgb[1]:02x}{root.muted.rgb[2]:02x}"
            self._Vibrant = f"#{root.vibrant.rgb[0]:02x}{root.vibrant.rgb[1]:02x}{root.vibrant.rgb[2]:02x}"

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def DarkMuted(self) -> str:
        """ 
        A dark but muted version of the color palette.  

        This value represents a dark, muted color from the image, meaning the color is darker than
        others in the image and has lower saturation. The resulting color is not vibrant or bright 
        but still retains some of the overall mood or tone of the image.  

        This value is typically used when you want a darker, less intense color that adds subtle depth 
        to a design. It's great for backgrounds, sidebars, or any UI element where you want a muted, 
        non-intrusive tone.  
        """
        return self._DarkMuted


    @property
    def DarkVibrant(self) -> str:
        """ 
        A darker and vibrant version of the dominant color.  

        This value represents a darker shade of the vibrant dominant color, retaining its saturation 
        and richness.  It's typically used when you want to use a darker variant of the most dominant 
        color in the image, but still with significant visual impact.  

        This value is commonly used for prominent elements that need to stand out in a dark color 
        palette, like header bars, call-to-action buttons, or elements that need to grab attention 
        but in a muted, dark fashion.  
        """
        return self._DarkVibrant


    @property
    def LightMuted(self) -> str:
        """ 
        A lighter but muted version of the color palette.  

        This value represents a light color with low saturation. It's a softer and more desaturated 
        version of the most prominent light color in the image.  

        This value is great for when you need a color that won't draw too much attention but still 
        provides a harmonious tone. It can be used for backgrounds, UI components, or designs that need 
        to remain visually calm or neutral.  
        """
        return self._LightMuted


    @property
    def LightVibrant(self) -> str:
        """ 
        A lighter and vibrant version of the dominant color.  

        This value represents a light, saturated color that retains vibrancy. It's less dark than the 
        darkVibrant swatch, but it maintains high saturation, making it stand out in designs that require 
        a colorful but light tone.  

        This value is typically used for elements that need to draw attention in a design without being 
        overpowering. It's useful for buttons, highlights, or icons that need to stand out in a bright, 
        colorful design while maintaining a softer appearance compared to darker vibrant tones.  
        """
        return self._LightVibrant


    @property
    def Muted(self) -> str:
        """ 
        A color that is less saturated and has a softer tone.  

        This value corresponds to a color that is desaturated or toned down. While it may be one of the 
        prominent colors in the image, its saturation is significantly reduced, making it softer and more 
        subtle compared to the vibrant color.  

        This value is useful in situations where you want a color that's not overpowering but still retains 
        visual presence. It works well for backgrounds, borders, or UI components that should be visible without 
        grabbing too much attention.  
        """
        return self._Muted


    @property
    def Vibrant(self) -> str:
        """ 
        The most dominant, bright, and saturated color in the image.  

        This value corresponds to the most vibrant color from the image, meaning it's the most saturated and 
        intense color found in the image. It's the color that grabs attention due to its brightness and boldness.  

        This value is ideal for creating designs that need a bold, eye-catching focal point. It can be used for 
        accent colors, calls to action (CTAs), buttons, and any design element where you want the color to stand 
        out and be visually stimulating.  
        """
        return self._Vibrant


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'dark_muted': self._DarkMuted,
            'dark_vibrant': self._DarkVibrant,
            'light_muted': self._LightMuted,
            'light_vibrant': self._LightVibrant,
            'muted': self._Muted,
            'vibrant': self._Vibrant,
        }
        return result
        

    def ToString(self, includeTitle:bool=True) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeTitle (str):
                True to include the class name title prefix.
        """
        msg:str = ''
        if includeTitle: 
            msg = 'ImageVibrantColors:'
        
        msg = '%s\n DarkMuted="%s"' % (msg, str(self._DarkMuted))
        msg = '%s\n DarkVibrant="%s"' % (msg, str(self._DarkVibrant))
        msg = '%s\n LightMuted="%s"' % (msg, str(self._LightMuted))
        msg = '%s\n LightVibrant="%s"' % (msg, str(self._LightVibrant))
        msg = '%s\n Muted="%s"' % (msg, str(self._Muted))
        msg = '%s\n Vibrant="%s"' % (msg, str(self._Vibrant))
        return msg 
