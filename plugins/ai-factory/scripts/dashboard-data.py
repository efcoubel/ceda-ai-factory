#!/usr/bin/env python3
"""Builds the factory dashboard's datasets from every registered ai-factory project.

Reads only local files: each project's profile, ticket folders, doctor report and pending learnings,
plus the live snapshots the dashboard skill writes beforehand (development queue, validation queue,
open MRs/PRs).
Writes one JSON array per dataset in --out and records today's snapshot in the history.

Usage: dashboard-data.py --out <dir> [--register <project root>] [--changed]
With --changed, prints the datasets to upload: those whose content differs from the last upload
recorded in ~/.ai-factory/dashboard.json, or all of them once a day so none shows as stale.
"""
import argparse
import hashlib
import json
import re
import statistics
from datetime import date, datetime, timedelta
from pathlib import Path

HOME = Path.home() / ".ai-factory"
REGISTRY = HOME / "projects.json"
HISTORY = HOME / "history"
DASHBOARD = HOME / "dashboard.json"
JOURNAL_LINE = re.compile(r"^(?:[-*]\s+)?(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})(?::\d{2})?\s+[—–-]\s+([^:]+):\s*(.*)$")
BLOCKED_LINE = re.compile(r"^(?:[-*]\s+)?blocked:\s*(.*)$", re.IGNORECASE)
OTHER_LINE = re.compile(r"^(?:[-*]\s+)?(?:rejected|fin|note):", re.IGNORECASE)
STEP_NAME = re.compile(r"^(?:ticket-\d-)?([\w-]+)")
TITLE_SUFFIX = re.compile(r"\s*[·—–-]\s*plan\s*$", re.IGNORECASE)
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


def parse_time(day, time):
    return datetime.strptime(f"{day} {time}", "%Y-%m-%d %H:%M")


def read_journal(lines, now):
    """Returns (at, step, text) entries, the current block's reason, and the lines nothing could read."""
    journal, block, unread = [], None, []
    for line in lines:
        match = JOURNAL_LINE.match(line)
        if match:
            text = match.group(4)
            blocked = BLOCKED_LINE.match(text)
            at = parse_time(match.group(1), match.group(2))
            if at > now:
                unread.append(f"future date: {line}")
                continue
            journal.append((at, STEP_NAME.match(match.group(3).strip()).group(1), text))
            block = blocked.group(1).strip() if blocked else None
        elif BLOCKED_LINE.match(line):
            block = BLOCKED_LINE.match(line).group(1).strip()
        elif not OTHER_LINE.match(line):
            unread.append(line)
    return journal, block, unread


def hours_between(start, end):
    return round((end - start).total_seconds() / 3600, 1)


def ticket_row(project, folder):
    lines = [line.strip() for line in (folder / "state.md").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return None
    state = lines[0].removeprefix("#").strip().lower()
    journal, block, unread = read_journal(lines[1:], datetime.now())
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
        title = TITLE_SUFFIX.sub("", heading.removeprefix("# ").strip())
        title = re.sub(rf"^{re.escape(folder.name)}\s*[·—–:-]\s*", "", title)
    return {
        "project": project,
        "key": folder.name,
        "title": title or folder.name,
        "state": state,
        "blocked": "yes" if block is not None else "no",
        "blocked_reason": block or "",
        "started_at": started.isoformat() if started else None,
        "last_at": last.isoformat() if last else None,
        "shipped_at": shipped.isoformat() if shipped else None,
        "done_at": done.isoformat() if done else None,
        "lead_hours": hours_between(started, done) if started and done else None,
        "frame_to_ship_hours": hours_between(started, shipped) if started and shipped else None,
        "review_rounds": rounds,
        "first_pass": ("yes" if rounds == 1 else "no") if rounds else None,
        "unread_lines": unread,
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


def health_rows(project, root, tickets):
    pilot = root / ".ai-factory" / "state" / "pilot"
    doctor = read_json(pilot / "doctor.json", {})
    rows = [
        {"project": project, "check": str(check.get("id")), "status": check.get("status"), "detail": check.get("detail", "")}
        for check in doctor.get("checks", [])
    ]
    if not rows:
        rows.append({"project": project, "check": "doctor", "status": "warning", "detail": "No doctor report yet: run /ai-factory:doctor"})
    for ticket in tickets:
        lines = ticket.pop("unread_lines")
        if lines:
            rows.append({
                "project": project,
                "check": f"journal {ticket['key']}",
                "status": "warning",
                "detail": f"{len(lines)} unreadable line(s) in state.md, dates and lead time may be wrong: {lines[0][:80]}",
            })
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


def dataset_hash(rows):
    stable = [{key: value for key, value in row.items() if key != "updated_at"} for row in rows]
    return hashlib.sha256(json.dumps(stable, sort_keys=True).encode("utf-8")).hexdigest()


def changed_datasets(hashes):
    dashboard = read_json(DASHBOARD, {})
    uploaded_at = dashboard.get("uploaded_at")
    if not uploaded_at or datetime.now() - datetime.fromisoformat(uploaded_at) > timedelta(hours=24):
        return sorted(hashes)
    uploaded = dashboard.get("uploaded", {})
    return sorted(name for name, value in hashes.items() if uploaded.get(name) != value)


def build(out, show_changed):
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
        health, doctor_at = health_rows(project, root, tickets)
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
        if not show_changed:
            print(f"{name}: {len(rows)} rows")
    hashes = {name: dataset_hash(rows) for name, rows in datasets.items()}
    (out / "hashes.json").write_text(json.dumps(hashes, indent=1) + "\n", encoding="utf-8")
    if show_changed:
        print(" ".join(changed_datasets(hashes)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--register", help="add this project root to the registry first")
    parser.add_argument("--changed", action="store_true", help="print only the datasets to upload")
    args = parser.parse_args()
    if args.register:
        register(args.register)
    build(args.out, args.changed)
