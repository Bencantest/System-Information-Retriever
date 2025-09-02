# System Information Retriever

A simple and fast Python program that retrieves and displays detailed system information for your **CPU**, **GPU**, and **RAM**.  
Designed primarily for **Windows**, this script uses the `psutil` and `wmi` libraries for efficient data retrieval.

---

##  Prerequisites

- Python 3 must be installed on your system.
- The script was developed and tested with **Python 3**.

---

##  Getting Started

To get a copy of this project up and running on your local machine, follow these steps:

###  Installation

1. **Clone this repository** to your local machine:

   ```bash
   git clone https://github.com/Bencantest/SysInfoRetriever.git

2.  **Navigate to the project directory:**

     cd SysInfoRetriever

3.  **Install required libraries:**   
    pip install -r requirements.txt

4.  **Usage**
  To run the program, execute the following command from the project directory:
      python get_sys_info.py

5. **⚠️ Note**

This program utilizes Windows-specific libraries (specifically wmi) to retrieve detailed GPU and RAM speed information.

On non-Windows systems, the script falls back to using psutil to retrieve basic CPU and RAM information.

GPU details will not be available on non-Windows platforms.



      
