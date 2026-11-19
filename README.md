# manim-animations

Short mathematical films made with [Manim](https://www.manim.community/). The browsable library is a static site in [`docs/`](docs/) and is published with GitHub Pages.

**Library:** https://guylemon.github.io/manim-animations/

That address starts working after the repository setting below is turned on. Until then, open the same page locally.

## Browse locally

From the repository root:

```bash
python3 -m http.server -d docs 8000
```

Then open http://127.0.0.1:8000/

The page reads [`docs/catalog.json`](docs/catalog.json) and groups the films by topic. A second control lists them by year, and that arrangement is also available at `?view=date`. Each card shows the title, a short mathematical description, a video player when a render is listed, and any links to the scene file and the related issue. A filter box narrows the list by title, topic, or text in the description.

## Render a scene locally

Scenes use [Manim Community](https://www.manim.community/) 0.22. A LaTeX install is required for the labels. From the repository root:

```bash
pip install "manim>=0.22,<0.23"
manim -qh --fps 30 scenes/kinematic_rotation.py KinematicRotation
```

`-qh` renders at 1080p. `--fps 30` is enough for playback on the library page and keeps the file smaller than the 60 fps default. Use `-qm` for a faster 720p preview, or `-ql` while adjusting the scene. If `manim` is not on your `PATH`, run `python3 -m manim` with the same arguments.

Manim writes the MP4 under `media/videos/`. That directory is local scratch and is not committed. Copy the file the catalog should serve into `docs/videos/` — for this scene, `docs/videos/gro-35-kinematic-rotation.mp4` — then point the catalog entry at that path. Do not store the published video with Git LFS. GitHub Pages would serve the pointer text instead of the film.

The Pages workflow does not render scenes. It checks that every path listed in the catalog exists.

## Add an animation

Adding a film is one catalog entry, plus the video file when a render exists.

1. Render the scene to MP4 or WebM.
2. Commit the file under `docs/videos/`. A stable name such as `docs/videos/gro-35-kinematic-rotation.mp4` is enough. Keep each file under GitHub's 100 MB limit.
3. Add one object to the `animations` array in [`docs/catalog.json`](docs/catalog.json). Paths inside `video` are relative to `docs/`.
4. Check the catalog, then open a pull request:

```bash
python3 scripts/validate_catalog.py
```

The Pages workflow runs that check on every pull request. After the pull request is merged to `main`, the workflow publishes `docs/`.

Within a topic, cards stay in the order they appear in the catalog. The chronological view sorts by `date`, newest first, and leaves undated entries at the end.

### Catalog fields

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Unique slug, used as the card's link anchor. Lowercase letters, numbers, and hyphens. |
| `title` | yes | Name shown on the card. |
| `description` | yes | Short mathematical description. `$...$` is inline math and `$$...$$` is display math. |
| `topic` | yes | Group heading. Topics are listed alphabetically. |
| `chapter` | no | Finer label, shown on the card. |
| `date` | no | `YYYY-MM-DD`. Used only for the chronological view. |
| `status` | no | `ready` (the default) or `upcoming` when the film is not rendered yet. |
| `video` | no | A path under `docs/`, such as `videos/example.mp4`, or an `https://` URL. An object `{"mp4", "webm", "poster"}` supplies more than one file. |
| `source` | no | Scene file in this repository, such as `scenes/rotation.py`, or an `https://` URL. The page links to it on GitHub. |
| `issue` | no | URL of the related Linear issue, or any other issue. |
| `issueId` | no | Short label for that link, such as `GRO-35`. |

Example of a finished entry:

```json
{
  "id": "gro-35-kinematic-rotation",
  "title": "Kinematic rotation of △ABC about a point on line L",
  "topic": "Plane isometries",
  "chapter": "Lang, Basic Mathematics, Chapter 6",
  "date": "2026-11-19",
  "status": "ready",
  "description": "Fix a point $O$ on a line $L$. Rotation about $O$ through an angle $\\theta$ carries $\\triangle ABC$ as a rigid body.",
  "video": "videos/gro-35-kinematic-rotation.mp4",
  "source": "scenes/kinematic_rotation.py",
  "issue": "https://linear.app/gl-grokbots/issue/GRO-35/kinematic-rotation-of-abc-about-a-point-on-line-l",
  "issueId": "GRO-35"
}
```

To offer both containers, use an object instead of a single path:

```json
"video": {
  "mp4": "videos/gro-35-kinematic-rotation.mp4",
  "webm": "videos/gro-35-kinematic-rotation.webm"
}
```

Leave `video` and `source` as `null` and set `"status": "upcoming"` when the scene or the render is not in the repository yet. The card keeps the description and the issue link, and the player appears once `video` points at a file that exists.

### Where the video comes from

The player uses the file GitHub Pages serves with the site, from `docs/videos/`, so it plays inline on the card. There is also an "Open video file" link.

Do not store these files with Git LFS. GitHub Pages would serve the pointer text instead of the video. If a render is too large to commit, set `video` to an `https://` URL and the same player will use that address.

`scripts/validate_catalog.py` rejects a `video` or `source` path that does not exist, a duplicate `id`, and a catalog that is not valid JSON.

## Publish on GitHub Pages

[`.github/workflows/pages.yml`](.github/workflows/pages.yml) deploys the `docs/` directory with GitHub Actions. The site can be published only after Pages is switched on for the repository. This change is a GitHub setting, and it is not stored in the repository:

1. Merge this work to `main`.
2. Open **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.

The next push to `main`, or **Actions → Pages → Run workflow**, publishes the library at:

https://guylemon.github.io/manim-animations/

No custom domain is configured. A file named `docs/.nojekyll` is included so the same folder also works if the source is later changed to "Deploy from a branch" with branch `main` and folder `/docs`.

## What is listed today

[GRO-35](https://linear.app/gl-grokbots/issue/GRO-35/kinematic-rotation-of-abc-about-a-point-on-line-l), the kinematic rotation of the plane about a point on a line, is the film in the catalog. Its scene is [`scenes/kinematic_rotation.py`](scenes/kinematic_rotation.py) and the render served by the library is [`docs/videos/gro-35-kinematic-rotation.mp4`](docs/videos/gro-35-kinematic-rotation.mp4).
