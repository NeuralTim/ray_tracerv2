class Light():
    def __init__(self, position, strenght, colour) -> None:
        self.pos = position      # in Vec3
        self.strenght = strenght # float from 0 to 1
        self.colour = colour     # in Vec3