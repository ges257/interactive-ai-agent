"""
test_profile.py
Unit tests for profile.yaml schema + v41 content sanity.
"""

import yaml
from tools import load_profile, get_profile_as_yaml_string


def test_profile_loads(profile_path):
    profile = load_profile(profile_path)
    assert isinstance(profile, dict)
    assert profile["name"] == "Gregory Evan Schwartz"


def test_required_top_level_keys(profile_path):
    profile = load_profile(profile_path)
    for key in ("name", "headline", "location", "contact", "summary",
                "education", "experience", "publications", "skills"):
        assert key in profile, f"missing required key: {key}"


def test_contact_email(profile_path):
    profile = load_profile(profile_path)
    assert profile["contact"]["email"] == "gregory.e.schwartz@gmail.com"


def test_v41_has_agent_systems_category(profile_path):
    """v41 adds a new experience category; make sure it's present."""
    profile = load_profile(profile_path)
    categories = {
        entry.get("category") for entry in profile["experience"]
        if entry.get("category")
    }
    assert "Agent Systems Engineering" in categories


def test_v41_has_glass_build_team(profile_path):
    profile = load_profile(profile_path)
    names = []
    for entry in profile["experience"]:
        for project in entry.get("projects", []) or []:
            names.append(project.get("name", ""))
    assert any("GLASS Build Team" in n for n in names)


def test_v41_has_governance_enforcer(profile_path):
    profile = load_profile(profile_path)
    flat_text = get_profile_as_yaml_string(profile_path)
    assert "Claude Governance Enforcer" in flat_text


def test_v41_inferred_applied_ai_bullets_removed(profile_path):
    """The three inferred projects should be out of Applied AI."""
    profile = load_profile(profile_path)
    applied_ai_names = []
    for entry in profile["experience"]:
        if entry.get("category") == "Applied AI":
            for project in entry.get("projects", []) or []:
                applied_ai_names.append(project.get("name", ""))
    for removed in ("SEC 10-K", "Synthetic Data Engine (Market)",
                    "GLASS (Doc"):
        assert not any(removed in n for n in applied_ai_names), (
            f"{removed!r} should have been removed from Applied AI"
        )


def test_summary_includes_new_keywords(profile_path):
    profile = load_profile(profile_path)
    summary = profile["summary"]
    for keyword in ("multi-agent orchestration",
                    "agentic build pipelines",
                    "knowledge-graph reasoning",
                    "LLM safety and governance engineering"):
        assert keyword in summary, f"missing keyword in summary: {keyword!r}"


def test_source_comment_updated(profile_path):
    """Top-of-file comment should reference v41, not v25."""
    with open(profile_path, encoding="utf-8") as f:
        first_lines = "".join(f.readline() for _ in range(4))
    assert "v41" in first_lines
    assert "v25" not in first_lines


def test_pdf_asset_shipped(pdf_path):
    assert pdf_path.exists(), f"v41 PDF missing at {pdf_path}"
    assert pdf_path.stat().st_size > 50_000
