"""
agent.py
Purpose: Core chat agent with Claude API integration for interactive professional profile
Author: Gregory E. Schwartz (gregory.e.schwartz@gmail.com)
Date: 2026-04-17
"""

import os
import json
import re
from typing import Iterator
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from tools import (
    load_profile,
    get_profile_as_yaml_string,
    append_lead_to_sheet,
    simulate_lead_logging
)
from prompts import build_system_prompt


MODEL_ID = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 1024
LEAD_LOG_PATTERN = re.compile(r"\[\[LEAD_LOG\]\]\s*(\{.*?\})\s*$", re.DOTALL)


class AgenticProfileAgent:
    """Interactive AI agent representing a professional profile."""

    def __init__(self, profile_path: str = "profile.yaml"):
        self.profile_path = profile_path
        self.profile = load_profile(profile_path)
        self.profile_yaml = get_profile_as_yaml_string(profile_path)
        self.name = self.profile.get('name', 'Unknown')

        self.system_prompt = build_system_prompt(self.profile_yaml, self.name)

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or Anthropic is None:
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)

        self.history = []
        self.sheets_configured = bool(os.getenv('GOOGLE_SHEETS_ID'))

    def _system_blocks(self):
        """System prompt packaged for prompt caching (ephemeral cache)."""
        return [
            {
                "type": "text",
                "text": self.system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    def chat(self, user_message: str) -> str:
        """Non-streaming chat — used by example-question buttons."""
        if not self.client:
            return "Error: Claude API not configured. Set ANTHROPIC_API_KEY in .env file."

        self.history.append({"role": "user", "content": user_message})

        try:
            response = self.client.messages.create(
                model=MODEL_ID,
                max_tokens=MAX_TOKENS,
                system=self._system_blocks(),
                messages=self.history,
            )
            raw_text = response.content[0].text
        except Exception as error:
            self.history.pop()
            return f"Error communicating with Claude: {str(error)}"

        return self._finalize(raw_text)

    def chat_stream(self, user_message: str) -> Iterator[str]:
        """Streaming chat — yields text deltas suitable for st.write_stream.

        After the stream completes, the full text is parsed for a trailing
        [[LEAD_LOG]] marker; that line is stripped from the user-visible
        response and handled as a lead-logging side effect.
        """
        if not self.client:
            yield "Error: Claude API not configured. Set ANTHROPIC_API_KEY in .env file."
            return

        self.history.append({"role": "user", "content": user_message})
        buffered = []
        lead_marker_seen = False

        try:
            with self.client.messages.stream(
                model=MODEL_ID,
                max_tokens=MAX_TOKENS,
                system=self._system_blocks(),
                messages=self.history,
            ) as stream:
                for text_delta in stream.text_stream:
                    buffered.append(text_delta)
                    combined = "".join(buffered)
                    if "[[LEAD_LOG]]" in combined and not lead_marker_seen:
                        lead_marker_seen = True
                        visible_prefix = combined.split("[[LEAD_LOG]]")[0]
                        emitted = "".join(buffered[:-1])
                        tail_visible = visible_prefix[len(emitted):]
                        if tail_visible:
                            yield tail_visible
                    elif not lead_marker_seen:
                        yield text_delta
        except Exception as error:
            self.history.pop()
            yield f"\n\nError communicating with Claude: {str(error)}"
            return

        full_text = "".join(buffered)
        self._finalize(full_text, already_streamed=True)

    def _finalize(self, raw_text: str, already_streamed: bool = False) -> str:
        """Strip LEAD_LOG marker, handle lead-logging side effect, return clean text."""
        match = LEAD_LOG_PATTERN.search(raw_text)
        lead_json = None
        if match:
            visible_text = raw_text[: match.start()].rstrip()
            try:
                lead_json = json.loads(match.group(1))
            except json.JSONDecodeError:
                lead_json = None
        else:
            visible_text = raw_text.strip()

        self.history.append({"role": "assistant", "content": visible_text})

        if lead_json:
            self._log_lead(lead_json)

        return visible_text

    def _log_lead(self, parsed: dict) -> None:
        """Persist a captured lead via Google Sheets or the simulate fallback."""
        company = parsed.get('company')
        contact_name = parsed.get('contact_name')
        contact_email = parsed.get('contact_email')
        role_title = parsed.get('role_title')
        notes = parsed.get('notes', '')

        if self.sheets_configured:
            append_lead_to_sheet(company, contact_name, contact_email, role_title, notes)
        else:
            simulate_lead_logging(company, contact_name, contact_email, role_title, notes)

    def reset_conversation(self):
        """Clear conversation history."""
        self.history = []

    def get_quick_intro(self) -> str:
        """Return a brief introduction based on profile data."""
        headline = self.profile.get('headline', '')
        summary = self.profile.get('summary', '')
        first_sentence = summary.split('.')[0] + '.' if summary else ''
        return f"{self.name}\n{headline}\n\n{first_sentence}"
