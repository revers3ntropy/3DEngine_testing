# ================================================================================================
# |------------------------------------={ Project Name }=----------------------------------------|
# ================================================================================================
#
#                                   Programmers : Joseph Coppin
#
#                                     File Name : renderer.py
#
#                                       Created : Month 00, 2020
#
# ------------------------------------------------------------------------------------------------
#
#   Imports:
import pygame as py

import global_data
import matrix

from vector import Vector3
import vector
from triangle import clip_against_plane

from triangle import Triangle
import triangle

#
# ------------------------------------------------------------------------------------------------
#
#                                       interacts with pygame.
#
# ------------------------------------------------------------------------------------------------
#
#   pygame_tick
#   draw_triangle_solid
#   draw_triangle_wireframe
#   render_triangle
#   render_mesh
#   clip_against_screen
#
# ================================================================================================
screen_x = 1000
screen_y = 600

background_colour = (255, 255, 255)
run_FPS = 60

py.init()

screen = py.display.set_mode((screen_x, screen_y))
clock = py.time.Clock()

draw_wireframe = True
wireframe_colour = (0, 0, 0)

draw_solid = False

draw_texture = True

projection_matrix = matrix.projection(global_data.fov, screen_y / screen_x, 0.1, 100000)

depth_buffer = [0] * screen_y * screen_x


def reset_depth_buffer():
    global depth_buffer
    depth_buffer = [0] * screen_y * screen_x


def pygame_tick():

    py.display.flip()
    clock.tick(run_FPS)
    screen.fill(background_colour)

    reset_depth_buffer()

    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            quit()


def draw_mesh(mesh):

    # Set up rotation matrices
    rotate_z = matrix.rotation_z(1)
    rotate_x = matrix.rotation_x(1)

    trans = matrix.translate(0, 0, 10)  # position in world space

    world_matrix = matrix.matrix_x_matrix(rotate_z, rotate_x)
    world_matrix = matrix.matrix_x_matrix(world_matrix, trans)

    up = Vector3(0, 1, 0, 1)
    target = Vector3(0, 0, 1, 1)
    camera_rotation = matrix.rotation_y(global_data.yaw)
    global_data.camera_look_direction = matrix.matrix_x_vector(camera_rotation, target)
    target = vector.add(global_data.camera_position, global_data.camera_look_direction)

    camera_matrix = matrix.point_at(global_data.camera_position, target, up)

    # make view matrix from camera
    view_matrix = matrix.quick_inverse(camera_matrix)

    triangles_to_draw = []

    # prepare triangles
    for tri in mesh:
        tri_projected = Triangle.get_empty()
        tri_transformed = Triangle.get_empty()
        tri_viewed = Triangle.get_empty()

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

            clipped = triangle.clip_against_plane(Vector3(0, 0, 1.1, 1), Vector3(0, 0, 1, 1),
                                                  tri_viewed)

            second = False

            for clipped_tri in clipped:

                # prevents the new triangle overwriting the old one when added to the list to draw
                if second:
                    old_colour = tri_projected.colour

                    tri_projected = Triangle.get_empty()
                    tri_projected.colour = old_colour

                second = True

                # apply any colour changes from clipping
                tri_projected.colour = clipped_tri.colour

                # Project triangles from 3D --> 2D
                tri_projected.p[0] = matrix.matrix_x_vector(projection_matrix,
                                                            clipped_tri.p[0])
                tri_projected.p[1] = matrix.matrix_x_vector(projection_matrix,
                                                            clipped_tri.p[1])
                tri_projected.p[2] = matrix.matrix_x_vector(projection_matrix,
                                                            clipped_tri.p[2])
                tri_projected.t[0] = clipped_tri.t[0]
                tri_projected.t[1] = clipped_tri.t[1]
                tri_projected.t[2] = clipped_tri.t[2]

                tri_projected.t[0].u = tri_projected.t[0].u / tri_projected.p[0].w
                tri_projected.t[1].u = tri_projected.t[1].u / tri_projected.p[1].w
                tri_projected.t[2].u = tri_projected.t[2].u / tri_projected.p[2].w

                tri_projected.t[0].v = tri_projected.t[0].v / tri_projected.p[0].w
                tri_projected.t[1].v = tri_projected.t[1].v / tri_projected.p[1].w
                tri_projected.t[2].v = tri_projected.t[2].v / tri_projected.p[2].w

                tri_projected.t[0].w = 1 / tri_projected.p[0].w
                tri_projected.t[1].w = 1 / tri_projected.p[1].w
                tri_projected.t[2].w = 1 / tri_projected.p[2].w

                # scale into view
                tri_projected.p[0] = vector.divide(tri_projected.p[0], tri_projected.p[0].w)
                tri_projected.p[1] = vector.divide(tri_projected.p[1], tri_projected.p[1].w)
                tri_projected.p[2] = vector.divide(tri_projected.p[2], tri_projected.p[2].w)

                # Scale into view
                offset_view = Vector3(1, 1, 0, 1)
                tri_projected.p[0] = vector.add(tri_projected.p[0], offset_view)
                tri_projected.p[1] = vector.add(tri_projected.p[1], offset_view)
                tri_projected.p[2] = vector.add(tri_projected.p[2], offset_view)

                tri_projected.p[0].x *= 0.5 * screen_x
                tri_projected.p[0].y *= 0.5 * screen_y
                tri_projected.p[1].x *= 0.5 * screen_x
                tri_projected.p[1].y *= 0.5 * screen_y
                tri_projected.p[2].x *= 0.5 * screen_x
                tri_projected.p[2].y *= 0.5 * screen_y

                # store triangle for sorting and rendering
                triangles_to_draw.append(tri_projected)

    # sort the list of triangles into the order of their appearance, so that you don't have things
    # further away rendering in front of close things
    def sort_criteria(v):
        return (v.p[0].z + v.p[1].z + v.p[2].z) / 3

    triangles_to_draw.sort(reverse=True, key=sort_criteria)

    # clip triangles against the edge of the screen and render triangles
    triangles_to_draw = clip_against_screen(triangles_to_draw)
    render_mesh(triangles_to_draw)


