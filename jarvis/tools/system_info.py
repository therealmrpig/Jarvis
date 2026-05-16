import platform
import subprocess
from jarvis.tools.registry import registry


@registry.register(name="get_system_info", description="Get system information including CPU usage, memory usage, disk usage, uptime, and macOS version.")
def get_system_info() -> str:
    try:
        os_version = platform.platform()

        uptime = subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip()

        disk = subprocess.run(["df", "-h", "/"], capture_output=True, text=True).stdout.strip()
        disk_line = disk.split("\n")[1] if "\n" in disk else disk

        mem = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout.strip()
        pages = {}
        for line in mem.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                pages[k.strip()] = v.strip().rstrip(".")

        active = int(pages.get("Pages active", "0"))
        wired = int(pages.get("Pages wired down", "0"))
        free = int(pages.get("Pages free", "0"))
        page_size = 16384
        used_gb = (active + wired) * page_size / 1e9
        free_gb = free * page_size / 1e9

        cpu = subprocess.run(["top", "-l", "1", "-n", "0", "-F"], capture_output=True, text=True, timeout=2)
        cpu_line = ""
        for line in cpu.stdout.split("\n"):
            if "CPU usage" in line:
                cpu_line = line.strip()
                break

        return f"OS: {os_version}\nUptime: {uptime}\nCPU: {cpu_line}\nMemory: {used_gb:.1f}GB used, {free_gb:.1f}GB free\nDisk (/): {disk_line}"
    except Exception as e:
        return f"Error getting system info: {str(e)}"
