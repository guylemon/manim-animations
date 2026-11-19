"""Kinematic rotation of the plane about a point on a line.

Every point turns about a fixed point O on a line L through the same angle,
so distances are preserved and triangle ABC moves as a rigid body. L is
carried to a line L' through O. The picture illustrates the distance-preserving
mappings in Lang, Basic Mathematics, Chapter 6, §1.

The turn is the map P -> P(t) for t from 0 to 1, with |OP(t)| = |OP| and
directed angle from OP to OP(t) equal to t*theta. Theta is 60 degrees.

Render from the repository root:

    manim -qh --fps 30 scenes/kinematic_rotation.py KinematicRotation
"""

from __future__ import annotations

import numpy as np
from manim import (
    TAU,
    Arc,
    Circle,
    Create,
    DashedVMobject,
    DecimalNumber,
    Dot,
    DOWN,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    LEFT,
    Line,
    MathTex,
    Polygon,
    RIGHT,
    RoundedRectangle,
    Scene,
    Sector,
    Tex,
    UP,
    ValueTracker,
    VGroup,
    VMobject,
    always_redraw,
    smooth,
)

# Counterclockwise through a sixth of a turn. Large enough that L and L'
# are easy to tell apart, and small enough that the triangle stays on screen.
THETA = TAU / 6
THETA_DEGREES = 60

# O is the origin. L is the horizontal line through O. ABC sits in the first
# quadrant, off the line, so the center is visibly not a vertex of the triangle.
A_POINT = np.array([2.05, 0.28, 0.0])
B_POINT = np.array([2.55, 1.25, 0.0])
C_POINT = np.array([1.05, 1.25, 0.0])
# Other points of the plane, so the motion is not only the triangle's.
SAMPLE_POINTS = (
    np.array([1.15, -1.55, 0.0]),
    np.array([-2.35, 1.05, 0.0]),
    np.array([3.40, -0.85, 0.0]),
    np.array([-1.15, -2.15, 0.0]),
)

BACKGROUND = "#0e1218"
PANEL = "#1a2330"
PANEL_STROKE = "#3d4f66"
CREAM = "#f6f1e7"
MUTED = "#b7c3d1"
GRID = "#3d5672"
GRID_HALF = "#2a3c52"
LATTICE = "#8ea3b8"
LINE_COLOR = "#8ec5ff"
LINE_IMAGE = "#ffd166"
VERTEX_COLORS = ("#ff8b7b", "#7ddeb3", "#d4c2ff")
SAMPLE_COLOR = "#d5e2f0"
TRI_FILL = "#f0d2aa"
TRI_STROKE = "#f7efe4"

# Square grid large enough that a 60 degree turn still covers the camera.
GRID_EXTENT = 9.5
# Inner disk reserved for the angle mark at O.
ANGLE_RADIUS = 0.98

Z_GRID = 0
Z_LATTICE = 1
Z_ORBIT = 2
Z_GHOST = 3
Z_LINE = 5
Z_TRIANGLE = 6
Z_VERTEX = 7
Z_ANGLE = 8
Z_PIN = 9
Z_LABEL = 10
Z_PANEL = 12


def rotation_matrix(angle: float) -> np.ndarray:
    """Counterclockwise rotation about the origin, acting on column vectors."""
    cosine = float(np.cos(angle))
    sine = float(np.sin(angle))
    return np.array(
        [[cosine, -sine, 0.0], [sine, cosine, 0.0], [0.0, 0.0, 1.0]],
        dtype=float,
    )


def rotate_about_origin(point: np.ndarray, angle: float) -> np.ndarray:
    return rotation_matrix(angle) @ np.asarray(point, dtype=float)


def directed_angle(start: np.ndarray, end: np.ndarray) -> float:
    """Counterclockwise angle from `start` to `end`, in [0, tau)."""
    before = float(np.arctan2(start[1], start[0]))
    after = float(np.arctan2(end[1], end[0]))
    return (after - before) % TAU


