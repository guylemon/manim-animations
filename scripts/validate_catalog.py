#!/usr/bin/env python3
"""Check docs/catalog.json before the animation library is published."""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CATALOG = DOCS / "catalog.json"
ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
STATUSES = {"ready", "upcoming"}
SITE_FILES = ("index.html", "styles.css", "app.js", "catalog.json")


def main() -> int:
    errors = [f"docs/{name} is missing" for name in SITE_FILES if not (DOCS / name).is_file()]
    app = DOCS / "app.js"
    if app.is_file() and "catalog.json" not in app.read_text(encoding="utf-8"):
        errors.append("docs/app.js does not load catalog.json")

    data = None
    if CATALOG.is_file():
        try:
            data = json.loads(CATALOG.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"docs/catalog.json is not valid JSON: {exc}")
    if data is not None:
        errors.extend(validate_data(data, ROOT, DOCS))

    if errors:
        print("Catalog validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    count = len(data.get("animations", [])) if isinstance(data, dict) else 0
    print(f"Catalog OK: {count} animation(s).")
    return 0


def validate_data(data: object, root: Path, docs: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["catalog root must be an object"]

    for key in ("title", "animations"):
        if key not in data:
            errors.append(f"missing top-level {key!r}")

    animations = data.get("animations", [])
    if not isinstance(animations, list):
        errors.append("'animations' must be a list")
        return errors

    seen: set[str] = set()
    for index, item in enumerate(animations):
        where = f"animations[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            continue
        for key in ("id", "title", "description", "topic"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{where}.{key} must be a non-empty string")

        anim_id = item.get("id")
        if isinstance(anim_id, str):
            if not ID_RE.fullmatch(anim_id):
                errors.append(f"{where}.id must be lowercase letters, numbers, and hyphens")
            elif anim_id in seen:
                errors.append(f"duplicate id {anim_id!r}")
            else:
                seen.add(anim_id)

        status = item.get("status", "ready")
        if status not in STATUSES:
            errors.append(f"{where}.status must be 'ready' or 'upcoming'")

        for key in ("chapter", "issueId"):
            if key in item and item[key] is not None and not isinstance(item[key], str):
                errors.append(f"{where}.{key} must be a string or null")

        if item.get("date") not in (None, ""):
            date = item.get("date")
            if not isinstance(date, str) or not DATE_RE.fullmatch(date):
                errors.append(f"{where}.date must be YYYY-MM-DD")
            else:
                try:
                    dt.date.fromisoformat(date)
                except ValueError:
                    errors.append(f"{where}.date is not a real date")

        video = item.get("video")
        if video not in (None, ""):
            if isinstance(video, str):
                check_site_path(video, f"{where}.video", docs, errors)
            elif isinstance(video, dict):
                if not any(video.get(key) for key in ("mp4", "webm")):
                    errors.append(f"{where}.video needs an mp4 or webm path")
                for key in ("mp4", "webm", "poster"):
                    if video.get(key):
                        check_site_path(str(video[key]), f"{where}.video.{key}", docs, errors)
            else:
                errors.append(f"{where}.video must be a string, object, or null")

        source = item.get("source")
        if source not in (None, ""):
            if not isinstance(source, str):
                errors.append(f"{where}.source must be a string or null")
            else:
                check_repo_path(source, f"{where}.source", root, errors)

        issue = item.get("issue")
        if issue not in (None, ""):
            if not isinstance(issue, str) or not issue.startswith(("https://", "http://")):
                errors.append(f"{where}.issue must be an http(s) URL or null")

    return errors


def check_site_path(path: str, label: str, docs: Path, errors: list[str]) -> None:
    if path.startswith(("https://", "http://")):
        return
    relative = safe_relative(path)
    if relative is None:
        errors.append(f"{label}: use a docs/-relative path or an https URL, not {path!r}")
        return
    if not (docs / relative).is_file():
        errors.append(f"{label}: file not found at docs/{relative.as_posix()}")


def check_repo_path(path: str, label: str, root: Path, errors: list[str]) -> None:
    if path.startswith(("https://", "http://")):
        return
    relative = safe_relative(path)
    if relative is None:
        errors.append(f"{label}: use a repository-relative path or an https URL, not {path!r}")
        return
    if not (root / relative).is_file():
        errors.append(f"{label}: file not found at {relative.as_posix()}")


def safe_relative(path: str) -> Path | None:
    if path.startswith(("/", "\\")) or "\\" in path:
        return None
    parts = Path(path).parts
    if any(part == ".." for part in parts):
        return None
    return Path(*parts) if parts else None


if __name__ == "__main__":
    sys.exit(main())
