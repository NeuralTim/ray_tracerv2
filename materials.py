class Materials():
    def __init__(self, colour, roughnes, reflectivity, diffuse) -> None:
        self.colour = colour                # color of the object
        self.roughness = roughnes           # apply offsets to calculated ray direction proportional to its value
        self.reflectivity = reflectivity    # defines how reflective is the object (how much it will be tinted by secondary reflections. One means it's perfect mirror)
        self.diffuse = diffuse              # defines how random are directions of secondary rays. This value is then perturbated by roughness

        #### All of this components are stored as objects of Vec3 class ####