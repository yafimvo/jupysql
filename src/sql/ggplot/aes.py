
class aes():
    def __init__(self,
                 x=None,
                 y=None,
                 cmap=None,
                 fill=None):
        """
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
        self.x = x
        self.y = y
        self.cmap = cmap
        self.fill = fill

    def __radd__(self, gg):
        gg.mapping.x = self.x
        gg.mapping.y = self.y
        gg.mapping.cmap = self.cmap
        gg.mapping.fill = self.fill
        return gg
