"""Minimal dual-number algebra for forward-mode automatic differentiation."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Dual:
    val: float
    der: float = 0.0

    def __add__(self, other: float | "Dual") -> "Dual":
        o = to_dual(other)
        return Dual(self.val + o.val, self.der + o.der)

    def __radd__(self, other: float | "Dual") -> "Dual":
        return self.__add__(other)

    def __sub__(self, other: float | "Dual") -> "Dual":
        o = to_dual(other)
        return Dual(self.val - o.val, self.der - o.der)

    def __rsub__(self, other: float | "Dual") -> "Dual":
        o = to_dual(other)
        return Dual(o.val - self.val, o.der - self.der)

    def __mul__(self, other: float | "Dual") -> "Dual":
        o = to_dual(other)
        return Dual(self.val * o.val, self.der * o.val + self.val * o.der)

    def __rmul__(self, other: float | "Dual") -> "Dual":
        return self.__mul__(other)

    def __truediv__(self, other: float | "Dual") -> "Dual":
        o = to_dual(other)
        if o.val == 0.0:
            raise ZeroDivisionError("dual division by zero")
        val = self.val / o.val
        der = (self.der * o.val - self.val * o.der) / (o.val * o.val)
        return Dual(val, der)

    def __rtruediv__(self, other: float | "Dual") -> "Dual":
        o = to_dual(other)
        return o.__truediv__(self)

    def __neg__(self) -> "Dual":
        return Dual(-self.val, -self.der)

    def __pow__(self, power: int | float) -> "Dual":
        if isinstance(power, int):
            if power == 0:
                return Dual(1.0, 0.0)
            val = self.val ** power
            der = power * (self.val ** (power - 1)) * self.der
            return Dual(val, der)
        # general real power: x^a = exp(a*log x)
        if self.val <= 0.0:
            raise ValueError("dual power with non-positive base for non-integer exponent")
        return exp(log(self) * float(power))


def to_dual(x: float | Dual) -> Dual:
    if isinstance(x, Dual):
        return x
    return Dual(float(x), 0.0)


def exp(x: float | Dual) -> Dual:
    d = to_dual(x)
    e = math.exp(d.val)
    return Dual(e, e * d.der)


def log(x: float | Dual) -> Dual:
    d = to_dual(x)
    if d.val <= 0.0:
        raise ValueError("log domain error")
    return Dual(math.log(d.val), d.der / d.val)


def sigmoid(x: float | Dual) -> Dual:
    d = to_dual(x)
    # numerically stable logistic
    if d.val >= 0:
        z = math.exp(-d.val)
        val = 1.0 / (1.0 + z)
    else:
        z = math.exp(d.val)
        val = z / (1.0 + z)
    der = val * (1.0 - val) * d.der
    return Dual(val, der)


__all__ = ["Dual", "exp", "log", "sigmoid", "to_dual"]
