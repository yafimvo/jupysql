from abc import abstractmethod


class geom:
    """
    Base class of all geom

    Parameters
    ----------
    fill : str
        The inner color of a shape

    color : str, default 'None'
        The edge color of a shape
    """

    def __init__(self, fill=None, color=None):
        self.fill = fill
        self.color = color

    def __add__(self, gg):
        return gg

    def __radd__(self, gg):
        return gg + self

    @abstractmethod
    def draw(self, gg):
        """
        Draws plot
        """
        pass