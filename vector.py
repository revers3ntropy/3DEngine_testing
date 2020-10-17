# ================================================================================================
# |------------------------------------={ Project Name }=----------------------------------------|
# ================================================================================================
#
#                                   Programmers : Joseph Coppin
#
#                                     File Name : file_name.py
#
#                                       Created : Month 00, 2020
#
# ------------------------------------------------------------------------------------------------
#
#   Imports:
import math
#
# ------------------------------------------------------------------------------------------------
#
#                                       What the file does.
#
# ------------------------------------------------------------------------------------------------
#
# ================================================================================================


class Vector2:
    def __init__(self, u, v):
        self.u = u
        self.v = v


class Vector3:
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    # ================================================================================================
    #   normalise - sets the vector to a normalised version of itself
    #
    #   Parameters:     none
    #
    #   Returns:    none
    #
    # ================================================================================================
    def normalise(self):
        length = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        if length > 0:
            self.x /= length
            self.y /= length
            self.z /= length


# ================================================================================================
#   add - More detailed description of what the function does.
# ================================================================================================
def add(v1: Vector3, v2: Vector3):
    return Vector3(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z, 1)


# ================================================================================================
#   sub - subtracts one vector from another
# ================================================================================================
def subtract(v1: Vector3, v2: Vector3):
    return Vector3(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z, 1)


# ================================================================================================
#   multiply - Times one vector by another
# ================================================================================================
def multiply(v1: Vector3, k: float):
    return Vector3(v1.x * k, v1.y * k, v1.z * k, 1)


def divide(v1: Vector3, k: float):
    if k != 0:
        return Vector3(v1.x / k, v1.y / k, v1.z / k, 1)
    else:
        return Vector3(1, 1, 1, 1)


# ================================================================================================
#   dot_product - returns how close to each other two vectors are
# ================================================================================================
def dot_product(v1: Vector3, v2: Vector3):
    return v1.x*v2.x + v1.y*v2.y + v1.z * v2.z


# ================================================================================================
#   first_function - Returns the length of the vector
# ================================================================================================
def length(v: Vector3):
    return math.sqrt(dot_product(v, v))


# ================================================================================================
#   cross_product - returns a vector at a right angle to both inputted vectors
# ================================================================================================
def cross_product(v1: Vector3, v2: Vector3):
    return Vector3(
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x,
        1)


# ================================================================================================
#   intersect_plane - no clue
# ================================================================================================
def intersect_plane(plane_p: Vector3, plane_n: Vector3, line_start: Vector3, line_end: Vector3, t: float):
    plane_n.normalise()
    plane_d = -dot_product(plane_n, plane_p)
    ad = dot_product(line_start, plane_n)
    bd = dot_product(line_end, plane_n)
    t = (-plane_d - ad) / (bd - ad)
    line_start_to_end = subtract(line_end, line_start)
    line_to_intersect = multiply(line_start_to_end, t)
    return add(line_start, line_to_intersect)