# system_monitor.py

import psutil


class SystemMonitor:

    CPU_WARNING_THRESHOLD = 80.0

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=0.5)

    def get_status(self):
        cpu = self.get_cpu_usage()

        if cpu >= self.CPU_WARNING_THRESHOLD:
            return {
                "ok": False,
                "cpu": cpu,
            }

        return {
            "ok": True,
            "cpu": cpu,
        }
