"""
tools.py
Purpose: Utility functions for profile loading, email validation, and lead logging
Author: Gregory E. Schwartz (gregory.e.schwartz@gmail.com)
Date: 2026-01-06
"""

import os
import yaml
from datetime import datetime
from typing import Optional
from pathlib import Path

# google api is optional dependency
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False


def load_profile(profile_path: str = "profile.yaml") -> dict:
    """Load and parse the profile YAML file."""
    path = Path(profile_path)
    if not path.exists():
        raise FileNotFoundError(f"Profile file not found: {profile_path}")

    with open(path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    return data.get('profile', data)


def get_profile_as_yaml_string(profile_path: str = "profile.yaml") -> str:
    """Load profile and return as formatted YAML string for prompt injection."""
    with open(profile_path, 'r', encoding='utf-8') as file:
        return file.read()


def validate_email(email: str) -> bool:
    """Validate email format with basic structural checks."""
    if not email or not isinstance(email, str):
        return False

    if email.count('@') != 1:
        return False

    local_part, domain = email.split('@')

    if not local_part or len(local_part) < 1:
        return False

    if '.' not in domain:
        return False

    domain_parts = domain.split('.')
    if any(len(part) == 0 for part in domain_parts):
        return False

    # tld must have at least 2 characters
    if len(domain_parts[-1]) < 2:
        return False

    return True


def get_sheets_service():
    """Initialize and return Google Sheets API service."""
    if not GOOGLE_SHEETS_AVAILABLE:
        return None

    creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    if not Path(creds_file).exists():
        return None

    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = service_account.Credentials.from_service_account_file(
            creds_file, scopes=scopes
        )
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception:
        return None


def append_lead_to_sheet(
    company: Optional[str],
    contact_name: Optional[str],
    contact_email: Optional[str],
    role_title: Optional[str],
    notes: Optional[str]
) -> dict:
    """Append a lead row to the configured Google Sheet."""
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')

    if not sheet_id:
        return {'status': 'error', 'message': 'GOOGLE_SHEETS_ID not configured'}

    service = get_sheets_service()
    if not service:
        return {'status': 'error', 'message': 'Google Sheets service not available'}

    if contact_email and not validate_email(contact_email):
        return {'status': 'error', 'message': f'Invalid email format: {contact_email}'}

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [
        timestamp,
        company or '',
        contact_name or '',
        contact_email or '',
        role_title or '',
        notes or '',
        'New'
    ]

    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range='Leads!A:G',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [row]}
        ).execute()

        updates = result.get('updates', {})
        return {
            'status': 'ok',
            'message': 'Lead logged successfully',
            'row_number': updates.get('updatedRows', 1)
        }
    except Exception as error:
        return {'status': 'error', 'message': f'Failed to append: {str(error)}'}


def simulate_lead_logging(
    company: Optional[str],
    contact_name: Optional[str],
    contact_email: Optional[str],
    role_title: Optional[str],
    notes: Optional[str]
) -> dict:
    """Simulate lead logging when Google Sheets is not configured."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    lead_data = {
        'timestamp': timestamp,
        'company': company or 'N/A',
        'contact_name': contact_name or 'N/A',
        'contact_email': contact_email or 'N/A',
        'role_title': role_title or 'N/A',
        'notes': notes or 'N/A',
        'status': 'New'
    }

    return {
        'status': 'ok',
        'message': 'Lead logged (simulation mode)',
        'simulated': True,
        'data': lead_data
    }
