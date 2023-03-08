from sql import plot
from .geom import geom


class geom_histogram(geom):
    def __init__(self, bins, **kwargs):
        self.bins = bins
        super().__init__(**kwargs)

    def __radd__(self, gg):
        p = plot.histogram(table=gg.table,
                           column=gg.mapping.x,
                           bins=self.bins,
                           conn=gg.conn,
                           with_=gg.with_,
                           color=self.color,
                           edgecolor=self.edgecolor,
                           )
        gg.plot = p
        return gg
