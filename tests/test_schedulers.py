import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from schedulers import ValidationError, parse_task_text, run_schedule  # noqa: E402


def P(name, burst, arrival=0, priority=1):
    return {"name": name, "burst": burst, "arrival": arrival, "priority": priority}


def waits(res):
    return [r["waiting"] for r in res["processes"]]


class Textbook(unittest.TestCase):
    def test_fcfs(self):  # P1=24, P2=3, P3=3
        r = run_schedule([P("P1", 24), P("P2", 3), P("P3", 3)], "FCFS")
        self.assertEqual(waits(r), [0, 24, 27])
        self.assertEqual(r["averages"]["waiting"], 17.0)

    def test_sjf(self):  # 6, 8, 7, 3 -> avg waiting 7
        r = run_schedule([P("P1", 6), P("P2", 8), P("P3", 7), P("P4", 3)], "SJF")
        self.assertEqual(waits(r), [3, 16, 9, 0])
        self.assertEqual(r["averages"]["waiting"], 7.0)

    def test_priority(self):  # avg waiting 8.2
        r = run_schedule([P("P1", 10, 0, 3), P("P2", 1, 0, 1), P("P3", 2, 0, 4),
                          P("P4", 1, 0, 5), P("P5", 5, 0, 2)], "PRIORITY", priority_order="low")
        self.assertEqual(waits(r), [6, 0, 16, 18, 1])
        self.assertEqual(r["averages"]["waiting"], 8.2)

    def test_rr(self):  # 24, 3, 3 with q=4 -> avg waiting 5.67
        r = run_schedule([P("P1", 24), P("P2", 3), P("P3", 3)], "RR", 4)
        self.assertEqual(waits(r), [6, 4, 7])
        self.assertEqual(r["averages"]["waiting"], 5.67)


TASKS = [P("T1", 20, 0, 4), P("T2", 25, 0, 2), P("T3", 25, 0, 3), P("T4", 15, 0, 3), P("T5", 10, 0, 10)]


class ProjectSpec(unittest.TestCase):
    """Textbook programming project: priority 1..10, higher number = higher priority."""

    def order(self, res):
        return [s["name"] for s in res["segments"]]

    def test_priority_higher_number_first(self):
        r = run_schedule(TASKS, "PRIORITY")
        self.assertEqual(self.order(r), ["T5", "T1", "T3", "T4", "T2"])
        self.assertEqual([x["waiting"] for x in r["processes"]], [10, 70, 30, 55, 0])

    def test_priority_low_order_flips(self):
        r = run_schedule(TASKS, "PRIORITY", priority_order="low")
        self.assertEqual(self.order(r), ["T2", "T3", "T4", "T1", "T5"])

    def test_priority_rr_default_quantum_is_10(self):
        r = run_schedule(TASKS, "PRIORITY_RR")
        self.assertEqual(r["quantum"], 10)
        # T5 (10) and T1 (20, two slices), then T3/T4 rotate, then T2
        self.assertEqual(self.order(r), ["T5", "T1", "T3", "T4", "T3", "T4", "T3", "T2"])
        self.assertEqual(self.order(r)[0], "T5")
        self.assertEqual(self.order(r)[-1], "T2")

    def test_fcfs_sjf_rr_with_textbook_tasks(self):
        self.assertEqual(self.order(run_schedule(TASKS, "FCFS")), ["T1", "T2", "T3", "T4", "T5"])
        self.assertEqual(self.order(run_schedule(TASKS, "SJF")), ["T5", "T4", "T1", "T2", "T3"])
        r = run_schedule(TASKS, "RR", 10)
        self.assertEqual(r["total_time"], 95)

    def test_task_file_parser(self):
        procs, errs = parse_task_text("# c\nT1, 4, 20\n\nT2,2,25\n")
        self.assertEqual(errs, [])
        self.assertEqual([p["name"] for p in procs], ["T1", "T2"])
        self.assertEqual(procs[1]["burst"], "25")

    def test_task_file_parser_errors(self):
        _, errs = parse_task_text("T1, 4\nT2, x, 5")
        self.assertIn("1-р мөр", errs[0])
        _, errs = parse_task_text("\n# only comment")
        self.assertIn("даалгавар алга", errs[0])


