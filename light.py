class Light():
    def __init__(self, position, strenght, colour) -> None:
        self.pos = position      # &Vec3& position of light source
        self.strenght = strenght # &scalar& from 0 to 1
        self.colour = colour     # &Vec3& colour of light