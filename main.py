import numpy as np
import random as r
import time
import matplotlib.pyplot as plt
from Vec3d import Vec3
from cam import Cam
from materials import Materials
from sphere import Sphere
from light import Light

# camera, objects, intersection funcs for them, materials


# linera interpolation
def lerp(point_a, x, point_b):
    return (point_b - point_a) * x + point_a

def generate_rays(resolution, FOV):
    #### generates list of vetors for each pixel on the screen ####
    
    # list of rows with vectors
    rays = []

    # calculating constant z distance for vectors
    angle = FOV/2
    dist_to_projection_plane = 1/np.tan(np.radians(angle))*(resolution[0]/2)

    # iterating thru all pixels
    for y in range(-resolution[1]//2, resolution[1]//2):
        row = []
        for x in range(-resolution[0]//2, resolution[0]//2):
            pixel = Vec3([x, -y, dist_to_projection_plane])
            pixel.normalize()
            row.append(pixel)


        rays.append(row)

    return rays

def lighting(obj, hit_point, lights, ambient_component):

    # calculating point normal
    normal = hit_point.subtract_R(obj.origin)
    normal.normalize()

    # object colour
    obj_colour = obj.materials.colour

    # light colour
    light_colour = lights.colour

    # calculating light direction
    light_dir = lights.pos.subtract_R(hit_point)
    light_dir.normalize()

    # calculating intensity of light in point
    point_intensity = light_dir.dot_R(normal)

    # scaling intensity by strenght of ilumination source
    point_intensity *= lights.strenght

    # calculating colour (px_colour = intensity * light colour * object colour + ambient component)
    pixel_colour = light_colour.mult_R(point_intensity)
    pixel_colour.mult(obj_colour)
    ambient = pixel_colour.mult_R(ambient_component)
    pixel_colour.add(ambient)

    return pixel_colour

def samples_for_soft_shadows(obj, hit_point, number_of_samples, normal_factor):
    # generates points which are random rotations of normal vector around sphere origin
    samples = []

    # calculating normal and its length
    normal = hit_point.subtract_R(obj.origin)
    normal_length = obj.origin.dist(hit_point)

    # calculating how much in all directions vector can move (bigger sphere --> less movement, smaller one --> more movement)
    angle_range = (1*normal_factor)/normal_length

    for i in range(number_of_samples):
        # generating all 3 axis rotation angles
        x_angle = r.randint(-int(angle_range)*100, int(angle_range)*100)/200
        y_angle = r.randint(-int(angle_range)*100, int(angle_range)*100)/200
        z_angle = r.randint(-int(angle_range)*100, int(angle_range)*100)/200

        # rotating normal
        sample = normal.rotate_x(x_angle)
        sample = sample.rotate_y(y_angle)
        sample = sample.rotate_z(z_angle)

        # adding origin to vector
        samples.append(sample.add_R(obj.origin))

    return samples
    

def compute_shadows(obj, objects, samples, lights, total_shadow_value):
    number_of_samples = len(samples)
    in_light_points = 0
    # iterating thru all generated samples
    for hit_point in samples:
        # calculating direction of ray from light source to considerd point on sphere
        ray_dir = lights.pos.subtract_R(hit_point)
        # normalization of length
        ray_dir.normalize()

        # checking if ray collide with sphere itself in the side alredy covered by shadow of itself
        did_hit = obj.intersect(ray_dir=ray_dir, ray_origin=hit_point, nearer=False)
        if did_hit[0]:
            # calculating and normalizing vector from considered point on sphere to point which creates shadow on this spot
            dir_from_hit_point_to_shadowing_point = did_hit[1].subtract_R(hit_point)
            dir_from_hit_point_to_shadowing_point.normalize()
            # checking if this vector points towards light source (means that object oclude itself by is own wall)
            if ray_dir.dot_R(dir_from_hit_point_to_shadowing_point) > 0:
                return 1
        # variable for insreesing number of points in shadow
        in_shadow = False
        # iterating thru all objects, except collider object itself
        for O in objects:
            if O is not obj:
                did_hit = O.intersect(ray_dir=ray_dir, ray_origin=hit_point, nearer=False)
                if did_hit[0]:
                    # calculating and normalizing vector from considered point on sphere to point which creates shadow on this spot
                    dir_from_hit_point_to_shadowing_point = did_hit[1].subtract_R(hit_point)
                    dir_from_hit_point_to_shadowing_point.normalize()
                    # checking if this vector points towards light source
                    if ray_dir.dot_R(dir_from_hit_point_to_shadowing_point) > -0.1: # -0.1 is treshold I attempted to set correctly by trying and failing, not any specific
                        # if point is in shadow stop iterating
                        in_shadow = True
                        break
        # increesing number of points wchich are not in shadow
        if in_shadow == False:
            in_light_points += 1
    # calculating ratio of in shadow to all points
    strenght_of_light_in_this_spot = in_light_points/number_of_samples
    total_light_strenght = lights.strenght
    # liner interpolation
    shadow_value = lerp(total_shadow_value, strenght_of_light_in_this_spot, total_light_strenght)

    return shadow_value

def ambient_occlusion(objects, hit_point, normal, samples):
    vectors = []
    # generating random vectors if half-sphere around the normal
    for i in range(samples):
        normal.normalize()
        x_rot = r.randint(-90, 90)
        y_rot = r.randint(-90, 90)
        z_rot = r.randint(-90, 90)

        # rotating normal vector
        new_vector = normal.rotate_x(x_rot)
        new_vector = new_vector.rotate_y(y_rot)
        new_vector = new_vector.rotate_z(z_rot)

        vectors.append(new_vector)

    collisions = 0
    for vec in vectors:
        for obj in objects:
            collision = obj.intersect(vec, hit_point, False)
            if collision[0]:
                v = collision[1].subtract_R(hit_point)
                if collision[1] != obj and v.dot_R(vec) > 0:
                    collisions += 1
                    break
    ratio = collisions/samples
    return lerp(0, ratio, 0.2)+0.5
    

def check_ray_intersection(ray_origin, ray_dir, last_hitpoint, last_hit_obj, objects, lights, ambient, pixel_pos, return_gradient):
        collisions = []
        for collider in objects:
            if collider != last_hit_obj:
                collision = collider.intersect(ray_dir=ray_dir, ray_origin=ray_origin, nearer=True)
                if collision[0]:
                    collisions.append([collider, camera.pos.dist(collision[1]), collision[1]])
        collisions1 = [x for x in collisions if ray_dir.dot_R(x[2].subtract_R(last_hitpoint)) > 0]
        collisions1 = sorted(collisions1, key=lambda x: x[1])
        if len(collisions) > 0:
            pixel_colour = lighting(obj=collisions1[0][0], hit_point=collisions1[0][2], lights=lights, ambient_component=ambient)
            samples = samples_for_soft_shadows(obj=collisions1[0][0], hit_point=collisions1[0][2], number_of_samples=8, normal_factor=10)
            shadow_value = compute_shadows(obj=collisions1[0][0], objects=objects, samples=samples, lights=lights, total_shadow_value=0.15)
            pixel_colour.mult(shadow_value)
            return pixel_colour.pos, collisions1[0][0], collisions1[0][1]
        else:
            if return_gradient:
                return [pixel_pos[1]/camera.resolution[1], 0.2, 0.1], None, None
            else:
                return None, None, None
                    

def trace(rays, camera, objects, lights, depth, ambient):
    a = time.time()
    print('#### Image rendering... ####')
    progress = 0
    image = []
    for y in range(camera.resolution[1]):
        row = []
        fancy_progress_marks = str(int(progress/10)*'==')
        for x in range(camera.resolution[0]):
            # checking colisions
            pixel_colour, last_hit_obj, last_hitpoint = check_ray_intersection(ray_origin=camera.pos, ray_dir=rays[y][x], last_hitpoint=camera.pos, last_hit_obj=None, objects=objects, lights=lights, ambient=ambient, pixel_pos=[x, y], return_gradient=True)
            row.append(pixel_colour)
        progress += 100/camera.resolution[1]
        print(f'Progress: {fancy_progress_marks}>{round(progress, 2)}%', end='\r')
        image.append(row)
    # changing all numbers to floats (for ploting working correctly)
    image = np.array(image, dtype=float)
    b = time.time()
    print('\n')
    print('$ Image rendering => Done $')
    print()
    print(f'Render time: {round(b-a, 2)} seconds')
    plt.imshow(image)
    plt.show()

########################################################################################################################
########################################################################################################################
########################################################################################################################

print('''          _______     __________   ___        _   ___________     __________   _______
         |  ___  \\   |  ________| |   \\      | | |  _______  \\   |  ________| |  ___  \\
         | |   \  |  | |          | |\\ \\     | | | |	   \\  \\  | |          | |   \\  |
         | |    | |  | |          | | \\ \\    | | | |	    |  | | |          | |    | |
         | |__ /  |  | |______    | |  \\ \\   | | | |	    |  | | |______    | |__ /  |
         |  __   /   |  ______|   | |   \\ \\  | | | |	    |  | |  ______|   |  __   /
         | |  \\ \\    | |          | |    \\ \\ | | | |	    |  | | |          | |  \\ \\
         | |   \\ \\   | |          | |     \\ \\| | | |        |  | | |          | |   \\ \\
         | |    \\ \\  | |________  | |      \\   | | |_______/  /  | |________  | |    \\ \\
         |_|     \\_\\ |__________| |_|       \\__| |___________/   |__________| |_|     \\_\\''')
print()
print('#### Initializing objects... #####')
camera = Cam(pos=Vec3([0, 0, 0]), cam_normal=Vec3([0, 0, 1]), FOV=90, near_plane=1, far_plane=20, resolution=[800, 600])
light = Light(position=Vec3([20, 40, 5]), strenght=1, colour=Vec3([1, 1, 1]))
objects = [Sphere(origin=Vec3([0, -11.6, 7.2]), radius=10, materials=Materials(colour=Vec3([0.8, 0.3, 0.3]), roughnes=0.1, reflectivity=0.8, diffuse=0)), Sphere(origin=Vec3([0, 0, 7]), radius=2, materials=Materials(Vec3([1, 0, 0]), roughnes=0.1, reflectivity=0.8, diffuse=0))]
print('$ Initializing objects => Done $')
print()
print('#### Generating basic rays set... ####')
rays = generate_rays(camera.resolution, camera.FOV)
print('$ Rays set generating => Done $')
print()
trace(rays=rays, camera=camera, objects=objects, lights=light, depth=1, ambient=0.2)
