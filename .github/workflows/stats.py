"""Calculs statistiques pour AgriGestion Mobile."""
from datetime import datetime, timedelta
from collections import defaultdict


def global_progress(fields):
    total = sum(len(f.get('tasks', [])) for f in fields)
    if total == 0:
        return 0
    done = sum(sum(1 for t in f.get('tasks', []) if t.get('done', False)) for f in fields)
    return round(100 * done / total)


def fields_status_count(fields):
    en_cours = termines = 0
    for f in fields:
        tasks = f.get('tasks', [])
        if tasks and all(t.get('done', False) for t in tasks):
            termines += 1
        else:
            en_cours += 1
    return en_cours, termines


def tasks_last_7_days(fields):
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    counts = defaultdict(int)
    for f in fields:
        for t in f.get('tasks', []):
            if t.get('done') and t.get('done_at'):
                try:
                    counts[datetime.fromisoformat(t['done_at']).date()] += 1
                except (ValueError, TypeError):
                    pass
    return [(d.strftime("%a"), counts[d]) for d in days]


def tasks_by_crop(fields):
    crops = defaultdict(int)
    for f in fields:
        crops[f.get('crop', 'Inconnu')] += 1
    return dict(crops)


def total_tasks_done(fields):
    return sum(sum(1 for t in f.get('tasks', []) if t.get('done', False)) for f in fields)


def total_tasks(fields):
    return sum(len(f.get('tasks', [])) for f in fields)


def format_date(iso_string):
    if not iso_string:
        return ""
    try:
        return datetime.fromisoformat(iso_string).strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError):
        return ""
