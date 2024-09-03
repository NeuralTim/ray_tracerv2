import numpy as np
from Vec3d import Vec3

class Plane():
    def __init__(self, surface_normal, distance_from_0_0_0, materials) -> None:
        self.id = 'plane'
        self.surface_normal = surface_normal
        self.distance_from_0_0_0 = distance_from_0_0_0
        self.materials = materials

    # nearer is placeholder for compatibility with sphere inresect code
    def intersect(self, ray_dir, ray_origin, nearer):
        # defining variables for method to work on as normal lists
        normal = self.surface_normal.pos
        origin = ray_origin.pos
        dir = ray_dir.pos

        # calculating numerator and denumerator
        numerator = -(normal[0]*origin[0] + normal[1]*origin[1] + normal[2]*origin[2] - self.distance_from_0_0_0)
        denominator = normal[0]*dir[0] + normal[1]*dir[1] + normal[2]*dir[2]

        # line is not paralel to plane
        if denominator != 0:
            t = numerator/denominator
            point = [dir[0]*t+origin[0], dir[1]*t+origin[1], dir[2]*t+origin[2]]
            return [True, Vec3(point)]
        # line is paralel to plane or line lays on plane
        else:
            return [False]


    def chess_board(self, hit_point):
        # returns colour of pixel based on it's coordinates in chessboard pattern
        if (int(hit_point.z)%2 != 0 and int(hit_point.x)%2 == 0) or (int(hit_point.z)%2 == 0 and int(hit_point.x)%2 != 0):
            return Vec3([1.0, 0.0, 0.0])
        else:
            return Vec3([0.0, 0.0, 1.0])
        
