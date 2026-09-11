"""Read-only presentation audit; run: python tools/check_presentation.py REPO TITLE SLUG.

Checks local documentation, anchors and the conceptual SVG. Not a Markdown
standard validator, external-link crawler or scientific validation.
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

root = Path(sys.argv[1]).resolve()
title, slug = sys.argv[2:4]
paths = [root / p for p in ("README.md", "docs/START_HERE.md",
         "docs/REPOSITORY_IDENTITY.md", "CONTRIBUTING.md")]
if (root / "docs/data-and-figures.md").exists():
    paths.append(root / "docs/data-and-figures.md")
issues, checked, external = [], [], set()

def without_code(text):
    return re.sub(r"(?ms)^[ ]{0,3}(\x60{3,}|~{3,}).*?^\1[ \t]*$", "", text)

def anchors(path):
    text = without_code(path.read_text())
    found = set(re.findall(r"(?:id|name)=[\"']([^\"']+)[\"']", text))
    seen = {}
    for heading in re.findall(r"(?m)^#{1,6}\s+(.+?)(?:\s+#+)?$", text):
        heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading)
        heading = re.sub(r"<[^>]*>", "", html.unescape(heading)).lower()
        name = re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")
        count = seen.get(name, 0)
        seen[name] = count + 1
        found.add(name + (f"-{count}" if count else ""))
    return found

for path in paths:
    if not path.is_file():
        issues.append(f"Missing document: {path.relative_to(root)}")
        continue
    scrubbed = without_code(path.read_text())
    links = re.findall(r"\]\((<[^>]+>|[^\s)]+)(?:\s+[\"'][^)]*)?\)", scrubbed)
    links += re.findall(r"(?:href|src)=[\"']([^\"']+)[\"']", scrubbed)
    links += re.findall(r"(?m)^\s*\[[^]]+\]:\s*(\S+)", scrubbed)
    for link in links:
        link = html.unescape(link.strip("<>"))
        parsed = urlsplit(link)
        if parsed.scheme in ("http", "https", "mailto"):
            external.add(link)
            continue
        if parsed.scheme:
            issues.append(f"{path.relative_to(root)}: unsupported scheme {link}")
            continue
        target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        if not target.exists():
            issues.append(f"{path.relative_to(root)}: missing {link}")
            continue
        if parsed.fragment and target.is_file() and target.suffix.lower() == ".md":
            if unquote(parsed.fragment) not in anchors(target):
                issues.append(f"{path.relative_to(root)}: missing anchor {link}")
        checked.append(link)
    if "example.com" in scrubbed or "github_username" in scrubbed:
        issues.append(f"{path.relative_to(root)}: template placeholder present")

readme = (root / "README.md").read_text()
if readme.splitlines()[0] != "# " + title:
    issues.append("README heading does not match canonical title")
expected = f"https://github.com/500ft/{slug}/actions/workflows/ci.yml/badge.svg?branch=main"
if expected not in readme:
    issues.append("README CI badge is not bound to renamed main")
for image_alt in re.findall(r"!\[([^]]*)\]\(", readme):
    if not image_alt.strip():
        issues.append("README image has empty alternative text")
svg = root / "docs/media/project-overview.svg"
try:
    tree = ET.parse(svg)
    ns = "{http://www.w3.org/2000/svg}"
    if not tree.findtext(ns + "title") or not tree.findtext(ns + "desc"):
        issues.append("Conceptual SVG is missing title/description")
    if tree.findall(".//" + ns + "script"):
        issues.append("Conceptual SVG contains script")
except (ET.ParseError, FileNotFoundError) as exc:
    issues.append(f"Invalid SVG: {exc}")
result = {"repository": slug, "files_checked": len(paths),
          "local_links_checked": len(checked),
          "external_links_not_fetched": len(external), "issues": issues,
          "scientific_validation": False}
print(json.dumps(result, indent=2))
raise SystemExit(bool(issues))