def clip_against_screen(triangles_to_draw: [Triangle]):
    if len(triangles_to_draw) > 0:

        running_triangles = []

        for tri in triangles_to_draw:
            triangles = [tri]
            new_tris = 1

            for p in range(4):
                while new_tris > 0:
                    test = triangles[0]
                    triangles.pop(0)
                    new_tris -= 1

                    if p == 0:
                        tris_to_add = clip_against_plane(Vector3(0, 0, 0, 1), Vector3(0, 1, 0, 1),
                                                         test)
                    elif p == 1:
                        tris_to_add = clip_against_plane(Vector3(0, screen_y - 1, 0, 1),
                                                         Vector3(0, -1, 0, 1), test)
                    elif p == 2:
                        tris_to_add = clip_against_plane(Vector3(0, 0, 0, 1), Vector3(1, 0, 0, 1),
                                                         test)
                    elif p == 3:
                        tris_to_add = clip_against_plane(Vector3(screen_x - 1, 0, 0, 1),
                                                         Vector3(-1, 0, 0, 1), test)
                    else:
                        tris_to_add = []

                    for t in tris_to_add:
                        triangles.append(t)

                new_tris = len(triangles)

            for t in triangles:
                running_triangles.append(t)

        return running_triangles
    return []


def render_mesh(mesh: [Triangle]):
    for triangle in mesh:
        render_triangle(triangle)


def render_triangle(t: Triangle):
    if draw_solid:
        draw_triangle_solid((int(t.p[0].x), int(t.p[0].y)),
                            (int(t.p[1].x), int(t.p[1].y)),
                            (int(t.p[2].x), int(t.p[2].y)),
                            t.colour)

    if draw_wireframe:
        draw_triangle_wireframe((int(t.p[0].x), int(t.p[0].y)),
                                (int(t.p[1].x), int(t.p[1].y)),
                                (int(t.p[2].x), int(t.p[2].y)))

    if draw_texture:
        draw_triangle_texture(t.p[0].x, t.p[0].y, t.t[0].u, t.t[0].v, t.t[0].w,
                              t.p[1].x, t.p[1].y, t.t[1].u, t.t[1].v, t.t[1].w,
                              t.p[2].x, t.p[2].y, t.t[2].u, t.t[2].v, t.t[2].w,
                              None)


def draw_triangle_solid(p1, p2, p3, colour):
    py.draw.polygon(screen, colour, (p1, p2, p3))


def draw_triangle_wireframe(p1, p2, p3):
    py.draw.line(screen, wireframe_colour, p1, p2, 1)
    py.draw.line(screen, wireframe_colour, p2, p3, 1)
    py.draw.line(screen, wireframe_colour, p3, p1, 1)


