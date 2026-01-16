# GameDev.tv Video Downloader

A Python tool used to download your purchased courses on [GameDev.tv](https://gamedev.tv/), a platform for game development tutorials.

### Prerequisites:
1. **Python 3.14.2** (Tested Version). Ensure Python is installed on your machine. You can download it [here](https://www.python.org/downloads/).
2. **Selenium-Wire**: This tool is used for web scraping in this project. Make sure it's installed by running:

```bash
pip install selenium-wire
```

3. I recommend that you create a virtual environment to manage dependencies separately:

```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/macOS
.\venv\Scripts\activate   # For Windows
```

### Installation:

1. Download the Python file (`gamedevtv-download.py`) from this repository.
2. Navigate to the directory where the file is located.

### Usage:
Run the following command in your terminal:
`python3 gamedevtv-download.py -e [your email] -p [your password]`

Replace [your email] with your GameDev.tv account email.
Replace [your password] with your GameDev.tv account password.

Example:
`python3 gamedevtv-download.py -e game@dev.com -p my_password`

Wait for the program to log in to your GameDev.tv account.
A list of available courses will appear, and you can select which ones to download by typing the course numbers (e.g., 1, 3-6, 8).

### Example:
```
[eric@eric-ms7e06 Desktop]$ python3 gamedevtv-download.py -e game@dev.com -p my_password
Logging in as game@dev.com...

The following courses are available. Make a selection with the courses you wish to download.
(e.g., '1, 3-6, 8')

==== AVAILABLE COURSES ====
1: unreal-game-feel
2: unity-rpg-core-combat
3: unreal-action-combat
4: unreal-environment-design
5: cpp-fundamentals
6: unreal-action-adventure

Type the range of courses to download: 1, 3-4
Starting download for unreal-game-feel...
(Downloads shown here)
```

### Important Notes:
- Pagination does not work with this script. Anything that appears on the first page of your Dashboard will be detected. I do not have enough courses to implement pagination yet. This script will be updated when I can fully test it.
- Having a fast internet connection is important. If your internet is too slow, and it takes 30+ seconds to load a course, it will be skipped. You will be missing content.
- This was only tested on Linux. Windows/MacOS 

### Collaboration:
- Feel free to open any issues if you have troubles with the script, and I will do my best to respond and patch the issues.