def _assert_rigid_motion() -> None:
    """Guard the coordinates used in the scene.

    The animation drives every mobject from this same rotation, so checking
    the map on the named points checks the motion the viewer is meant to see.
    """
    named = {"A": A_POINT, "B": B_POINT, "C": C_POINT}
    samples = list(SAMPLE_POINTS)
    original_sides = (
        np.linalg.norm(B_POINT - A_POINT),
        np.linalg.norm(C_POINT - B_POINT),
        np.linalg.norm(A_POINT - C_POINT),
    )
    assert min(original_sides) > 0.8
    # O is not inside the triangle: it lies on L, outside ABC.
    crosses = []
    for start, end in (
        (A_POINT, B_POINT),
        (B_POINT, C_POINT),
        (C_POINT, A_POINT),
    ):
        edge = end - start
        crosses.append(edge[0] * (0.0 - start[1]) - edge[1] * (0.0 - start[0]))
    assert not (
        all(value > 0 for value in crosses) or all(value < 0 for value in crosses)
    )

    for step in range(11):
        angle = (step / 10) * THETA
        moved = {name: rotate_about_origin(point, angle) for name, point in named.items()}
        sides = (
            np.linalg.norm(moved["B"] - moved["A"]),
            np.linalg.norm(moved["C"] - moved["B"]),
            np.linalg.norm(moved["A"] - moved["C"]),
        )
        assert np.allclose(sides, original_sides, atol=1e-9)
        for point in (*named.values(), *samples):
            image = rotate_about_origin(point, angle)
            assert np.isclose(np.linalg.norm(image), np.linalg.norm(point), atol=1e-9)
            if np.linalg.norm(point) > 1e-8 and angle > 0:
                turned = directed_angle(point, image)
                assert np.isclose(turned, angle, atol=1e-9)
    image_of_l = rotate_about_origin(np.array([1.0, 0.0, 0.0]), THETA)
    assert np.isclose(directed_angle(np.array([1.0, 0.0, 0.0]), image_of_l), THETA)
    assert np.isclose(np.degrees(THETA), THETA_DEGREES)


_assert_rigid_motion()


def with_halo(mobject, width=5):
    mobject.set_stroke(BACKGROUND, width=width, background=True)
    return mobject


def build_grid() -> VGroup:
    lines = VGroup()
    half_steps = np.arange(-GRID_EXTENT, GRID_EXTENT + 1e-6, 0.5)
    for value in half_steps:
        major = abs(value - round(value)) < 1e-6 and abs(round(value)) > 1e-6
        # The axes are drawn again, thicker, as the line L and are not special
        # grid lines. Keep every grid line, including the axes, equally quiet.
        color = GRID if major or abs(value) < 1e-6 else GRID_HALF
        width = 1.35 if major or abs(value) < 1e-6 else 0.8
        opacity = 0.85 if major or abs(value) < 1e-6 else 0.55
        start_h = np.array([-GRID_EXTENT, value, 0.0])
        end_h = np.array([GRID_EXTENT, value, 0.0])
        start_v = np.array([value, -GRID_EXTENT, 0.0])
        end_v = np.array([value, GRID_EXTENT, 0.0])
        lines.add(
            Line(start_h, end_h, stroke_color=color, stroke_width=width, stroke_opacity=opacity),
            Line(start_v, end_v, stroke_color=color, stroke_width=width, stroke_opacity=opacity),
        )
    lines.set_z_index(Z_GRID)
    return lines


def build_lattice() -> VGroup:
    dots = VGroup()
    blocked = [np.array([0.0, 0.0, 0.0]), *SAMPLE_POINTS, A_POINT, B_POINT, C_POINT]
    for x in range(-8, 9):
        for y in range(-8, 9):
            if x * x + y * y > 8.4**2 or x * x + y * y < 0.4**2:
                continue
            point = np.array([float(x), float(y), 0.0])
            if any(np.linalg.norm(point - other) < 0.2 for other in blocked):
                continue
            dots.add(Dot(point, radius=0.032, color=LATTICE, fill_opacity=0.9))
    dots.set_z_index(Z_LATTICE)
    return dots


