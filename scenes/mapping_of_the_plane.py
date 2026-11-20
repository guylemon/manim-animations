"""A mapping of the plane into itself.

Definition from Serge Lang, Basic Mathematics, Chapter 6, §1, printed
pp. 133–134: an association sending each point of the plane to a point of
the plane, the notation P ↦ P', the value F(P), the image, and equality of
two mappings. The film stops before distance-preserving maps and the concrete
constructions later in the section. The background is the same
coordinate grid as the kinematic-rotation scene.

There is no voiceover in this repository. The storyboard's narration is
shown as on-screen captions, which is how the kinematic-rotation scene
already presents its text.

Render from the repository root:

    manim -qh --fps 30 scenes/mapping_of_the_plane.py MappingOfThePlane
"""

from __future__ import annotations

import numpy as np
from manim import (
    Arrow,
    Create,
    Dot,
    DOWN,
    FadeIn,
    FadeOut,
    GrowArrow,
    GrowFromCenter,
    Indicate,
    LEFT,
    LaggedStart,
    Line,
    MathTex,
    RIGHT,
    RoundedRectangle,
    Scene,
    ShowPassingFlash,
    Tex,
    Transform,
    UP,
    UR,
    VGroup,
    Write,
)

# Eight scenes, about 81 seconds. Each definitional sentence is held on
# screen, with its diagram, for more than two seconds.
# Palette and caption panels match the kinematic-rotation scene.
BACKGROUND = "#0e1218"
PANEL = "#1a2330"
PANEL_STROKE = "#3d4f66"
CREAM = "#f6f1e7"
MUTED = "#b7c3d1"
GRID = "#3d5672"
GRID_HALF = "#2a3c52"
# Points use the other film's line blue. Arrows and emphasis use its
# image gold. The brief redraw of the arrow uses its warm vertex color.
BLUE = "#8ec5ff"
ORANGE = "#ffd166"
GOLD = "#ff8b7b"
RED = "#ff8b7b"
GRID_EXTENT = 9.5

Z_GRID = 0
Z_CARD = 1
Z_ARROW = 2
Z_POINT = 4
Z_LABEL = 6
Z_PANEL = 8

# Scenes 2–6. The three associations point in different directions and have
# different lengths, so the picture is not a translation or a turn.
PAIRS = (
    {
        "name": "P_1",
        "image_name": "P_1'",
        "short": "P",
        "short_image": "P'",
        "mapsto": r"P \mapsto P'",
        "start": np.array([-3.35, 0.15, 0.0]),
        "end": np.array([-1.15, 1.45, 0.0]),
        "start_dir": LEFT,
        "end_dir": UP,
    },
    {
        "name": "P_2",
        "image_name": "P_2'",
        "short": "P_2",
        "short_image": "P_2'",
        "mapsto": r"P_2 \mapsto P_2'",
        "start": np.array([1.55, 1.25, 0.0]),
        "end": np.array([3.85, -0.25, 0.0]),
        "start_dir": UP,
        "end_dir": RIGHT,
    },
    {
        "name": "P_3",
        "image_name": "P_3'",
        "short": "P_3",
        "short_image": "P_3'",
        "mapsto": r"P_3 \mapsto P_3'",
        "start": np.array([-2.15, -0.75, 0.0]),
        "end": np.array([0.65, -0.05, 0.0]),
        "start_dir": LEFT,
        "end_dir": DOWN,
    },
)

# From the special-arrow scene through the image, only this pair remains.
# It sits in the middle of the coordinate plane.
FOCUS_START = np.array([-1.35, -0.2, 0.0])
FOCUS_END = np.array([1.45, 1.2, 0.0])

