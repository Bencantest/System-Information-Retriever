import platform
import psutil
import socket
import wmi 
import os

def get_system_info():
    
    #Retrieves and print and print system information: CPU, GPU and RAM
    
    if os.name != 'nt':
        print("This script is optimized for Windows to get detailed GPU and RAM speed info.")
        print("Falling back to psutil for a basic overview.")
        
        print("\n--- CPU Information ---")
        print(f"Name: {platform.processor()}")
        print(f"Physical cores: {psutil.cpu_count(logical=False)}")
        print(f"Logical processors: {psutil.cpu_count(logical=True)}")
        
        # GPU Info (Not available via psutil)
        print("\n--- GPU Information ---")
        print("GPU information is not available using psutil.")
        
        print("\n--- RAM Information ---")
        mem_info = psutil.virtual_memory()
        print(f"Total: {round(mem_info.total / (1024 ** 3), 2)} GB")
        return

    
    try:
        c = wmi.WMI()
    except wmi.WMI:
        print("Error: The 'wmi' library is not installed or configured correctly.")
        print("Please install it by running: pip install wmi")
        return

    print("\n--- CPU Information ---")
    try:
        cpu_info = c.Win32_Processor()[0]
        print(f"Name: {cpu_info.Name.strip()}")
        print(f"Cores: {cpu_info.NumberOfCores}")
        print(f"Threads: {cpu_info.NumberOfLogicalProcessors}")
        print(f"Max Clock Speed: {round(cpu_info.MaxClockSpeed / 1000, 2)} GHz")
    except Exception as e:
        print(f"Could not retrieve CPU information: {e}")

    print("\n--- GPU Information ---")
    try:
        gpu_info = c.Win32_VideoController()[0]
        vram_gb = round(gpu_info.AdapterRAM / (1024 ** 3), 2)
        print(f"Name: {gpu_info.Name}")
        print(f"VRAM: {vram_gb} GB")
    except Exception as e:
        print(f"Could not retrieve GPU information: {e}")
        
    print("\n--- RAM Information ---")
    try:
        # Get total memory using psutil
        total_mem_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        print(f"Total Physical Memory: {total_mem_gb} GB")

        # Get detailed memory chip info using WMI 
        for mem_chip in c.Win32_PhysicalMemory():
            print(f"  Device Locator: {mem_chip.DeviceLocator}")
            print(f"  Speed: {mem_chip.Speed} MHz")
            print(f"  Memory Type: {mem_chip.SMBIOSMemoryType}")

    except Exception as e:
        print(f"Could not retrieve RAM information: {e}")


if __name__ == "__main__":
    get_system_info()
