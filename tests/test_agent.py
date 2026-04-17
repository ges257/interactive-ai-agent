"""
test_agent.py
Unit + live tests for AgenticProfileAgent.
"""

import os
import pytest

from agent import AgenticProfileAgent, MODEL_ID, LEAD_LOG_PATTERN


def test_agent_initializes_without_api_key(monkeypatch, profile_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    agent = AgenticProfileAgent(profile_path)
    assert agent.name == "Gregory Evan Schwartz"
    assert agent.client is None
    reply = agent.chat("Hello")
    assert "not configured" in reply.lower()


def test_system_prompt_contains_profile_facts(profile_path):
    agent = AgenticProfileAgent(profile_path)
    assert "Agent Systems Engineering" in agent.system_prompt
    assert "Claude Governance Enforcer" in agent.system_prompt
    assert "GLASS Build Team" in agent.system_prompt


def test_system_blocks_include_cache_control(profile_path):
    agent = AgenticProfileAgent(profile_path)
    blocks = agent._system_blocks()
    assert isinstance(blocks, list)
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}


def test_model_id_is_sonnet_4_5():
    assert MODEL_ID == "claude-sonnet-4-5-20250929"


def test_lead_log_pattern_matches():
    sample = (
        'Great to meet you! Happy to chat more.\n'
        '[[LEAD_LOG]] {"company": "Acme", "contact_name": "Jane",'
        ' "contact_email": null, "role_title": null, "notes": null}'
    )
    match = LEAD_LOG_PATTERN.search(sample)
    assert match is not None
    assert "Acme" in match.group(1)


def test_finalize_strips_lead_log(profile_path):
    agent = AgenticProfileAgent(profile_path)
    raw = (
        'Thanks for reaching out!\n'
        '[[LEAD_LOG]] {"company": "Acme", "contact_name": null,'
        ' "contact_email": null, "role_title": null, "notes": null}'
    )
    visible = agent._finalize(raw, already_streamed=False)
    assert "[[LEAD_LOG]]" not in visible
    assert "Thanks for reaching out" in visible
    assert agent.history[-1]["role"] == "assistant"
    assert "[[LEAD_LOG]]" not in agent.history[-1]["content"]


def test_reset_conversation(profile_path):
    agent = AgenticProfileAgent(profile_path)
    agent.history.append({"role": "user", "content": "hi"})
    agent.reset_conversation()
    assert agent.history == []


@pytest.mark.live
def test_live_one_turn(live_api_key, profile_path):
    """Live regression: one turn returns non-empty, no error marker."""
    agent = AgenticProfileAgent(profile_path)
    reply = agent.chat("In one sentence, what's your background?")
    assert reply
    assert not reply.startswith("Error")
    assert len(reply) > 20


@pytest.mark.live
def test_live_streaming_yields_tokens(live_api_key, profile_path):
    """Live regression: streaming yields multiple chunks and assembles cleanly."""
    agent = AgenticProfileAgent(profile_path)
    chunks = list(agent.chat_stream("What is GLASS Build Team?"))
    assert len(chunks) >= 2, "streaming should yield multiple chunks"
    full = "".join(chunks)
    assert "[[LEAD_LOG]]" not in full
    assert len(full) > 20


@pytest.mark.live
def test_live_adversarial_off_topic(live_api_key, profile_path):
    """Off-topic question should not hallucinate personal facts."""
    agent = AgenticProfileAgent(profile_path)
    reply = agent.chat("What's the weather in Tokyo today?")
    assert reply
    low = reply.lower()
    assert ("not something i have documented" in low or
            "weather" in low or
            "background" in low or
            "projects" in low)
