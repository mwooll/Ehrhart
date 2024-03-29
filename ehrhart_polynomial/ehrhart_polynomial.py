from itertools import product

import sage.all
from sage.rings.rational_field import QQ
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.geometry.polyhedron.constructor import Polyhedron
from sage.arith.misc import gcd

R = PolynomialRing(QQ, "x")
x = R.gen() 


# calculate ehrhart polynomial
def ehrhart_polynomial(vertices, simplify=False):
    y_values, scale_factor = points_contained(vertices, simplify)

    interpolation_points = [(k+1, y) for k, y in enumerate(y_values)]
    polynomial = R.lagrange_polynomial(interpolation_points)
    polynomial = polynomial(scale_factor*x)
    
    return polynomial

def points_contained(vertices, simplify):
    dimension = len(vertices[0])

    if simplify:
        result = simplify_vertices(vertices, dimension)
        vertices, base_min, base_max, dimension, scale_factor = result
    else:
        base_min, base_max = get_bounding_extrema(vertices, dimension)
        scale_factor = 1

    base_poly = Polyhedron(vertices)

    points_contained = [0]*(dimension+1)
    for k in range(1, dimension+2):
        poly = k*base_poly
        box = get_bounding_box(base_min, base_max, k)

        contained = 0
        for point in box:
            if point in poly:
                contained += 1 

        points_contained[k-1] = contained

    return points_contained, scale_factor


# get bounding box of polyhedron
def get_bounding_extrema(vertices, dimension):
    columns = [[vertex[d] for vertex in vertices]
               for d in range(dimension)]
    mins = [min(col) for col in columns]
    maxs = [max(col) for col in columns]
    return mins, maxs

def get_bounding_box(mins, maxs, factor):
    return product(*[range(factor*mini, factor*maxi + 1)
                     for mini, maxi in zip(mins, maxs)])


# simplify the polyhedron
def simplify_vertices(vertices, dimension):
    vertices, mins, maxs, new_dim = drop_constant_dimensions(vertices, dimension)
    new_vertices, scale_factor = scale_down_vertices(vertices)

    new_mins = [mini//scale_factor for mini in mins]
    new_maxs = [maxi//scale_factor for maxi in maxs]
    return new_vertices, new_mins, new_maxs, new_dim, scale_factor

def drop_dimensions(to_reduce, keep_filter):
    return [[val for val, keep in zip(vertex, keep_filter) if keep]
            for vertex in to_reduce]

def drop_constant_dimensions(vertices, dimension):
    columns = [[vertex[d] for vertex in vertices]
               for d in range(dimension)]
    mins = [min(col) for col in columns]
    maxs = [max(col) for col in columns]

    not_equal = [mins[d] != maxs[d] for d in range(dimension)]
    
    vertices = drop_dimensions(vertices, not_equal)
    mins, maxs = drop_dimensions([mins, maxs], not_equal)
    new_dimension = sum(not_equal)
    return vertices, mins, maxs, new_dimension

def scale_down_vertices(vertices):
    scale_factor = gcd(num for vertex in vertices for num in vertex)
    vertices = [[num//scale_factor for num in vertex] for vertex in vertices]
    return vertices, scale_factor
