import copy
import json
from pathlib import Path

import pytest

from catanroads.site_worksheet import render, ROOT, OUTPUT


def manifest():
    return json.loads((ROOT / "config/sites.geojson").read_text())


def test_development_sheet_excludes_untouched_holdout():
    document = render(manifest())
    assert "dev-01-braided" in document and "negative-01" in document
    assert "confound-01" in document
    assert "holdout-01" not in document
    assert "98.2" not in document
    assert document.count("ref_imagery_date") == 6  # intro + five individual forms


def test_manifest_is_not_mutated_or_promoted():
    original = manifest()
    snapshot = copy.deepcopy(original)
    render(original)
    assert original == snapshot
    assert all(x["properties"]["verified"] is False for x in original["features"])


def test_new_nonholdout_site_is_not_lost():
    original = manifest()
    extra = copy.deepcopy(original["features"][0])
    extra["properties"]["id"] = "new-development"
    original["features"].append(extra)
    assert "new-development" in render(original)


def test_duplicate_site_ids_are_rejected():
    original = manifest()
    original["features"].append(original["features"][0])
    with pytest.raises(ValueError):
        render(original)


def test_committed_sheet_matches():
    assert OUTPUT.read_text() == render(manifest())
