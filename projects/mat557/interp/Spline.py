from typing import cast
from dearpygui.dearpygui import get_value
from manim import *  # pyright: ignore
from manim.opengl import *# pyright: ignore
from manim.typing import *# pyright: ignore
import numpy as np
from numpy.typing import NDArray


def quaternion_to_matrix(q):
    w, x, y, z = q
    d = np.sqrt(w**2+x**2+y**2+z**2)
    # d=1
    w/=d 
    x/=d 
    y/=d 
    z/=d
    # Rotation matrix formula
    m = np.array([
        [1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
        [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y]
    ])
    return m


def create_splines(input: list[tuple[float, NDArray]]):

    x = np.array([t for (t, _) in input]).ravel() # parametric input
    y = np.vstack([y for (_, y) in input]) # parametric output

    dim = len(y[0])
    n = len(x)

    del_x = x[1:] - x[:-1]
    del_y = y[1:] - y[:-1]

    m = del_y / del_x[:, np.newaxis]
    del_m = m[1:] - m[:-1]

    matrix = np.zeros([n-2,n-2])

    for i in range(0, n-2):
        for j in range(0, n-2):
            if i == j:
                matrix[i,j] = 2 * (del_x[i] + del_x[i+1])
            elif j == i + 1:
                matrix[i,j] = del_x[i]
            elif i == j + 1:
                matrix[i,j] = del_x[j]

    # second derivatives
    matrix = 6 * np.linalg.inv(matrix) 
    # matrix * del_m

    d2y = np.linalg.matmul(matrix, del_m)
    d2y = np.vstack([np.zeros((1,dim)), d2y, np.zeros((1,dim))])

    def spline(i: int,t: float) -> NDArray:
        return (
            y[i] 
            + m[i] * (t-x[i]) 
            + ((1/6) 
              * (1/del_x[i]) 
              * (t - x[i]) 
              * (t - x[i+1])
              * ((-d2y[i]) * (t - 2*x[i+1] + x[i]) + (d2y[i+1] * (t - 2*x[i] + x[i+1]))))
        )

    def full(t: float) -> NDArray:
        for i in range(0, n-1):
            if t <= x[i+1] and t >= x[i]:
                return spline(i, t)
        raise Exception("Out of domain")
        
    return full



QSPLINE_POINTS = [
    (0, quaternion_from_angle_axis(45, np.array([1, 0, 0 ]))),
    (0.33, quaternion_from_angle_axis(-90, np.array([0, 1, 0 ]))),
    (0.66, quaternion_from_angle_axis(-45, np.array([0.5, 1, 0 ]))),
    (1, quaternion_from_angle_axis(-40, np.array([1, 0.5, 1 ]))),
]

QMAX_T = max([t for (t, _) in QSPLINE_POINTS])
QMIN_T = min([t for (t, _) in QSPLINE_POINTS])

qspline = create_splines(QSPLINE_POINTS)

class Spline(ThreeDScene):
    def construct(self):



        axes = ThreeDAxes()

        x_label = axes.get_x_axis_label(Tex("x"))
        y_label = axes.get_y_axis_label(Tex("y")).shift(UP * 1.8)
        z_label = axes.get_y_axis_label(Tex("z")).shift(IN * 1.8)

        # 3D variant of the Dot() object


        # zoom out so we see the axes
        # self.set_camera_orientation(zoom=0.5)

        self.add(axes, x_label, y_label, z_label)

        # for (t, point) in SPLINE_POINTS:
        #     self.add(Dot3D(point).set_color(RED.interpolate(BLUE, (t - MIN_T) / (MAX_T - MIN_T) )))
        for (t, _) in QSPLINE_POINTS:
            arrow = Arrow3D(start=(0,0,0), color=RED.interpolate(BLUE, (t - QMIN_T) / (QMAX_T - QMIN_T) )).apply_matrix(
                quaternion_to_matrix(qspline(t)))
            self.add(arrow)
            self.add(MathTex(f"t={t}").move_to(arrow.end_point).scale(0.5).set_color(arrow.color))

        t = ValueTracker(QMIN_T)



        # built-in updater which begins camera rotation
        self.set_camera_orientation(phi=45*DEGREES,theta=-110*DEGREES)
        # self.begin_ambient_camera_rotation(rate=0.15)

        # self.add_fixed_in_frame_mobjects(MathTex("epic=5+2").to_corner(UL))

        dot = Dot3D()
        dot.color = GREEN
        # dot.add_updater(lambda d: d.move_to(spline(t.get_value())))
        # self.add(dot)

        # self.add_fixed_in_frame_mobjects(MathTex(r"t=0").to_corner(UL).add_updater(lambda m: m.become(MathTex(f"t={t.get_value():.2f}"))))
        
        t.set_value(QSPLINE_POINTS[0][0])

        # self.add(ParametricFunction(spline, t_range=(MIN_T,MAX_T)));

        arrow = Arrow3D(start=(0,0,0), color=PURPLE)
        arrow.add_updater(lambda a: a.become(Arrow3D(start=(0,0,0), color=PURPLE).apply_matrix(quaternion_to_matrix(qspline(t.get_value())))) )
        self.add(arrow)

        def path(t:float):
            mat = quaternion_to_matrix(qspline(t))
            return np.linalg.matmul(mat,RIGHT)

        self.add(ParametricFunction(path, t_range=(QMIN_T, QMAX_T)))

        self.play(t.animate(run_time=(QMAX_T - QMIN_T)*3,rate_func=linear).set_value(QMAX_T)) # pyright: ignore
        self.wait(0.5)

