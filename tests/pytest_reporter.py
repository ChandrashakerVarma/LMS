from collections import defaultdict

class PytestReportCollector:
    def __init__(self):
        self.results = defaultdict(lambda: {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "failures": []
        })

    def add_result(self, module, outcome, nodeid, error=None):
        data = self.results[module]
        data["total"] += 1

        if outcome == "passed":
            data["passed"] += 1
        elif outcome == "failed":
            data["failed"] += 1
            if error:
                data["failures"].append(f"{nodeid}\n{error}")

collector = PytestReportCollector()
