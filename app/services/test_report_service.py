import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.test_report_m import TestReport


def parse_schemathesis_report(report_path: str) -> dict:
    with open(report_path, "r") as f:
        data = json.load(f)

    checks = data.get("checks", [])

    total = len(checks)
    passed = len([c for c in checks if c.get("status") == "success"])
    failed = total - passed

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
    }

def save_test_report(report_dict: dict):
    db = SessionLocal()
    try:
        for module_name, module_results in report_dict.items():
            print("Saving module:", module_name)  # DEBUG

            test_report = TestReport(
                module_name=module_name,
                total_tests=module_results.get("total", 0),
                passed=module_results.get("passed", 0),
                failed=module_results.get("failed", 0),
                failures=module_results.get("failures", [])
            )

            db.add(test_report)

        db.commit()
        print("✅ Commit successful")
    except Exception as e:
        db.rollback()
        print("❌ DB Error:", e)
    finally:
        db.close()