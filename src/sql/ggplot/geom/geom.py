class geom():
    """
    Base class of all geom
    """

    def __init__(self, fill=None, color=None):
        """
        fill : str
            The inner color of shape

        color : str, default 'None'
            The edge color of shape
        """
        self.fill = fill
        self.color = color
