"""CPU scheduling algorithms (Operating System Concepts, ch. 5 project).

Algorithms: FCFS, SJF (non-preemptive), PRIORITY (non-preemptive),
RR (round-robin) and PRIORITY_RR (priority order, round-robin among equals,
preempted when a higher-priority process arrives).
Priority convention follows the textbook project: priorities range 1..10 and a
HIGHER number means a HIGHER priority (default, priority_order="high").
priority_order="low" gives the chapter-5 lecture convention (smaller = higher).
Standard library only.
"""

# Names follow the lecture (Lec 5): Mongolian description + English term.
ALGORITHMS = {
    "FCFS": "Эхэнд ирсэн нь эхэлж үйлчлүүлэх (FCFS)",
    "SJF": "Богино-ажил-эхэнд (SJF), тасалдалгүй",
    "PRIORITY": "Эрэмбэлэлттэй төлөвлөлт (Priority), тасалдалгүй",
    "RR": "Round Robin (RR)",
    "PRIORITY_RR": "Эрэмбэтэй төлөвлөлт + Round Robin",
}
FIELD_MN = {"arrival": "ирэх цаг", "burst": "CPU ээлж (burst)", "priority": "эрэмбэ"}
NEEDS_QUANTUM = {"RR", "PRIORITY_RR"}
MAX_PROCESSES = 50
MAX_VALUE = 100000
PRIORITY_MIN, PRIORITY_MAX = 1, 10
DEFAULT_QUANTUM = 10  # textbook: time quantum is 10 ms
PRIORITY_ORDERS = {"high": "Их тоо = өндөр эрэмбэ (ном)",
                   "low": "Бага тоо = өндөр эрэмбэ"}


class ValidationError(ValueError):
    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def _to_int(value):
    if isinstance(value, bool):
        raise ValueError
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.strip().lstrip("+-").isdigit():
        return int(value.strip())
    raise ValueError


def validate(raw_processes, algorithm, quantum, priority_order="high"):
    """Return (clean_processes, quantum) or raise ValidationError."""
    errors = []
    if priority_order not in PRIORITY_ORDERS:
        errors.append(f"Мэдэгдэхгүй эрэмбийн дараалал '{priority_order}'. 'high' эсвэл 'low' өгнө үү.")
    if algorithm not in ALGORITHMS:
        errors.append(f"Мэдэгдэхгүй алгоритм '{algorithm}'. Сонгох боломжтой: {', '.join(ALGORITHMS)}.")
    if not isinstance(raw_processes, list) or not raw_processes:
        raise ValidationError(errors + ["Дор хаяж нэг процесс нэмнэ үү."])
    if len(raw_processes) > MAX_PROCESSES:
        raise ValidationError(errors + [f"Процесс хэт олон байна ({len(raw_processes)}). Дээд хязгаар {MAX_PROCESSES}."])

    clean, seen = [], set()
    for i, p in enumerate(raw_processes, start=1):
        if not isinstance(p, dict):
            errors.append(f"{i}-р мөр: name, arrival, burst, priority талбартай объект байх ёстой.")
            continue
        name = str(p.get("name", "")).strip()
        label = f"{i}-р мөр ({name or 'нэргүй'})"
        if not name:
            errors.append(f"{i}-р мөр: нэр хоосон байна.")
        elif name in seen:
            errors.append(f"{label}: '{name}' нэр давхардсан байна.")
        seen.add(name)
        vals = {}
        for field, minimum, top in (("arrival", 0, MAX_VALUE), ("burst", 1, MAX_VALUE),
                                    ("priority", PRIORITY_MIN, PRIORITY_MAX)):
            raw = p.get(field)
            if raw is None or raw == "":
                raw = {"arrival": 0, "priority": PRIORITY_MIN}.get(field, raw)
            try:
                v = _to_int(raw)
            except (ValueError, TypeError):
                errors.append(f"{label}: {FIELD_MN[field]} бүхэл тоо байх ёстой.")
                continue
            if v < minimum:
                errors.append(f"{label}: {FIELD_MN[field]} хамгийн багадаа {minimum} байх ёстой.")
            elif v > top:
                errors.append(f"{label}: {FIELD_MN[field]} хамгийн ихдээ {top} байх ёстой.")
            else:
                vals[field] = v
        if len(vals) == 3 and name:
            clean.append({"name": name, "idx": len(clean), **vals})

    q = None
    if algorithm in NEEDS_QUANTUM:
        try:
            q = _to_int(DEFAULT_QUANTUM if quantum in (None, "") else quantum)
            if q < 1 or q > MAX_VALUE:
                errors.append(f"Квант 1-ээс {MAX_VALUE} хооронд байх ёстой.")
        except (ValueError, TypeError):
            errors.append("Квант бүхэл тоо байх ёстой.")
    if errors:
        raise ValidationError(errors)
    return clean, q


