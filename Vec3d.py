import numpy as np

class Vec3():
    def __init__(self, pos) -> None:
        self.x = pos[0]
        self.y = pos[1]
        self.z = pos[2]
        self.pos = [self.x, self.y, self.z]

    # instant change of value 'pos' versions

    def normalize(self):
        norm = np.linalg.norm(self.pos)
        self.x /= norm
        self.y /= norm
        self.z /= norm
        self.pos = [self.x, self.y, self.z]

    def mult(self, other):
        if isinstance(other, Vec3):
            self.x, self.y, self.z = self.x*other.x, self.y*other.y, self.z*other.z
            self.pos = [self.x, self.y, self.z]
        else:
            self.x, self.y, self.z = self.x*other, self.y*other, self.z*other
            self.pos = [self.x, self.y, self.z]

    def div(self, other):
        if isinstance(other, Vec3):
            self.x, self.y, self.z = self.x/other.x, self.y/other.y, self.z/other.z
            self.pos = [self.x, self.y, self.z]
        else:
            self.x, self.y, self.z = self.x/other, self.y/other, self.z/other
            self.pos = [self.x, self.y, self.z]

    def add(self, other):
        if isinstance(other, Vec3):
            self.x, self.y, self.z = self.x+other.x, self.y+other.y, self.z+other.z
            self.pos = [self.x, self.y, self.z]
        else:
            self.x, self.y, self.z = self.x+other, self.y+other, self.z+other
            self.pos = [self.x, self.y, self.z]

    def subtract(self, other):
        if isinstance(other, Vec3):
            self.x, self.y, self.z = self.x-other.x, self.y-other.y, self.z-other.z
            self.pos = [self.x, self.y, self.z]
        else:
            self.x, self.y, self.z = self.x-other, self.y-other, self.z-other
            self.pos = [self.x, self.y, self.z]


    # read only versions for keeping 'pos' unchanged

    def normalize_R(self):
        norm = np.linalg.norm(self.pos)
        return Vec3([self.x / norm,
                self.y / norm,
                self.z / norm])
    
    def length_R(self):
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def mult_R(self, other):
        if isinstance(other, Vec3): 
            return Vec3([self.x*other.x, self.y*other.y, self.z*other.z])
        else:
            return Vec3([self.x*other, self.y*other, self.z*other])
    
    def div_R(self, other):
        if isinstance(other, Vec3):
            return Vec3([self.x/other.x, self.y/other.y, self.z/other.z])
        else:
            return Vec3([self.x/other, self.y/other, self.z/other])
    
    def dot_R(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z

    def add_R(self, other):
        if isinstance(other, Vec3):
            return Vec3([self.x+other.x, self.y+other.y, self.z+other.z])
        else:
            return Vec3([self.x+other, self.y+other, self.z+other])
    
    def subtract_R(self, other):
        if isinstance(other, Vec3):
            return Vec3([self.x-other.x, self.y-other.y, self.z-other.z])
        else:
            return Vec3([self.x-other, self.y-other, self.z-other])
        
    def dist(self, other):
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
    
    def rotate_x(self, theta):
        matrix = [[1, 0, 0],
                  [0, np.cos(np.radians(theta)), -np.sin(np.radians(theta))],
                  [0, np.sin(np.radians(theta)), np.cos(np.radians(theta))]]
        result = np.matmul(matrix, self.pos)
        return Vec3([result[0], result[1], result[2]])

    def rotate_y(self, theta):
        matrix = [[np.cos(np.radians(theta)), 0, np.sin(np.radians(theta))],
                  [0, 1, 0],
                  [-np.sin(np.radians(theta)), 0, np.cos(np.radians(theta))]]
        result = np.matmul(matrix, self.pos)
        return Vec3([result[0], result[1], result[2]])

    def rotate_z(self, theta):
        matrix = [[np.cos(np.radians(theta)), -np.sin(np.radians(theta)), 0],
                  [np.sin(np.radians(theta)), np.cos(np.radians(theta)), 0],
                  [0, 0, 1]]
        result = np.matmul(matrix, self.pos)
        return Vec3([result[0], result[1], result[2]])    