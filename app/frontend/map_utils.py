from pathlib import Path

LATEST_MAP_FILE = Path("")
DEFAULT_MAP_FILE = Path("static/default_map.html")

def cleanup_dir():
    """remove all html maps except the latest map and the default map"""
    static_dir = Path("static")
    keep_files = {LATEST_MAP_FILE.name, DEFAULT_MAP_FILE.name}
    for file in static_dir.glob("*.html"):
        if file.name not in keep_files:
            file.unlink()

def get_latest_map_path():
    """get the path of the latest HTML map file"""
    global LATEST_MAP_FILE
    try:
        latest_map_path = Path("static/latest_map.txt").read_text().strip()
        new_map_file = Path(latest_map_path)
        if str(new_map_file) != str(LATEST_MAP_FILE):
            LATEST_MAP_FILE = new_map_file
    except Exception:
        LATEST_MAP_FILE = DEFAULT_MAP_FILE

    cleanup_dir()
    return str(LATEST_MAP_FILE)
