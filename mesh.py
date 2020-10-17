# ================================================================================================
# |------------------------------------={ Project Name }=----------------------------------------|
# ================================================================================================
#
#                                   Programmers : Joseph Coppin
#
#                                     File Name : mesh.py
#
#                                       Created : Month 00, 2020
#
# ------------------------------------------------------------------------------------------------
#
#   Imports:
from vector import Vector3
from triangle import Triangle
#
# ------------------------------------------------------------------------------------------------
#
#                                       What the file does.
#
# ------------------------------------------------------------------------------------------------
#
#
# ================================================================================================


class Mesh:
    def __init__(self, triangles):
        self.triangles = triangles

    def load_from_file(self, file_name):
        with open(file_name) as file:
            stash = []
            for line in file:
                line = line.split()
                if len(line) > 0:

                    if line[0] == 'v':
                        stash.append(Vector3(round(float(line[1])), round(float(line[2])), round(float(line[3])), 1))

                    if line[0] == 'f':
                        self.triangles.append(Triangle(
                            stash[round(float(line[1])) - 1],
                            stash[round(float(line[2])) - 1],
                            stash[round(float(line[3])) - 1],
                        ))
