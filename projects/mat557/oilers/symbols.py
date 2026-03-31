from sympy import *

r1, r2, r3 = symbols("r1:4", function=True)


def P(z):
    return (z - r1) * (z - r2) * (z - r3)


z = Symbol("z")

f = P(z)
df = Derivative(P(z), z, evaluate=True)


newtons = z - f / df

newtons = simplify(newtons)

print(latex(newtons))
