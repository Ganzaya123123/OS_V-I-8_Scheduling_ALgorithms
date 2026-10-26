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

## Tests
```bash
python -m unittest discover -s tests -v
```

## Layout
| Path | Content |
|---|---|
| `src/schedulers.py` | Algorithms and input validation |
| `src/server.py` | Local web server and `POST /api/schedule` |
| `src/static/index.html` | UI: process table, Gantt chart, playback |
| `tests/` | Textbook examples, boundary and error tests |
| `examples/` | Scenario files for **Load JSON file** in the UI |
| `docs/` | Manual PDF, screenshots |

## Conventions
- Smaller priority number = higher priority.
- Priority+RR: highest priority runs first, equal priorities rotate by quantum,
  and a newly arrived higher-priority process preempts.
- Response time = first CPU start − arrival. Waiting = turnaround − burst.

## Third-party code, libraries and AI
- Libraries: none (Python standard library only).
- AI assistance: (describe what was generated and what the team reviewed/changed).
