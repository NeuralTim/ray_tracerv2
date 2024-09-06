import numpy as np
import random as r
import time
import matplotlib.pyplot as plt
from Vec3d import Vec3
from cam import Cam
from materials import Materials
from sphere import Sphere
from plane import Plane
from light import Light
from PIL import Image

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

def equator(obj, hit_point, lights, treshold):
    # function checks, if given point is closer to natural shadow border than hardcoded treshold
    normal = hit_point.subtract_R(obj.origin)
    normal.normalize()
    vec = lights.pos.subtract_R(obj.origin)
    vec.normalize()
    dot = vec.dot_R(normal)
    if dot > -treshold and dot < treshold:
        return 0
    return 1

def calculate_reflected_ray_dir(ray_dir, normal, reverse_direction):
    # calculates direction of perfectly reflected ray

    # normalization
    ray_dir.normalize()

    # reversing direction if needed
    if reverse_direction:
        ray_dir = ray_dir.mult_R(-1)
    
    # normalization
    normal.normalize()

    # t in length of vector projected on normal
    t = ray_dir.dot_R(normal)

    # creating new vector pointing in the same direction as normal with length of 2*t
    new_normal = normal.mult_R(2*t)

    # subtracting (probably reversed) direction of starting ray from new vector
    return new_normal.subtract_R(ray_dir)


def apply_random_offset_to_ray_for_sphere(angle_range, ray_dir):
    # fuction for spheres only -> rotates normal vector by some samll angles

    # calculating offsets angles
    x_angle = r.randint(-int(angle_range)*100, int(angle_range)*100)/200
    y_angle = r.randint(-int(angle_range)*100, int(angle_range)*100)/200
    z_angle = r.randint(-int(angle_range)*100, int(angle_range)*100)/200
    # rotating normal
    sample = ray_dir.rotate_x(x_angle)
    sample = sample.rotate_y(y_angle)
    sample = sample.rotate_z(z_angle)

    return sample


def apply_random_offset_to_ray_for_plane(point, ratio):
    # function for planes only -> adds some small random number to hitpoint coordinates
    
    # calculating offsets
    x_off = r.randint(-ratio*100, ratio*100)/200
    y_off = r.randint(-ratio*100, ratio*100)/200
    z_off = r.randint(-ratio*100, ratio*100)/200

    return Vec3([point.x+x_off, point.y+y_off, point.z+z_off])

def lighting(camera, light, shadowness, obj, hit_point, scene_ambient):
    # calculates actual colour of pixel

    # defining shinines by reading in object materials
    shinines = obj.materials.shinines
    diffuse = obj.materials.diffuse
    specular = obj.materials.specular
    ambient = obj.materials.ambient

    # calculating diffuse component
    
    # setting correct normals
    if obj.id == 'sphere':
        obj_normal = hit_point.subtract_R(obj.origin)
        obj_normal.normalize()
    else:
        obj_normal = obj.surface_normal
        obj_normal.normalize()

    hit_point_to_ligth = light.pos.subtract_R(hit_point)
    hit_point_to_ligth.normalize()

    angle = max(obj_normal.dot_R(hit_point_to_ligth), 0) 
    
    diffuse_component = light.colour.mult_R(light.strenght)
    diffuse_component.mult(angle)
    diffuse_component.mult(diffuse)
    diffuse_component.mult(shadowness)

    # ambient component
    ambient = obj.materials.colour.mult_R(ambient)
    ambient_component = ambient.mult_R(scene_ambient)

    # specular component

    direction_to_light = light.pos.subtract_R(hit_point)

    reflected_light_direction = calculate_reflected_ray_dir(ray_dir=direction_to_light, normal=obj_normal, reverse_direction=True)

    direction_to_cam = camera.pos.subtract_R(hit_point)
    direction_to_cam.normalize()

    

    specular_component = specular*(max(direction_to_cam.dot_R(reflected_light_direction), 0))**shinines
    specular_component = light.colour.mult_R(specular_component)
    specular_component.mult(shadowness)

    # final colour calculation

    total = specular_component.add_R(ambient_component)
    total.add(diffuse_component)
    total.mult(obj.materials.colour)

    return total


def samples_for_soft_shadows(obj, hit_point, lights, number_of_samples, normal_factor):
    # generates points which are random rotations of normal vector around sphere origin
    samples = []
    # do this only for sphere checker
    if obj.id == 'sphere':
        # checking if point is near to shadow line of object itself
        is_on_equator = equator(obj, hit_point, lights, 0.1)
        # if it is, then don't do sampling
        if is_on_equator == 0:
            return [hit_point]*number_of_samples
        # calculating normal and its length
        normal = hit_point.subtract_R(obj.origin)
        normal_length = obj.origin.dist(hit_point)
        
        # calculating how much in all directions vector can move (bigger sphere --> less movement, smaller one --> more movement)
        angle_range = normal_factor/normal_length
        for i in range(number_of_samples):
            # generating all 3 axis rotation angles
            sample = apply_random_offset_to_ray_for_sphere(angle_range=angle_range, ray_dir=normal)
            # adding origin to vector
            samples.append(sample.add_R(obj.origin))
    else:
        for i in range(number_of_samples):
            # adding some small random numbers to coordinates of hitpoint
            sample = apply_random_offset_to_ray_for_plane(point=hit_point, ratio=0.2)
        
            samples.append(sample)

    return samples


