import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_DATA_FILE = Path(__file__).with_name("tasks_data.json")
PRIORITY_LEVELS = ["low", "medium", "high", "urgent"]
PRIORITY_RANK = {name: index for index, name in enumerate(PRIORITY_LEVELS)}


def parse_due_date(raw: str) -> str:
    try:
        parsed = datetime.strptime(raw, "%Y-%m-%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Due date must use YYYY-MM-DD format, for example 2025-11-07."
        ) from exc
    return parsed.date().isoformat()


def load_tasks(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError:
        print(f"Warning: Could not parse {path}; starting with an empty task list.")
        return []
    if not isinstance(data, list):
        print(f"Warning: Expected a list of tasks in {path}; starting fresh.")
        return []
    return data


def save_tasks(path: Path, tasks: Iterable[Dict[str, Any]]) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(list(tasks), handle, indent=2, ensure_ascii=False)


def next_task_id(tasks: Iterable[Dict[str, Any]]) -> int:
    try:
        return max(task["id"] for task in tasks) + 1
    except ValueError:
        return 1


def add_task(args: argparse.Namespace) -> None:
    tasks = load_tasks(args.storage_path)
    task = {
        "id": next_task_id(tasks),
        "title": args.title,
        "description": args.description,
        "due_date": args.due,
        "priority": args.priority,
        "completed": False,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "completed_at": None,
    }
    tasks.append(task)
    save_tasks(args.storage_path, tasks)
    print(f"Task {task['id']} added: {task['title']}")


def list_tasks(args: argparse.Namespace) -> None:
    tasks = load_tasks(args.storage_path)
    if not tasks:
        print("No tasks found.")
        return

    to_display = sort_tasks(tasks, args.sort_by)
    print_task_table(to_display, show_description=args.verbose)


def sort_tasks(tasks: List[Dict[str, Any]], sort_by: Optional[str]) -> List[Dict[str, Any]]:
    if sort_by == "priority":
        key_fn = lambda task: (
            PRIORITY_RANK.get(task.get("priority"), len(PRIORITY_RANK)),
            task.get("due_date") or "9999-12-31",
            task.get("id", 0),
        )
    elif sort_by == "due":
        key_fn = lambda task: (
            task.get("due_date") or "9999-12-31",
            PRIORITY_RANK.get(task.get("priority"), len(PRIORITY_RANK)),
            task.get("id", 0),
        )
    else:
        key_fn = lambda task: task.get("id", 0)
    return sorted(tasks, key=key_fn)


def print_task_table(tasks: List[Dict[str, Any]], show_description: bool = False) -> None:
    headers = ["ID", "Title", "Priority", "Due", "Status"]
    if show_description:
        headers.append("Description")

    rows = []
    for task in tasks:
        status = "Completed" if task.get("completed") else "Pending"
        row = [
            str(task.get("id", "")),
            task.get("title", ""),
            task.get("priority", "").capitalize(),
            task.get("due_date") or "-",
            status,
        ]
        if show_description:
            row.append(task.get("description") or "-")
        rows.append(row)

    col_widths = [
        max(len(header), *(len(row[idx]) for row in rows))
        for idx, header in enumerate(headers)
    ]

    header_line = "  ".join(
        header.ljust(col_widths[idx]) for idx, header in enumerate(headers)
    )
    separator = "  ".join("-" * width for width in col_widths)

    print(header_line)
    print(separator)
    for row in rows:
        print("  ".join(row[idx].ljust(col_widths[idx]) for idx in range(len(headers))))


def complete_task(args: argparse.Namespace) -> None:
    tasks = load_tasks(args.storage_path)
    task = find_task(tasks, args.task_id)
    if not task:
        print(f"Task {args.task_id} not found.")
        return
    if task.get("completed"):
        print(f"Task {args.task_id} is already completed.")
        return
    task["completed"] = True
    task["completed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save_tasks(args.storage_path, tasks)
    print(f"Task {args.task_id} marked as completed.")


def delete_task(args: argparse.Namespace) -> None:
    tasks = load_tasks(args.storage_path)
    new_tasks = [task for task in tasks if task.get("id") != args.task_id]
    if len(new_tasks) == len(tasks):
        print(f"Task {args.task_id} not found.")
        return
    save_tasks(args.storage_path, new_tasks)
    print(f"Task {args.task_id} deleted.")


def search_tasks(args: argparse.Namespace) -> None:
    tasks = load_tasks(args.storage_path)
    keyword = args.keyword.lower()
    matched = [
        task for task in tasks if keyword in task.get("title", "").lower()
    ]
    if not matched:
        print(f"No tasks found containing '{args.keyword}'.")
        return
    matched = sort_tasks(matched, args.sort_by)
    print_task_table(matched, show_description=args.verbose)


def find_task(tasks: Iterable[Dict[str, Any]], task_id: int) -> Optional[Dict[str, Any]]:
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simple command-line task manager."
    )
    parser.add_argument(
        "--data-file",
        default=str(DEFAULT_DATA_FILE),
        help=f"Path to the tasks JSON file (default: {DEFAULT_DATA_FILE}).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task.")
    add_parser.add_argument("title", help="Title of the task.")
    add_parser.add_argument(
        "-d",
        "--description",
        default="",
        help="Optional description for the task.",
    )
    add_parser.add_argument(
        "--due",
        type=parse_due_date,
        help="Due date in YYYY-MM-DD format.",
    )
    add_parser.add_argument(
        "-p",
        "--priority",
        choices=PRIORITY_LEVELS,
        default="medium",
        help="Priority level for the task.",
    )
    add_parser.set_defaults(handler=add_task)

    list_parser = subparsers.add_parser("list", help="List all tasks.")
    list_parser.add_argument(
        "--sort-by",
        choices=["priority", "due"],
        help="Sort tasks by priority or due date.",
    )
    list_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show task descriptions in the table.",
    )
    list_parser.set_defaults(handler=list_tasks)

    complete_parser = subparsers.add_parser("complete", help="Mark a task as completed.")
    complete_parser.add_argument("task_id", type=int, help="ID of the task to mark complete.")
    complete_parser.set_defaults(handler=complete_task)

    delete_parser = subparsers.add_parser("delete", help="Delete a task.")
    delete_parser.add_argument("task_id", type=int, help="ID of the task to delete.")
    delete_parser.set_defaults(handler=delete_task)

    search_parser = subparsers.add_parser("search", help="Search tasks by title keyword.")
    search_parser.add_argument("keyword", help="Keyword to search for in task titles.")
    search_parser.add_argument(
        "--sort-by",
        choices=["priority", "due"],
        help="Optional sorting for search results.",
    )
    search_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show task descriptions in the table.",
    )
    search_parser.set_defaults(handler=search_tasks)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    storage_path = Path(args.data_file).expanduser()
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    setattr(args, "storage_path", storage_path)
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
