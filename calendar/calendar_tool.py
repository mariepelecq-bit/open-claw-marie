#!/usr/bin/env python3
"""
Google Calendar tool for OpenClaw
Usage:
  python3 calendar_tool.py list [--days 7]
  python3 calendar_tool.py add --title "..." --date "2026-03-20" [--time "14:00"] [--duration 60] [--description "..."]
"""
import sys
import os
import json
import argparse
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from google.oauth2 import service_account

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "../analytics/credentials/service-account.json")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)

CALENDAR_ID = "mariepelecqav@gmail.com"

def get_calendar_id(service):
    return CALENDAR_ID

JOURS_FR = {0:'Lun',1:'Mar',2:'Mer',3:'Jeu',4:'Ven',5:'Sam',6:'Dim'}

def list_events(days=7):
    service = get_service()
    cal_id = get_calendar_id(service)
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)
    
    events_result = service.events().list(
        calendarId=cal_id,
        timeMin=now.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    
    events = events_result.get("items", [])
    
    if not events:
        return f"📅 Aucun événement dans les {days} prochains jours."
    
    lines = [f"📅 Agenda — {days} prochains jours :\n"]
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date", ""))
        if "T" in start:
            dt = datetime.fromisoformat(start)
            date_str = f"{JOURS_FR[dt.weekday()]} {dt.strftime('%d/%m à %H:%M')}"
        else:
            dt = datetime.fromisoformat(start)
            date_str = f"{JOURS_FR[dt.weekday()]} {dt.strftime('%d/%m')} (journée)"
        summary = e.get("summary", "(sans titre)")
        lines.append(f"• {date_str} — {summary}")
    
    return "\n".join(lines)

def add_event(title, date_str, time_str=None, duration=60, description=None):
    service = get_service()
    cal_id = get_calendar_id(service)
    
    if time_str:
        start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=duration)
        event = {
            "summary": title,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Paris"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "Europe/Paris"},
        }
    else:
        event = {
            "summary": title,
            "start": {"date": date_str},
            "end": {"date": date_str},
        }
    
    if description:
        event["description"] = description
    
    result = service.events().insert(calendarId=cal_id, body=event).execute()
    return f"✅ Événement ajouté : **{title}** le {date_str}" + (f" à {time_str}" if time_str else "")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    
    list_p = subparsers.add_parser("list")
    list_p.add_argument("--days", type=int, default=7)
    
    add_p = subparsers.add_parser("add")
    add_p.add_argument("--title", required=True)
    add_p.add_argument("--date", required=True)
    add_p.add_argument("--time")
    add_p.add_argument("--duration", type=int, default=60)
    add_p.add_argument("--description")
    
    args = parser.parse_args()
    
    if args.command == "list":
        print(list_events(args.days))
    elif args.command == "add":
        print(add_event(args.title, args.date, args.time, args.duration, args.description))
    else:
        parser.print_help()