# Scene 7. Offsets from the center of each plane card.
CARD_SIZE = (5.3, 3.05)
CARD_Y = 0.48
LEFT_CENTER = np.array([-3.55, CARD_Y, 0.0])
RIGHT_CENTER = np.array([3.55, CARD_Y, 0.0])
COMPARE = (
    # name, domain, image under both maps, domain label side, image label side
    ("P", np.array([-1.2, 0.55, 0.0]), np.array([0.2, 0.85, 0.0]), LEFT, UP),
    ("Q", np.array([1.05, 0.35, 0.0]), np.array([1.25, -0.45, 0.0]), UP, RIGHT),
    # R's image sits under Q, so its label goes left, off the shaft and away from Q.
    ("R", np.array([-1.05, -0.58, 0.0]), np.array([0.15, 0.05, 0.0]), LEFT, LEFT),
)
# G sends R somewhere else, until the two maps are made to agree.
G_R_IMAGE = np.array([0.2, -0.95, 0.0])


def _segments_cross(a, b, c, d, eps=1e-6) -> bool:
    r = b - a
    s = d - c
    denom = r[0] * s[1] - r[1] * s[0]
    if abs(denom) < eps:
        return False
    delta = c - a
    t = (delta[0] * s[1] - delta[1] * s[0]) / denom
    u = (delta[0] * r[1] - delta[1] * r[0]) / denom
    return eps < t < 1 - eps and eps < u < 1 - eps


def _assert_layout() -> None:
    """The associations are visible, distinct, and not a rigid motion."""
    starts = [item["start"] for item in PAIRS]
    ends = [item["end"] for item in PAIRS]
    for start, end in zip(starts, ends, strict=True):
        length = float(np.linalg.norm(end - start))
        assert length > 1.4
    cloud = [*starts, *ends]
    for i, point in enumerate(cloud):
        for other in cloud[i + 1 :]:
            assert np.linalg.norm(point - other) > 0.9
    for i in range(len(PAIRS)):
        for j in range(i + 1, len(PAIRS)):
            assert not _segments_cross(starts[i], ends[i], starts[j], ends[j])
    # Not a translation: the arrow vectors are not equal.
    vectors = [end - start for start, end in zip(starts, ends, strict=True)]
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            assert not np.allclose(vectors[i], vectors[j], atol=0.2)

    half_w, half_h = CARD_SIZE[0] / 2, CARD_SIZE[1] / 2
    local = [domain for _name, domain, _image, _d, _e in COMPARE]
    local += [image for _name, _domain, image, _d, _e in COMPARE]
    local.append(G_R_IMAGE)
    for point in local:
        assert abs(point[0]) < half_w - 0.7
        assert abs(point[1]) < half_h - 0.45
    for i, point in enumerate(local):
        for other in local[i + 1 :]:
            assert np.linalg.norm(point - other) > 0.7
    for i in range(len(COMPARE)):
        for j in range(i + 1, len(COMPARE)):
            assert not _segments_cross(
                COMPARE[i][1], COMPARE[i][2], COMPARE[j][1], COMPARE[j][2]
            )
    domain_r = COMPARE[2][1]
    image_r = COMPARE[2][2]
    assert not np.allclose(G_R_IMAGE, image_r, atol=0.3)
    assert not _segments_cross(domain_r, G_R_IMAGE, COMPARE[0][1], COMPARE[0][2])
    assert not _segments_cross(domain_r, G_R_IMAGE, COMPARE[1][1], COMPARE[1][2])


_assert_layout()


def with_halo(mobject, width=5):
    mobject.set_stroke(BACKGROUND, width=width, background=True)
    return mobject


