from typing import Callable, cast
from manim import *  # pyright: ignore
from manim.opengl import *  # pyright: ignore
from manim.renderer.opengl_renderer import OpenGLCamera
from manim.typing import *  # pyright: ignore
from manim_slides.slide import ThreeDSlide
from numpy.typing import NDArray
import numpy as np
import pyquaternion as quat
from pyquaternion import Quaternion


def euler_to_quat(yaw: float, pitch: float, roll: float) -> Quaternion:
    return (
        Quaternion(axis=[0, 0, 1], degrees=yaw)
        * Quaternion(axis=[0, 1, 0], degrees=pitch)
        * Quaternion(axis=[1, 0, 0], degrees=roll)
    )


def apply_quaternion(q_arr: NDArray, point: Point3D) -> Point3DLike:
    return np.array(Quaternion(q_arr).rotate(point))


def parametric_create_splines(input: list[tuple[float, NDArray]]):
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

    def full(t: float):
        t = (t - max_t) / (max_t - min_t)
        return spline(np.floor(t), t - np.floor(t))

    return full


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


class RotationRender(ThreeDScene):
    spline_points: list[tuple[float, NDArray]]
    splinegen: Callable[[list[tuple[float, NDArray]]], Callable[[float], Point3D]] = (
        create_splines
    )

    def construct(self):

        QMAX_T = max([t for (t, _) in self.spline_points])
        QMIN_T = min([t for (t, _) in self.spline_points])

        qspline = RotationRender.splinegen(self.spline_points)

        self.camera.zoom = 3.0

        # self.begin_ambient_camera_rotation()

        axes = ThreeDAxes()

        x_label = axes.get_x_axis_label(Tex("x"))
        y_label = axes.get_y_axis_label(Tex("y")).shift(UP * 1.8)
        z_label = axes.get_y_axis_label(Tex("z")).shift(IN * 1.8)

        self.add(axes, x_label, y_label, z_label)

        for t, _ in self.spline_points:
            print("T=", t)
            self.add(
                Arrow3D(
                    start=(0, 0, 0),
                    end=(apply_quaternion(qspline(t), RIGHT)),
                    thickness=0.005,
                    height=0.2,
                    color=RED.interpolate(BLUE, (t - QMIN_T) / (QMAX_T - QMIN_T)),
                )
            )
        t = ValueTracker(QMIN_T)

        self.set_camera_orientation(phi=45 * DEGREES, theta=40 * DEGREES, zoom=2)

        t_display = DecimalNumber(QMIN_T).to_corner(UL)
        t_display.add_updater(lambda m: m.set_value(t.get_value()))
        self.add_fixed_in_frame_mobjects(t_display)

        # self.camera.zoom = 2

        t.set_value(self.spline_points[0][0])

        # self.add(Sphere(radius=0.95, color=BLUE, opacity=0.5))

        self.add(
            Arrow3D(start=(0, 0, 0), color=WHITE).add_updater(
                lambda m: m.put_start_and_end_on(
                    (0, 0, 0),
                    np.array(apply_quaternion(qspline(t.get_value()), RIGHT)) * 1.3,
                )
            )
        )
        self.add(
            Dot3D(radius=0.02, color=WHITE).add_updater(
                lambda m: m.move_to(
                    np.array(apply_quaternion(qspline(t.get_value()), RIGHT)) * 1.3,
                )
            )
        )

        def update_plane(m: Mobject):
            m.become(
                Cube(side_length=0.5, color=PURPLE).apply_matrix(
                    Quaternion(qspline(t.get_value())).rotation_matrix
                )
            )

        self.add(Cube().add_updater(update_plane))

        def path(t: float):
            return np.array(apply_quaternion(qspline(t), RIGHT)) * 1.3

        self.add(ParametricFunction(path, t_range=(QMIN_T, QMAX_T), dt=1e-2))

        # self.interactive_embed()
        def animate_t(value: float, run_time=(QMAX_T - QMIN_T) * 3):
            return t.animate(run_time=run_time, rate_func=linear).set_value(  # pyright:ignore
                value
            )

        self.play(animate_t(QMAX_T))

        self.wait(1)
        self.move_camera(theta=130 * DEGREES, added_anims=[animate_t(0, run_time=0.5)])
        self.play(animate_t(QMAX_T))

        self.wait(1)
        self.move_camera(theta=200 * DEGREES, added_anims=[animate_t(0, run_time=0.5)])
        self.play(animate_t(QMAX_T))


class RotTrivial(RotationRender):
    spline_points = [
        (0, Quaternion(degrees=0, axis=[0, 0, 1]).q),
        (0.25, Quaternion(degrees=90, axis=[0, 0, 1]).q),
        (0.75, Quaternion(degrees=180, axis=[0, 0, 1]).q),
        (1, Quaternion(degrees=270, axis=[0, 0, 1]).q),
    ]


class RotAllDirs(RotationRender):
    spline_points = [
        (0, Quaternion(degrees=0, axis=[0, 0, 1]).q),
        (0.4, euler_to_quat(yaw=90, pitch=-30, roll=0).q),
        (0.8, euler_to_quat(yaw=35, pitch=-90, roll=30).q),
        (1.0, euler_to_quat(yaw=-140, pitch=-180, roll=-15).q),
    ]


class RotPara(RotationRender):
    splinegen = parametric_create_splines
    spline_points = RotAllDirs.spline_points
