System Information Retriever 
This is a simple and fast Python program that retrieves and displays detailed system information for your CPU, GPU, and RAM. It's designed to be used on Windows and uses the psutil and wmi libraries for efficient data retrieval.

Prerequisites
You'll need to have Python 3 installed on your system.

Getting Started
Follow these steps to get a copy of the project up and running on your local machine.

Installation
Clone this repository to your local machine:

Bash

git clone https://github.com/Bencantest/SysInfoRetriever.git
Navigate to the project directory:

Bash

cd SysInfoRetriever
Install the required libraries:

Bash

pip install -r requirements.txt
Usage
To run the program, simply execute the following command from the project directory:

Bash

python get_sys_info.py
The program will then print your system's specifications to the console in a clear, organized format.

Note 💡
This program utilizes Windows-specific libraries (wmi) to get detailed information about the GPU and RAM speed. If you run this script on a non-Windows operating system, it will fall back to using psutil for basic CPU and RAM information, but GPU details will not be available.