def _rank(priority, priority_order):
    """Smaller rank = scheduled first."""
    return -priority if priority_order == "high" else priority


def _push(segs, name, start, end):
    if segs and segs[-1]["name"] == name and segs[-1]["end"] == start:
        segs[-1]["end"] = end
    else:
        segs.append({"name": name, "start": start, "end": end})


def _non_preemptive(procs, key):  # key already encodes the priority order
    t, done, segs, first, finish = 0, set(), [], {}, {}
    while len(done) < len(procs):
        ready = [p for p in procs if p["name"] not in done and p["arrival"] <= t]
        if not ready:
            nxt = min(p["arrival"] for p in procs if p["name"] not in done)
            _push(segs, None, t, nxt)
            t = nxt
            continue
        p = min(ready, key=key)
        first[p["name"]] = t
        start = t
        t += p["burst"]
        finish[p["name"]] = t
        done.add(p["name"])
        _push(segs, p["name"], start, t)
    return segs, first, finish


def _round_robin(procs, quantum, use_priority, order="high"):
    rem = {p["name"]: p["burst"] for p in procs}
    seq, first, finish, segs = {}, {}, {}, []
    counter = 0
    t = 0

    def admit(upto):
        nonlocal counter
        for p in sorted(procs, key=lambda p: (p["arrival"], p["idx"])):
            if p["name"] not in seq and p["arrival"] <= upto:
                seq[p["name"]] = counter
                counter += 1

    while len(finish) < len(procs):
        admit(t)
        ready = [p for p in procs if p["name"] in seq and p["name"] not in finish]
        if not ready:
            nxt = min(p["arrival"] for p in procs if p["name"] not in seq)
            _push(segs, None, t, nxt)
            t = nxt
            continue
        p = min(ready, key=lambda p: ((_rank(p["priority"], order) if use_priority else 0), seq[p["name"]]))
        name = p["name"]
        run = min(quantum, rem[name])
        preempted = False
        if use_priority:
            sooner = [q["arrival"] for q in procs
                      if q["name"] not in seq and t < q["arrival"] < t + run
                      and _rank(q["priority"], order) < _rank(p["priority"], order)]
            if sooner:
                run, preempted = min(sooner) - t, True
        first.setdefault(name, t)
        _push(segs, name, t, t + run)
        t += run
        rem[name] -= run
        admit(t)
        if rem[name] == 0:
            finish[name] = t
        elif not preempted:
            seq[name] = counter
            counter += 1
    return segs, first, finish


def run_schedule(raw_processes, algorithm, quantum=None, priority_order="high"):
    procs, q = validate(raw_processes, algorithm, quantum, priority_order)
    if algorithm == "FCFS":
        res = _non_preemptive(procs, lambda p: (p["arrival"], p["idx"]))
    elif algorithm == "SJF":
        res = _non_preemptive(procs, lambda p: (p["burst"], p["arrival"], p["idx"]))
    elif algorithm == "PRIORITY":
        res = _non_preemptive(procs, lambda p: (_rank(p["priority"], priority_order), p["arrival"], p["idx"]))
    elif algorithm == "RR":
        res = _round_robin(procs, q, False, priority_order)
    else:
        res = _round_robin(procs, q, True, priority_order)
    segs, first, finish = res

    rows = []
    for p in procs:
        n = p["name"]
        turnaround = finish[n] - p["arrival"]
        rows.append({
            "name": n, "arrival": p["arrival"], "burst": p["burst"], "priority": p["priority"],
            "completion": finish[n], "turnaround": turnaround,
            "waiting": turnaround - p["burst"], "response": first[n] - p["arrival"],
        })
    k = len(rows)
    avg = {m: round(sum(r[m] for r in rows) / k, 2) for m in ("waiting", "turnaround", "response")}
    busy = sum(s["end"] - s["start"] for s in segs if s["name"])
    end = segs[-1]["end"]
    return {"algorithm": algorithm, "quantum": q, "priority_order": priority_order, "segments": segs, "processes": rows,
            "averages": avg, "total_time": end,
            "cpu_utilization": round(100 * busy / end, 2) if end else 0}


def parse_task_text(text):
    """Parse the textbook task file: one '[name], [priority], [burst]' per line.

    Blank lines and lines starting with '#' are ignored. All tasks arrive at 0.
    Returns (processes, errors); processes are raw dicts for run_schedule().
    """
    procs, errors = [], []
    for n, line in enumerate(str(text).splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [x.strip() for x in line.split(",")]
        if len(parts) != 3 or not all(parts):
            errors.append(f"{n}-р мөр: '[нэр], [эрэмбэ], [CPU ээлж]' хэлбэртэй байх ёстой, олдсон: '{line}'.")
            continue
        procs.append({"name": parts[0], "priority": parts[1], "burst": parts[2], "arrival": 0})
    if not procs and not errors:
        errors.append("Файлд даалгавар алга.")
    return procs, errors
