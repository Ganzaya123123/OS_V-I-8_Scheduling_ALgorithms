"""Command line front end (textbook style): python src/cli.py tasks.txt RR

Task file lines: [task name], [priority], [CPU burst]   e.g.  T1, 4, 20
"""
import argparse
import sys

from schedulers import (ALGORITHMS, DEFAULT_QUANTUM, ValidationError,
                        parse_task_text, run_schedule)


def main(argv=None):
    ap = argparse.ArgumentParser(description="CPU scheduling simulator (CLI)")
    ap.add_argument("file", help="task file, e.g. examples/textbook_tasks.txt")
    ap.add_argument("algorithm", choices=list(ALGORITHMS), type=str.upper)
    ap.add_argument("--quantum", type=int, default=DEFAULT_QUANTUM, help="RR quantum (default 10)")
    ap.add_argument("--priority-order", choices=["high", "low"], default="high",
                    help="'high': bigger number = higher priority (textbook, default)")
    a = ap.parse_args(argv)
    try:
        with open(a.file, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"Cannot read '{a.file}': {e.strerror}", file=sys.stderr)
        return 2
    procs, errors = parse_task_text(text)
    if not errors:
        try:
            res = run_schedule(procs, a.algorithm, a.quantum, a.priority_order)
        except ValidationError as e:
            errors = e.errors
    if errors:
        print("Input error:", file=sys.stderr)
        for m in errors:
            print("  - " + m, file=sys.stderr)
        return 1
    for s in res["segments"]:
        print(f"{s['start']:>5} - {s['end']:<5} {s['name'] or 'idle'}")
    print(f"\n{'Task':<8}{'Wait':>6}{'Turnaround':>12}{'Response':>10}")
    for r in res["processes"]:
        print(f"{r['name']:<8}{r['waiting']:>6}{r['turnaround']:>12}{r['response']:>10}")
    av = res["averages"]
    print(f"{'Average':<8}{av['waiting']:>6}{av['turnaround']:>12}{av['response']:>10}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
