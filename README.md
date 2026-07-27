# System Information Retriever

A simple, fast Python tool that retrieves and displays detailed system information:
**CPU, GPU, RAM, Disk, Network, Battery, OS/BIOS, and Uptime.**

Runs on any OS. On **Windows**, it uses `wmi` for rich detail (CPU model, GPU VRAM,
RAM stick speed/type, motherboard, BIOS, SSD/HDD detection). On **Linux/macOS**, it
falls back to `psutil`/`platform` for a solid overview (GPU model detail is
Windows-only).

---

## Features

- **CPU** — cores, threads, current usage %, model name and clock speed (Windows)
- **GPU** — name and VRAM (Windows only)
- **RAM** — total/used/available, usage %, per-stick speed & type (Windows)
- **Disk** — every mounted partition: capacity, free space, usage %, and SSD/HDD type
- **Network** — interfaces, IP addresses, MAC addresses, link status, active connection count
- **Battery** — charge %, plugged-in status, time remaining (laptops)
- **OS / BIOS** — OS version/build, architecture, hostname, motherboard model, BIOS version (Windows)
- **Uptime** — boot time and time since boot
- **Export** — save the full report as `.json`, `.csv`, or `.txt`

---

## Prerequisites

- Python 3.0+

---

## Getting Started

### Installation

1. **Clone this repository:**

   ```bash
   git clone https://github.com/Bencantest/SysInfoRetriever.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd SysInfoRetriever
   ```

3. **Install required libraries:**

   ```bash
   pip install -r requirements.txt
   ```

### Usage

Print a full report to the terminal:

```bash
python SysInfoRetriever.py
```

Export the report to a file (format is inferred from the extension):

```bash
python SysInfoRetriever.py --export report.json
python SysInfoRetriever.py --export report.csv
python SysInfoRetriever.py --export report.txt
```

---

## ⚠️ Notes

- On non-Windows systems, `wmi` isn't imported at all, and the script uses
  `psutil`/`platform` for everything. GPU model/VRAM, per-stick RAM speed, and
  motherboard/BIOS detail remain Windows-only since there's no cross-platform
  equivalent of WMI.
- Reading active network connections may require elevated privileges
  (Administrator on Windows, root on Linux/macOS) — if permission is denied,
  the script reports that instead of crashing.
- SSD/HDD detection on Linux reads `/sys/block/*/queue/rotational`; on Windows
  it uses `Win32_DiskDrive.MediaType` via WMI. Detection can be "Unknown" on
  unusual storage setups (e.g. virtual disks, network drives).
