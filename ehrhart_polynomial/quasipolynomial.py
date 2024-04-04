from math import lcm

from integerperiodicfunction import IntegerPeriodicFunction

class QuasiPolynomial():
    def __init__(self, coefs=None):
        if coefs is None:
            coefs = [0]
        else:
            if not isinstance(coefs, (tuple, list)):
                return TypeError("coefs must be instance of list or tuple, or be None"
                                 + f", but has type {type(coefs)}")

        for index, coef in enumerate(coefs):
            if isinstance(coef, (int, float)):
                coefs[index] = IntegerPeriodicFunction([coef])
            elif isinstance(coef, IntegerPeriodicFunction):
                pass
            elif hasattr(coef, "__int__"):
                coefs[index] = IntegerPeriodicFunction([int(coef)])
            elif hasattr(coef, "__float__"):
                coefs[index] = IntegerPeriodicFunction([float(coef)])
            else:
                raise TypeError("elements of coefs must be instances of "
                                + "IntegerPeriodicFunction, int or float,"
                                + " or implement __int__ or __float__"
                                + f"but is has type {type(coef)}")

        self.coefs, self.degree = self._reduce_coefs(coefs)
        self.period = self._calculate_peroid()

    """
    methods called in __init__
    """
    def _reduce_coefs(self, coefs):
        degree = len(coefs)
        while coefs[degree-1] == 0 and degree > 1:
            degree -= 1

        if degree == 0:
            coefs = [0]
            degree = 1
        else:
            coefs = coefs[:degree]

        return coefs, degree

    def _calculate_peroid(self):
        periods = (coef.period for coef in self.coefs)
        period = lcm(*periods)
        return period

    """
    use class obejct as function
    """
    def __call__(self, value):
        result = 0
        for power, coef in enumerate(self.coefs):
            result += coef(value) * value**power
        return result

    """
    standard dunder methods
    """
    def __str__(self):
        function_str = "QuasiPolynomial given by \n"
        function_str += f"{self.coefs[0].coefficient_repr('k')}"
        for power, coef in enumerate(self.coefs[1:]):
            function_str += f" + {coef.coefficient_repr('k')}*k" + f"^{power+1}"*(power>0)
        return function_str

    def __repr__(self):
        return f"QuasiPolynomial({self.coefs})"

    """
    comparison operators
    """
    def __eq__(self, other):
        if isinstance(other, QuasiPolynomial):
            return self.coefs == other.coefs
        return False

    """
    math support
    """
    def __neg__(self):
        return QuasiPolynomial([-c for c in self.coefs])

    def __add__(self, other):
        if isinstance(other, QuasiPolynomial):
            add_coefs = []
            if self.degree > other.degree:
                sum_coefs = self.coefs.copy()
                add_coefs = other.coefs
            else:
                sum_coefs = other.coefs.copy()
                add_coefs = self.coefs

            for index, coef in enumerate(add_coefs):
                sum_coefs[index] += coef

            return QuasiPolynomial(sum_coefs)

        elif isinstance(other, (int, float, IntegerPeriodicFunction)):
            return QuasiPolynomial([c + other*(index==0)
                                    for index, c in enumerate(self.coefs)])

        elif hasattr(other, "__int__"):
            return QuasiPolynomial([c + int(other)*(index==0)
                                    for index, c in enumerate(self.coefs)])

        elif hasattr(other, "__float__"):
            return QuasiPolynomial([c + float(other)*(index==0)
                                    for index, c in enumerate(self.coefs)])

        else:
            raise TypeError("other must be instance of QuasiPolynomial, "
                            + "int or float, or implement __int__ or __float__"
                            + f"but is has type {type(other)}")

    __radd__ = __add__

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        if isinstance(other, (int, float, IntegerPeriodicFunction)):
            return QuasiPolynomial([other*c for c in self.coefs])
            
        elif isinstance(other, QuasiPolynomial):
            mul_coefs = [0]*(self.degree + other.degree + 1)
            for self_power, self_coef in enumerate(self.coefs):
                for  other_power, other_coef in enumerate(other.coefs):
                    mul_coefs[self_power + other_power] += self_coef*other_coef
            return QuasiPolynomial(mul_coefs)

        elif hasattr(other, "__int__"):
            return QuasiPolynomial([c*int(other) for c in self.coefs])

        elif hasattr(other, "__float__"):
            return QuasiPolynomial([c*float(other) for c in self.coefs])

        else:
            raise TypeError("other must be instance of QuasiPolynomial, "
                            + "int or float, or implement __int__ or __float__"
                            + f"but is has type {type(other)}")
    __rmul__ = __mul__

    def __truediv__(self, other):
        return self.__mul__(1/other)
    
    def __rtruediv__(self, other):
        raise NotImplementedError

if __name__ == "__main__":
    coefs = [1, IntegerPeriodicFunction([2, 3]), IntegerPeriodicFunction([1, 2, 3])]
    ipf = QuasiPolynomial(coefs)
    poly = QuasiPolynomial([1, 2, 3])

    # print(ipf + poly)
    print(poly + IntegerPeriodicFunction([0, 1]))