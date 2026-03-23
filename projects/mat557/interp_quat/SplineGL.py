from typing import TypeAlias, cast, Callable

import typing

import manimlib as mn
from manimlib import *  # pyright: ignore
import numpy as np
from numpy.typing import NDArray
from pyquaternion import Quaternion

# VectorND: TypeAlias = npt.NDArray[PointDType]


def euler_to_quat(yaw: float, pitch: float, roll: float) -> Quaternion:
    return (
        Quaternion(axis=[0, 0, 1], degrees=yaw)
        * Quaternion(axis=[0, 1, 0], degrees=pitch)
        * Quaternion(axis=[1, 0, 0], degrees=roll)
    )


def apply_quaternion(q_arr: NDArray, point):
    return np.array(Quaternion(q_arr).rotate(point))


SplineInputPoints = list[tuple[float, NDArray]]


def parametric_create_splines(input: SplineInputPoints):
    ts = [t for (t, _) in input]

    max_t = np.max(ts)
    min_t = np.min(ts)

    x = np.vstack([x for (_, x) in input])  # parametric output

    dim = len(x[0])
    n = len(input)

    del_x = x[1:] - x[:-1]
    del2_x = del_x[1:] - del_x[:-1]

    matrix = np.zeros([n - 2, n - 2])

    for i in range(0, n - 2):
        for j in range(0, n - 2):
            if i == j:
                matrix[i, j] = 4
            elif j == i + 1 or i == j + 1:
                matrix[i, j] = 1
    matrix = 6 * np.linalg.inv(matrix)

    d2s = (matrix * np.array(del2_x).transpose()).transpose()
    d2s = np.vstack([np.zeros((1, dim)), d2s, np.zeros((1, dim))])

    def spline(i: int, t: float) -> NDArray:
        return (
            x[i]
            + t * del_x[i]
            + (1 / 6) * t * (t - 1) * (-del2_x[i] * (t - 2) + del2_x[i + 1] * (t + 1))
        )

    def full(t: float) -> NDArray:
        t = (t - max_t) / (max_t - min_t)
        idx_t = max(min(np.floor(t), n - 1), 0)
        return spline(idx_t, t - idx_t)

    return full


def create_splines(input: SplineInputPoints):

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
        if t <= x[0]:
            return spline(0, t)
        return spline(n - 2, t)

    return full


class RotationRender(ThreeDScene):
    always_depth_test = True
    splinegen: Callable[[SplineInputPoints], Callable[[float], NDArray]] = (
        create_splines
    )
    spline_points: SplineInputPoints = [
        (0, Quaternion(degrees=0, axis=[0, 0, 1]).q),
        (0.4, euler_to_quat(yaw=90, pitch=-30, roll=0).q),
        (0.8, euler_to_quat(yaw=35, pitch=-90, roll=30).q),
        (1.0, euler_to_quat(yaw=-140, pitch=-140, roll=-40).q),
    ]

    def construct(self):

        QMAX_T = max([t for (t, _) in self.spline_points])
        QMIN_T = min([t for (t, _) in self.spline_points])

        qspline = RotationRender.splinegen(self.spline_points)

        self.add(ThreeDAxes())

        for t, _ in self.spline_points:
            print("T=", t)
            self.add(
                Sphere(
                    radius=0.08,
                    color=BLUE,
                ).move_to(apply_quaternion(qspline(t), RIGHT) * 1.3)
            )
        t = ValueTracker(QMIN_T)

        self.add(
            VGroup(
                Tex("t="),
                DecimalNumber(QMIN_T).add_updater(lambda m: m.set_value(t.get_value())),
            )
            .arrange(RIGHT)
            .fix_in_frame()
            .to_corner(UL)
        )

        # self.camera.zoom = 2

        t.set_value(self.spline_points[0][0])

        self.add(
            Line(color=PURPLE, buff=2).add_updater(
                lambda m: m.set_points_by_ends(
                    apply_quaternion(qspline(t.get_value()), RIGHT) * 0.5,
                    apply_quaternion(qspline(t.get_value()), RIGHT) * 1.3,
                )
            )
        )
        self.add(
            Sphere(radius=0.1, color=PURPLE).add_updater(
                lambda m: m.move_to(
                    np.array(apply_quaternion(qspline(t.get_value()), RIGHT)) * 1.3,
                )
            )
        )

        # self.add(Arrow().add_updater(lambda m: m.set_points_by_ends()))

        def update_plane(m: Mobject):
            m.become(
                Cube(side_length=1.0, color=PURPLE).apply_matrix(
                    Quaternion(qspline(t.get_value())).rotation_matrix
                )
            )
            # color=RED.interpolate(BLUE, (t - QMIN_T) / (QMAX_T - QMIN_T)),

        self.add(Cube().add_updater(update_plane))

        curve = ParametricCurve(
            t_func=lambda t: apply_quaternion(qspline(t), RIGHT) * 1.3,
            # stroke_width=0.05,
            t_range=(QMIN_T, QMAX_T, 1e-2),
        )
        self.add(curve)

        # self.interactive_embed()
        def animate_t(value: float, run_time=(QMAX_T - QMIN_T) * 3):
            return t.animate(run_time=run_time, rate_func=linear).set_value(value)

        self.frame.set_phi(45 * DEG)
        self.frame.set_theta(40 * DEG)
        self.play(animate_t(QMAX_T))
        self.embed()


class RotTrivial(RotationRender):
    spline_points = [
        (0, Quaternion(degrees=0, axis=[0, 0, 1]).q),
        (0.25, Quaternion(degrees=90, axis=[0, 0, 1]).q),
        (0.75, Quaternion(degrees=180, axis=[0, 0, 1]).q),
        (1, Quaternion(degrees=270, axis=[0, 0, 1]).q),
    ]


class RotTrivial2(RotationRender):
    spline_points = [
        (0.00, Quaternion(degrees=0, axis=[0, 0, 1]).q),
        (0.25, Quaternion(degrees=90, axis=[0, 0, 1]).q),
        (0.75, Quaternion(degrees=90, axis=[1, 0, 0]).q),
        (1.00, Quaternion(degrees=90, axis=[1, 1, 0]).q),
    ]


class RotAllDirs(RotationRender):
    spline_points = [
        (0, Quaternion(degrees=0, axis=[0, 0, 1]).q),
        (0.4, euler_to_quat(yaw=90, pitch=-30, roll=0).q),
        (0.8, euler_to_quat(yaw=35, pitch=-90, roll=30).q),
        (1.0, euler_to_quat(yaw=-140, pitch=-150, roll=-45).q),
    ]


class RotPara(RotationRender):
    splinegen = parametric_create_splines
    spline_points = RotAllDirs.spline_points
