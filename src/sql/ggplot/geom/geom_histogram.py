from sql import plot
from .geom import geom


class geom_histogram(geom):
    def __init__(self, bins, **kwargs):
        """
        Parameters
        ----------
        bins: int
            Number of bins
        """
        self.bins = bins

        super().__init__(**kwargs)

    def __radd__(self, gg):
        p = plot.histogram(table=gg.table,
                           column=gg.mapping.x,
                           cmap=gg.mapping.cmap,
                           bins=self.bins,
                           conn=gg.conn,
                           with_=gg.with_,
                           category=gg.mapping.fill,
                           color=self.fill,
                           edgecolor=self.color
                           )
        gg.plot = p
        return gg
