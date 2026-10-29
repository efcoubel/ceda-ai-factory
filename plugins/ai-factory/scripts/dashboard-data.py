#!/usr/bin/env python3
"""Builds the factory dashboard's datasets from every registered ai-factory project.

Reads only local files: each project's profile, ticket folders, doctor report and pending learnings,
plus the live snapshots the dashboard skill writes beforehand (development queue, validation queue,
open MRs/PRs).
Writes one JSON array per dataset in --out and records today's snapshot in the history.

Usage: dashboard-data.py --out <dir> [--register <project root>]
"""
import argparse
import json
import re
import statistics
from datetime import date, datetime
from pathlib import Path

HOME = Path.home() / ".ai-factory"
REGISTRY = HOME / "projects.json"
HISTORY = HOME / "history"
JOURNAL_LINE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) — ([^:]+): (.*)$")
REVIEW_ROUND = re.compile(r"^#+\s*Round\s+\d+", re.IGNORECASE | re.MULTILINE)
PENDING_STATES = {"pending", "changed"}
DECIDED_STATES = {"ok", "rejected", "changed", "done", "failed"}
OPEN_STATES = {"framing", "planned", "planned (auto)", "coded", "reviewed", "tested", "shipped", "feedback", "staging"}


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "project"


def register(root):
    root = Path(root).expanduser().resolve()
    if not (root / ".ai-factory" / "profile.json").is_file():
        raise SystemExit(f"No .ai-factory/profile.json in {root}")
    registry = read_json(REGISTRY, {"projects": []})
    if not any(Path(entry["root"]) == root for entry in registry["projects"]):
        name = read_json(root / ".ai-factory" / "profile.json", {}).get("project", {}).get("name", root.name)
        registry["projects"].append({"root": str(root), "slug": slug(name)})
        HOME.mkdir(parents=True, exist_ok=True)
        REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def parse_time(text):
    return datetime.strptime(text, "%Y-%m-%d %H:%M")


def hours_between(start, end):
    return round((end - start).total_seconds() / 3600, 1)


