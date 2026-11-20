"""Shared palette for the films in this repository.

Manim puts the scene file's directory on ``sys.path`` before it loads the
file, so a scene next to this module imports the colors directly::

    from theme import BACKGROUND, BLUE, ORANGE

    class Example(Scene):
        def construct(self):
            self.camera.background_color = BACKGROUND

Render from the repository root, the same way as the existing scenes::

    manim -ql scenes/example.py Example

The names used by the current films are the ones to import. A few of those
names describe roles rather than hues, and two of them share a hex:

* ``BLUE`` and ``LINE_COLOR`` are both ``#8ec5ff``.
* ``ORANGE`` and ``LINE_IMAGE`` are both ``#ffd166``. The hex is a gold, and
  the mapping scene's historical name ``ORANGE`` stays so that scene does
  not change.
* ``GOLD`` and ``RED`` are both ``#ff8b7b``. ``GOLD`` is the warm vertex and
  the redrawn arrow; ``RED`` is the mismatch mark. Same ink, both names.

``IMAGE_GOLD`` is another name for the gold ``#ffd166``. ``WARM`` is another
name for the coral ``#ff8b7b``. ``Theme`` exposes the same values as
attributes (``Theme.BLUE``).
"""

from __future__ import annotations

# Camera background, and the halo drawn behind captions so type stays
# readable on the grid.
BACKGROUND = "#0e1218"

# Caption panel fill, and the stroke around that panel.
PANEL = "#1a2330"
PANEL_STROKE = "#3d4f66"

# Primary caption and title ink.
CREAM = "#f6f1e7"

# Secondary type: subtitles, section labels, and the equals signs in readouts.
MUTED = "#b7c3d1"

# Coordinate grid. Major lines, including the axes, use GRID. Half-unit
# lines use the darker GRID_HALF.
GRID = "#3d5672"
GRID_HALF = "#2a3c52"

# Points, and the tracked line L before it turns. The mapping scene calls
# this BLUE. The rotation scene calls it LINE_COLOR.
BLUE = "#8ec5ff"
LINE_COLOR = BLUE

# Arrows, emphasized words, and the image of a line (L' after the turn).
# The hex is gold. The mapping scene's name for it is ORANGE; the rotation
# scene's name is LINE_IMAGE. IMAGE_GOLD is the same color under a name
# that matches the hue.
ORANGE = "#ffd166"
LINE_IMAGE = ORANGE
IMAGE_GOLD = ORANGE

# Warm coral. In the mapping scene, GOLD redraws the arrow and RED marks
# that two maps disagree. In the rotation scene it is vertex A. WARM is
# the same color under a name that matches the hue.
GOLD = "#ff8b7b"
RED = GOLD
WARM = GOLD

# Vertices B and C of the triangle. A is GOLD, above.
VERTEX_MINT = "#7ddeb3"
VERTEX_LILAC = "#d4c2ff"
VERTEX_COLORS = (GOLD, VERTEX_MINT, VERTEX_LILAC)

# Quiet lattice of sample dots on the rotation film.
LATTICE = "#8ea3b8"

# The extra points that turn with the plane, apart from the triangle.
SAMPLE_COLOR = "#d5e2f0"

# Fill and stroke of triangle ABC.
TRI_FILL = "#f0d2aa"
TRI_STROKE = "#f7efe4"

# Caption panels in both films. The rounded rectangle around a caption uses
# these three numbers; the F/G plane frames in the mapping scene do not.
PANEL_CORNER_RADIUS = 0.1
PANEL_STROKE_WIDTH = 1.25
PANEL_FILL_OPACITY = 0.94

# Shared coordinate grid. The extent is large enough that a sixth of a turn
# still covers the camera. Major lines (and the axes) are a little stronger
# than the half-unit lines.
GRID_EXTENT = 9.5
GRID_MAJOR_STROKE_WIDTH = 1.35
GRID_MINOR_STROKE_WIDTH = 0.8
GRID_MAJOR_OPACITY = 0.85
GRID_MINOR_OPACITY = 0.55


class Theme:
    """The constants on this module, as attributes.

    ``Theme.ORANGE`` is ``ORANGE``. Useful when a scene wants one object
    instead of a long import list.
    """


_PUBLIC = (
    "BACKGROUND",
    "PANEL",
    "PANEL_STROKE",
    "CREAM",
    "MUTED",
    "GRID",
    "GRID_HALF",
    "BLUE",
    "LINE_COLOR",
    "ORANGE",
    "LINE_IMAGE",
    "IMAGE_GOLD",
    "GOLD",
    "RED",
    "WARM",
    "VERTEX_MINT",
    "VERTEX_LILAC",
    "VERTEX_COLORS",
    "LATTICE",
    "SAMPLE_COLOR",
    "TRI_FILL",
    "TRI_STROKE",
    "PANEL_CORNER_RADIUS",
    "PANEL_STROKE_WIDTH",
    "PANEL_FILL_OPACITY",
    "GRID_EXTENT",
    "GRID_MAJOR_STROKE_WIDTH",
    "GRID_MINOR_STROKE_WIDTH",
    "GRID_MAJOR_OPACITY",
    "GRID_MINOR_OPACITY",
)

for _name in _PUBLIC:
    setattr(Theme, _name, globals()[_name])
del _name

__all__ = [*_PUBLIC, "Theme"]
