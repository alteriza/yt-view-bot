# YouTube View Bot Traffic

A simple YouTube viewer bot traffic application optimized for Linux, developed and tested on ArchLinux XFCE. This script is fully written in Python and uses a graphical user interface (UI).

## Prerequisites

Before setting up the project, make sure you have the following installed on your Linux system:
* **Python 3** (and `python3-venv` package if you are on Ubuntu/Debian)
* **Git**

## Installation

Follow these steps to clone the repository and set up the local environment:

### 1. Clone the Repository
Open your terminal and run the following command to download the source code:
```bash
git clone https://github.com
cd yt-view-bot
```

### 2. Set Up a Virtual Environment (venv)
Create a localized environment to keep the required Python packages isolated from your system-wide packages:
```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment
Activate the environment before installing dependencies or running the script:
```bash
source venv/bin/activate
```
*(Your terminal prompt should now show `(venv)` at the beginning).*

### 4. Install Dependencies
Install all required Python libraries listed in the requirements file:
```bash
pip install -r req.txt
```

---

## Configuration & Usage

Before launching the app, you can configure your list of proxies in the `proxies.txt` file inside the repository folder.

### Running the Application
Once the dependencies are installed and the `venv` is active, launch the GUI interface by running:
```bash
python ui.py
```

### Deactivating the Environment
When you are done using the application, you can safely close the virtual environment by executing:
```bash
deactivate
```

---

## Repository Files

* `ui.py` — The graphical user interface framework.
* `main.py` — The core logic running the traffic automation.
* `proxies.txt` — Configuration file for inputting your proxy server lists.
* `req.txt` — Contains the exact external libraries required for execution.

## License

This project is licensed under the [MIT License](LICENSE).
