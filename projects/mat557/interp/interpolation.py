from typing import Sequence
from manim import *
from manim.typing import Point3D, Vector3D
from numpy.typing import NDArray  # pyright: ignore


def apply_quaternion(q: Sequence[float], point: Point3D, normalize=False):
    if normalize:
        w, x, y, z = q
        q /= np.sqrt(w**2 + x**2 + y**2 + z**2)
    # Rotation matrix formula
    # m = np.array(
    #     [
    #         [1 - 2 * y * y - 2 * z * z, 2 * x * y - 2 * z * w, 2 * x * z + 2 * y * w],
    #         [2 * x * y + 2 * z * w, 1 - 2 * x * x - 2 * z * z, 2 * y * z - 2 * x * w],
    #         [2 * x * z - 2 * y * w, 2 * y * z + 2 * x * w, 1 - 2 * x * x - 2 * y * y],
    #     ]
    # )

    return quaternion_mult(q, (0,...point) ,quaternion_conjugate(q))


def create_splines(input: list[tuple[float, NDArray]]):

    x = np.array([t for (t, _) in input]).ravel()  # parametric input
    y = np.vstack([y for (_, y) in input])  # parametric output

    dim = len(y[0])
    n = len(x)

    del_x = x[1:] - x[:-1]
    del_y = y[1:] - y[:-1]

    m = del_y / del_x[:, np.newaxis]
    del_m = m[1:] - m[:-1]

    matrix = np.zeros([n - 2, n - 2])

    for i in range(0, n - 2):
        for j in range(0, n - 2):
            if i == j:
                matrix[i, j] = 2 * (del_x[i] + del_x[i + 1])
            elif j == i + 1:
                matrix[i, j] = del_x[i]
            elif i == j + 1:
                matrix[i, j] = del_x[j]

    # second derivatives
    matrix = 6 * np.linalg.inv(matrix)
    # matrix * del_m

    d2y = np.linalg.matmul(matrix, del_m)
    d2y = np.vstack([np.zeros((1, dim)), d2y, np.zeros((1, dim))])

    def spline(i: int, t: float) -> NDArray:
        return (
            y[i]
            + m[i] * (t - x[i])
            + (
                (1 / 6)
                * (1 / del_x[i])
                * (t - x[i])
                * (t - x[i + 1])
                * (
                    (-d2y[i]) * (t - 2 * x[i + 1] + x[i])
                    + (d2y[i + 1] * (t - 2 * x[i] + x[i + 1]))
                )
            )
        )

    def full(t: float) -> NDArray:
        for i in range(0, n - 1):
            if t <= x[i + 1] and t >= x[i]:
                return spline(i, t)
        raise Exception("Out of domain")

    return full
