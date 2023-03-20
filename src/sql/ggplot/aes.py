
class aes():
    """
    Aesthetic mappings

    Parameters
    ----------
    x: str | list
        x aesthetic mapping

    y: str | list
        y aesthetic mapping

    fill : str
        Create a stacked graph which is a combination of
        'x' and 'fill'

    cmap : str, default 'viridis
        Apply a color map to the stacked graph
    """

    def __init__(self,
                 x=None,
                 y=None,
                 cmap=None,
                 fill=None):
        self.x = x
        self.y = y
        self.cmap = cmap
        self.fill = fill

    # def __radd__(self, gg):
    #     print("add aes 1")
    #     # gg.mapping.x = self.x
    #     # gg.mapping.y = self.y
    #     # gg.mapping.cmap = self.cmap
    #     # gg.mapping.fill = self.fill
    #     gg + self
    #     return gg

    # def __add__(self, gg):
    #     print("add aes 2")
    #     gg.mapping.x = self.x
    #     gg.mapping.y = self.y
    #     gg.mapping.cmap = self.cmap
    #     gg.mapping.fill = self.fill
    #     return gg

    # def __add__(self, gg):
    #     print("adding aes 2 ", type(gg))
    #     return gg
        # return self.__radd__(other)

    # def __radd__(self, gg):
    #     print("adding aes 2", type(gg))
    #     return gg.__radd__(self)