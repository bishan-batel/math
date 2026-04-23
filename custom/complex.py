from typing import *
from manimlib import *


def apply_complex_map_to_plane(
    obj: VMobject,
    plane: ComplexPlane,
    function: Callable[[complex], complex],
    animate=False,
    **kwargs,
) -> VMobject:

    def func(v):
        return plane.n2p(function(plane.p2n(v)))

    if animate:
        return obj.animate(**kwargs).apply_function(func)
    else:
        return obj.apply_function(func)
