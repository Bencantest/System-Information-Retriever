
import argparse
import csv
import json
import os
import platform
import socket
from datetime import datetime, timedelta

import psutil

# wmi is only available (and only useful) on Windows.
try:
    import wmi
    WMI_AVAILABLE = os.name == 'nt'
except ImportError:
    WMI_AVAILABLE = False

# Human-readable RAM type codes (SMBIOSMemoryType from WMI).
_MEMORY_TYPE_MAP = {
    20: "DDR", 21: "DDR2", 22: "DDR2 FB-DIMM", 24: "DDR3",
    26: "DDR4", 34: "DDR5",
}


def _safe(fn, default="N/A"):
    
    try:
        return fn()
    except Exception:
        return default


def get_os_bios_info():
    
    info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "OS Release": platform.release(),
        "Platform": platform.platform(),
        "Architecture": platform.machine(),
        "Hostname": socket.gethostname(),
    }

    if WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            bios = c.Win32_BIOS()[0]
            info["BIOS Manufacturer"] = _safe(lambda: bios.Manufacturer.strip())
            info["BIOS Version"] = _safe(lambda: bios.SMBIOSBIOSVersion.strip())
            info["BIOS Release Date"] = _safe(lambda: bios.ReleaseDate)
        except Exception as e:
            info["BIOS Error"] = str(e)

        try:
            board = c.Win32_BaseBoard()[0]
            info["Motherboard Manufacturer"] = _safe(lambda: board.Manufacturer.strip())
            info["Motherboard Model"] = _safe(lambda: board.Product.strip())
        except Exception as e:
            info["Motherboard Error"] = str(e)

    return info


def get_cpu_info():
    info = {
        "Physical Cores": psutil.cpu_count(logical=False),
        "Logical Processors": psutil.cpu_count(logical=True),
        "Current Usage %": psutil.cpu_percent(interval=0.5),
    }

    if WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            for i, cpu in enumerate(c.Win32_Processor()):
                prefix = "" if i == 0 else f" (CPU {i + 1})"
                info[f"Name{prefix}"] = cpu.Name.strip()
                info[f"Max Clock Speed{prefix} (GHz)"] = round(cpu.MaxClockSpeed / 1000, 2)
        except Exception as e:
            info["Error"] = str(e)
    else:
        info["Name"] = platform.processor() or "Unknown"

    return info


def get_gpu_info():
    info = {}

    if WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            gpus = c.Win32_VideoController()
            if not gpus:
                info["Status"] = "No GPU detected"
            for i, gpu in enumerate(gpus):
                prefix = "" if i == 0 else f" (GPU {i + 1})"
                info[f"Name{prefix}"] = gpu.Name
                try:
                    vram_gb = round(gpu.AdapterRAM / (1024 ** 3), 2)
                    info[f"VRAM{prefix} (GB)"] = vram_gb
                except Exception:
                    info[f"VRAM{prefix} (GB)"] = "Unavailable"
        except Exception as e:
            info["Error"] = str(e)
    else:
        info["Status"] = "GPU info not available on this platform via psutil"

    return info


def get_ram_info():
    mem = psutil.virtual_memory()
    info = {
        "Total (GB)": round(mem.total / (1024 ** 3), 2),
        "Available (GB)": round(mem.available / (1024 ** 3), 2),
        "Used (GB)": round(mem.used / (1024 ** 3), 2),
        "Usage %": mem.percent,
    }

    if WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            for i, chip in enumerate(c.Win32_PhysicalMemory()):
                label = chip.DeviceLocator or f"Module {i + 1}"
                mem_type = _MEMORY_TYPE_MAP.get(chip.SMBIOSMemoryType, f"Unknown ({chip.SMBIOSMemoryType})")
                info[f"{label} Speed (MHz)"] = chip.Speed
                info[f"{label} Type"] = mem_type
        except Exception as e:
            info["Chip Detail Error"] = str(e)

    return info


def _disk_type_windows(device_path):
    
    try:
        c = wmi.WMI()
        for drive in c.Win32_DiskDrive():
            media = (drive.MediaType or "").lower()
            if "ssd" in media or "solid state" in media:
                return "SSD"
            if "fixed hard disk" in media:
                return "HDD (or unspecified)"
        return "Unknown"
    except Exception:
        return "Unknown"


def _disk_type_linux(device_path):
    
    try:
        dev_name = os.path.basename(device_path.rstrip("/"))
        # Strip partition numbers, e.g. sda1 -> sda
        base = dev_name.rstrip("0123456789")
        path = f"/sys/block/{base}/queue/rotational"
        if os.path.exists(path):
            with open(path) as f:
                return "HDD" if f.read().strip() == "1" else "SSD"
    except Exception:
        pass
    return "Unknown"


