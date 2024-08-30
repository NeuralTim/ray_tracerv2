import numpy as np
from Vec3d import Vec3


class Sphere():
    def __init__(self, origin, radius, materials) -> None:
        self.origin = origin        # in Vec3
        self.radius = radius
        self.materials = materials  # described as an object of class Materials

    def get_normal(self, point):
        #### returns normal for the sphere in given point ####
        
        return self.origin.subtract_R(point).normalize()

    
    def intersect(self, ray_dir, ray_origin, nearer):
        #### returns existing cross points ####

        # calculating t value by checing lenght of vector projection 
        T = ray_dir.dot_R(self.origin.subtract_R(ray_origin))

        # calculating nearest point to sphere origin placed on ray
        D = ray_origin.add_R(ray_dir.mult_R(T))

        # calculating vector from sphere origin to that point
        X = self.origin.subtract_R(D)

        # finding and squaring it's lenght for future calculation
        X = X.length_R()**2

        # squaring lenght or radius to keep scale and for future calculations
        R = self.radius**2

        # checking if intersection has appered
        if R >= X:

            # calculating distance from nearest to sphere origin point to the surface of thr sphere
            offset = np.sqrt(R - X)

            # new scaling factors for ray direction vector
            T_zero = T - offset
            T_one = T + offset

            # calculating cross point nearest to camera
            T_zero, T_one = ray_origin.add_R(ray_dir.mult_R(T_zero)), ray_origin.add_R(ray_dir.mult_R(T_one))
            if nearer:
                if ray_origin.dist(T_zero) > ray_origin.dist(T_one):
                    return [True, T_one]
                else:
                    return [True, T_zero]
            else:
                if ray_origin.dist(T_zero) < ray_origin.dist(T_one):
                    return [True, T_one]
                else:
                    return [True, T_zero]
        
        return [False]