def build_tracked_line() -> Line:
    line = Line(
        np.array([-GRID_EXTENT, 0.0, 0.0]),
        np.array([GRID_EXTENT, 0.0, 0.0]),
        stroke_color=LINE_COLOR,
        stroke_width=4.5,
    )
    line.set_z_index(Z_LINE)
    return line


def place_vertex_label(label, point: np.ndarray, centroid: np.ndarray) -> None:
    away = np.asarray(point, dtype=float) - np.asarray(centroid, dtype=float)
    norm = float(np.linalg.norm(away))
    direction = away / norm if norm > 1e-6 else np.array([0.0, 1.0, 0.0])
    position = np.asarray(point, dtype=float) + direction * 0.40
    position = position.copy()
    position[0] = float(np.clip(position[0], -6.5, 6.5))
    position[1] = float(np.clip(position[1], -3.15, 3.16))
    label.move_to(position)


def capture(mobjects) -> list[list[tuple[VMobject, np.ndarray]]]:
    families = []
    seen: set[int] = set()
    for mob in mobjects:
        family = []
        for sub in mob.get_family():
            if id(sub) in seen:
                continue
            seen.add(id(sub))
            family.append((sub, np.array(sub.points, copy=True)))
        families.append(family)
    return families


def apply_pose(snapshots, angle: float) -> None:
    transform = rotation_matrix(angle).T
    for family in snapshots:
        for sub, points in family:
            if len(points) == 0:
                continue
            sub.points[:, :] = points @ transform


def panel_around(contents: VGroup, buff_x=0.28, buff_y=0.2) -> VGroup:
    frame = RoundedRectangle(
        width=contents.width + 2 * buff_x,
        height=contents.height + 2 * buff_y,
        corner_radius=0.1,
        fill_color=PANEL,
        fill_opacity=0.94,
        stroke_color=PANEL_STROKE,
        stroke_width=1.25,
    )
    frame.move_to(contents)
    group = VGroup(frame, contents)
    group.set_z_index(Z_PANEL)
    return group


def make_caption(text: str) -> VGroup:
    label = with_halo(Tex(text, color=CREAM).scale(0.58), width=3)
    if label.width > 11.4:
        label.scale(11.4 / label.width)
    return panel_around(label, buff_x=0.32, buff_y=0.16).move_to(np.array([0.15, -3.46, 0.0]))


def measurement(
    symbol: str,
    getter,
    decimals: int,
    unit: str | None = None,
    color: str = CREAM,
    live: bool = True,
) -> tuple[MathTex, DecimalNumber]:
    """A symbol and a decimal read from `getter`.

    Side lengths pass ``live=False`` so an invariant value is not rebuilt every
    frame. The updater still watches it, and rewrites the glyphs if it changes.
    """
    name = MathTex(symbol, color=color).scale(0.64)
    value = DecimalNumber(
        getter(),
        num_decimal_places=decimals,
        group_with_commas=False,
        edge_to_fix=LEFT,
        font_size=28,
        unit=unit,
        unit_buff_per_font_unit=0.002,
    )
    value.set_color(color)

    def updater(mob, source=getter, places=decimals, ink=color, always=live):
        new = float(source())
        if always or round(new, places) != round(mob.get_value(), places):
            mob.set_value(new)
            mob.set_color(ink)

    value.add_updater(updater)
    return name, value


def stack_equations(rows: list[tuple[VMobject, VMobject]]) -> VGroup:
    """Align the left-hand symbols on the right and the numbers on the left."""
    symbols = VGroup(*(name for name, _value in rows))
    symbols.arrange(DOWN, buff=0.16, aligned_edge=RIGHT)
    left = symbols.get_right()[0] + 0.18
    values = VGroup()
    for symbol, value in rows:
        value.move_to(
            np.array([left, symbol.get_y(), 0.0]),
            aligned_edge=np.array([-1.0, 0.0, 0.0]),
        )
        value.set_y(symbol.get_y())
        values.add(value)
    return VGroup(symbols, values)


