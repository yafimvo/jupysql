from sql.ggplot.aes import aes


class ggplot:
    """
    Create a new ggplot
    """

    def __init__(self, table, mapping: aes = None, conn=None, with_=None) -> None:
        self.table = table
        self.with_ = [with_] if with_ else None
        self.mapping = mapping if mapping is not None else aes()
        self.conn = conn

    def __add__(self, other) -> 'ggplot':
        """
        Add to ggplot
        """
        return self.__iadd__(other)

    def __iadd__(self, other: aes) -> 'ggplot':
        """
        Add aes to ggplot
        """
        return other.__radd__(self)
