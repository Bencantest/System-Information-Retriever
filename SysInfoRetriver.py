import platform
import psutil
import socket
import wmi
import os

def get_system_info():
    """
    Retrieves and prints detailed system information for CPU, GPU, and RAM.
    It uses the psutil library for cross-platform information and the wmi library
    specifically for detailed Windows-based information as requested.
    """
    # Check if the platform is Windows, as the WMI calls are specific to Windows.
    if os.name != 'nt':
        print("This script is optimized for Windows to get detailed GPU and RAM speed info.")
        print("Falling back to psutil for a basic overview.")
        
        # CPU Info (fallback)
        print("\n--- CPU Information ---")
        print(f"Name: {platform.processor()}")
        print(f"Physical cores: {psutil.cpu_count(logical=False)}")
        print(f"Logical processors: {psutil.cpu_count(logical=True)}")
        
        # GPU Info (Not available via psutil)
        print("\n--- GPU Information ---")
        print("GPU information is not available using psutil.")
        
        # RAM Info (fallback)
        print("\n--- RAM Information ---")
        mem_info = psutil.virtual_memory()
        print(f"Total: {round(mem_info.total / (1024 ** 3), 2)} GB")
        return

    # WMI is a Windows-specific library for interacting with Windows Management Instrumentation.
    # It requires the 'wmi' and 'pywin32' packages.
    try:
        c = wmi.WMI()
    except wmi.WMI:
        print("Error: The 'wmi' library is not installed or configured correctly.")
        print("Please install it by running: pip install wmi")
        return

    # --- CPU Information ---
    print("\n--- CPU Information ---")
    try:
        cpu_info = c.Win32_Processor()[0]
        print(f"Name: {cpu_info.Name.strip()}")
        print(f"Cores: {cpu_info.NumberOfCores}")
        print(f"Threads: {cpu_info.NumberOfLogicalProcessors}")
        print(f"Max Clock Speed: {round(cpu_info.MaxClockSpeed / 1000, 2)} GHz")
    except Exception as e:
        print(f"Could not retrieve CPU information: {e}")

    # --- GPU Information ---
    print("\n--- GPU Information ---")
    try:
        gpu_info = c.Win32_VideoController()[0]
        vram_gb = round(gpu_info.AdapterRAM / (1024 ** 3), 2)
        print(f"Name: {gpu_info.Name}")
        print(f"VRAM: {vram_gb} GB")
    except Exception as e:
        print(f"Could not retrieve GPU information: {e}")
        
    # --- RAM Information ---
    print("\n--- RAM Information ---")
    try:
        # Get total memory using psutil, which is reliable
        total_mem_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        print(f"Total Physical Memory: {total_mem_gb} GB")

        # Get detailed memory chip info using WMI as requested
        for mem_chip in c.Win32_PhysicalMemory():
            print(f"  Device Locator: {mem_chip.DeviceLocator}")
            print(f"  Speed: {mem_chip.Speed} MHz")
            print(f"  Memory Type: {mem_chip.SMBIOSMemoryType}")

    except Exception as e:
        print(f"Could not retrieve RAM information: {e}")


if __name__ == "__main__":
    get_system_info()
