#!/usr/bin/env python3
"""
Rappel quotidien publication - vérifie si aujourd'hui est un jour de publication
et envoie un rappel avec le contenu prévu dans le calendrier Notion
"""
import requests
import json
from datetime import datetime, timezone

NOTION_TOKEN = open('/data/.openclaw/workspace/credentials/notion_token.txt').read().strip()
CALENDAR_DB_ID = '32753e7444de81f4a478de1b1e2eda49'

PUBLISH_DAYS = {0: "Lundi", 2: "Mercredi", 4: "Vendredi", 6: "Dimanche"}

def get_today_posts():
    today = datetime.now().strftime("%Y-%m-%d")
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    resp = requests.post(
        f'https://api.notion.com/v1/databases/{CALENDAR_DB_ID}/query',
        headers=headers,
        json={"filter": {"property": "Date", "date": {"equals": today}}}
    )
    return resp.json().get('results', [])

def format_post(page):
    props = page['properties']
    titre = ''.join([t['plain_text'] for t in props.get('Titre', {}).get('title', [])])
    post_type = (props.get('Type de post', {}).get('select') or {}).get('name', '')
    statut = (props.get('Statut', {}).get('status') or {}).get('name', '')
    plateformes = [p['name'] for p in props.get('Plateforme', {}).get('multi_select', [])]
    lien = (props.get('Lien affiliation', {}).get('url') or '')
    notes = ''.join([t['plain_text'] for t in props.get('Notes', {}).get('rich_text', [])])
    
    lines = [f"• **{titre or '(sans titre)'}**"]
    if post_type:
        lines.append(f"  {post_type}")
    if plateformes:
        lines.append(f"  📲 {' + '.join(plateformes)}")
    if statut:
        lines.append(f"  Statut : {statut}")
    if lien:
        lines.append(f"  🔗 {lien}")
    if notes:
        lines.append(f"  💬 {notes}")
    return '\n'.join(lines)

def run():
    today = datetime.now()
    weekday = today.weekday()
    day_name = PUBLISH_DAYS.get(weekday)
    
    if not day_name:
        return None  # Pas un jour de publication
    
    posts = get_today_posts()
    
    lines = [f"📅 Rappel publication — {day_name} {today.strftime('%d/%m')} !\n"]
    
    if not posts:
        lines.append("Aucun contenu planifié pour aujourd'hui dans le calendrier Notion.")
        lines.append("👉 https://www.notion.so/32753e7444de8126b18ee9dc5623bcfb")
    else:
        lines.append(f"{len(posts)} élément(s) à publier aujourd'hui :\n")
        for post in posts:
            lines.append(format_post(post))
        lines.append(f"\n👉 https://www.notion.so/32753e7444de8126b18ee9dc5623bcfb")
    
    return '\n'.join(lines)

if __name__ == '__main__':
    msg = run()
    if msg:
        print(msg)
    else:
        print("SKIP")  # Pas un jour de publication