def get_disk_info():
    disks = []
    for part in psutil.disk_partitions(all=False):
        entry = {
            "Device": part.device,
            "Mountpoint": part.mountpoint,
            "Filesystem": part.fstype,
        }
        try:
            usage = psutil.disk_usage(part.mountpoint)
            entry["Total (GB)"] = round(usage.total / (1024 ** 3), 2)
            entry["Used (GB)"] = round(usage.used / (1024 ** 3), 2)
            entry["Free (GB)"] = round(usage.free / (1024 ** 3), 2)
            entry["Usage %"] = usage.percent
        except (PermissionError, OSError):
            entry["Status"] = "Not accessible"
            disks.append(entry)
            continue

        if os.name == 'nt' and WMI_AVAILABLE:
            entry["Type"] = _disk_type_windows(part.device)
        elif platform.system() == "Linux":
            entry["Type"] = _disk_type_linux(part.device)
        else:
            entry["Type"] = "Unknown"

        disks.append(entry)

    return {"partitions": disks}


def get_network_info():
    info = {"interfaces": {}, "active_connections": None}

    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    for iface, addr_list in addrs.items():
        iface_info = {"is_up": stats[iface].isup if iface in stats else "Unknown"}
        for addr in addr_list:
            family = addr.family.name if hasattr(addr.family, "name") else str(addr.family)
            iface_info.setdefault(family, []).append(addr.address)
        info["interfaces"][iface] = iface_info

    try:
        conns = psutil.net_connections(kind="inet")
        established = [c for c in conns if c.status == "ESTABLISHED"]
        info["active_connections"] = len(established)
    except (psutil.AccessDenied, PermissionError):
        info["active_connections"] = "Permission denied (try running as admin/root)"

    return info


def get_battery_info():
    battery = psutil.sensors_battery()
    if battery is None:
        return {"Status": "No battery detected (desktop system or unsupported OS)"}

    return {
        "Percent": battery.percent,
        "Plugged In": battery.power_plugged,
        "Time Left": (
            "Calculating..." if battery.secsleft == psutil.POWER_TIME_UNLIMITED
            else "Unknown" if battery.secsleft == psutil.POWER_TIME_UNKNOWN
            else str(timedelta(seconds=battery.secsleft))
        ),
    }


def get_uptime_info():
    boot_timestamp = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_timestamp)
    uptime = datetime.now() - boot_time
    return {
        "Boot Time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Uptime": str(timedelta(seconds=int(uptime.total_seconds()))),
    }


def collect_all_info():
    return {
        "OS / BIOS": get_os_bios_info(),
        "CPU": get_cpu_info(),
        "GPU": get_gpu_info(),
        "RAM": get_ram_info(),
        "Disk": get_disk_info(),
        "Network": get_network_info(),
        "Battery": get_battery_info(),
        "Uptime": get_uptime_info(),
    }


def print_report(data):
    for section, content in data.items():
        print(f"\n--- {section} Information ---")
        if section == "Disk":
            for disk in content.get("partitions", []):
                print(f"  Device: {disk.get('Device')}")
                for k, v in disk.items():
                    if k != "Device":
                        print(f"    {k}: {v}")
        elif section == "Network":
            for iface, details in content.get("interfaces", {}).items():
                print(f"  Interface: {iface}")
                for k, v in details.items():
                    print(f"    {k}: {v}")
            print(f"  Active Connections: {content.get('active_connections')}")
        else:
            for k, v in content.items():
                print(f"{k}: {v}")


def _flatten(data, parent_key=""):
    
    rows = []
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}.{k}" if parent_key else str(k)
            rows.extend(_flatten(v, new_key))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            rows.extend(_flatten(item, f"{parent_key}[{i}]"))
    else:
        rows.append((parent_key, data))
    return rows


def export_report(data, filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".json":
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

    elif ext == ".csv":
        rows = _flatten(data)
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Key", "Value"])
            writer.writerows(rows)

    elif ext == ".txt":
        with open(filepath, "w") as f:
            for section, content in data.items():
                f.write(f"--- {section} Information ---\n")
                for key, value in _flatten(content):
                    f.write(f"{key}: {value}\n")
                f.write("\n")

    else:
        raise ValueError(f"Unsupported export format: '{ext}'. Use .json, .csv, or .txt")

    print(f"\nReport exported to: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Retrieve and display system information.")
    parser.add_argument(
        "--export",
        metavar="FILEPATH",
        help="Export the report to a file. Format is inferred from extension: .json, .csv, or .txt",
    )
    args = parser.parse_args()

    if os.name != 'nt':
        print("Note: Full CPU model, GPU, motherboard/BIOS, and RAM speed detail")
        print("require Windows (WMI). Other sections work on any OS.\n")

    data = collect_all_info()
    print_report(data)

    if args.export:
        export_report(data, args.export)


if __name__ == "__main__":
    main()