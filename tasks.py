#!/usr/bin/env python3
"""Miirr — a tiny CLI task manager stored in tasks.json."""

import json
import sys
from pathlib import Path

DB = Path(__file__).parent / "tasks.json"


def load():
    if DB.exists():
        return json.loads(DB.read_text())
    return []


def save(tasks):
    DB.write_text(json.dumps(tasks, indent=2))


def add(title):
    tasks = load()
    task = {"id": (tasks[-1]["id"] + 1) if tasks else 1, "title": title, "done": False}
    tasks.append(task)
    save(tasks)
    print(f"Added #{task['id']}: {title}")


def done(task_id):
    tasks = load()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save(tasks)
            print(f"Done  #{task_id}: {t['title']}")
            return
    print(f"Task #{task_id} not found.")


def remove(task_id):
    tasks = load()
    remaining = [t for t in tasks if t["id"] != task_id]
    if len(remaining) == len(tasks):
        print(f"Task #{task_id} not found.")
        return
    save(remaining)
    print(f"Removed #{task_id}")


def list_tasks():
    tasks = load()
    if not tasks:
        print("No tasks yet. Add one with:  python tasks.py add \"your task\"")
        return
    for t in tasks:
        mark = "x" if t["done"] else " "
        print(f"  [{mark}] #{t['id']}  {t['title']}")


USAGE = """Usage:
  python tasks.py list
  python tasks.py add "task title"
  python tasks.py done <id>
  python tasks.py remove <id>
"""

COMMANDS = {
    "list": lambda _: list_tasks(),
    "add":  lambda args: add(" ".join(args)) if args else print("Provide a title."),
    "done": lambda args: done(int(args[0])) if args else print("Provide a task id."),
    "remove": lambda args: remove(int(args[0])) if args else print("Provide a task id."),
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(USAGE)
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])
