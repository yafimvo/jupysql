from sql import plot
from .geom import geom


class geom_histogram(geom):
    """
    Histogram plot

    Parameters
    ----------
    bins: int
        Number of bins
    """

    def __init__(self, bins=None, **kwargs):
        self.bins = bins

        super().__init__(**kwargs)

    def draw(self, gg):
        plot.histogram(table=gg.table,
                       column=gg.mapping.x,
                       cmap=gg.mapping.cmap,
                       bins=self.bins,
                       conn=gg.conn,
                       with_=gg.with_,
                       category=gg.mapping.fill,
                       color=self.fill,
                       edgecolor=self.color,
                       ax=gg.ax
                       )
        return gg

    # def __radd__(self, gg):
    #     p = plot.histogram(table=gg.table,
    #                        column=gg.mapping.x,
    #                        cmap=gg.mapping.cmap,
    #                        bins=self.bins,
    #                        conn=gg.conn,
    #                        with_=gg.with_,
    #                        category=gg.mapping.fill,
    #                        color=self.fill,
    #                        edgecolor=self.color
    #                        )
    #     gg.plot = p
    #     return gg

    def __add__(self, gg):
        return gg

    # def __iadd__(self, other):
    #     print("adding geom 2", type(other))
    #     return other.__radd__(self)

    def __radd__(self, gg):
        print("adding geom 3", type(gg))
        gg + self
        return gg
