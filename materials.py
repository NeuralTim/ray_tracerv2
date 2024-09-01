class Materials():
    def __init__(self, colour, roughnes, reflectivity, diffuse, shinines, specular, ambient) -> None:
        self.colour = colour                # $Vec3& colour of the object
        self.roughness = roughnes           # $scalar$ applys offsets to calculated ray direction proportional to its value
        self.reflectivity = reflectivity    # $scalar$ describes how reflective is the object (Zero means all light is absorbed. One means it's perfect mirror)
        self.diffuse = diffuse              # $scalar$ describes desribes how much light is absorbed in particular point relaitive to angle of normal to vector from hit poiny to light source 
        self.shinines = shinines            # $scalar$ describes how sharp are light spots on object
        self.specular = specular            # $scalar$ describes how big and inteense are light spots on object
        self.ambient = ambient              # $scalar$ describes how much of scene ambient light object absorbs