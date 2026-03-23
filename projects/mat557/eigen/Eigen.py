from manimlib import *


class Ex(InteractiveScene):
    def construct(self) -> None:
        axes = NumberPlane()
        axes.add_coordinate_labels()
        axes.set_z_index(-10)
        self.axes = axes

        self.add(axes)

        self.A = np.array([[3, 0], [0, 2]])
        self.A = np.array([[2, -1], [1, 2]])

        self.add(
            always_redraw(
                lambda: (
                    Tex(
                        f"A=\\begin{{bmatrix}} {self.A[0][0]} & {self.A[1][0]} \\\\ {self.A[0][1]} & {self.A[1][1]} \\end{{bmatrix}}"
                    )
                    .to_corner(UL)
                    .fix_in_frame()
                )
            )
        )

        self.x0 = ValueTracker(np.array([1, 1]))

        def lines():
            group = VGroup()
            x = np.array(self.x0.get_value())
            A = self.A
            for _ in range(50):
                dot = Dot(axes.x_axis.n2p(x[0]) + axes.y_axis.n2p(x[1]))
                group.add(dot)

                xp = x
                x = np.linalg.matmul(A, x)
                x /= np.linalg.norm(x)

                group.add(
                    Arrow(
                        start=axes.x_axis.n2p(xp[0]) + axes.y_axis.n2p(xp[1]),
                        end=axes.x_axis.n2p(x[0]) + axes.y_axis.n2p(x[1]),
                        stroke_width=4,
                        color=BLUE,
                    )
                )
            return group

        self.add(always_redraw(lines))
        self.embed()

    def on_mouse_drag(self, point, d_point, buttons: int, modifiers: int):
        p = self.axes.p2c(point)
        self.x0.set_value(np.array([p[0], p[1]]))