class Extra(unittest.TestCase):
    def test_idle_gap(self):
        r = run_schedule([P("A", 2, 0), P("B", 2, 5)], "FCFS")
        self.assertEqual(r["segments"][1], {"name": None, "start": 2, "end": 5})
        self.assertEqual(r["total_time"], 7)
        self.assertLess(r["cpu_utilization"], 100)

    def test_rr_arrival_before_requeue(self):
        r = run_schedule([P("A", 5, 0), P("B", 2, 1)], "RR", 2)
        self.assertEqual([s["name"] for s in r["segments"]], ["A", "B", "A"])

    def test_priority_rr_equal_priorities_rotate(self):
        r = run_schedule([P("A", 4, 0, 1), P("B", 4, 0, 1), P("C", 2, 0, 2)], "PRIORITY_RR", 2, "low")
        self.assertEqual([s["name"] for s in r["segments"]], ["A", "B", "A", "B", "C"])

    def test_priority_rr_preempts_on_higher_priority_arrival(self):
        r = run_schedule([P("LOW", 6, 0, 5), P("HIGH", 2, 2, 1)], "PRIORITY_RR", 10, "low")
        self.assertEqual([(s["name"], s["start"], s["end"]) for s in r["segments"]],
                         [("LOW", 0, 2), ("HIGH", 2, 4), ("LOW", 4, 8)])

    def test_single_process_and_response(self):
        r = run_schedule([P("A", 1)], "SJF")
        self.assertEqual(r["processes"][0]["response"], 0)


class Errors(unittest.TestCase):
    def err(self, procs, algo="FCFS", q=None):
        with self.assertRaises(ValidationError) as c:
            run_schedule(procs, algo, q)
        return " ".join(c.exception.errors)

    def test_empty(self):
        self.assertIn("Дор хаяж нэг", self.err([]))

    def test_zero_burst(self):
        self.assertIn("CPU ээлж (burst) хамгийн багадаа 1", self.err([P("A", 0)]))

    def test_negative_arrival(self):
        self.assertIn("ирэх цаг хамгийн багадаа 0", self.err([P("A", 1, -1)]))

    def test_non_numeric(self):
        self.assertIn("бүхэл тоо", self.err([P("A", "abc")]))

    def test_decimal_rejected(self):
        self.assertIn("бүхэл тоо", self.err([P("A", "2.5")]))

    def test_duplicate_names(self):
        self.assertIn("давхардсан", self.err([P("A", 1), P("A", 2)]))

    def test_missing_quantum_uses_default(self):
        self.assertEqual(run_schedule([P("A", 1)], "RR", None)["quantum"], 10)

    def test_non_numeric_quantum(self):
        self.assertIn("Квант", self.err([P("A", 1)], "RR", "abc"))

    def test_zero_quantum(self):
        self.assertIn("Квант", self.err([P("A", 1)], "RR", 0))

    def test_unknown_algorithm(self):
        self.assertIn("Мэдэгдэхгүй алгоритм", self.err([P("A", 1)], "XYZ"))

    def test_priority_out_of_range(self):
        self.assertIn("эрэмбэ хамгийн багадаа 1", self.err([P("A", 1, 0, 0)]))
        self.assertIn("эрэмбэ хамгийн ихдээ 10", self.err([P("A", 1, 0, 11)]))

    def test_bad_priority_order(self):
        with self.assertRaises(ValidationError):
            run_schedule([P("A", 1)], "FCFS", priority_order="up")

    def test_huge_value(self):
        self.assertIn("хамгийн ихдээ", self.err([P("A", 10**9)]))


if __name__ == "__main__":
    unittest.main()
