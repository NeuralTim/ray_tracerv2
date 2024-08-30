class Cam():
    def __init__(self, pos, cam_normal, FOV, near_plane, far_plane, resolution) -> None:
        self.pos = pos               # position in Vec3
        self.cam_normal = cam_normal # camera looking direction in Vec3
        self.FOV = FOV               # field of view in degrees
        self.near_plane = near_plane # nearest render distance
        self.far_plane = far_plane   # furthest render distance
        self.resolution = resolution # 2D vector describing resolution in X and Y axis
