# ================================================================================================
# |------------------------------------={ Project Name }=----------------------------------------|
# ================================================================================================
#
#                                   Programmers : Joseph Coppin
#
#                                     File Name : triangle.py
#
#                                       Created : Month 00, 2020
#
# ------------------------------------------------------------------------------------------------
#
#   Imports:
from vector import Vector3
from vector import Vector2
import vector
#
# ------------------------------------------------------------------------------------------------
#
#                                      Holds triangle object.
#
# ------------------------------------------------------------------------------------------------
#
# ================================================================================================


class Triangle:
    def __init__(self, p1: Vector3, p2: Vector3, p3: Vector3, t1: Vector2, t2: Vector2, t3: Vector2):
        # coordinates
        self.p = [p1, p2, p3]
        self.colour = (0, 0, 0)
        # texture coordinates
        self.t = [t1, t2, t3]

    @staticmethod
    def get_empty():
        return Triangle(Vector3(0, 0, 0, 1), Vector3(0, 0, 0, 1), Vector3(0, 0, 0, 1), Vector2(0, 0), Vector2(0, 0), Vector2(0, 0))


def clip_against_plane(plane_p: Vector3, plane_n: Vector3, in_tri: Triangle):
    # init a list of triangles for returning
    out = []
    # Make sure plane normal is indeed normal
    plane_n.normalise()

    def dist(p: Vector3):
        # Return shortest distance from point to plane, plane normal must be normalised
        return (plane_n.x * p.x + plane_n.y * p.y + plane_n.z * p.z -
                vector.dot_product(plane_n, plane_p))

    # Create two temporary storage lists to classify points either side of plane.
    # If distance sign is positive, point lies on "inside" of plane.
    inside_points = []
    outside_points = []
    # similar storage for texture coordinates
    inside_point_texture = []
    outside_point_texture = []

    # Get signed distance of each point in triangle to plane
    d0 = dist(in_tri.p[0])
    d1 = dist(in_tri.p[1])
    d2 = dist(in_tri.p[2])

    if d0 >= 0:
        inside_points.append(in_tri.p[0])
        inside_point_texture.append(in_tri.t[0])
    else:
        outside_points.append(in_tri.p[0])
        outside_point_texture.append(in_tri.t[0])
    if d1 >= 0:
        inside_points.append(in_tri.p[1])
        inside_point_texture.append(in_tri.t[1])
    else:
        outside_points.append(in_tri.p[1])
        outside_point_texture.append(in_tri.t[1])
    if d2 >= 0:
        inside_points.append(in_tri.p[2])
        inside_point_texture.append(in_tri.t[2])
    else:
        outside_points.append(in_tri.p[2])
        outside_point_texture.append(in_tri.t[2])

    inside_point_count = len(inside_points)
    outside_point_count = len(outside_points)

    # Now classify triangle points, and break the input triangle into smaller output triangles if
    # required. There are four possible outcomes...

    if inside_point_count == 0:
        # All points lie on the outside of plane, so do nothing and the whole triangle will be clipped
        pass
        # No returned triangles are valid

    if inside_point_count == 3:
        # All points lie on the inside of plane, so allow the triangle to simply pass through

        out.append(in_tri)

        # for debug:
        # out[0].colour = (0, 255, 0)

        # Just the one returned original triangle is valid, so return it

    if inside_point_count == 1 and outside_point_count == 2:
        # Triangle should be clipped. As two points lie outside
        # the plane, the triangle simply becomes a smaller triangle

        # adds a new point to the out list
        out.append(Triangle(Vector3(0, 0, 0, 1), Vector3(0, 0, 0, 1), Vector3(0, 0, 0, 1),
                            Vector2(0, 0), Vector2(0, 0), Vector2(0, 0)))

        # Copy appearance info to new triangle. Set to value for debug
        out[0].colour = in_tri.colour

        # The inside point is valid, so keep that...
        out[0].p[0] = inside_points[0]
        out[0].t[0] = inside_point_texture[0]

        # but the two new points are at the locations where the
        # original sides of the triangle (lines) intersect with the plane
        t: float
        temp = vector.intersect_plane(plane_p, plane_n, inside_points[0], outside_points[0])
        out[0].p[1] = temp[0]
        t = temp[1]

        out[0].t[1].u = t * (outside_point_texture[0].u - inside_point_texture[0].u) + inside_point_texture[0].u
        out[0].t[1].v = t * (outside_point_texture[0].v - inside_point_texture[0].v) + inside_point_texture[0].v

        temp = vector.intersect_plane(plane_p, plane_n, inside_points[0], outside_points[1])
        out[0].p[2] = temp[0]
        t = temp[1]
        out[0].t[2].u = t * (outside_point_texture[1].u - inside_point_texture[0].u) + inside_point_texture[0].u
        out[0].t[2].v = t * (outside_point_texture[1].v - inside_point_texture[0].v) + inside_point_texture[0].v

        # Return the newly formed single triangle

    if inside_point_count == 2 and outside_point_count == 1:
        # Triangle should be clipped. As two points lie inside the plane,
        # the clipped triangle becomes a "quad". Fortunately, we can
        # represent a quad with two new triangles

        # adds a new point to the out list
        out.append(Triangle.get_empty())
        out.append(Triangle.get_empty())

        # Copy appearance info to new triangles. Set to value for debug
        out[0].colour = in_tri.colour

        out[1].colour = in_tri.colour

        # The first triangle consists of the two inside points and a new
        # point determined by the location where one side of the triangle
        # intersects with the plane
        out[0].p[0] = inside_points[0]
        out[0].p[1] = inside_points[1]
        out[0].t[0] = inside_point_texture[0]
        out[0].t[1] = inside_point_texture[1]

        t: float
        temp = vector.intersect_plane(plane_p, plane_n, inside_points[0], outside_points[0])
        t = temp[1]
        out[0].t[2].u = t * (outside_point_texture[0].u - inside_point_texture[0].u) + inside_point_texture[0].u
        out[0].t[2].v = t * (outside_point_texture[0].v - inside_point_texture[0].v) + inside_point_texture[0].v
        out[0].p[2] = temp[0]

        # The second triangle is composed of one of he inside points, a
        # new point determined by the intersection of the other side of the
        # triangle and the plane, and the newly created point above
        out[1].p[0] = inside_points[1]
        out[1].t[0] = inside_point_texture[1]
        out[1].p[1] = out[0].p[2]
        out[1].t[1] = out[1].t[2]

        temp = vector.intersect_plane(plane_p, plane_n, inside_points[1], outside_points[0])
        out[1].p[2] = temp[0]
        t = temp[1]
        out[1].t[2].u = t * (outside_point_texture[0].u - inside_point_texture[1].u) + inside_point_texture[1].u
        out[1].t[2].v = t * (outside_point_texture[0].v - inside_point_texture[1].v) + inside_point_texture[1].v

        # Return the two newly formed triangles which form a quad

    return out
