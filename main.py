import pygame as py
import time

import global_data
import renderer

import matrix
import vector
from vector import Vector3
from triangle import Triangle
import triangle


def tick():
    start_time = time.time()

    # user input
    keys = py.key.get_pressed()

    try:
        fps_mod = 1 / global_data.fps
    except ZeroDivisionError:
        fps_mod = 100

    # movement
    forwards_movement = vector.multiply(global_data.camera_look_direction, global_data.camera_movement_speed * fps_mod)

    if keys[py.K_SPACE]:
        global_data.camera_position.y -= global_data.camera_movement_speed * fps_mod
    if keys[py.K_LSHIFT]:
        global_data.camera_position.y += global_data.camera_movement_speed * fps_mod

    if keys[py.K_d]:
        global_data.camera_position.x += global_data.camera_movement_speed * fps_mod
    if keys[py.K_a]:
        global_data.camera_position.x -= global_data.camera_movement_speed * fps_mod

    if keys[py.K_w]:
        global_data.camera_position = vector.add(global_data.camera_position, forwards_movement)
    if keys[py.K_s]:
        global_data.camera_position = vector.subtract(global_data.camera_position, forwards_movement)

    # looking
    if keys[py.K_LEFT]:
        global_data.yaw += global_data.camera_movement_speed * fps_mod
    if keys[py.K_RIGHT]:
        global_data.yaw -= global_data.camera_movement_speed * fps_mod

    renderer.pygame_tick()

    # Set up rotation matrices
    rotate_z = matrix.rotation_z(1)
    rotate_x = matrix.rotation_x(1)

    trans = matrix.translate(0, 0, 10)  # position in world space

    world_matrix = matrix.matrix_x_matrix(rotate_z, rotate_x)
    world_matrix = matrix.matrix_x_matrix(world_matrix, trans)

    triangles_to_draw = []

    up = Vector3(0, 1, 0, 1)
    target = Vector3(0, 0, 1, 1)
    camera_rotation = matrix.rotation_y(global_data.yaw)
    global_data.camera_look_direction = matrix.matrix_x_vector(camera_rotation, target)
    target = vector.add(global_data.camera_position, global_data.camera_look_direction)

    camera_matrix = matrix.point_at(global_data.camera_position, target, up)

    # make view matrix from camera
    view_matrix = matrix.quick_inverse(camera_matrix)

    # prepare triangles
    for tri in global_data.cube.triangles:
        tri_projected = Triangle(None, None, None, None, None, None)
        tri_transformed = Triangle(None, None, None, None, None, None)
        tri_viewed = Triangle(None, None, None, None, None, None)

        # world matrix transform
        tri_transformed.p[0] = matrix.matrix_x_vector(world_matrix, tri.p[0])
        tri_transformed.p[1] = matrix.matrix_x_vector(world_matrix, tri.p[1])
        tri_transformed.p[2] = matrix.matrix_x_vector(world_matrix, tri.p[2])
        tri_transformed.t[0] = tri.t[0]
        tri_transformed.t[1] = tri.t[1]
        tri_transformed.t[2] = tri.t[2]

        # get lines on either side of the triangle
        line1 = vector.subtract(tri_transformed.p[1], tri_transformed.p[0])
        line2 = vector.subtract(tri_transformed.p[2], tri_transformed.p[0])

        # take cross product of lines to get normal to triangle surface
        normal = vector.cross_product(line1, line2)
        normal.normalise()

        # get a raw from triangle to camera
        camera_ray: Vector3 = vector.subtract(tri_transformed.p[0], global_data.camera_position)

        # (Set to > if you want to see the invisible side of everything)
        # Some optimisation:
        # Check how close the ray cast from the camera to the normal of the triangle is from each other.
        # Negative number is returned if they are facing away from each other
        if vector.dot_product(normal, camera_ray) < 0:

            # illumination
            light_direction = Vector3(0, -1, -1, 1)
            light_direction.normalise()

            brightness = max(0.1, vector.dot_product(light_direction, normal)) * 150

            if brightness > 255:
                brightness = 255
            if brightness < 0:
                brightness = 0

            tri_projected.colour = (brightness, brightness, brightness)

            # convert World Space --> View Space
            tri_viewed.p[0] = matrix.matrix_x_vector(view_matrix, tri_transformed.p[0])
            tri_viewed.p[1] = matrix.matrix_x_vector(view_matrix, tri_transformed.p[1])
            tri_viewed.p[2] = matrix.matrix_x_vector(view_matrix, tri_transformed.p[2])
            tri_viewed.t[0] = tri_transformed.t[0]
            tri_viewed.t[1] = tri_transformed.t[1]
            tri_viewed.t[2] = tri_transformed.t[2]

            # to preserve the colour
            tri_viewed.colour = tri_projected.colour

            clipped = triangle.clip_against_plane(Vector3(0, 0, 0.1, 1), Vector3(0, 0, 1, 1), tri_viewed)

            second = False

            for clipped_tri in clipped:

                # prevents the new triangle overwriting the old one when added to the list to draw
                if second:
                    old_colour = tri_projected.colour

                    tri_projected = Triangle(None, None, None, None, None, None)
                    tri_projected.colour = old_colour

                second = True

                # apply any colour changes from clipping
                tri_projected.colour = clipped_tri.colour

                # Project triangles from 3D --> 2D
                tri_projected.p[0] = matrix.matrix_x_vector(renderer.projection_matrix, clipped_tri.p[0])
                tri_projected.p[1] = matrix.matrix_x_vector(renderer.projection_matrix, clipped_tri.p[1])
                tri_projected.p[2] = matrix.matrix_x_vector(renderer.projection_matrix, clipped_tri.p[2])
                tri_projected.t[0] = clipped.t[0]
                tri_projected.t[1] = clipped.t[1]
                tri_projected.t[2] = clipped.t[2]

                # scale into view
                tri_projected.p[0] = vector.divide(tri_projected.p[0], tri_projected.p[0].w)
                tri_projected.p[1] = vector.divide(tri_projected.p[1], tri_projected.p[1].w)
                tri_projected.p[2] = vector.divide(tri_projected.p[2], tri_projected.p[2].w)

                # Scale into view
                offset_view = Vector3(1, 1, 0, 1)
                tri_projected.p[0] = vector.add(tri_projected.p[0], offset_view)
                tri_projected.p[1] = vector.add(tri_projected.p[1], offset_view)
                tri_projected.p[2] = vector.add(tri_projected.p[2], offset_view)

                tri_projected.p[0].x *= 0.5 * renderer.screen_x
                tri_projected.p[0].y *= 0.5 * renderer.screen_y
                tri_projected.p[1].x *= 0.5 * renderer.screen_x
                tri_projected.p[1].y *= 0.5 * renderer.screen_y
                tri_projected.p[2].x *= 0.5 * renderer.screen_x
                tri_projected.p[2].y *= 0.5 * renderer.screen_y

                # store triangle for sorting and rendering
                triangles_to_draw.append(tri_projected)

    # sort the list of triangles into the order of their appearance, so that you don't have things
    # further away rendering in front of close things
    def sort_criteria(v):
        return (v.p[0].z + v.p[1].z + v.p[2].z) / 3

    triangles_to_draw.sort(reverse=True, key=sort_criteria)

    # clip triangles against the edge of the screen and render triangles
    triangles_to_draw = renderer.clip_against_screen(triangles_to_draw)
    renderer.render_mesh(triangles_to_draw)

    global_data.tick += 1
    global_data.fps = round(1.0 / (time.time() - start_time))
    if global_data.tick % 10 == 0:
        py.display.set_caption(f'FPS: {global_data.fps}')


while True:
    tick()
