#!/usr/bin/env python3
"""
Weekly Google Analytics report for marieweb.fr
"""
import os
import json
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Dimension, Metric, OrderBy
)
from google.oauth2 import service_account

PROPERTY_ID = "527914409"
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials/service-account.json")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

def get_client():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    return BetaAnalyticsDataClient(credentials=creds)

def run_report():
    client = get_client()
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    
    date_range = DateRange(start_date="7daysAgo", end_date="yesterday")

    # Vue d'ensemble
    overview = client.run_report(RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[date_range],
        metrics=[
            Metric(name="totalUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
        ]
    ))
    
    users = int(overview.rows[0].metric_values[0].value) if overview.rows else 0
    sessions = int(overview.rows[0].metric_values[1].value) if overview.rows else 0
    pageviews = int(overview.rows[0].metric_values[2].value) if overview.rows else 0

    # Top 10 pages
    pages = client.run_report(RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[date_range],
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="totalUsers"),
            Metric(name="sessions"),
        ],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=10
    ))

    # Sources de trafic
    sources = client.run_report(RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[date_range],
        dimensions=[Dimension(name="sessionSource")],
        metrics=[
            Metric(name="totalUsers"),
            Metric(name="sessions"),
        ],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="totalUsers"), desc=True)],
        limit=10
    ))

    # Build report
    generated_at = today.strftime("%d/%m/%Y à %H:%M")
    report = f"""Rapport Google Analytics - marieweb.fr

Période : 7 derniers jours
Généré le : {generated_at}

━━━━━━━━━━━━━━━━━━━━━

📈 VUE D'ENSEMBLE

👤 Utilisateurs : {users}
🔄 Sessions : {sessions}
📄 Pages vues : {pageviews}

━━━━━━━━━━━━━━━━━━━━━

📄 TOP 10 PAGES LES PLUS VISITÉES

"""
    for i, row in enumerate(pages.rows, 1):
        path = row.dimension_values[0].value
        views = int(row.metric_values[0].value)
        u = int(row.metric_values[1].value)
        s = int(row.metric_values[2].value)
        report += f"{i}. {path} — {views} vues ({u} utilisateurs, {s} sessions)\n"

    report += """
━━━━━━━━━━━━━━━━━━━━━

🌐 SOURCES DE TRAFIC

"""
    for row in sources.rows:
        source = row.dimension_values[0].value
        u = int(row.metric_values[0].value)
        s = int(row.metric_values[1].value)
        report += f"• {source} : {u} utilisateurs ({s} sessions)\n"

    report += f"""
━━━━━━━━━━━━━━━━━━━━━

📁 Rapport complet sauvegardé :
/data/.openclaw/workspace/analytics/reports/weekly_{date_str}.md
"""

    # Save to file
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filepath = os.path.join(REPORTS_DIR, f"weekly_{date_str}.md")
    with open(filepath, "w") as f:
        f.write(report)

    return report

if __name__ == "__main__":
    print(run_report())