def ticket_row(project, folder):
    lines = [line.strip() for line in (folder / "state.md").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return None
    state = lines[0].removeprefix("#").strip().lower()
    journal = [(parse_time(m.group(1)), m.group(2).strip(), m.group(3)) for m in map(JOURNAL_LINE.match, lines[1:]) if m]
    last_line = lines[-1]
    blocked = "blocked:" in last_line
    started = journal[0][0] if journal else None
    last = journal[-1][0] if journal else None
    shipped = next((at for at, step, _ in journal if step.startswith("ship")), None)
    done = last if state == "done" else None
    review = folder / "review.md"
    rounds = len(REVIEW_ROUND.findall(review.read_text(encoding="utf-8"))) if review.is_file() else 0
    plan = folder / "plan.md"
    title = ""
    if plan.is_file():
        heading = next((line for line in plan.read_text(encoding="utf-8").splitlines() if line.startswith("# ")), "")
        title = heading.removeprefix("# ").strip()
    return {
        "project": project,
        "key": folder.name,
        "title": title or folder.name,
        "state": state,
        "blocked": "yes" if blocked else "no",
        "blocked_reason": last_line.split("blocked:", 1)[1].strip() if blocked else "",
        "started_at": started.isoformat() if started else None,
        "last_at": last.isoformat() if last else None,
        "shipped_at": shipped.isoformat() if shipped else None,
        "done_at": done.isoformat() if done else None,
        "lead_hours": hours_between(started, done) if started and done else None,
        "frame_to_ship_hours": hours_between(started, shipped) if started and shipped else None,
        "review_rounds": rounds,
        "first_pass": ("yes" if rounds == 1 else "no") if rounds else None,
    }


def queue_rows(project, root, profile):
    if profile.get("tools", {}).get("queue", {}).get("adapter") == "file":
        rows, current = [], None
        queue = root / ".ai-factory" / "state" / "pilot" / "queue.md"
        text = queue.read_text(encoding="utf-8") if queue.is_file() else ""
        for line in text.splitlines():
            if line.startswith("## "):
                current = {"id": line[3:].strip()}
                rows.append(current)
            elif current is not None and (match := re.match(r"^- (\w+): (.*)$", line)):
                current[match.group(1)] = match.group(2).strip()
    else:
        rows = read_json(root / ".ai-factory" / "state" / "pilot" / "dashboard-queue.json", [])
    fields = ("id", "ticket", "pilot", "type", "status", "summary", "created_at", "decided_at")
    return [{"project": project, **{field: row.get(field) for field in fields}} for row in rows]


def health_rows(project, root):
    pilot = root / ".ai-factory" / "state" / "pilot"
    doctor = read_json(pilot / "doctor.json", {})
    rows = [
        {"project": project, "check": str(check.get("id")), "status": check.get("status"), "detail": check.get("detail", "")}
        for check in doctor.get("checks", [])
    ]
    if not rows:
        rows.append({"project": project, "check": "doctor", "status": "warning", "detail": "No doctor report yet: run /ai-factory:doctor"})
    pending = root / ".ai-factory" / "state" / "learnings-pending.md"
    count = sum(1 for line in pending.read_text(encoding="utf-8").splitlines() if line.startswith("- ")) if pending.is_file() else 0
    rows.append({
        "project": project,
        "check": "learnings",
        "status": "warning" if count else "ok",
        "detail": f"{count} finding(s) waiting to be moved to learnings.md" if count else "Nothing pending",
    })
    return rows, doctor.get("at")


def backlog_rows(project, root, tickets):
    started = {ticket["key"] for ticket in tickets}
    rows = read_json(root / ".ai-factory" / "state" / "pilot" / "dashboard-backlog.json", [])
    fields = ("key", "title", "type", "priority", "created_at")
    return [{"project": project, **{field: row.get(field) for field in fields}} for row in rows if str(row.get("key")) not in started]


def snapshot(project, tickets, queue, prs, backlog):
    open_tickets = [t for t in tickets if t["state"] in OPEN_STATES]
    leads = [t["lead_hours"] for t in tickets if t["lead_hours"] is not None]
    rounds = [t["review_rounds"] for t in tickets if t["review_rounds"]]
    decided = [q for q in queue if q["status"] in DECIDED_STATES and q["type"] != "human_task"]
    return {
        "project": project,
        "day": date.today().isoformat(),
        "todo": len(backlog),
        "open": len(open_tickets),
        "blocked": sum(1 for t in open_tickets if t["blocked"] == "yes"),
        "done_total": sum(1 for t in tickets if t["state"] == "done"),
        "median_lead_hours": statistics.median(leads) if leads else None,
        "mean_review_rounds": round(statistics.mean(rounds), 2) if rounds else None,
        "pending_actions": sum(1 for q in queue if q["status"] in PENDING_STATES),
        "approved_unchanged": sum(1 for q in decided if q["status"] in ("ok", "done")),
        "decided": len(decided),
        "open_prs": len(prs),
    }


def record_history(slug_name, today):
    HISTORY.mkdir(parents=True, exist_ok=True)
    path = HISTORY / f"{slug_name}.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.is_file() else []
    rows = [row for row in rows if row.get("day") != today["day"]] + [today]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return rows


def build(out):
    datasets = {name: [] for name in ("projects", "tickets", "backlog", "queue", "prs", "health", "history")}
    for entry in read_json(REGISTRY, {"projects": []})["projects"]:
        root, project = Path(entry["root"]), entry["slug"]
        profile = read_json(root / ".ai-factory" / "profile.json", None)
        if profile is None:
            datasets["health"].append({"project": project, "check": "profile", "status": "broken", "detail": f"No profile at {root}"})
            continue
        folders = sorted((root / ".ai-factory" / "state" / "tickets").glob("*/state.md"))
        tickets = [row for row in (ticket_row(project, f.parent) for f in folders) if row]
        backlog = backlog_rows(project, root, tickets)
        queue = queue_rows(project, root, profile)
        prs = [{"project": project, **pr} for pr in read_json(root / ".ai-factory" / "state" / "pilot" / "dashboard-prs.json", [])]
        health, doctor_at = health_rows(project, root)
        datasets["projects"].append({
            "project": project,
            "name": profile.get("project", {}).get("name", project),
            "team": profile.get("project", {}).get("team"),
            "plugin_version": profile.get("onboarding", {}).get("plugin_version"),
            "doctor_at": doctor_at,
            "updated_at": datetime.now().isoformat(timespec="minutes"),
        })
        datasets["tickets"] += tickets
        datasets["backlog"] += backlog
        datasets["queue"] += queue
        datasets["prs"] += prs
        datasets["health"] += health
        datasets["history"] += record_history(project, snapshot(project, tickets, queue, prs, backlog))
    out.mkdir(parents=True, exist_ok=True)
    for name, rows in datasets.items():
        (out / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{name}: {len(rows)} rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--register", help="add this project root to the registry first")
    args = parser.parse_args()
    if args.register:
        register(args.register)
    build(args.out)