def build_grid() -> VGroup:
    """The same quiet coordinate grid as the kinematic-rotation scene."""
    lines = VGroup()
    half_steps = np.arange(-GRID_EXTENT, GRID_EXTENT + 1e-6, 0.5)
    for value in half_steps:
        major = abs(value - round(value)) < 1e-6 and abs(round(value)) > 1e-6
        color = GRID if major or abs(value) < 1e-6 else GRID_HALF
        width = 1.35 if major or abs(value) < 1e-6 else 0.8
        opacity = 0.85 if major or abs(value) < 1e-6 else 0.55
        lines.add(
            Line(
                np.array([-GRID_EXTENT, value, 0.0]),
                np.array([GRID_EXTENT, value, 0.0]),
                stroke_color=color,
                stroke_width=width,
                stroke_opacity=opacity,
            ),
            Line(
                np.array([value, -GRID_EXTENT, 0.0]),
                np.array([value, GRID_EXTENT, 0.0]),
                stroke_color=color,
                stroke_width=width,
                stroke_opacity=opacity,
            ),
        )
    lines.set_z_index(Z_GRID)
    return lines


def make_dot(point, radius=0.062) -> VGroup:
    glow = Dot(point, radius=radius * 2.2, color=BLUE, fill_opacity=0.2)
    core = Dot(point, radius=radius, color=BLUE)
    group = VGroup(glow, core)
    group.set_z_index(Z_POINT)
    return group


def math_label(tex: str, scale=0.7, color=CREAM) -> MathTex:
    label = MathTex(tex, color=color).scale(scale)
    with_halo(label, width=4)
    label.set_z_index(Z_LABEL)
    return label


def association_arrow(start, end, width=3.1, color=ORANGE, tip_length=0.16) -> Arrow:
    arrow = Arrow(
        np.asarray(start, dtype=float),
        np.asarray(end, dtype=float),
        buff=0.16,
        stroke_width=width,
        tip_length=tip_length,
        color=color,
        max_tip_length_to_length_ratio=0.22,
        max_stroke_width_to_length_ratio=14,
    )
    arrow.set_z_index(Z_ARROW)
    return arrow


def panel_around(contents, buff_x=0.32, buff_y=0.16) -> VGroup:
    if contents.width > 11.4:
        contents.scale(11.4 / contents.width)
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


def caption_line(text: str, scale=0.58) -> Tex:
    """One caption line, set like the kinematic-rotation captions."""
    label = Tex(text, color=CREAM).scale(scale)
    with_halo(label, width=3)
    return label


def fit_lines(lines: list[str], scale=0.58) -> VGroup:
    # A single line uses the other film's caption size. Longer sentences
    # step down slightly so the panel still sits in that same bottom band.
    if len(lines) >= 4:
        scale = min(scale, 0.48)
    elif len(lines) == 3:
        scale = min(scale, 0.5)
    rows = VGroup(*[caption_line(line, scale=scale) for line in lines])
    rows.arrange(DOWN, buff=0.1)
    return rows


def emphasis(before: str, word: str, after: str, scale=0.58) -> Tex:
    line = Tex(before, r"\textbf{" + word + "}", after, color=CREAM).scale(scale)
    with_halo(line, width=3)
    line[1].set_color(ORANGE)
    return line


def mapsto_label(start, end, tex: str, scale=0.78) -> MathTex:
    label = math_label(tex, scale=scale)
    mid = (np.asarray(start) + np.asarray(end)) / 2
    delta = np.asarray(end) - np.asarray(start)
    normal = np.array([-delta[1], delta[0], 0.0])
    normal = normal / np.linalg.norm(normal)
    if normal[1] < 0:
        normal = -normal
    # Far enough off the shaft that a thick arrow does not cut the notation.
    label.move_to(mid + normal * 0.7)
    return label


def mismatch_cross(point, size=0.2) -> VGroup:
    arm_a = Line(
        point + np.array([-size, -size, 0.0]),
        point + np.array([size, size, 0.0]),
        color=RED,
        stroke_width=5.5,
    )
    arm_b = Line(
        point + np.array([-size, size, 0.0]),
        point + np.array([size, -size, 0.0]),
        color=RED,
        stroke_width=5.5,
    )
    mark = VGroup(arm_a, arm_b)
    mark.set_z_index(Z_LABEL + 1)
    return mark


