"""CPU scheduling algorithms (Operating System Concepts, ch. 5 project).

Algorithms: FCFS, SJF (non-preemptive), PRIORITY (non-preemptive),
RR (round-robin) and PRIORITY_RR (priority order, round-robin among equals,
preempted when a higher-priority process arrives).
Convention: a SMALLER priority number means a HIGHER priority.
Standard library only.
"""

ALGORITHMS = {
    "FCFS": "First-Come, First-Served",
    "SJF": "Shortest-Job-First (non-preemptive)",
    "PRIORITY": "Priority (non-preemptive)",
    "RR": "Round-Robin",
    "PRIORITY_RR": "Priority with Round-Robin",
}
NEEDS_QUANTUM = {"RR", "PRIORITY_RR"}
MAX_PROCESSES = 50
MAX_VALUE = 100000


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


def validate(raw_processes, algorithm, quantum):
    """Return (clean_processes, quantum) or raise ValidationError."""
    errors = []
    if algorithm not in ALGORITHMS:
        errors.append(f"Unknown algorithm '{algorithm}'. Choose one of: {', '.join(ALGORITHMS)}.")
    if not isinstance(raw_processes, list) or not raw_processes:
        raise ValidationError(errors + ["Add at least one process."])
    if len(raw_processes) > MAX_PROCESSES:
        raise ValidationError(errors + [f"Too many processes ({len(raw_processes)}). The limit is {MAX_PROCESSES}."])

    clean, seen = [], set()
    for i, p in enumerate(raw_processes, start=1):
        if not isinstance(p, dict):
            errors.append(f"Row {i}: expected an object with name, arrival, burst, priority.")
            continue
        name = str(p.get("name", "")).strip()
        label = f"Row {i} ({name or 'no name'})"
        if not name:
            errors.append(f"Row {i}: name is empty.")
        elif name in seen:
            errors.append(f"{label}: name '{name}' is used more than once.")
        seen.add(name)
        vals = {}
        for field, minimum in (("arrival", 0), ("burst", 1), ("priority", 0)):
            raw = p.get(field)
            if raw is None or raw == "":
                raw = 0 if field != "burst" else raw
            try:
                v = _to_int(raw)
            except (ValueError, TypeError):
                errors.append(f"{label}: {field} must be a whole number.")
                continue
            if v < minimum:
                errors.append(f"{label}: {field} must be at least {minimum}.")
            elif v > MAX_VALUE:
                errors.append(f"{label}: {field} must be at most {MAX_VALUE}.")
            else:
                vals[field] = v
        if len(vals) == 3 and name:
            clean.append({"name": name, "idx": len(clean), **vals})

    q = None
    if algorithm in NEEDS_QUANTUM:
        try:
            q = _to_int(quantum)
            if q < 1 or q > MAX_VALUE:
                errors.append(f"Quantum must be between 1 and {MAX_VALUE}.")
        except (ValueError, TypeError):
            errors.append("Quantum must be a whole number for this algorithm.")
    if errors:
        raise ValidationError(errors)
    return clean, q


def _push(segs, name, start, end):
    if segs and segs[-1]["name"] == name and segs[-1]["end"] == start:
        segs[-1]["end"] = end
    else:
        segs.append({"name": name, "start": start, "end": end})


def _non_preemptive(procs, key):
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


def _round_robin(procs, quantum, use_priority):
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
        p = min(ready, key=lambda p: ((p["priority"] if use_priority else 0), seq[p["name"]]))
        name = p["name"]
        run = min(quantum, rem[name])
        preempted = False
        if use_priority:
            sooner = [q["arrival"] for q in procs
                      if q["name"] not in seq and t < q["arrival"] < t + run
                      and q["priority"] < p["priority"]]
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


def run_schedule(raw_processes, algorithm, quantum=None):
    procs, q = validate(raw_processes, algorithm, quantum)
    if algorithm == "FCFS":
        res = _non_preemptive(procs, lambda p: (p["arrival"], p["idx"]))
    elif algorithm == "SJF":
        res = _non_preemptive(procs, lambda p: (p["burst"], p["arrival"], p["idx"]))
    elif algorithm == "PRIORITY":
        res = _non_preemptive(procs, lambda p: (p["priority"], p["arrival"], p["idx"]))
    elif algorithm == "RR":
        res = _round_robin(procs, q, False)
    else:
        res = _round_robin(procs, q, True)
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
    return {"algorithm": algorithm, "quantum": q, "segments": segs, "processes": rows,
            "averages": avg, "total_time": end,
            "cpu_utilization": round(100 * busy / end, 2) if end else 0}
