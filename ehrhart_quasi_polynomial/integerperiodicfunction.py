from sage.arith.functions import lcm
from sage.arith.misc import factor
from sage.categories.pushout import ConstructionFunctor
from sage.categories.commutative_rings import CommutativeRings
from sage.rings.ring import CommutativeRing
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element import RingElement


class IntegerPeriodicFunctionElement(RingElement):
    r"""
    An element of the Ring of Integer Periodic Functions.
    
    This class should not be used to construct elements, rather construct an
    instance of the parent class 'IntegerPeriodicFunctionRing' and let that
    construct the elements, as in the examples below.


    EXAMPLES::
        
        sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
        sage: ipfr = IntegerPeriodicFunctionRing(QQ)
        sage: ipfr()
        IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [0])
        sage: print(ipfr([1, 2, 3])) # doctest: +NORMALIZE_WHITESPACE
        IntegerPeriodicFunction over Rational Field given by
            1 if k%3 == 0
            2 if k%3 == 1
            3 if k%3 == 2
    """
    def __init__(self, parent, constants=None):
        r"""
        INPUT:
            - parent : instance of 'IntegerPeriodicFunctionRing'
            - constants : iterable of elements of 'parent.base()' (default=None)
        """
        base = parent.base()
        if constants is None:
            constants = [base(0)]
        elif not hasattr(constants, "__iter__"):
            constants = [base(constants)]
        else:
            constants = [base(c) for c in constants]
        self._period = self._calculate_period(constants)
        self._constants = constants[:self._period]
        RingElement.__init__(self, parent)

    def _calculate_period(self, constants):
        r"""
        Calculate the period of "constants".
        To get the period of self call '.period()'.
        """
        length = len(constants)

        if length == 1:
            return 1

        period = length
        factors = factor(length)
        for prime, power in factors._Factorization__x:
            div = self._get_period_divisor(constants, length, prime, power)
            period //= div
        
        return period

    def _get_period_divisor(self, constants, length, prime, power):
        r"""
        Return the largest power of 'prime' which divides the period of 'constants'.
        Needed to compute the period of 'constants'.
        """
        last_div = 1
        fact = prime
        for k in range(power):
            if constants[:length//fact]*fact != constants:
                return last_div
            
            last_div = fact
            fact *= prime
        return last_div

    def period(self):
        r"""
        Return the period of self

        EXAMPLES::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: ipfr([1, 2, 3]).period()
            3
            sage: ipfr([1, 1, 1]).period()
            1
            sage: p = ipfr([1, 2])*ipfr([1, 2, 3])
            sage: p.period()
            6
        """
        return self._period

    def constants(self):
        r"""
        Return the constants of self

        EXAMPLES::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: ipfr([1, 2, 3]).constants()
            [1, 2, 3]
        """
        return self._constants

    def __call__(self, k):
        r"""
        Return the value at 'k'%period.
        
        INPUT:
            - k : integer

        EXAMPLES::
            
            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: p = ipfr([1, 2, 3])
            sage: p(1)
            2
            sage: p(11)
            3
            sage: p(-6)
            1
        """
        try:
            return self._constants[k%self._period]
        except TypeError:
            raise TypeError("Integer periodic functions can only be evaluated at integer values.")

    def __getitem__(self, k):
        r"""
        Return the value at k%period or for all elements in the slice.

        INPUT:
            - k : integer or slice

        EXAMPLES::
            
            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: p = ipfr([1, 2, 3])
            sage: p[1]
            2
            sage: p[99]
            1
            sage: p[0:6]
            [1, 2, 3, 1, 2, 3]
            sage: p[3:0:-1]
            [1, 3, 2]
        """
        if isinstance(k, slice):
            step = k.step if k.step else 1
            return [self._constants[i%self._period] for i in range(k.start, k.stop, step)]

        try:
            return self._constants[k%self._period]
        except TypeError:
            raise TypeError("Integer periodic functions can only be evaluated at integer values.")

    def _repr_(self):
        return f"IntegerPeriodicFunctionElement({self.parent()}, {self._constants})"

    def __str__(self):
        function_str = f"IntegerPeriodicFunction over {self.parent().base_ring()} given by"
        for ind, val in enumerate(self._constants):
            function_str += f"\n\t{val} if k%{self._period} == {ind}"
        return function_str

    def __eq__(self, other):
        r"""
        Return whether self and 'other' are considered to be equal in the base ring

        TESTS::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: ipfr.zero() == 0
            True
            sage: p = ipfr([1, 2, 3])
            sage: q = ipfr([2, 3, 4])
            sage: p+1 == q
            True
        """
        if isinstance(other, self.__class__):
            return self._period == other.period() and self._constants == other.constants()
        else:
            return self._period == 1 and self._constants[0] == other

    def __bool__(self):
        r"""
        Return whether self is a non-zero element of the ring.
        
        TESTS::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: bool(ipfr.zero())
            False
            sage: bool(ipfr([1, 2, 3]))
            True
            sage: bool(IntegerPeriodicFunctionRing(SR).zero())
            False
        """
        return self._period != 1 or bool(self._constants[0] != self.parent().base().zero())

    def _neg_(self):
        r"""
        Return the additive inverse of self

        TESTS::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: -ipfr([1, 2, 3])
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [-1, -2, -3])
        """
        return self.__class__(self.parent(), [-c for c in self._constants])

    def _add_(self, other):
        r"""
        Ring addition
        
        TESTS::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: ipfr([1, 2, 3]) + ipfr([0, 1])
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [1, 3, 3, 2, 2, 4])
            sage: ipfr([1, 2, 3]) + 2
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [3, 4, 5])
            sage: ipfr([1, 2, 3]) + ipfr([3, 2, 1])
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [4])
        """
        add_period = lcm(self._period, other.period())
        add_constants = [self[k] + other[k] for k in range(add_period)]
        return self.__class__(self.parent(), add_constants)

    def _sub_(self, other):
        r"""
        TESTS::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: ipfr([1, 2, 3]) - ipfr([0, 1])
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [1, 1, 3, 0, 2, 2])
            sage: ipfr([1, 2, 3]) - 2
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [-1, 0, 1])
        """
        return self.__add__(-other)

    def _mul_(self, other):
        r"""
        Ring multiplication and scalar multiplication
        
        TESTS::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: ipfr([1, 2, 3]) * ipfr([0, 1])
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [0, 2, 0, 1, 0, 3])
            sage: ipfr([1, 2, 4]) * ipfr([4, 2, 1])
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [4])
            sage: ipfr([1, 2, 3]) * 2
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [2, 4, 6])
            sage: IntegerPeriodicFunctionRing(GF(3)).one()*0
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Finite Field of size 3, [0])
        """
        mul_period = lcm(self._period, other.period())
        mul_constants = [self[k]*other[k] for k in range(mul_period)]
        return self.__class__(self.parent(), mul_constants)


class IntegerPeriodicFunctionRing(UniqueRepresentation, CommutativeRing):
    # needed for automatic coercion
    Element = IntegerPeriodicFunctionElement
    def __init__(self, base):
        if base not in CommutativeRings():
            raise ValueError(f"{base} is not a commutative ring.")
        CommutativeRing.__init__(self, base)                         
            
    def _repr_(self):
        return f"Ring of Integer Periodic Functions over {self.base()}"

    def base_ring(self):
        r"""
        Return the base_ring of the base

        EXAMPLES::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: IntegerPeriodicFunctionRing(QQ).base_ring()
            Rational Field
            sage: IntegerPeriodicFunctionRing(SR).base_ring()
            Symbolic Ring
        """
        return self.base().base_ring()

    def characteristic(self):
        r"""
        Return the characteristic of the base
        EXAMPLES::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: IntegerPeriodicFunctionRing(QQ).characteristic()
            0
            sage: IntegerPeriodicFunctionRing(IntegerModRing(19)).characteristic()
            19
        """
        return self.base().characteristic()

    def _element_constructor_(self, *args, **kwds):
        r"""
        Handles the automatic coercion of objects to IntegerPeriodicFunctionElement

        EXAMPLES::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: ipfr(1)
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [1])
            sage: ipfr([1, 2, 3])
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [1, 2, 3])
            sage: ipfr([4, 4, 4, 4])
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [4])
            sage: ipfr()
            IntegerPeriodicFunctionElement(Ring of Integer Periodic Functions over Rational Field, [0])
        """
        if len(args) != 1:
            return self.element_class(self, *args, **kwds)
        x = args[0]
        if isinstance(x, self.element_class) and x.parent() == self:
            return x
        try:
            if hasattr(x, "__iter__"):
                return self.element_class(self, [self.base()(elem) for elem in x], **kwds)
            else:
                return self.element_class(self, [self.base()(x)], **kwds)
        except TypeError:
            raise TypeError(f"Unable to coerce {x} to an element of {self}")

    def _coerce_map_from_(self, S):
        r"""
        Return whether there is a coercion map from S to self.
        If so "self(s)" should work for all s in S

        TESTS::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: ipfr._coerce_map_from_(QQ)
            True
            sage: ipfr._coerce_map_from_(ZZ)
            True
            sage: print(ipfr._coerce_map_from_(SR))
            None
        """
        if self.base().has_coerce_map_from(S):
            return True

    def construction(self):
        r"""
        Return a ConstructionFunctor
        """
        return IntegerPeriodicFunctionFunctor(self._reduction[1][1:], self._reduction[2]), self.base()

    def is_integral_domain(self):
        r"""
        Return whether self is an integral domain, which is False

        TESTS::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: ipfr.is_integral_domain()
            False
        """
        return False

    def is_unique_factorization_domain(self):
        r"""
        Return whether self is a unique factorization domain (UFD), which is False

        TESTS::

            sage: from ehrhart_quasi_polynomial.integerperiodicfunction import IntegerPeriodicFunctionRing
            sage: ipfr = IntegerPeriodicFunctionRing(QQ)
            sage: ipfr.is_unique_factorization_domain()
            False
        """
        return False

class IntegerPeriodicFunctionFunctor(ConstructionFunctor):
    rank = 10
    def __init__(self, args=None, kwds=None):
        self.args = args or ()
        self.kwds = kwds or {}
        ConstructionFunctor.__init__(self, CommutativeRings(), CommutativeRings())

    def _apply_functor(self, R):
        return IntegerPeriodicFunctionRing(R, *self.args, **self.kwds)

    def merge(self, other):
        if isinstance(other, type(self)):
            return self
