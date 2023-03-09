from sql import plot
from .geom import geom


class geom_boxplot(geom):
    def __radd__(self, gg):

        p = plot.boxplot(
            table=gg.table,
            column=gg.mapping.x,
            conn=gg.conn,
            with_=gg.with_
        )

        gg.plot = p

        return gg
