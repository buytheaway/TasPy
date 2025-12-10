from __future__ import annotations

import pickle
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from google.auth.transport.requests import Request  # type: ignore[import]
from google.oauth2.credentials import Credentials  # type: ignore[import]
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]
from googleapiclient.discovery import build  # type: ignore[import]


SCOPES = [\"https://www.googleapis.com/auth/calendar\"]

# Ожидаем, что client_secret.json лежит в корне проекта рядом с tasks.db
BASE_DIR = Path(__file__).resolve().parents[2]
CLIENT_SECRET_FILE = BASE_DIR / \"client_secret.json\"
TOKEN_FILE = BASE_DIR / \"token.pickle\"


@dataclass
class CalendarEvent:
    id: str
    summary: str
    start: datetime
    end: datetime
    description: str = \"\"


def _ensure_credentials() -> Credentials:
    if not CLIENT_SECRET_FILE.exists():
        raise FileNotFoundError(
            f\"Не найден {CLIENT_SECRET_FILE}. Скачай OAuth client (Desktop app) в Google Cloud Console.\"
        )

    creds: Optional[Credentials] = None
    if TOKEN_FILE.exists():
        with TOKEN_FILE.open(\"rb\") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_FILE),
                SCOPES,
            )
            creds = flow.run_local_server(port=0)
        with TOKEN_FILE.open(\"wb\") as f:
            pickle.dump(creds, f)

    return creds


def get_calendar_service():
    \"\"\"Создать клиент Google Calendar API (v3).\"\"\"
    creds = _ensure_credentials()
    service = build(\"calendar\", \"v3\", credentials=creds)
    return service


def list_events_for_day(day: datetime, calendar_id: str = \"primary\") -> List[CalendarEvent]:
    \"\"\"Получить события за конкретный день (по локальному времени).\"\"\"
    service = get_calendar_service()

    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    time_min = start.isoformat()
    time_max = end.isoformat()

    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy=\"startTime\",
        )
        .execute()
    )
    items = events_result.get(\"items\", [])

    result: List[CalendarEvent] = []
    for ev in items:
        start_str = ev[\"start\"].get(\"dateTime\") or ev[\"start\"].get(\"date\")
        end_str = ev[\"end\"].get(\"dateTime\") or ev[\"end\"].get(\"date\")
        if start_str is None or end_str is None:
            continue
        # datetime.fromisoformat понимает 2024-01-01T10:00:00+03:00
        start_dt = datetime.fromisoformat(start_str)
        end_dt = datetime.fromisoformat(end_str)
        result.append(
            CalendarEvent(
                id=ev.get(\"id\", \"\"),
                summary=ev.get(\"summary\", \"(без названия)\"),
                start=start_dt,
                end=end_dt,
                description=ev.get(\"description\", \"\"),
            )
        )
    return result


def create_event(
    title: str,
    start: datetime,
    end: Optional[datetime] = None,
    description: str = \"\",
    calendar_id: str = \"primary\",
) -> Optional[str]:
    \"\"\"Создать событие в Google Calendar из задачи.

    Возвращает ID события или None при ошибке.
    \"\"\"
    service = get_calendar_service()
    if end is None:
        end = start + timedelta(hours=1)

    event_body = {
        \"summary\": title,
        \"description\": description,
        \"start\": {
            \"dateTime\": start.isoformat(),
        },
        \"end\": {
            \"dateTime\": end.isoformat(),
        },
    }

    try:
        created = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        return created.get(\"id\")
    except Exception as exc:  # pylint: disable=broad-except
        # Тут можно прикрутить нормальный логгер, пока просто print
        print(\"[Google Calendar] Ошибка при создании события:\", exc)
        return None
