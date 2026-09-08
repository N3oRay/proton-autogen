import psutil


class SystemMonitor:
    CPU_WARNING_THRESHOLD = 80.0
    CPU_CRITICAL_THRESHOLD = 95.0

    MEMORY_WARNING_THRESHOLD = 80.0
    MEMORY_CRITICAL_THRESHOLD = 95.0

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=0.5)

    def get_memory_usage(self):
        return psutil.virtual_memory().percent

    def get_cpu_count(self):
        return psutil.cpu_count(logical=True) or 1

    def get_status(self):
        cpu = self.get_cpu_usage()
        memory = self.get_memory_usage()

        if (
            cpu >= self.CPU_CRITICAL_THRESHOLD
            or memory >= self.MEMORY_CRITICAL_THRESHOLD
        ):
            level = "critical"
            ok = False
        elif (
            cpu >= self.CPU_WARNING_THRESHOLD
            or memory >= self.MEMORY_WARNING_THRESHOLD
        ):
            level = "warning"
            ok = False
        else:
            level = "ok"
            ok = True

        return {
            "ok": ok,
            "level": level,
            "cpu": cpu,
            "memory": memory,
            "cpu_count": self.get_cpu_count(),
        }
