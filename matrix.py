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
import vector
from vector import Vector3
import math
#
# ------------------------------------------------------------------------------------------------
#
#                                       What the file does.
#
# ------------------------------------------------------------------------------------------------
#
# global_function_1
#
# class 'preset'
#   function_1
#
# ================================================================================================


class Matrix4:
    def __init__(self):
        self.m = []
        self.init_matrix()

    # ================================================================================================
    #   first_function - Fills the matrix with 0s.
    # ================================================================================================
    def init_matrix(self):
        for j in range(4):
            line = []
            for k in range(4):
                line.append(0)
            self.m.append(line)


def get_identity_matrix():
    identity_matrix = Matrix4()
    identity_matrix.m[0][0] = 1
    identity_matrix.m[1][1] = 1
    identity_matrix.m[2][2] = 1
    identity_matrix.m[3][3] = 1
    return identity_matrix


def rotation_x(angle: float):
    matrix = Matrix4()

    matrix.m[0][0] = 1
    matrix.m[1][1] = math.cos(angle)
    matrix.m[1][2] = math.sin(angle)
    matrix.m[2][1] = -math.sin(angle)
    matrix.m[2][2] = math.cos(angle)
    matrix.m[3][3] = 1

    return matrix


def rotation_y(angle: float):
    matrix = Matrix4()

    matrix.m[0][0] = math.cos(angle)
    matrix.m[0][2] = math.sin(angle)
    matrix.m[2][0] = -math.sin(angle)
    matrix.m[1][1] = 1
    matrix.m[2][2] = math.cos(angle)
    matrix.m[3][3] = 1

    return matrix


def rotation_z(angle: float):
    matrix = Matrix4()

    matrix.m[0][0] = math.cos(angle)
    matrix.m[0][1] = math.sin(angle)
    matrix.m[1][0] = -math.sin(angle)
    matrix.m[1][1] = math.cos(angle)
    matrix.m[2][2] = 1
    matrix.m[3][3] = 1

    return matrix


def translate(x: float, y: float, z: float):
    matrix = Matrix4()
    matrix.m[0][0] = 1
    matrix.m[1][1] = 1
    matrix.m[2][2] = 1
    matrix.m[3][3] = 1
    matrix.m[3][0] = x
    matrix.m[3][1] = y
    matrix.m[3][2] = z

    return matrix


def projection(fov_degrees: float, aspect_ratio: float, near: float, far: float):
    fov_radians = 1 / math.tan(fov_degrees * 0.5 / 180 * 3.14159)

    matrix = Matrix4()

    matrix.m[0][0] = aspect_ratio * fov_radians
    matrix.m[1][1] = fov_radians
    matrix.m[2][2] = far / (far - near)
    matrix.m[3][2] = (-far * near) / (far - near)
    matrix.m[2][3] = 1
    matrix.m[3][3] = 0

    return matrix


def matrix_x_matrix(m1: Matrix4, m2: Matrix4):
    matrix = Matrix4()

    for c in range(4):
        for r in range(4):
            matrix.m[r][c] = m1.m[r][0] * m2.m[0][c] + m1.m[r][1] * m2.m[1][c] + m1.m[r][2] * \
                             m2.m[2][c] + m1.m[r][3] * m2.m[3][c]

    return matrix


def matrix_x_vector(m: Matrix4, i: Vector3):
    v = vector.Vector3(
        i.x * m.m[0][0] + i.y * m.m[1][0] + i.z * m.m[2][0] + i.w * m.m[3][0],
        i.x * m.m[0][1] + i.y * m.m[1][1] + i.z * m.m[2][1] + i.w * m.m[3][1],
        i.x * m.m[0][2] + i.y * m.m[1][2] + i.z * m.m[2][2] + i.w * m.m[3][2],
        i.x * m.m[0][3] + i.y * m.m[1][3] + i.z * m.m[2][3] + i.w * m.m[3][3]
    )
    return v


def point_at(pos: Vector3, target: Vector3, up: Vector3):
    # Calculate new forward direction
    new_forward = vector.subtract(target, pos)
    new_forward.normalise()

    # Calculate new Up direction
    a: Vector3 = vector.multiply(new_forward, vector.dot_product(up, new_forward))
    new_up: Vector3 = vector.subtract(up, a)
    new_up.normalise()

    # New Right direction is easy, its just cross product
    new_right: vector.Vector3 = vector.cross_product(new_up, new_forward)

    # Construct Dimensioning and Translation Matrix
    matrix = Matrix4()
    matrix.m[0][0] = new_right.x;	matrix.m[0][1] = new_right.y;	matrix.m[0][2] = new_right.z;	matrix.m[0][3] = 0
    matrix.m[1][0] = new_up.x;		matrix.m[1][1] = new_up.y;		matrix.m[1][2] = new_up.z;		matrix.m[1][3] = 0
    matrix.m[2][0] = new_forward.x;	matrix.m[2][1] = new_forward.y;	matrix.m[2][2] = new_forward.z;	matrix.m[2][3] = 0
    matrix.m[3][0] = pos.x;			matrix.m[3][1] = pos.y;			matrix.m[3][2] = pos.z;			matrix.m[3][3] = 1
    return matrix


def quick_inverse(m: Matrix4):  # Only for Rotation/Translation Matrices
    matrix = Matrix4()

    matrix.m[0][0] = m.m[0][0]; matrix.m[0][1] = m.m[1][0]; matrix.m[0][2] = m.m[2][0]; matrix.m[0][3] = 0
    matrix.m[1][0] = m.m[0][1]; matrix.m[1][1] = m.m[1][1]; matrix.m[1][2] = m.m[2][1]; matrix.m[1][3] = 0
    matrix.m[2][0] = m.m[0][2]; matrix.m[2][1] = m.m[1][2]; matrix.m[2][2] = m.m[2][2]; matrix.m[2][3] = 0
    matrix.m[3][0] = -(m.m[3][0] * matrix.m[0][0] + m.m[3][1] * matrix.m[1][0] + m.m[3][2] * matrix.m[2][0])
    matrix.m[3][1] = -(m.m[3][0] * matrix.m[0][1] + m.m[3][1] * matrix.m[1][1] + m.m[3][2] * matrix.m[2][1])
    matrix.m[3][2] = -(m.m[3][0] * matrix.m[0][2] + m.m[3][1] * matrix.m[1][2] + m.m[3][2] * matrix.m[2][2])
    matrix.m[3][3] = 1

    return matrix