class MappingOfThePlane(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND
        self.caption = None
        self.grid = build_grid()
        self.pairs = []
        self._scene_title()
        self._scene_association()
        self._scene_arrow_notation()
        self._scene_value_words()
        self._scene_name_f()
        self._scene_image()
        self._scene_equality()
        self._scene_recap()

    def _say(self, body, run_time=0.45):
        panel = panel_around(body)
        # Short captions share the other film's caption position. Taller
        # sentences stay in that same bottom band.
        if panel.height < 1.15:
            panel.move_to(np.array([0.15, -3.46, 0.0]))
        else:
            panel.to_edge(DOWN, buff=0.28)
        if self.caption is None:
            self.play(FadeIn(panel, shift=0.06 * UP), run_time=run_time)
        else:
            self.play(
                FadeOut(self.caption, shift=0.04 * DOWN),
                FadeIn(panel, shift=0.06 * UP),
                run_time=run_time,
            )
        self.caption = panel
        return panel

    def _say_lines(self, lines, run_time=0.45):
        return self._say(fit_lines(lines), run_time=run_time)

    # Scene 1, 8.0 s. Title and the coordinate plane. No sample points.
    def _scene_title(self):
        self.play(FadeIn(self.grid), run_time=0.6)
        title = with_halo(Tex("Mappings of the Plane", color=CREAM).scale(0.92), width=6)
        subtitle = with_halo(Tex(r"Chapter 6, \S 1", color=MUTED).scale(0.55), width=4)
        VGroup(title, subtitle).arrange(DOWN, buff=0.22).move_to(np.array([0.0, 1.15, 0.0]))
        title.set_z_index(Z_PANEL)
        subtitle.set_z_index(Z_PANEL)
        self.title = title
        self.subtitle = subtitle
        self.play(FadeIn(title, shift=0.1 * UP), run_time=0.7)
        self.play(FadeIn(subtitle), run_time=0.45)
        self._say_lines(
            ["We begin by defining a mapping of the plane into itself."],
            run_time=0.45,
        )
        self.wait(5.8)

    # Scene 2, 12.0 s. Each of P1, P2, P3 is joined to its image.
    def _scene_association(self):
        self.play(
            FadeOut(self.title),
            FadeOut(self.subtitle),
            FadeOut(self.caption),
            run_time=0.55,
        )
        self.caption = None

        domains = []
        for spec in PAIRS:
            dot = make_dot(spec["start"])
            label = math_label(spec["name"], scale=0.7)
            label.next_to(dot, spec["start_dir"], buff=0.14)
            spec_state = {
                "spec": spec,
                "dot": dot,
                "start_label": label,
            }
            self.pairs.append(spec_state)
            domains.append(GrowFromCenter(dot))
            domains.append(FadeIn(label))
        self.play(LaggedStart(*domains, lag_ratio=0.12), run_time=0.65)

        for state in self.pairs:
            spec = state["spec"]
            arrow = association_arrow(spec["start"], spec["end"], width=3.0)
            image = make_dot(spec["end"])
            image_label = math_label(spec["image_name"], scale=0.7)
            image_label.next_to(image, spec["end_dir"], buff=0.14)
            state["arrow"] = arrow
            state["image"] = image
            state["end_label"] = image_label
            self.play(
                GrowArrow(arrow),
                GrowFromCenter(image),
                FadeIn(image_label),
                run_time=0.72,
            )

        self._say_lines(
            ["To each point of the plane we associate another point of the plane."],
            run_time=0.4,
        )
        self.wait(2.4)
        self._say_lines(
            [
                "By a mapping (or a map) of the plane into itself,",
                "we shall mean an association which to each point of the plane",
                "associates another point of the plane.",
            ],
            run_time=0.5,
        )
        self.wait(5.34)

    # Scene 3, 10.0 s. From here until the comparison, only P ↦ P' remains.
    def _scene_arrow_notation(self):
        focus = self.pairs[0]
        spec = focus["spec"]
        others = []
        for state in self.pairs[1:]:
            others.extend(
                (
                    state["dot"],
                    state["image"],
                    state["start_label"],
                    state["end_label"],
                    state["arrow"],
                )
            )
        spec["start"] = FOCUS_START.copy()
        spec["end"] = FOCUS_END.copy()
        start_label = math_label(spec["short"], scale=0.78)
        end_label = math_label(spec["short_image"], scale=0.78)
        start_label.next_to(FOCUS_START, LEFT, buff=0.16)
        end_label.next_to(FOCUS_END, UP, buff=0.16)
        thick = association_arrow(FOCUS_START, FOCUS_END, width=7.2, tip_length=0.2)
        self.play(
            *[FadeOut(mob) for mob in others],
            focus["dot"].animate.move_to(FOCUS_START).scale(1.12),
            focus["image"].animate.move_to(FOCUS_END).scale(1.12),
            FadeOut(focus["start_label"]),
            FadeOut(focus["end_label"]),
            FadeIn(start_label),
            FadeIn(end_label),
            Transform(focus["arrow"], thick),
            run_time=0.9,
        )
        focus["start_label"] = start_label
        focus["end_label"] = end_label
        self.pairs = [focus]

        notation = mapsto_label(FOCUS_START, FOCUS_END, spec["mapsto"], scale=0.9)
        self.play(Write(notation), run_time=0.55)
        focus["notation"] = notation
        self._say_lines(
            [
                r"If $P$ is a point and $P'$ is the point associated with $P$",
                r"by the mapping, then we denote this by the special arrow.",
            ],
            run_time=0.4,
        )
        self.wait(8.15)

    # Scene 4, 12.0 s. Value, corresponds, mapped on. Then pulse P, then P'.
    def _scene_value_words(self):
        focus = self.pairs[0]
        phrases = (
            emphasis(r"$P'$ is the ", "value", r" of the mapping at $P$."),
            emphasis(r"$P'$ ", "corresponds", r" to $P$ under the mapping."),
            emphasis(r"$P$ is ", "mapped on", r" $P'$."),
        )
        pulses = (
            Indicate(focus["image"], color=ORANGE, scale_factor=1.28),
            [
                Indicate(focus["dot"], color=ORANGE, scale_factor=1.18),
                Indicate(focus["image"], color=ORANGE, scale_factor=1.18),
            ],
            ShowPassingFlash(
                focus["arrow"].copy().set_color(CREAM),
                time_width=0.45,
            ),
        )
        for phrase, pulse in zip(phrases, pulses, strict=True):
            self._say(phrase, run_time=0.35)
            if isinstance(pulse, list):
                self.play(*pulse, run_time=0.65)
            else:
                self.play(pulse, run_time=0.65)
            self.wait(2.1)
        self.play(Indicate(focus["dot"], color=BLUE, scale_factor=1.45), run_time=0.6)
        self.play(Indicate(focus["image"], color=BLUE, scale_factor=1.45), run_time=0.6)
        self.wait(1.5)

    # Scene 5, 10.0 s. The collection of arrows is named F, and F(P) = P'.
    def _scene_name_f(self):
        focus = self.pairs[0]
        self.f_letter = math_label("F", scale=1.15, color=ORANGE)
        self.f_letter.move_to(np.array([-4.15, 1.15, 0.0]))
        self.play(FadeIn(self.f_letter, scale=0.85), run_time=0.55)

        value = math_label(r"F(P)", scale=0.72, color=ORANGE)
        value.next_to(focus["image"], RIGHT, buff=0.18)
        equality = with_halo(MathTex(r"F(P) = P'", color=CREAM).scale(0.85), width=4)
        self.equality = panel_around(equality, buff_x=0.26, buff_y=0.14)
        self.equality.to_edge(UP, buff=0.22)
        self.play(Write(value), FadeIn(self.equality), run_time=0.7)
        self.value_label = value
        self._say_lines(
            [
                "Just as we used letters to denote numbers,",
                "it is useful to use letters to denote mappings.",
                r"Thus if $F$ is a mapping of the plane into itself,",
                r"we denote the value of $F$ at $P$ by the symbols $F(P)$.",
            ],
            run_time=0.45,
        )
        self.wait(8.3)

    # Scene 6, 8.0 s. Image of P under F, then the second sentence, arrow redrawn.
    def _scene_image(self):
        image_line = Tex(
            r"the ",
            r"\textbf{image}",
            r" of $P$ under $F$ $=$ $F(P)$",
            color=CREAM,
        ).scale(0.55)
        with_halo(image_line, width=3)
        image_line[1].set_color(ORANGE)
        image_panel = panel_around(image_line)
        image_panel.to_edge(DOWN, buff=0.22)
        self.play(FadeOut(self.caption), FadeIn(image_panel), run_time=0.5)
        self.caption = image_panel
        self.wait(2.3)

        sentence = fit_lines(
            [
                r"If $F(P) = P'$, then we also say that",
                r"$F$ maps $P$ on $P'$.",
            ],
        )
        sentence_panel = panel_around(sentence)
        sentence_panel.to_edge(DOWN, buff=0.22)
        image_home = image_panel.copy().next_to(sentence_panel, UP, buff=0.12)
        self.play(
            image_panel.animate.move_to(image_home.get_center()),
            FadeIn(sentence_panel),
            run_time=0.45,
        )
        self.caption = sentence_panel
        self.image_panel = image_panel

        focus = self.pairs[0]
        spec = focus["spec"]
        gold = association_arrow(
            spec["start"],
            spec["end"],
            width=7.2,
            tip_length=0.2,
            color=GOLD,
        )
        self.play(FadeOut(focus["arrow"]), Create(gold), run_time=0.85)
        focus["arrow"] = gold
        self.wait(3.9)

    # Scene 7, 15.0 s. F and G disagree at one point, then agree everywhere shown.
    def _scene_equality(self):
        leaving = [
            self.value_label,
            self.f_letter,
            self.equality,
            self.image_panel,
            self.caption,
        ]
        for state in self.pairs:
            leaving.extend(
                (
                    state["dot"],
                    state["image"],
                    state["start_label"],
                    state["end_label"],
                    state["arrow"],
                    state["notation"],
                )
            )
        self.play(*[FadeOut(mob) for mob in leaving], run_time=0.55)
        self.caption = None

        left = self._plane_card(LEFT_CENTER, "F")
        right = self._plane_card(RIGHT_CENTER, "G")
        self.cards = VGroup(left["card"], right["card"])
        self.play(FadeIn(self.cards), run_time=0.7)

        domains = []
        pictures = []
        for name, domain, image, domain_dir, image_dir in COMPARE:
            for card, letter, image_point in (
                (left, "F", image),
                (right, "G", image if name != "R" else G_R_IMAGE),
            ):
                start = card["center"] + domain
                end = card["center"] + image_point
                dot = make_dot(start, radius=0.05)
                picture = make_dot(end, radius=0.05)
                domain_label = math_label(name, scale=0.5)
                domain_label.next_to(dot, domain_dir, buff=0.1)
                image_label = math_label(rf"{letter}({name})", scale=0.46, color=ORANGE)
                side = image_dir if not (letter == "G" and name == "R") else DOWN
                image_label.next_to(picture, side, buff=0.14)
                arrow = association_arrow(start, end, width=2.7, tip_length=0.13)
                domains.extend((dot, domain_label))
                pictures.extend((picture, image_label, arrow))
                if letter == "G" and name == "R":
                    self.g_dot = picture
                    self.g_label = image_label
                    self.g_arrow = arrow
                    self.g_start = start
                    self.g_target = card["center"] + image
        self.play(LaggedStart(*[FadeIn(mob) for mob in domains], lag_ratio=0.08), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(mob) for mob in pictures], lag_ratio=0.05), run_time=0.85)
        self.compare_drawn = domains + pictures

        cross = mismatch_cross(self.g_dot.get_center())
        unequal = with_halo(MathTex(r"F \neq G", color=RED).scale(0.95))
        unequal.to_edge(UP, buff=0.2)
        unequal.set_z_index(Z_PANEL)
        self.play(FadeIn(cross), FadeIn(unequal, scale=1.08), run_time=0.4)
        self.play(Indicate(unequal, color=RED, scale_factor=1.12), run_time=0.45)
        self.wait(2.0)

        agreed = association_arrow(self.g_start, self.g_target, width=2.7, tip_length=0.13)
        self.play(
            self.g_dot.animate.move_to(self.g_target),
            Transform(self.g_arrow, agreed),
            self.g_label.animate.next_to(self.g_target, LEFT, buff=0.14),
            FadeOut(cross),
            FadeOut(unequal),
            run_time=1.25,
        )
        self.wait(0.55)

        definition = with_halo(
            MathTex(
                r"F = G \quad\text{if and only if, for every point } P, \quad F(P) = G(P).",
                color=CREAM,
            ).scale(0.62),
            width=3,
        )
        sentence = fit_lines(
            [
                r"In other words, a map $F$ is equal to a map $G$",
                r"if and only if $F$ and $G$ have the same value at every point $P$.",
            ],
        )
        sentence_panel = panel_around(sentence)
        sentence_panel.to_edge(DOWN, buff=0.22)
        self.definition = panel_around(definition)
        self.definition.next_to(sentence_panel, UP, buff=0.12)
        self.play(FadeIn(self.definition, shift=0.06 * UP), run_time=0.5)
        self.wait(2.6)
        self.play(FadeIn(sentence_panel), run_time=0.45)
        self.caption = sentence_panel
        self.wait(4.0)

    def _plane_card(self, center, letter):
        width, height = CARD_SIZE
        rect = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.06,
            stroke_color=PANEL_STROKE,
            stroke_width=10,
            fill_color=BACKGROUND,
            fill_opacity=0.35,
        )
        rect.move_to(center)
        rect.set_z_index(Z_CARD)
        title = math_label(letter, scale=0.95, color=ORANGE)
        title.next_to(rect, UP, buff=0.12)
        # The shared coordinate grid shows through the frame, so the two
        # planes are the same plane as the rest of the film.
        card = VGroup(rect, title)
        return {"card": card, "center": center, "title": title}

    # Scene 8, 6.0 s. The notations, then fade to black.
    def _scene_recap(self):
        self.play(
            FadeOut(self.cards),
            FadeOut(self.grid),
            *[FadeOut(mob) for mob in self.compare_drawn],
            FadeOut(self.definition),
            FadeOut(self.caption),
            run_time=0.5,
        )

        image_word = Tex(r"\textbf{image}", r" of $P$", color=CREAM).scale(0.7)
        image_word[0].set_color(ORANGE)
        lines = VGroup(
            MathTex(r"P \mapsto P'", color=CREAM).scale(1.05),
            MathTex(r"F(P)", color=ORANGE).scale(1.05),
            image_word,
            MathTex(r"F = G \Leftrightarrow F(P) = G(P)\ \forall P", color=CREAM).scale(0.72),
        ).arrange(DOWN, buff=0.38)
        if lines.width > 12.4:
            lines.scale(12.4 / lines.width)
        self.play(
            LaggedStart(*[FadeIn(line, shift=0.08 * UP) for line in lines], lag_ratio=0.22),
            run_time=1.15,
        )
        self.wait(3.15)
        self.play(FadeOut(lines), run_time=0.8)
        self.wait(0.4)
