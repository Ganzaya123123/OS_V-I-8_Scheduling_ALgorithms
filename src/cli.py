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
    ap.add_argument("--quantum", type=int, default=DEFAULT_QUANTUM, help="RR квант (анхдагч 10)")
    ap.add_argument("--priority-order", choices=["high", "low"], default="high",
                    help="'high': их тоо = өндөр эрэмбэ (ном, анхдагч); 'low': бага тоо = өндөр эрэмбэ")
    a = ap.parse_args(argv)
    try:
        with open(a.file, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"'{a.file}' файлыг уншиж чадсангүй: {e.strerror}", file=sys.stderr)
        return 2
    procs, errors = parse_task_text(text)
    if not errors:
        try:
            res = run_schedule(procs, a.algorithm, a.quantum, a.priority_order)
        except ValidationError as e:
            errors = e.errors
    if errors:
        print("Оролтын алдаа:", file=sys.stderr)
        for m in errors:
            print("  - " + m, file=sys.stderr)
        return 1
    for s in res["segments"]:
        print(f"{s['start']:>5} - {s['end']:<5} {s['name'] or 'сул (idle)'}")
    print(f"\n{'Процесс':<10}{'Хүлээлт':>9}{'Эргэлт':>9}{'Response':>10}")
    for r in res["processes"]:
        print(f"{r['name']:<10}{r['waiting']:>9}{r['turnaround']:>9}{r['response']:>10}")
    av = res["averages"]
    print(f"{'Дундаж':<10}{av['waiting']:>9}{av['turnaround']:>9}{av['response']:>10}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
