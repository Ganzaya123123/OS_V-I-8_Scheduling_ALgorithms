# V-1-8 – Scheduling Algorithms

**Course:** F.CSM302 Operating Systems, Assignment 1 (БД1)
**Code:** V-1-8 | **Textbook:** Operating System Concepts, ch. 5 programming project
**Members:** (name, student ID) – fill in

## Goal
Implement FCFS, SJF, Priority, Round-Robin and Priority-with-Round-Robin
scheduling, and show the result as an interactive Gantt chart with waiting,
turnaround and response times.

## Quick Start
Requires **Python 3.9+**. No packages to install.

```bash
git clone https://github.com/Ganzaya123123/OS_V-I-8_Scheduling_ALgorithms.git
cd OS_V-I-8_Scheduling_ALgorithms
python src/server.py            # add --port 8080 if 8000 is busy
```
Open http://127.0.0.1:8000, choose an example, press **Run schedule**.
Stop with Ctrl+C.

Textbook-style command line (task file lines are `[name], [priority], [burst]`):
```bash
python src/cli.py examples/textbook_tasks.txt PRIORITY
python src/cli.py examples/textbook_tasks.txt RR --quantum 10
python src/cli.py examples/textbook_tasks.txt PRIORITY_RR --priority-order low
```
Algorithms: `FCFS`, `SJF`, `PRIORITY`, `RR`, `PRIORITY_RR`.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Layout
| Path | Content |
|---|---|
| `src/schedulers.py` | Algorithms and input validation |
| `src/server.py` | Local web server and `POST /api/schedule` |
| `src/cli.py` | Command line version reading the textbook task file |
| `src/static/index.html` | UI: process table, Gantt chart, playback |
| `tests/` | Textbook examples, boundary and error tests |
| `examples/` | `.txt` task files and `.json` scenarios for **Load .json / .txt file** |
| `docs/` | Manual PDF, screenshots |

## Conventions
- Textbook project: priority is 1 to 10 and a **higher number = higher priority**
  (default). The UI and CLI also offer `low` (lower number = higher priority), which
  is the convention of the chapter 5.3 lecture examples.
- RR time quantum defaults to **10 ms** (textbook); it can be changed.
- Task file: `[name], [priority], [burst]`, all tasks arrive at time 0.
  The UI and JSON scenarios additionally allow an arrival time.
- Priority+RR: highest priority runs first, equal priorities rotate by quantum,
  and a newly arrived higher-priority process preempts.
- Response time = first CPU start - arrival. Waiting = turnaround - burst.

## Third-party code, libraries and AI
- Libraries: none (Python standard library only).
- AI assistance: (describe what was generated and what the team reviewed/changed).
