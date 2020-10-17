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
from PIL import Image

import global_data
import matrix

from vector import Vector3
from triangle import clip_against_plane

from triangle import Triangle
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

draw_solid = True

projection_matrix = matrix.projection(global_data.fov, screen_y / screen_x, 0.1, 100000)


def pygame_tick():
    py.display.flip()
    clock.tick(run_FPS)
    screen.fill(background_colour)

    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            quit()


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
                        tris_to_add = clip_against_plane(Vector3(0, 0, 0, 1), Vector3(0, 1, 0, 1), test)
                    elif p == 1:
                        tris_to_add = clip_against_plane(Vector3(0, screen_y - 1, 0, 1), Vector3(0, -1, 0, 1), test)
                    elif p == 2:
                        tris_to_add = clip_against_plane(Vector3(0, 0, 0, 1), Vector3(1, 0, 0, 1), test)
                    elif p == 3:
                        tris_to_add = clip_against_plane(Vector3(screen_x - 1, 0, 0, 1), Vector3(-1, 0, 0, 1), test)
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


def render_triangle(triangle: Triangle):
    if draw_solid:
        draw_triangle_solid((int(triangle.p[0].x), int(triangle.p[0].y)),
                            (int(triangle.p[1].x), int(triangle.p[1].y)),
                            (int(triangle.p[2].x), int(triangle.p[2].y)),
                            triangle.colour)

    if draw_wireframe:
        draw_triangle_wireframe((int(triangle.p[0].x), int(triangle.p[0].y)),
                                (int(triangle.p[1].x), int(triangle.p[1].y)),
                                (int(triangle.p[2].x), int(triangle.p[2].y)))


def draw_triangle_solid(p1, p2, p3, colour):
    py.draw.polygon(screen, colour, (p1, p2, p3))


def draw_triangle_wireframe(p1, p2, p3):
    py.draw.line(screen, wireframe_colour, p1, p2, 1)
    py.draw.line(screen, wireframe_colour, p2, p3, 1)
    py.draw.line(screen, wireframe_colour, p3, p1, 1)


def draw_triangle_texture(x1, y1, u1, v1, w1, x2, y2, u2, v2, w2, x3, y3, u3, v3, w3, texture):

    # swap based on y position on the screen
    def swap(a, b):
        temp = a
        b = a
        a = temp

    if y2 < y1:
        swap(y1, y2)
        swap(x1, x2)
        swap(u1, u2)
        swap(v1, v2)
        swap(w1, w2)

    if y3 < y1:
        swap(y1, y3)
        swap(x1, x3)
        swap(u1, u3)
        swap(v1, v3)
        swap(w1, w3)

    if y3 < y2:
        swap(y2, y3)
        swap(x2, x3)
        swap(u2, u3)
        swap(v2, v3)
        swap(w2, w3)

    # various info needed
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

    dax_step = 0
    dbx_step = 0
    du1_step = 0
    dv1_step = 0
    du2_step = 0
    dv2_step = 0

    if dy1:
        dax_step = dx1 / abs(dy1)
    if dy2:
        dbx_step = dx2 / abs(dy2)

    if dy1:
        du1_step = du1 / abs(dy1)
    if dy1:
        dv1_step = dv1 / abs(dy1)

    if dy2:
        du2_step = du2 / abs(dy2)
    if dy2:
        dv2_step = dv2 / abs(dy2)

    if dy1:
        for i in range(y1, y2):
            ax = x1 + float(i - y1) * dax_step
            bx = x1 + float(i - y1) * dbx_step

            tex_su = u1 + float(i - y1) * du1_step
            tex_sv = v1 + float(i - y1) * dv1_step

            tex_eu = u1 + float(i - y1) * du2_step
            tex_ev = v1 + float(i - y1) * dv2_step

            if ax > bx:
                swap(ax, bx)
                swap(tex_su, tex_eu)
                swap(tex_sv, tex_ev)

            tex_u = tex_su
            tex_v = tex_sv

            texture_step = 1 / (bx-ax)
            t = 0

            for j in range(ax, bx):
                tex_u = (1 - t) * tex_su + t * tex_eu
                tex_v = (1 - t) * tex_sv + t * tex_ev
                screen.set_at((j, i), tex.SampleGlyph(tex_u, tex_v), tex.SampleColour(tex_u, tex_v))
                t += texture_step
