"""
agent.py
Purpose: Core chat agent with Claude API integration for interactive professional profile
Author: Gregory E. Schwartz (gregory.e.schwartz@gmail.com)
Date: 2026-01-06
"""

import os
import json
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


class AgenticProfileAgent:
    """Interactive AI agent representing a professional profile."""

    def __init__(self, profile_path: str = "profile.yaml"):
        """Initialize the agent with profile data and Claude API."""
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

    def chat(self, user_message: str) -> str:
        """Process user message and return agent response."""
        if not self.client:
            return "Error: Claude API not configured. Set ANTHROPIC_API_KEY in .env file."

        self.history.append({"role": "user", "content": user_message})

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=self.system_prompt,
                messages=self.history
            )

            assistant_message = response.content[0].text

            try:
                parsed = json.loads(assistant_message)
                return self._handle_response(parsed)
            except json.JSONDecodeError:
                self.history.append({"role": "assistant", "content": assistant_message})
                return assistant_message

        except Exception as error:
            return f"Error communicating with Claude: {str(error)}"

    def _handle_response(self, parsed: dict) -> str:
        """Route parsed JSON response to appropriate handler."""
        response_type = parsed.get('type', 'reply')

        if response_type == 'reply':
            return self._handle_reply(parsed)
        elif response_type == 'log_lead':
            return self._handle_lead_log(parsed)
        else:
            return str(parsed)

    def _handle_reply(self, parsed: dict) -> str:
        """Handle standard reply response."""
        message = parsed.get('message', '')
        if not message:
            message = "I didn't generate a proper response. Could you rephrase?"

        self.history.append({"role": "assistant", "content": json.dumps(parsed)})
        return message

    def _handle_lead_log(self, parsed: dict) -> str:
        """Handle lead logging response with optional Google Sheets integration."""
        company = parsed.get('company')
        contact_name = parsed.get('contact_name')
        contact_email = parsed.get('contact_email')
        role_title = parsed.get('role_title')
        notes = parsed.get('notes', '')

        if self.sheets_configured:
            result = append_lead_to_sheet(
                company, contact_name, contact_email, role_title, notes
            )
        else:
            result = simulate_lead_logging(
                company, contact_name, contact_email, role_title, notes
            )

        email = self.profile.get('contact', {}).get('email', 'gregory.e.schwartz@gmail.com')

        if result['status'] == 'ok':
            confirmation = f"I've logged your interest! You can reach me at {email}. Looking forward to connecting!"
        else:
            confirmation = f"I tried to log this follow-up but encountered an issue. Please reach out directly at {email}."

        self.history.append({"role": "assistant", "content": json.dumps(parsed)})
        return confirmation

    def reset_conversation(self):
        """Clear conversation history."""
        self.history = []

    def get_quick_intro(self) -> str:
        """Return a brief introduction based on profile data."""
        headline = self.profile.get('headline', '')
        summary = self.profile.get('summary', '')

        # extract first sentence of summary
        first_sentence = summary.split('.')[0] + '.' if summary else ''

        return f"{self.name}\n{headline}\n\n{first_sentence}"
