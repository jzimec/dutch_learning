#!/usr/bin/env python3
"""Extract inline CSS/JS from index.html without touching course data or markup.
Run on a clean working tree, review the diff, and test before committing.
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
index = root / "index.html"
original = index.read_text(encoding="utf-8")
if original.count("<style>") != 1 or original.count("</style>") != 1:
    sys.exit("Expected exactly one plain <style> block; no changes made.")
styles = re.search(r"<style>(.*?)</style>", original, re.S)
if not styles:
    sys.exit("CSS block not found; no changes made.")
css_path = root / "assets" / "styles.css"
if css_path.exists():
    sys.exit("assets/styles.css exists; no changes made.")
updated = original[:styles.start()] + '<link rel="stylesheet" href="./assets/styles.css">' + original[styles.end():]
# Keep JS and embedded course data in place until their dependency order is audited.
if len(updated) >= len(original):
    sys.exit("No size reduction; no changes made.")
css_path.parent.mkdir(parents=True, exist_ok=True)
css_path.write_text(styles.group(1), encoding="utf-8")
index.write_text(updated, encoding="utf-8")
print(f"Extracted CSS: {len(styles.group(1)):,} characters")
print(f"index.html: {len(original):,} -> {len(updated):,} characters")
print("Review diff, run app regression checks, and commit only if verified.")
