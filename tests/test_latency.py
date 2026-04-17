"""
test_latency.py
Live test that prompt caching is actually wired — checks usage.cache_read_input_tokens
on the second request, which is the authoritative signal from the API.
Wall-clock latency is too noisy to assert on; token accounting is deterministic.
"""

import pytest

from agent import AgenticProfileAgent, MAX_TOKENS, MODEL_ID


@pytest.mark.live
def test_cache_read_tokens_on_second_call(live_api_key, profile_path):
    """Second identical request should report >0 cache_read_input_tokens."""
    agent = AgenticProfileAgent(profile_path)

    first = agent.client.messages.create(
        model=MODEL_ID,
        max_tokens=16,
        system=agent._system_blocks(),
        messages=[{"role": "user", "content": "hi"}],
    )
    first_cache_write = getattr(first.usage, "cache_creation_input_tokens", 0) or 0
    first_cache_read = getattr(first.usage, "cache_read_input_tokens", 0) or 0

    second = agent.client.messages.create(
        model=MODEL_ID,
        max_tokens=16,
        system=agent._system_blocks(),
        messages=[{"role": "user", "content": "hello"}],
    )
    second_cache_read = getattr(second.usage, "cache_read_input_tokens", 0) or 0

    print(
        f"\nfirst: cache_write={first_cache_write} cache_read={first_cache_read} | "
        f"second: cache_read={second_cache_read}"
    )

    # First request should either write the cache or read from a pre-existing one.
    assert first_cache_write > 0 or first_cache_read > 0, (
        "prompt caching not wired — no cache tokens on first call"
    )
    # Second identical system-prompt request must read from cache.
    assert second_cache_read > 0, (
        f"second call did not read from cache (got {second_cache_read} tokens)"
    )
