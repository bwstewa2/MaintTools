import os, sys

ZERO = str(0)+'\u00b0'
NINTY = str(90)+'\u00b0'
ONE_EIGHTY = str(180)+'\u00b0'
TWO_SEVENTY = str(270)+'\u00b0'
ALIGNER = 1
STATION = 0
WAFER_SIZE = {'8\"':203.2, '6\"': 152.4}
WAFER_IMAGE_SIZE = 210
ZOOM_MIN = 1
ZOOM_MAX = 4

def get_md_filepath(md_filename):
        if hasattr(sys, '_MEIPASS'):
            # Running as compiled executable
            return os.path.join(sys._MEIPASS, md_filename)
        else:
            # Running as script
            return os.path.join(".", md_filename)

__root = os.path.expanduser("~")
os.makedirs(f"{__root}/DeltaPy", exist_ok=True)
SETTING_FILE = f"{__root}/DeltaPy/Settings.csv"
ABOUT_FILE = get_md_filepath("README.md")
HISTORY_FILE = f"{__root}/DeltaPy/History.csv"

def open_about():
    os.startfile(ABOUT_FILE, 'open')

def open_history():
    os.startfile(HISTORY_FILE, 'open')

def open_settings():
    os.startfile(SETTING_FILE, 'open')