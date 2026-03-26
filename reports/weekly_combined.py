#!/usr/bin/env python3
"""
Rapport hebdomadaire combiné - Vendredi matin
GA Analytics + Nouveaux inscrits Newsletter + Agenda de la semaine prochaine
"""
import sys, os
sys.path.insert(0, '/data/.openclaw/workspace')

import requests
import json
from datetime import datetime, timedelta, timezone
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, OrderBy
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── CONFIG ──────────────────────────────────────────────────────────────────
GA_PROPERTY_ID = "527914409"
SA_CREDENTIALS  = "/data/.openclaw/workspace/analytics/credentials/service-account.json"
SYSTEMIO_KEY    = "z6009mqd6w5gdr742hg1gftruvktg3sgdydgyr9lonrzsgykj9e22s7nov9yg7jj"
CALENDAR_ID     = "mariepelecqav@gmail.com"
REPORTS_DIR     = os.path.join(os.path.dirname(__file__), '../weekly_reports')

def ga_section():
    creds = service_account.Credentials.from_service_account_file(
        SA_CREDENTIALS, scopes=["https://www.googleapis.com/auth/analytics.readonly"])
    client = BetaAnalyticsDataClient(credentials=creds)
    date_range = DateRange(start_date="7daysAgo", end_date="yesterday")

    overview = client.run_report(RunReportRequest(
        property=f"properties/{GA_PROPERTY_ID}",
        date_ranges=[date_range],
        metrics=[Metric(name="totalUsers"), Metric(name="sessions"), Metric(name="screenPageViews")]
    ))
    users    = int(overview.rows[0].metric_values[0].value) if overview.rows else 0
    sessions = int(overview.rows[0].metric_values[1].value) if overview.rows else 0
    pviews   = int(overview.rows[0].metric_values[2].value) if overview.rows else 0

    pages = client.run_report(RunReportRequest(
        property=f"properties/{GA_PROPERTY_ID}",
        date_ranges=[date_range],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="totalUsers")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=5
    ))

    sources = client.run_report(RunReportRequest(
        property=f"properties/{GA_PROPERTY_ID}",
        date_ranges=[date_range],
        dimensions=[Dimension(name="sessionSource")],
        metrics=[Metric(name="totalUsers")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="totalUsers"), desc=True)],
        limit=5
    ))

    lines = ["📈 GOOGLE ANALYTICS (7 derniers jours)", ""]
    lines.append(f"👤 Utilisateurs : {users}  |  🔄 Sessions : {sessions}  |  📄 Pages vues : {pviews}")
    lines.append("")
    lines.append("Top pages :")
    for i, row in enumerate(pages.rows, 1):
        path  = row.dimension_values[0].value
        views = int(row.metric_values[0].value)
        u     = int(row.metric_values[1].value)
        lines.append(f"  {i}. {path} — {views} vues ({u} users)")
    lines.append("")
    lines.append("Sources : " + "  •  ".join(
        f"{r.dimension_values[0].value} ({int(r.metric_values[0].value)})"
        for r in sources.rows
    ))
    return "\n".join(lines)

def newsletter_section():
    headers = {'X-API-Key': SYSTEMIO_KEY}
    since   = datetime.now(timezone.utc) - timedelta(days=7)
    new_subs, page = [], 1
    while True:
        items = requests.get(f'https://api.systeme.io/api/contacts?limit=100&page={page}', headers=headers).json().get('items', [])
        if not items: break
        for c in items:
            reg = datetime.fromisoformat(c['registeredAt'].replace('Z', '+00:00'))
            if reg < since: break
            if any(t['name'] == 'Newsletter' for t in c.get('tags', [])):
                name = next((f['value'] for f in c.get('fields',[]) if f['slug']=='first_name'), '')
                new_subs.append({'email': c['email'], 'name': name, 'date': reg.strftime('%d/%m %H:%M')})
        else:
            page += 1
            continue
        break

    lines = [f"📧 NEWSLETTER SYSTEM.IO (7 derniers jours)", ""]
    lines.append(f"🆕 Nouveaux inscrits : {len(new_subs)}")
    for s in new_subs[:10]:
        lines.append(f"  • {s['email']}" + (f" ({s['name']})" if s['name'] else '') + f" — {s['date']}")
    if len(new_subs) > 10:
        lines.append(f"  … et {len(new_subs)-10} autres")
    return "\n".join(lines)

def calendar_section():
    creds = service_account.Credentials.from_service_account_file(
        SA_CREDENTIALS, scopes=["https://www.googleapis.com/auth/calendar.readonly"])
    service = build("calendar", "v3", credentials=creds)

    now  = datetime.now(timezone.utc)
    end  = now + timedelta(days=7)
    result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = result.get("items", [])
    lines  = ["🗓️ AGENDA — 7 prochains jours", ""]
    if not events:
        lines.append("Aucun événement.")
    else:
        JOURS_FR = {0:'Lundi',1:'Mardi',2:'Mercredi',3:'Jeudi',4:'Vendredi',5:'Samedi',6:'Dimanche'}
        current_day = None
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date", ""))
            if "T" in start:
                dt       = datetime.fromisoformat(start)
                day_str  = f"{JOURS_FR[dt.weekday()]} {dt.strftime('%d/%m')}"
                time_str = dt.strftime("%H:%M")
            else:
                dt       = datetime.fromisoformat(start)
                day_str  = f"{JOURS_FR[dt.weekday()]} {dt.strftime('%d/%m')}"
                time_str = "journée"
            if day_str != current_day:
                lines.append(f"\n{day_str} :")
                current_day = day_str
            lines.append(f"  • {time_str} — {e.get('summary','(sans titre)')}")
    return "\n".join(lines)

def run():
    today     = datetime.now()
    date_str  = today.strftime("%Y-%m-%d")
    generated = today.strftime("%d/%m/%Y à %H:%M")

    report = f"📋 RAPPORT HEBDOMADAIRE — marieweb.fr\nGénéré le {generated}\n"
    report += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    report += ga_section()         + "\n\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    report += newsletter_section()

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(os.path.join(REPORTS_DIR, f"weekly_{date_str}.md"), "w") as f:
        f.write(report)

    return report

if __name__ == "__main__":
    print(run())