def draw_triangle_texture(x1: int, y1: int, u1: float, v1: float, w1: float,
                          x2: int, y2: int, u2: float, v2: float, w2: float,
                          x3: int, y3: int, u3: float, v3: float, w3: float,
                          texture):
    global depth_buffer

    if y2 < y1:
        y1, y2 = y2, y1
        x1, x2 = x2, x1
        u1, u2 = u2, u1
        v1, v2 = v2, v1
        w1, w2 = w2, w1

    if y3 < y1:
        y1, y3 = y3, y1
        x1, x3 = x3, x1
        u1, u3 = u3, u1
        v1, v3 = v3, v1
        w1, w3 = w3, w1

    if y3 < y2:
        y2, y3 = y3, y2
        x2, x3 = x3, x2
        u2, u3 = u3, u2
        v2, v3 = v3, v2
        w2, w3 = w3, w2

    dy1 = y2 - y1
    dx1 = x2 - x1
    dv1 = v2 - v1
    du1 = u2 - u1
    dw1 = w2 - w1

    dy2 = y3 - y1
    dx2 = x3 - x1
    dv2 = v3 - v1
    du2 = u3 - u1
    dw2 = w3 - w1

    tex_u: float
    tex_v: float
    tex_w: float

    dax_step = 0
    dbx_step = 0
    du1_step = 0
    dv1_step = 0
    du2_step = 0
    dv2_step = 0
    dw1_step = 0
    dw2_step = 0

    if dy1:
        dax_step = dx1 / float(abs(dy1))
    if dy2:
        dbx_step = dx2 / float(abs(dy2))

    if dy1:
        du1_step = du1 / float(abs(dy1))
    if dy1:
        dv1_step = dv1 / float(abs(dy1))
    if dy1:
        dw1_step = dw1 / float(abs(dy1))

    if dy2:
        du2_step = du2 / float(abs(dy2))
    if dy2:
        dv2_step = dv2 / float(abs(dy2))
    if dy2:
        dw2_step = dw2 / float(abs(dy2))

    if dy1:
        i = y1
        while i <= y2:
            i += 1

            ax: int = x1 + float(i - y1) * dax_step
            bx: int = x1 + float(i - y1) * dbx_step

            # texture start
            tex_su = u1 + float(i - y1) * du1_step
            tex_sv = v1 + float(i - y1) * dv1_step
            tex_sw = w1 + float(i - y1) * dw1_step

            # texture end
            tex_eu = u1 + float(i - y1) * du2_step
            tex_ev = v1 + float(i - y1) * dv2_step
            tex_ew = w1 + float(i - y1) * dw2_step

            if ax > bx:
                ax, bx = bx, ax
                tex_su, tex_eu = tex_eu, tex_su
                tex_sv, tex_ev = tex_ev, tex_sv
                tex_sw, tex_ew = tex_ew, tex_sw

            tex_u = tex_su
            tex_v = tex_sv
            tex_w = tex_sw

            texture_step = 1 / float(bx - ax)
            t = 0

            j = ax
            while j < bx:
                j += 1

                tex_u = (1 - t) * tex_su + t * tex_eu
                tex_v = (1 - t) * tex_sv + t * tex_ev
                tex_w = (1 - t) * tex_sw + t * tex_ew

                if tex_w > depth_buffer[int(i * screen_x + j)]:
                    sample_x = int(round(screen_x * tex_u / tex_w))
                    sample_y = int(round(screen_y * tex_v / tex_w))
                    screen.set_at((int(j), int(i)), (255, 0, 0))  # texture.getpixel((sample_x, sample_y)
                    depth_buffer[round(int(i * screen_x + j))] = tex_w

                t += texture_step

    dy1 = y3 - y2
    dx1 = x3 - x2
    dv1 = v3 - v2
    du1 = u3 - u2
    dw1 = w3 - w2

    if dy1:
        dax_step = dx1 / float(abs(dy1))
    if dy2:
        dbx_step = dx2 / float(abs(dy2))

    du1_step = 0
    dv1_step = 0
    if dy1:
        du1_step = du1 / float(abs(dy1))
    if dy1:
        dv1_step = dv1 / float(abs(dy1))
    if dy1:
        dw1_step = dw1 / float(abs(dy1))

    if dy1:
        i = y2
        while i <= y3:
            i += 1

            ax: int = x2 + float(i - y2) * dax_step
            bx: int = x1 + float(i - y1) * dbx_step

            tex_su = u2 + float(i - y2) * du1_step
            tex_sv = v2 + float(i - y2) * dv1_step
            tex_sw = w2 + float(i - y2) * dw1_step

            tex_eu = u1 + float(i - y1) * du2_step
            tex_ev = v1 + float(i - y1) * dv2_step
            tex_ew = w1 + float(i - y1) * dw2_step

            if ax > bx:
                ax, bx = bx, ax
                tex_su, tex_eu = tex_eu, tex_su
                tex_sv, tex_ev = tex_ev, tex_sv
                tex_sw, tex_ew = tex_ew, tex_sw

            tex_u = tex_su
            tex_v = tex_sv
            tex_w = tex_sw

            texture_step = 1 / float(bx - ax)
            t = 0

            j = ax
            while j < bx:
                j += 1

                tex_u = (1 - t) * tex_su + t * tex_eu
                tex_v = (1 - t) * tex_sv + t * tex_ev
                tex_w = (1 - t) * tex_sw + t * tex_ew

                if tex_w > depth_buffer[int(i * screen_x + j)]:
                    sample_x = int(round(tex_u / tex_w))
                    sample_y = int(round(tex_v / tex_w))
                    screen.set_at((int(j), int(i)), (0, 255, 0))  # texture.getpixel((sample_x, sample_y)
                    depth_buffer[round(i * screen_x + j)] = tex_w

                t += texture_step
