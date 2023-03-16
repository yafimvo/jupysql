from sql.ggplot.aes import aes
from sql.ggplot.geom.geom import geom
import matplotlib as mpl
import matplotlib.pyplot as plt


def _create_single_panel_ax():
    # figure = plt.figure()
    # ax = plt.gca()
    figure, ax = plt.subplots()
    axs = [ax]
    return figure, axs


class ggplot:
    """
    Create a new ggplot
    """
    figure: mpl.figure.Figure
    # axs: list[mpl.axes.Axes]

    def __init__(self, table, mapping: aes = None, conn=None, with_=None) -> None:
        self.table = table
        self.with_ = [with_] if with_ else None
        self.mapping = mapping if mapping is not None else aes()
        self.conn = conn

        figure, axs = _create_single_panel_ax()

        self.ax = axs[0]
        self.figure = figure

    def __exit__(self) -> str:
        print("draw....")

    def __add__(self, other) -> 'ggplot':
        """
        Add to ggplot
        """
        print("adding ggplot 1", type(aes))
        self._draw(other)
        return self.__iadd__(other)

    def __iadd__(self, other):
        print("adding ggplot 2", type(other))
        return other.__add__(self)

    # def __add__(self, other) -> 'ggplot':
    #     """
    #     Add to ggplot
    #     """
    #     print("adding ggplot 1", type(aes))
    #     return self.__iadd__(other)

    # def __iadd__(self, other: aes) -> 'ggplot':
    #     """
    #     Add aes to ggplot
    #     """
    #     # if isinstance(other, geom):
    #     #     other.draw(self)

    #     # if isinstance(other, aes):
    #     #     # todo: self.mapping = aes
    #     #     self.mapping.x = other.x
    #     #     self.mapping.y = other.y
    #     #     self.mapping.cmap = other.cmap
    #     #     self.mapping.fill = other.fill

    #     return other.__radd__(self)

    def draw(self, other) -> mpl.figure.Figure:
        # setup
        figure, axs = _create_single_panel_ax()
        print("herehere")
        # self._setup_parameters()
        # self.facet.strips.generate()  # type: ignore[attr-defined]
        # self._resize_panels()
        plt.show()
        self.figure = figure
        return self.figure

    def _draw(self, other) -> mpl.figure.Figure:
        if isinstance(other, geom):
            other.draw(self)

        # if isinstance(other, aes):
        #     # todo: self.mapping = aes
        #     self.mapping.x = other.x
        #     self.mapping.y = other.y
        #     self.mapping.cmap = other.cmap
        #     self.mapping.fill = other.fill

        return self.figure

    def get_base(self, object):
        for base in object.__class__.__bases__:
            return base.__name__