def orbit(start: np.ndarray, color: str, tracker: ValueTracker, width=2.6, opacity=1.0):
    radius = float(np.linalg.norm(start))
    start_angle = float(np.arctan2(start[1], start[0]))

    def builder():
        turned = max(float(tracker.get_value()), 0.0) * THETA
        arc = Arc(
            radius=radius,
            start_angle=start_angle,
            angle=max(turned, 1e-4),
            arc_center=np.array([0.0, 0.0, 0.0]),
            color=color,
            stroke_width=width,
        )
        arc.set_stroke(opacity=0.0 if turned < 0.03 else opacity)
        arc.set_z_index(Z_ORBIT)
        return arc

    return always_redraw(builder)


def angle_mark(tracker: ValueTracker):
    turned = max(float(tracker.get_value()), 0.0) * THETA
    group = VGroup()
    if turned < 0.04:
        group.set_z_index(Z_ANGLE)
        return group
    sector = Sector(
        radius=ANGLE_RADIUS,
        start_angle=0.0,
        angle=turned,
        arc_center=np.array([0.0, 0.0, 0.0]),
        color=LINE_IMAGE,
        fill_opacity=0.3,
        stroke_width=0,
    )
    arc = Arc(
        radius=ANGLE_RADIUS,
        start_angle=0.0,
        angle=turned,
        arc_center=np.array([0.0, 0.0, 0.0]),
        color=LINE_IMAGE,
        stroke_width=2.6,
    )
    if turned > 0.28:
        arc.add_tip(tip_length=0.12, tip_width=0.1)
    label = MathTex(r"\theta", color=LINE_IMAGE).scale(0.62)
    mid = turned / 2
    label.move_to(np.array([np.cos(mid), np.sin(mid), 0.0]) * 1.28)
    label.set_opacity(min(1.0, (turned - 0.15) / 0.25))
    with_halo(label, width=4)
    group.add(sector, arc, label)
    group.set_z_index(Z_ANGLE)
    return group


