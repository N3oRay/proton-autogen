# diagnostic.py

import json
from pathlib import Path
from collections import Counter, defaultdict


IGNORED_EXEC_NAMES = {
    "--call",
    "--gamemode",
    "--mangohud",
    "--wine",
    "missing.exe",
}


def is_real_executable(path):

    name = Path(path).name

    if name in IGNORED_EXEC_NAMES:
        return False

    return True


def load_logs(log_file):

    logs = []

    path = Path(log_file).expanduser()

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:

            for line_number, line in enumerate(f, 1):

                line = line.strip()

                if not line:
                    continue

                try:
                    logs.append(json.loads(line))

                except json.JSONDecodeError:
                    print(
                        f"Invalid JSON line skipped: {line_number}"
                    )

    except OSError as e:
        print(f"Cannot read log file: {e}")

    return logs



def analyze_issues(logs):

    issues = defaultdict(lambda: {
        "count": 0,
        "severity": "",
    })


    missing_exe = []

    for log in logs:

        msg = log.get("message", "")


        # MangoHud
        if "Could not find cpu temp sensor" in msg:

            item = issues["MANGOHUD_CPU_SENSOR"]

            item["count"] += 1
            item["severity"] = "info"


        # Executable absent
        if "Executable not found:" in msg:
            path = msg.split(
                "Executable not found:"
            )[-1].strip()


            if not is_real_executable(path):
                continue


            item = issues["MISSING_EXECUTABLE"]

            item["count"] += 1
            item["severity"] = "info"

            missing_exe.append(path)


    result = []

    for name, data in issues.items():

        issue = {
            "type": name.lower(),
            "severity": data["severity"],
            "count": data["count"]
        }


        if name == "MISSING_EXECUTABLE":
            issue["paths"] = list(set(missing_exe))


        result.append(issue)


    return result



def diagnostic_report(log_file):

    logs = load_logs(log_file)


    report = {

        "status": "OK",

        "summary": {
            "total_logs": len(logs),
            "errors": 0,
            "warnings": 0,
        },

        "system": {},

        "profiles": Counter(),

        "issues": []
    }



    for entry in logs:

        level = entry.get("level", "")
        message = entry.get("message", "")


        if level == "ERROR":
            report["summary"]["errors"] += 1


        elif level == "WARNING":
            report["summary"]["warnings"] += 1



        # System

        if "System information:" in message:

            for line in message.splitlines():

                if "gpu:" in line:
                    report["system"]["gpu"] = (
                        line.split(":")[1].strip()
                    )

                if "desktop:" in line:
                    report["system"]["desktop"] = (
                        line.split(":")[1].strip()
                    )



        # Profiles

        if "Apply PROFILE=" in message:

            profile = (
                message
                .split("PROFILE=")[1]
                .split("|")[0]
                .strip()
            )

            report["profiles"][profile] += 1



    report["profiles"] = dict(report["profiles"])


    report["issues"] = analyze_issues(logs)



    # Détermination état

    critical = any(
        x["severity"] == "high"
        for x in report["issues"]
    )

    warning = any(
        issue["severity"] == "medium"
        for issue in report["issues"]
    )



    if critical:
        report["status"] = "ERROR"

    elif warning:
        report["status"] = "WARNING"

    else:
        report["status"] = "OK"


    if not logs:
        report["status"] = "NO_DATA"



    return report
