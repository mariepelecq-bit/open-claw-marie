#!/usr/bin/env python3
"""
Rapport quotidien System.io - nouveaux inscrits à la Newsletter (dernières 24h)
"""
import requests
import json
import os
from datetime import datetime, timedelta, timezone

API_KEY = 'z6009mqd6w5gdr742hg1gftruvktg3sgdydgyr9lonrzsgykj9e22s7nov9yg7jj'
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '../systemio_reports')
NEWSLETTER_TAG = 'Newsletter'

def get_new_subscribers():
    headers = {'X-API-Key': API_KEY}
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    
    new_subscribers = []
    page = 1
    
    while True:
        resp = requests.get(
            f'https://api.systeme.io/api/contacts?limit=100&page={page}',
            headers=headers
        )
        data = resp.json()
        items = data.get('items', [])
        if not items:
            break
        
        for contact in items:
            registered = datetime.fromisoformat(contact['registeredAt'].replace('Z', '+00:00'))
            if registered < since:
                return new_subscribers  # sorted by date desc, stop when too old
            
            tags = [t['name'] for t in contact.get('tags', [])]
            if NEWSLETTER_TAG in tags:
                new_subscribers.append({
                    'email': contact['email'],
                    'name': next((f['value'] for f in contact.get('fields', []) if f['slug'] == 'first_name'), ''),
                    'country': next((f['value'] for f in contact.get('fields', []) if f['slug'] == 'country'), ''),
                    'registered': registered.strftime('%d/%m/%Y %H:%M'),
                    'source': contact.get('sourceURL', '')
                })
        page += 1
    
    return new_subscribers

def get_total_newsletter():
    headers = {'X-API-Key': API_KEY}
    total = 0
    page = 1
    while True:
        resp = requests.get(
            f'https://api.systeme.io/api/contacts?limit=100&page={page}&tagName={NEWSLETTER_TAG}',
            headers=headers
        )
        items = resp.json().get('items', [])
        total += len(items)
        if len(items) < 100:
            break
        page += 1
    return total

def run():
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    generated = today.strftime('%d/%m/%Y à %H:%M')
    
    new_subs = get_new_subscribers()
    total = get_total_newsletter()
    count = len(new_subs)
    
    lines = [f"📧 Rapport Newsletter System.io — marieweb.fr"]
    lines.append(f"Généré le {generated}")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"")
    lines.append(f"📊 Total inscrits Newsletter : {total}")
    lines.append(f"🆕 Nouveaux inscrits (24h) : {count}")
    lines.append(f"")
    
    if count == 0:
        lines.append("Aucun nouvel inscrit dans les dernières 24 heures.")
    else:
        lines.append("Nouveaux inscrits :")
        for s in new_subs:
            name = f" ({s['name']})" if s['name'] else ''
            country = f" 🌍 {s['country']}" if s['country'] else ''
            lines.append(f"• {s['email']}{name}{country} — {s['registered']}")
    
    report = '\n'.join(lines)
    
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(os.path.join(REPORTS_DIR, f'newsletter_{date_str}.md'), 'w') as f:
        f.write(report)
    
    return report

if __name__ == '__main__':
    print(run())