class KinematicRotation(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND
        tracker = ValueTracker(0.0)

        grid = build_grid()
        lattice = build_lattice()
        moving_line = build_tracked_line()
        pin, pin_label = self._pin()
        line_label = with_halo(MathTex("L", color=LINE_COLOR).scale(0.78))
        line_label.move_to(np.array([-6.25, 0.38, 0.0]))
        line_label.set_z_index(Z_LABEL)

        triangle, vertices, labels = self._triangle()
        samples = VGroup(
            *[
                Dot(point, radius=0.05, color=SAMPLE_COLOR).set_z_index(Z_VERTEX)
                for point in SAMPLE_POINTS
            ]
        )
        title = with_halo(Tex(r"Rotation of the plane about $O$", color=CREAM).scale(0.72), width=7)
        title.move_to(np.array([-3.15, 3.52, 0.0]))
        title.set_z_index(Z_PANEL)

        side_panel = self._side_panel(vertices)
        side_panel.move_to(np.array([-5.15, -2.05, 0.0]))
        parameter_panel, spacers = self._parameter_panel()
        parameter_panel.move_to(np.array([5.15, 2.62, 0.0]))
        readouts = VGroup(
            self._readout(tracker.get_value, spacers[0].get_left(), decimals=2),
            self._readout(
                lambda: float(tracker.get_value()) * THETA_DEGREES,
                spacers[1].get_left(),
                decimals=0,
                unit=r"^{\circ}",
                color=LINE_IMAGE,
            ),
        )

        orbits = VGroup(
            orbit(A_POINT, VERTEX_COLORS[0], tracker, width=2.8),
            orbit(B_POINT, VERTEX_COLORS[1], tracker, width=2.8),
            orbit(C_POINT, VERTEX_COLORS[2], tracker, width=2.8),
            *[orbit(point, SAMPLE_COLOR, tracker, width=1.7, opacity=0.75) for point in SAMPLE_POINTS],
        )
        angle = always_redraw(lambda: angle_mark(tracker))

        # Updated before the labels, which read the vertex positions.
        driver = VMobject()
        driver.set_z_index(-1)
        self.add(driver)

        self.play(FadeIn(grid), FadeIn(lattice), run_time=1.0)
        self.play(FadeIn(title, shift=0.12 * np.array([0.0, -1.0, 0.0])), run_time=0.7)
        self.play(Create(moving_line), run_time=1.15)
        self.play(
            GrowFromCenter(pin),
            FadeIn(pin_label),
            FadeIn(line_label),
            run_time=0.75,
        )
        caption = self._say(None, r"Fix a point $O$ on the line $L$.")
        self.wait(0.85)

        self.play(
            Create(triangle),
            FadeIn(vertices),
            FadeIn(labels),
            FadeIn(samples),
            run_time=1.5,
        )
        caption = self._say(caption, r"$\triangle ABC$ rides with the plane.")
        self.play(FadeIn(side_panel), run_time=0.7)
        self.wait(0.9)

        caption = self._say(caption, r"Turn the whole plane about $O$ through angle $\theta$.")
        self.play(FadeIn(parameter_panel), FadeIn(readouts), run_time=0.75)
        self.wait(0.7)

        ghost_line = DashedVMobject(moving_line.copy(), num_dashes=34, dashed_ratio=0.55)
        ghost_line.set_stroke(color=LINE_COLOR, width=2.2, opacity=0.8)
        ghost_line.set_z_index(Z_GHOST)
        ghost_triangle = DashedVMobject(
            triangle.copy().set_fill(opacity=0).set_stroke(color=CREAM, width=1.8, opacity=0.8),
            num_dashes=28,
            dashed_ratio=0.5,
        )
        ghost_triangle.set_z_index(Z_GHOST)
        rings = VGroup()
        for point, color in zip((A_POINT, B_POINT, C_POINT), VERTEX_COLORS, strict=True):
            ring = Dot(point, radius=0.055, color=color, fill_opacity=0.0, stroke_width=1.6, stroke_color=color)
            ring.set_z_index(Z_GHOST)
            rings.add(ring)
        self.add(ghost_line)
        self.play(FadeIn(ghost_triangle), FadeIn(rings), run_time=0.55)
        caption = self._say(caption, r"Every point keeps its distance from $O$.")
        self.add(orbits, angle)

        rigid = [grid, lattice, moving_line, triangle, vertices, samples]
        snapshots = capture(rigid)
        driver.add_updater(lambda _mob: apply_pose(snapshots, float(tracker.get_value()) * THETA))
        self.play(tracker.animate.set_value(1.0), run_time=8.0, rate_func=smooth)
        driver.clear_updaters()
        self.wait(0.35)

        image_label = with_halo(MathTex("L'", color=LINE_IMAGE).scale(0.78))
        image_label.move_to(np.array([-1.05, -2.55, 0.0]))
        image_label.set_z_index(Z_LABEL)
        caption = self._say(caption, r"$L$ maps to $L'$, and the side lengths stay the same.")
        self.play(
            moving_line.animate.set_color(LINE_IMAGE),
            FadeIn(image_label),
            run_time=0.9,
        )
        self.wait(2.8)

    def _pin(self):
        dot = Dot(np.array([0.0, 0.0, 0.0]), radius=0.07, color=CREAM)
        ring = Circle(radius=0.16, color=CREAM, stroke_width=1.6)
        pin = VGroup(ring, dot)
        pin.set_z_index(Z_PIN)
        label = with_halo(MathTex("O", color=CREAM).scale(0.72))
        label.move_to(np.array([-0.36, -0.36, 0.0]))
        label.set_z_index(Z_LABEL)
        return pin, label

    def _triangle(self):
        points = (A_POINT, B_POINT, C_POINT)
        triangle = Polygon(
            *points,
            color=TRI_STROKE,
            fill_color=TRI_FILL,
            fill_opacity=0.3,
            stroke_width=2.8,
        )
        triangle.set_z_index(Z_TRIANGLE)
        vertices = VGroup()
        labels = VGroup()
        names = ("A", "B", "C")
        for point, name, color in zip(points, names, VERTEX_COLORS, strict=True):
            dot = Dot(point, radius=0.068, color=color)
            dot.set_z_index(Z_VERTEX)
            vertices.add(dot)
            label = with_halo(MathTex(name, color=color).scale(0.66))
            label.set_z_index(Z_LABEL)
            labels.add(label)

        def follow(label, dot):
            def updater(mob):
                centers = [item.get_center() for item in vertices]
                place_vertex_label(mob, dot.get_center(), np.mean(centers, axis=0))

            updater(label)
            label.add_updater(updater)

        for label, dot in zip(labels, vertices, strict=True):
            follow(label, dot)
        return triangle, vertices, labels

    def _side_panel(self, vertices: VGroup) -> VGroup:
        pairs = (("AB", 0, 1), ("BC", 1, 2), ("CA", 2, 0))
        rows = []
        for symbol, i, j in pairs:
            getter = lambda i=i, j=j: float(
                np.linalg.norm(vertices[i].get_center() - vertices[j].get_center())
            )
            name, value = measurement(symbol, getter, decimals=2, live=False)
            equals = MathTex("=", color=MUTED).scale(0.58)
            rows.append((VGroup(name, equals).arrange(RIGHT, buff=0.1), value))
        block = stack_equations(rows)
        header = Tex("side lengths", color=MUTED).scale(0.46)
        header.next_to(block, UP, buff=0.14).align_to(block, LEFT)
        return panel_around(VGroup(header, block))

    def _parameter_panel(self):
        """Static labels, plus invisible spacers that reserve the number column.

        The changing numerals are drawn separately. Updating a DecimalNumber
        inside a group leaves faint copies of the previous glyphs.
        """
        theta_name = MathTex(r"\theta", color=LINE_IMAGE).scale(0.64)
        theta_equals = MathTex("=", color=MUTED).scale(0.58)
        theta_value = MathTex(r"60^{\circ}", color=CREAM).scale(0.64)
        theta_left = VGroup(theta_name, theta_equals).arrange(RIGHT, buff=0.1)

        t_left = VGroup(
            MathTex("t", color=CREAM).scale(0.64),
            MathTex("=", color=MUTED).scale(0.58),
        ).arrange(RIGHT, buff=0.1)
        angle_left = VGroup(
            MathTex(r"t\theta", color=LINE_IMAGE).scale(0.64),
            MathTex("=", color=MUTED).scale(0.58),
        ).arrange(RIGHT, buff=0.1)

        # 1.00 and 60° are the widest values these readouts take.
        t_spacer = DecimalNumber(1, num_decimal_places=2, group_with_commas=False, font_size=28)
        angle_spacer = DecimalNumber(
            THETA_DEGREES,
            num_decimal_places=0,
            group_with_commas=False,
            font_size=28,
            unit=r"^{\circ}",
            unit_buff_per_font_unit=0,
        )
        t_spacer.set_opacity(0)
        angle_spacer.set_opacity(0)
        block = stack_equations(
            [(theta_left, theta_value), (t_left, t_spacer), (angle_left, angle_spacer)]
        )
        panel = panel_around(block)
        return panel, (t_spacer, angle_spacer)

    def _readout(self, getter, anchor, decimals: int, unit: str | None = None, color: str = CREAM):
        def builder(source=getter, ink=color, places=decimals, mark=unit, home=np.array(anchor, copy=True)):
            number = DecimalNumber(
                float(source()),
                num_decimal_places=places,
                group_with_commas=False,
                font_size=28,
                unit=mark,
                unit_buff_per_font_unit=0,
            )
            number.set_color(ink)
            number.move_to(home, aligned_edge=LEFT)
            number.set_z_index(Z_PANEL + 1)
            return number

        return always_redraw(builder)

    def _say(self, current, text: str):
        new = make_caption(text)
        if current is None:
            self.play(FadeIn(new), run_time=0.5)
        else:
            self.play(FadeOut(current), run_time=0.22)
            self.play(FadeIn(new), run_time=0.32)
        return new
