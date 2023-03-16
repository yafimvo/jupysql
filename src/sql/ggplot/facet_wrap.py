class facet():
    def __init__():
        pass


class facet_wrap(facet):
    """
    Splits a plot into a matrix of panels

    Parameters
    ----------
    facet : str
        Column to groupby and plot on different panels. 
    """

    def __init__(self, facet: str):
        self.facet = facet
        pass

    # def __radd__(self, gg):
    #     # import matplotlib.pyplot as plt
    #     import numpy as np

    #     # print("face wrap... ", type(gg))

    #     # # Some example data to display
    #     # x = np.linspace(0, 2 * np.pi, 400)
    #     # y = np.sin(x ** 2)
    #     # fig, (ax1, ax2) = plt.subplots(1, 2)
    #     # fig.suptitle('Horizontally stacked subplots')
    #     # ax1.plot(x, y)
    #     # ax2.plot(x, -y)

    #     im = gg.plot.imshow(np.arange(100).reshape((10, 10)))

    #     return gg

    def __add__(self, other):
        print("adding face 1")
        return self.__iadd__(other)

    def __iadd__(self, other):
        print("adding face 2")
        return other.__radd__(self)

    def __radd__(self, gg):
        print("adding face 3", type(gg))
        return gg.__add__(self)