def compute_shadows(obj, objects, samples, lights):
    number_of_samples = len(samples)
    in_light_points = 0
    # iterating thru all generated samples
    for hit_point in samples:
        # calculating direction of ray from light source to considerd point on sphere
        ray_dir = lights.pos.subtract_R(hit_point)
        # normalization of length
        ray_dir.normalize()
        
        # do this only for sphere checker
        if obj.id == 'sphere':
            # checking if ray collide with sphere itself in the side alredy covered by shadow of itself
            did_hit = obj.intersect(ray_dir=ray_dir, ray_origin=hit_point, nearer=False)
            if did_hit[0]:
                # calculating and normalizing vector from considered point on sphere to point which creates shadow on this spot
                dir_from_hit_point_to_shadowing_point = did_hit[1].subtract_R(hit_point)
                dir_from_hit_point_to_shadowing_point.normalize()
                # checking if this vector points towards light source (means that object oclude itself by is own wall)
                if ray_dir.dot_R(dir_from_hit_point_to_shadowing_point) > 0:
                    return 1
        # variable for increesing number of points in shadow
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
                    if ray_dir.dot_R(dir_from_hit_point_to_shadowing_point) > 0:
                        # if point is in shadow stop iterating
                        in_shadow = True
                        break
        # increesing number of points wchich are not in shadow
        if in_shadow == False:
            in_light_points += 1
    # calculating ratio of in shadow to all points
    strenght_of_light_in_this_spot = in_light_points/number_of_samples
    return strenght_of_light_in_this_spot
    

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
    

def check_ray_intersection(ray_origin, ray_dir, last_hitpoint, last_hit_obj, objects, lights, pixel_pos, return_gradient, depth):
        # checking treshod for recursion
        if depth == 0:
            return None
        
        # list for storing collisions
        collisions = []

        # iterating thru all objects
        for collider in objects:

            # checking if ray is not trying to collide with object which was hit last time
            if collider != last_hit_obj:

                # checkig if ray collide with anything
                collision = collider.intersect(ray_dir=ray_dir, ray_origin=ray_origin, nearer=True)

                # if collision occured -> add it to list of collisions
                if collision[0]:
                    collisions.append([collider, camera.pos.dist(collision[1]), collision[1]])

        # checking if collision is not behind camera
        collisions1 = [x for x in collisions if ray_dir.dot_R(x[2].subtract_R(last_hitpoint)) > 0]

        # checking if any collision made it thru last test
        if len(collisions1) > 0:
            # sorting collisions by distance to camera
            collisions1 = sorted(collisions1, key=lambda x: x[1])

            if collisions1[0][0].id == 'sphere':
                # creating samples for making soft shadows
                samples = samples_for_soft_shadows(obj=collisions1[0][0], hit_point=collisions1[0][2], lights=light, number_of_samples=15, normal_factor=8)

                # computing shadows which occured by object's occlusion and passing walue of shadow for pixel to next funciton
                shadow_value = compute_shadows(obj=collisions1[0][0], objects=objects, samples=samples, lights=lights)

                # computing lighting for pixel using phong's lighting model with respect to shadow value of pixel
                pixel_colour = lighting(camera=camera, light=lights, shadowness=shadow_value, obj=collisions1[0][0], hit_point=collisions1[0][2], scene_ambient=0.2)

                # multipling colour of pixel by 1-refectivity to check how much of light was actually absorbed
                pixel_colour.mult(1-collisions1[0][0].materials.reflectivity)

                # computing direction for reflected ray
                new_ray_dir = calculate_reflected_ray_dir(normal=collisions1[0][2].subtract_R(collisions1[0][0].origin), ray_dir=ray_dir, reverse_direction=True)

                # perturbating direction with respect to roughness of object
                new_ray_dir = apply_random_offset_to_ray_for_sphere(angle_range=90*collisions1[0][0].materials.roughness, ray_dir=new_ray_dir)
            
            else:
                # checking current pixel base colour by calling chess_board method on it's position
                collisions1[0][0].materials.colour = collisions1[0][0].chess_board(hit_point=collisions1[0][2])

                 # creating samples for making soft shadows
                samples = samples_for_soft_shadows(obj=collisions1[0][0], hit_point=collisions1[0][2], lights=light, number_of_samples=15, normal_factor=8)

                # computing shadows which occured by object's occlusion and passing walue of shadow for pixel to next funciton
                shadow_value = compute_shadows(obj=collisions1[0][0], objects=objects, samples=samples, lights=lights)

                # computing lighting for pixel using phong's lighting model with respect to shadow value of pixel 
                pixel_colour = lighting(camera=camera, light=lights, shadowness=shadow_value, obj=collisions1[0][0], hit_point=collisions1[0][2], scene_ambient=0.2)

                # multipling colour of pixel by 1-refectivity to check how much of light was actually absorbed
                pixel_colour.mult(1-collisions1[0][0].materials.reflectivity)

                # computing direction for reflected ray
                new_ray_dir = calculate_reflected_ray_dir(normal=collisions1[0][0].surface_normal, ray_dir=ray_dir, reverse_direction=True)

                # perturbating direction with respect to roughness of object
                new_ray_dir = apply_random_offset_to_ray_for_sphere(angle_range=90*collisions1[0][0].materials.roughness, ray_dir=new_ray_dir)

            # recursive checking next collisions of reflected rays
            reflected = check_ray_intersection(ray_origin=collisions1[0][2],
                                                    ray_dir=new_ray_dir,  
                                                    last_hitpoint=collisions1[0][2], 
                                                    last_hit_obj=collisions1[0][0], 
                                                    objects=objects,
                                                    lights=lights,
                                                    pixel_pos=pixel_pos, 
                                                    return_gradient=False, 
                                                    depth=depth-1)

            # cheecking if ray didn't go to void
            if reflected != None:
                # multipling by amount of light which was reflected
                reflected.mult(collisions1[0][0].materials.reflectivity)
                pixel_colour.add(reflected)

            return pixel_colour
        else:
            if return_gradient:
                return Vec3([pixel_pos[1]/camera.resolution[1], 0.2, 0.1])
            else:
                return None
                    

