"""
Плейсхолдер под Google Calendar.
Когда будешь готов, установи:
  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

Создай creds (OAuth client ID) и положи client_secret.json рядом с tasks.db.
Первый запуск откроет браузер для авторизации и создаст token.json.
"""

from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timedelta

try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle, os.path
    HAVE_GOOGLE = True
except Exception:
    HAVE_GOOGLE = False

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def _service():
    if not HAVE_GOOGLE:
        return None
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)
    return build("calendar", "v3", credentials=creds)

def list_events_for_day(day: datetime) -> List[dict]:
    srv = _service()
    if not srv: return []
    start = day.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    end = (day + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    events = srv.events().list(calendarId="primary", timeMin=start, timeMax=end, singleEvents=True, orderBy="startTime").execute()
    return events.get("items", [])

def create_event(title: str, start: datetime, end: datetime, description: str = "") -> Optional[str]:
    srv = _service()
    if not srv: return None
    body = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start.isoformat()},
        "end": {"dateTime": end.isoformat()},
    }
    e = srv.events().insert(calendarId="primary", body=body).execute()
    return e.get("id")
