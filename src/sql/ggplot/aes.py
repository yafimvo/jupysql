
class aes():
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def __radd__(self, gg):
        gg.mapping.x = self.x
        gg.mapping.y = self.y
        return gg