def trace(rays, camera, objects, lights, depth):

    # start stoper
    a = time.time()
    print('#### Image rendering... ####')

    # initializing of progress incrementor
    progress = 0

    # matrix for filal image
    image = []

    # iterating thru all rows
    for y in range(camera.resolution[1]):
        row = []

        # printing progres
        fancy_progress_marks = str(int(progress/10)*'==')

        # itrating thru all pixels in row
        for x in range(camera.resolution[0]):

            # checking colisions
            pixel_colour = check_ray_intersection(ray_origin=camera.pos, ray_dir=rays[y][x], last_hitpoint=camera.pos, last_hit_obj=None, objects=objects, lights=lights, pixel_pos=[x, y], return_gradient=True, depth=depth)
            
            # adding pixel colour to current ray
            row.append(pixel_colour.pos)

        # incrementing progress
        progress += 100/camera.resolution[1]
        print(f'Progress: {fancy_progress_marks}>{round(progress, 2)}%', end='\r')

        # adding row to image
        image.append(row)

    # changing all numbers to floats (for ploting working correctly)
    image = np.array(image, dtype=float)

    # stoping timer
    b = time.time()
    print('\n')
    print('$ Image rendering => Done $')
    print()
    t = int(b-a)
    minutes = t//60
    seconds = t%60
    print(f'Render time: {minutes} minutes {seconds} seconds')
    plt.imshow(image)
    plt.show()

    # data normalization from 0 to 1
    min_val = image.min()
    max_val = image.max()
    normalized_rgb_data = (image - min_val) / (max_val - min_val)

    # scaling data from 0 to 255
    rgb_data_scaled = np.clip(normalized_rgb_data * 255, 0, 255).astype(np.uint8)

    # creating image from RGB data
    img = Image.fromarray(rgb_data_scaled, 'RGB')

    # writing image to file
    img.save('two_balls_render.png')
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
light = Light(position=Vec3([30, 20, -50]), strenght=2, colour=Vec3([1, 1, 1]))
floor = Plane(surface_normal=Vec3([0, 1, 0]), distance_from_0_0_0=-1.5, materials=Materials(colour=Vec3([1, 0, 1]), roughnes=0.0, reflectivity=0.7, diffuse=0.3, shinines=10, specular=0.6, ambient=0.2))
s1 = Sphere(origin=Vec3([-1.5, 0, 5]), radius=1.5, materials=Materials(colour=Vec3([1, 1, 1]), roughnes=0.05, reflectivity=0.7, diffuse=0.5, shinines=50, specular=0.9, ambient=0.1))
s2 = Sphere(origin=Vec3([1.5, 0, 5]), radius=1.5, materials=Materials(colour=Vec3([1, 0, 0]), roughnes=0, reflectivity=0.7, diffuse=0.5, shinines=50, specular=0.9, ambient=0.1))
objects = [s1, s2, floor]
print('$ Initializing objects => Done $')
print()
print('#### Generating basic rays set... ####')
rays = generate_rays(camera.resolution, camera.FOV)
print('$ Rays set generating => Done $')
print()
trace(rays=rays, camera=camera, objects=objects, lights=light, depth=8)
