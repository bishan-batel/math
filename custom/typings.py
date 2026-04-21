from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TYPE_CHECKING, Self, overload
    from manimlib.typing import Vect3

    @overload
    def __mul__(a: Vect3, b: float) -> Vect3: ...
