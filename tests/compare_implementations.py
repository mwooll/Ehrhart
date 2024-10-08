from ehrhart_quasi_polynomial import ehrhart_quasi_polynomial

from sage.geometry.polyhedron.constructor import Polyhedron

from unittest import TestCase, main


def simplex(dim):
    vertices = [[0 for k in range(dim)] for v in range(dim+1)]
    for d in range(dim):
        vertices[d][d] = 1
    return vertices

class Comparer(TestCase):
    def compare(self, vertices):
        own = ehrhart_quasi_polynomial(vertices)
        latte = Polyhedron(vertices).ehrhart_polynomial(variable="x")
        self.assertEqual(own, latte)

    # latte fails for polytopes with only 1 vertex
    # though the ehrhart_polynomial is just 1 anyway (if the vertex is integral)
    def degree_0(self):
        point = [[0, 0, 0, 0, 0]]
        self.compare(point)

    def test_degree_1(self):
        axis = [[-3], [3]]
        self.compare(axis)

        diagonal = [[0, 0], [1, 1]]
        self.compare(diagonal)

    def test_degree_2(self):
        triangle = [[0, 0], [3, 0], [0, 6]]
        self.compare(triangle)

        square = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        self.compare(square)

        dont_know = [[0, 0], [-1, 1], [2, 0], [0, 1]]
        self.compare(dont_know)

    def test_degree_3(self):
        cube = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]]
        self.compare(cube)

    def test_simplex(self):
        for d in range(2, 6):
            smplx = simplex(d)
            self.compare(smplx)


if __name__ == "__main__":
    main()